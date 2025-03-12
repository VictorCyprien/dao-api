from typing import Dict, List

from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.treasury import Token, Transfer
from api.views.treasury.treasury_blp import blp as treasury_blp
from helpers.errors_file import ErrorHandler, NotFound
from api.schemas.treasury_schemas import TreasurySchema
from api.schemas.communs_schemas import PagingError

@treasury_blp.route("/daos/<string:dao_id>")
class DAOTreasuryView(MethodView):
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