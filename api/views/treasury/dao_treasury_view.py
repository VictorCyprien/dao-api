from typing import Dict, List

from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.models.treasury import Token, Transfer
from api.views.treasury.treasury_blp import blp as treasury_blp
from api.views.daos.dao_view_handler import DaoViewHandler
from helpers.errors_file import ErrorHandler, NotFound, Unauthorized, BadRequest
from api.schemas.treasury_schemas import TreasurySchema, TreasuryUpdatePercentagesSchema
from api.schemas.communs_schemas import PagingError
from helpers.logging_file import Logger

logger = Logger()

@treasury_blp.route("/daos/<string:dao_id>")
class DAOTreasuryView(DaoViewHandler):
    @treasury_blp.doc(operationId='GetDAOTreasury')
    @treasury_blp.response(404, PagingError, description="DAO not found")
    @treasury_blp.response(200, TreasurySchema, description="Treasury information for a specific DAO")
    @jwt_required()
    def get(self, dao_id: str):
        """Get Treasury information for a specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Check if DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get all tokens for the DAO
        tokens = Token.get_by_dao_id(dao_id, db.session)
        
        # Get recent transfers for the DAO - now directly from the DAO relationship
        recent_transfers = Transfer.get_by_dao_id(dao_id, db.session)[:10]  # Limit to 10 most recent
        
        # Calculate the total value and daily change (simplified)
        total_value = sum(token.amount * token.price for token in tokens)
        
        # In a real implementation, you would calculate these from historical data
        daily_change = 111172.70  # Placeholder value
        daily_change_percentage = 0.42  # Placeholder value
        
        # Create the treasury response
        treasury = {
            "total_value": total_value,
            "daily_change": daily_change,
            "daily_change_percentage": daily_change_percentage,
            "tokens": tokens,
            "recent_transfers": recent_transfers
        }
        
        return treasury 


@treasury_blp.route("/daos/<string:dao_id>/update-percentages")
class DAOTokensPercentagesView(DaoViewHandler):
    @treasury_blp.doc(operationId='UpdateDAOTokenPercentages')
    @treasury_blp.response(404, PagingError, description="DAO not found")
    @treasury_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @treasury_blp.response(400, PagingError, description="Bad Request - Error updating token percentages")
    @treasury_blp.response(200, TreasuryUpdatePercentagesSchema, description="Token percentages updated successfully")
    @jwt_required()
    def put(self, dao_id: str):
        """Update the percentages of tokens in the DAO's treasury without changing prices"""
        db: SQLAlchemy = current_app.db
        
        # Check if DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if user has permission (must be a DAO admin)
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
        
        # Check if there are tokens to update
        tokens = Token.get_by_dao_id(dao_id, db.session)
        if not tokens:
            return {
                "action": "updated_percentages",
                "message": "No tokens found in the treasury to update"
            }
            
        # Update token percentages
        success = self._update_token_percentages(dao_id, db)
        if not success:
            raise BadRequest("Failed to update token percentages")
        
        # Get updated token data
        tokens = Token.get_by_dao_id(dao_id, db.session)
        
        # Get recent transfers
        recent_transfers = Transfer.get_by_dao_id(dao_id, db.session)[:10]
        
        # Calculate the total value
        total_value = sum(token.amount * token.price for token in tokens)
        
        # In a real implementation, you would calculate these from historical data
        daily_change = 111172.70  # Placeholder value
        daily_change_percentage = 0.42  # Placeholder value
        
        # Create the treasury response
        treasury = {
            "action": "updated_percentages",
            "message": "Token percentages updated successfully",
            "total_value": total_value,
            "daily_change": daily_change,
            "daily_change_percentage": daily_change_percentage,
            "tokens": tokens,
            "recent_transfers": recent_transfers
        }
        
        logger.info(f"Successfully updated token percentages for DAO {dao_id}")
        return treasury
