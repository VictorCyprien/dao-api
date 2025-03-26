from typing import Dict

from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

import requests
from requests.exceptions import Timeout, RequestException

import datetime
import pytz

import re

from api.models import Token
from api.config import config
from api.models.dao import DAO
from api.models.wallet_monitor import WalletMonitor

from helpers.logging_file import Logger


logger = Logger()

class DaoViewHandler(MethodView):
    def _check_if_wallet_is_valid(self, wallet_address: str) -> bool:
        """
        Check if a wallet address is a valid Solana address
        
        Solana addresses:
        - Are base58 encoded
        - Are 32-44 characters long
        - Should not contain invalid base58 characters
        """
        if wallet_address is None or wallet_address == "":
            return False
        
        # Base58 alphabet: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
        # Check length (typical Solana addresses are 32-44 chars)
        if not (32 <= len(wallet_address) <= 44):
            return False
            
        # Check if it only contains valid base58 characters
        base58_pattern = re.compile(r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$')
        if not base58_pattern.match(wallet_address):
            return False
            
        return True


    def _add_wallet_to_surveillance(self, dao: DAO, db: SQLAlchemy) -> bool:
        """
        Add a wallet address to the wallets_to_monitor table using the WalletMonitor model
        
        Args:
            dao: The DAO object that contains the treasury wallet address
            db: SQLAlchemy database instance
            
        Returns:
            True if the wallet was added successfully, False otherwise
        """
        try:
            # Check if wallet is already being monitored
            existing = WalletMonitor.get_by_address(dao.treasury_address, db.session)
            if existing:
                logger.info(f"Wallet {dao.treasury_address} is already being monitored")
                return True
                
            # Create and add the new wallet monitor entry
            wallet_monitor = WalletMonitor.create(dao.treasury_address)
            db.session.add(wallet_monitor)
            
            logger.info(f"Added treasury wallet {dao.treasury_address} to monitoring for DAO {dao.dao_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding wallet to monitoring: {e}")
            return False
        
    
    def _delete_wallet_from_surveillance(self, dao: DAO, wallet_address: str, db: SQLAlchemy) -> bool:
        """
        Delete a wallet address from the wallets_to_monitor table using the WalletMonitor model
        
        Args:
            wallet_address: The address of the wallet to delete from the wallets_to_monitor table   
            db: SQLAlchemy database instance
            
        Returns:
            True if the wallet was deleted successfully, False otherwise
        """
        try:
            # Get the wallet monitor entry to delete
            wallet_monitor = WalletMonitor.get_by_address(wallet_address, db.session)
            if not wallet_monitor:
                logger.info(f"Wallet {wallet_address} not found in monitoring")
                return True
            
            # Delete the wallet monitor entry   
            db.session.delete(wallet_monitor)
            logger.info(f"Deleted treasury wallet {wallet_address} from monitoring for DAO {dao.dao_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting wallet from monitoring: {e}")
            return False
    

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
