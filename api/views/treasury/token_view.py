from typing import Dict, List

from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from api.models.dao import DAO
from api.models.treasury import Token
from api.schemas.treasury_schemas import TokenCreateSchema, TokenSchema, TokenSchemaResponse, TokenUpdateSchema
from api.schemas.communs_schemas import PagingError
from api.views.treasury.treasury_blp import blp as treasury_blp
from helpers.errors_file import ErrorHandler, NotFound, BadRequest
from helpers.logging_file import Logger
from helpers.cache_decorator import cached_view
from helpers.build_cache_key import make_token_key

logger = Logger()

@treasury_blp.route("/daos/<string:dao_id>/tokens")
class TokensView(MethodView):
    @treasury_blp.doc(operationId='GetDAOTokens')
    @treasury_blp.response(404, PagingError, description="DAO not found")
    @treasury_blp.response(200, TokenSchema(many=True), description="List of all tokens for the DAO")
    @jwt_required()
    @cached_view(timeout=1800, make_key=make_token_key)
    def get(self, dao_id: str):
        """Get all tokens for a specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Check if DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if DAO has a treasury wallet address
        if not dao.treasury_address:
            raise NotFound(ErrorHandler.DAO_NO_TREASURY)
        
        # Get all tokens for the DAO
        tokens = Token.get_by_wallet_address(dao.treasury_address, db.session)
        
        return tokens
    
    # @treasury_blp.arguments(TokenCreateSchema)
    # @treasury_blp.doc(operationId='CreateToken')
    # @treasury_blp.response(404, PagingError, description="DAO not found")
    # @treasury_blp.response(400, PagingError, description="Bad Request")
    # @treasury_blp.response(201, TokenSchemaResponse, description="Token created successfully")
    # @jwt_required()
    # def post(self, input_data: Dict, dao_id: str):
    #     """Create a new token for a specific DAO"""
    #     db: SQLAlchemy = current_app.db
        
    #     # Check if DAO exists
    #     dao = DAO.get_by_id(dao_id, db.session)
    #     if not dao:
    #         raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
    #     # Create the token
    #     try:
    #         token = Token.create(input_data)
    #         db.session.add(token)
    #         db.session.commit()
            
    #         return {
    #             "action": "created",
    #             "token": token
    #         }
    #     except Exception as error:
    #         db.session.rollback()
    #         logger.error(f"Error creating token: {error}")
    #         raise BadRequest(ErrorHandler.TOKEN_CREATE_ERROR)
