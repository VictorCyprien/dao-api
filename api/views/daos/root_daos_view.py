from typing import Dict, List
import requests
import json

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.schemas.dao_schemas import (
    DAOSchema, 
    InputCreateDAOSchema,
    DAOSchemaResponse,
)
from api.schemas.communs_schemas import PagingError

from api.views.daos.daos_blp import blp as daos_blp
from api.views.daos.dao_view_handler import DaoViewHandler

from helpers.errors_file import ErrorHandler, NotFound, BadRequest
from helpers.logging_file import Logger
from helpers.minio_file import minio_manager


logger = Logger()

@daos_blp.route("/")
class RootDAOsView(DaoViewHandler):
    @daos_blp.doc(operationId='GetAllDAOs')
    @daos_blp.response(200, DAOSchema(many=True), description="List of all DAOs")
    def get(self):
        """List all DAOs"""
        db: SQLAlchemy = current_app.db
        daos = DAO.get_all(db.session)
        return daos


    @daos_blp.arguments(InputCreateDAOSchema)
    @daos_blp.doc(operationId='CreateDAO')
    @daos_blp.response(404, PagingError, description="User not found") 
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @daos_blp.response(201, DAOSchemaResponse, description="DAO created successfully")
    @jwt_required(fresh=True)
    def post(self, input_data: Dict):
        """Create a new DAO"""
        db: SQLAlchemy = current_app.db

        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)

        try:
            # Create the DAO and assign admin/member roles
            dao = DAO.create(input_data)
            dao.admins.append(auth_user)
            dao.members.append(auth_user)
            db.session.add(dao)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error creating DAO: {error}")
            raise BadRequest(f"Unable to create the DAO: {str(error)}")
        
        # Try to fetch wallet data and add tokens to the DAO's treasury
        try:
            wallet_data = self._fetch_wallet_data(auth_user.wallet_address)
            
            # Add tokens from wallet to DAO treasury
            tokens_added = self._add_tokens_to_treasury(wallet_data, dao.dao_id, db)
            
            # Update token percentages
            if tokens_added > 0:
                self._update_token_percentages(dao.dao_id, db)
            
        except Exception as wallet_error:
            logger.error(f"Error processing wallet data: {wallet_error}")
        
        return {
            "action": "created",
            "dao": dao
        }
