from typing import Dict

from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy

import requests
from requests.exceptions import Timeout, RequestException

from api.models import Token
from api.config import config

from helpers.logging_file import Logger


logger = Logger()

class DaoViewHandler(MethodView):
    def _fetch_wallet_data(self, wallet_address: str) -> Dict:
        """
        Fetch wallet data from the wallet API
        
        Args:
            wallet_address: The wallet address to fetch data for
            
        Returns:
            Dict containing wallet data from the API
        """
        api_host = config.WALLET_API_HOST
        timeout = config.WALLET_API_TIMEOUT

        # Format the URL according to the API docs
        api_url = f"{api_host}/api/wallets/{wallet_address}"
        headers = {
            "Content-Type": "application/json",
        }

        try:    
            response = requests.get(api_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            wallet_data = response.json()
            logger.info(f"Successfully retrieved wallet data for {wallet_address}")
            
            # The API returns data in the format {wallet_address: data}
            # Extract the actual data for easier processing
            if wallet_address in wallet_data:
                return wallet_data[wallet_address]
            return wallet_data
            
        except Timeout as error:
            logger.error(f"Timeout error fetching wallet data: {error}")
            return {"error": f"Timeout error fetching wallet data: {str(error)}"}
        
        except RequestException as error:
            logger.error(f"Error fetching wallet data: {error}")
            return {"error": f"Failed to fetch wallet data: {str(error)}"}
        
            

    def _add_tokens_to_treasury(self, wallet_data: Dict, dao_id: str, db: SQLAlchemy) -> int:
        """
        Process wallet data and add tokens to the DAO's treasury
        
        Args:
            wallet_data: The wallet data from the API
            dao_id: The ID of the DAO to add tokens to
            db: SQLAlchemy database instance
            
        Returns:
            Number of tokens added to the treasury
        """
        if "error" in wallet_data or not wallet_data.get("token_accounts"):
            return 0
            
        token_accounts = wallet_data.get("token_accounts", {})
        tokens_added = 0

        # TODO : Get price of current token with other API (CoinGecko, CoinMarketCap, etc.)
        default_price = config.WALLET_API_DEFAULT_PRICE
        
        for token_address, token_data in token_accounts.items():
            try:
                # Extract token data
                symbol = token_data.get("symbol", token_address[:8] + "...")
                decimals = token_data.get("decimals", 9)
                raw_balance = token_data.get("balance", 0)
                
                # Calculate decimal value (like the API does)
                decimal_value = raw_balance / (10 ** decimals) if decimals > 0 else raw_balance
                
                # Create token input data
                token_input = {
                    "dao_id": dao_id,
                    "name": f"{symbol} Token",
                    "symbol": symbol,
                    "contract": token_address,
                    "amount": decimal_value,
                    "price": default_price,
                    "percentage": 0  # Will be calculated later
                }
                
                # Create and add token
                token = Token.create(token_input)
                db.session.add(token)
                tokens_added += 1
                
            except Exception as e:
                logger.error(f"Error adding token {token_address} to treasury: {e}")
                # Continue with other tokens even if one fails
                continue
                
        # Commit the changes if tokens were added
        if tokens_added > 0:
            try:
                db.session.commit()
                logger.info(f"Added {tokens_added} tokens to DAO {dao_id} treasury")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to commit token changes: {e}")
                return 0
                
        return tokens_added
        

    def _update_token_percentages(self, dao_id: str, db: SQLAlchemy) -> bool:
        """
        Update the percentage values for all tokens in a DAO's treasury
        
        Args:
            dao_id: The ID of the DAO
            db: SQLAlchemy database instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all tokens for the DAO
            tokens = Token.get_by_dao_id(dao_id, db.session)
            
            if not tokens:
                return False
                
            # Calculate total value (sum of amount * price for all tokens)
            total_value = sum(token.amount * token.price for token in tokens)
            
            if total_value <= 0:
                # Set equal percentages if total value is zero or negative
                equal_percentage = round(100 / len(tokens)) if len(tokens) > 0 else 0
                for token in tokens:
                    token.percentage = equal_percentage
            else:
                # Calculate percentage for each token
                for token in tokens:
                    token_value = token.amount * token.price
                    # Calculate percentage and round to nearest integer
                    token.percentage = round((token_value / total_value) * 100)
            
            # Commit changes
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating token percentages: {e}")
            return False
