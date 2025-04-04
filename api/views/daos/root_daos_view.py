from typing import Dict, List
import requests
import json
import datetime
import pytz

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.models.wallet_monitor import WalletMonitor
from api.schemas.dao_schemas import (
    DAOSchema, 
    InputCreateDAOSchema,
    DAOSchemaResponse,
)
from api.schemas.communs_schemas import PagingError

from api.views.daos.daos_blp import blp as daos_blp
from api.views.daos.dao_view_handler import DaoViewHandler

from api.config import config

from helpers.errors_file import ErrorHandler, NotFound, BadRequest
from helpers.logging_file import Logger
from helpers.minio_file import MinioHelper



logger = Logger()

@daos_blp.route("/")
class RootDAOsView(DaoViewHandler):
    @daos_blp.doc(operationId='GetAllDAOs')
    @daos_blp.response(200, DAOSchema(many=True), description="List of all DAOs")
    def get(self):
        """List all DAOs"""
        db: SQLAlchemy = current_app.db
        daos = DAO.get_all(db.session)

        # Set profile pictures for all daos
        [setattr(dao, "profile_picture", MinioHelper.get_cached_file_url(dao.profile_picture, config.MINIO_BUCKET_DAOS)) if dao.profile_picture is not None else None for dao in daos]

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
        
        # Validate treasury wallet address if provided
        if input_data.get("treasury", None) is not None:
            if not self._check_if_wallet_is_valid(input_data["treasury"]):
                raise BadRequest(ErrorHandler.INVALID_WALLET_ADDRESS)

        try:
            # Create the DAO and assign admin/member roles
            dao = DAO.create(input_data)
            dao.admins.append(auth_user)
            dao.members.append(auth_user)
            db.session.add(dao)
            
            # Check if a treasury wallet address was provided
            if dao.treasury_address:
                self._add_wallet_to_surveillance(dao, db)
            
            
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error creating DAO: {error}")
            raise BadRequest(f"Unable to create the DAO: {str(error)}")
        
        return {
            "action": "created",
            "dao": dao
        }
