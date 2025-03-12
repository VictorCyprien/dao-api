from typing import Dict

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
from helpers.errors_file import ErrorHandler, NotFound, BadRequest
from helpers.logging_file import Logger

logger = Logger()

@daos_blp.route("/")
class RootDAOsView(MethodView):
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
            dao = DAO.create(input_data)
            dao.admins.append(auth_user)
            dao.members.append(auth_user)
            db.session.add(dao)
            db.session.commit()
            
            return {
                "action": "created",
                "dao": dao
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error creating DAO: {error}")
            raise BadRequest(ErrorHandler.DAO_CREATE)
