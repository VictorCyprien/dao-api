from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.treasury import Token, Transfer
from api.schemas.communs_schemas import PagingError
from api.schemas.treasury_schemas import TransferSchema, TransferSchemaResponse, TransferCreateSchema
from api.views.treasury.treasury_blp import blp as treasury_blp
from helpers.errors_file import BadRequest, ErrorHandler, NotFound
from helpers.logging_file import Logger

logger = Logger()

@treasury_blp.route("/daos/<string:dao_id>/transfers")
class DAOTransfersView(MethodView):
    @treasury_blp.doc(operationId='GetDAOTransfers')
    @treasury_blp.response(404, PagingError, description="DAO not found")
    @treasury_blp.response(200, TransferSchema(many=True), description="List of all transfers for the DAO")
    @jwt_required()
    def get(self, dao_id: str):
        """Get all transfers for a specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Check if DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get all transfers for the DAO
        transfers = Transfer.get_by_dao_id(dao_id, db.session)
        
        return transfers
    
    @treasury_blp.arguments(TransferCreateSchema)
    @treasury_blp.doc(operationId='CreateDAOTransfer')
    @treasury_blp.response(404, PagingError, description="DAO not found")
    @treasury_blp.response(401, PagingError, description="Unauthorized")
    @treasury_blp.response(201, TransferSchemaResponse, description="Transfer created successfully")
    @jwt_required()
    def post(self, input_data: Dict, dao_id: str):
        """Create a new transfer for a specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Check if DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if token exists and belongs to the DAO
        token = Token.get_by_id(input_data["token_id"], db.session)
        if not token:
            raise NotFound(ErrorHandler.TOKEN_NOT_FOUND)
        
        if token.dao_id != dao_id:
            raise BadRequest(ErrorHandler.TOKEN_NOT_BELONG_TO_DAO)
        
        # Create the transfer
        try:
            transfer = Transfer.create(input_data)
            db.session.add(transfer)
            
            # Update token amount based on the transfer
            # If the DAO receives tokens, increase the amount; if it sends tokens, decrease it
            # We're assuming the DAO's address is either the sender or receiver
            dao_members = [member.wallet_address for member in dao.members]
            
            if transfer.to_address in dao_members:
                # DAO is receiving tokens
                token.amount += transfer.amount
            elif transfer.from_address in dao_members:
                # DAO is sending tokens
                token.amount -= transfer.amount
            
            db.session.commit()
            
            return {
                "action": "created",
                "transfer": transfer
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error creating transfer: {error}")
            raise BadRequest(ErrorHandler.TRANSFER_CREATE_ERROR)
        