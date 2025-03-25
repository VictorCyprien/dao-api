from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.schemas.dao_schemas import (
    DAOSchema,
    DAOUpdateSchema,
    DAOSchemaResponse
)
from api.schemas.communs_schemas import PagingError
from api.views.daos.daos_blp import blp as daos_blp
from helpers.errors_file import BadRequest, NotFound, ErrorHandler, Unauthorized
from helpers.logging_file import Logger
from helpers.minio_file import MinioHelper


logger = Logger()


@daos_blp.route("/<string:dao_id>")
class OneDAOView(MethodView):
    @daos_blp.doc(operationId='GetDAOById')
    @daos_blp.response(404, PagingError, description="DAO not found")
    @daos_blp.response(200, DAOSchema, description="DAO retrieved successfully")
    def get(self, dao_id: str):
        """Get a DAO by ID"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        if dao.profile_picture is not None:
            dao.profile_picture = MinioHelper.get_cached_file_url(dao.profile_picture)
        if dao.banner_picture is not None:
            dao.banner_picture = MinioHelper.get_cached_file_url(dao.banner_picture)
        
        return dao
    

    @daos_blp.arguments(DAOUpdateSchema)
    @daos_blp.doc(operationId='UpdateDAO')
    @daos_blp.response(404, PagingError, description="DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @daos_blp.response(200, DAOSchemaResponse, description="DAO updated successfully")
    @jwt_required(fresh=True)
    def put(self, input_data: Dict, dao_id: str):
        """Update a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if user is owner or admin
        if dao.owner_id != auth_user.user_id or auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.DAO_NOT_ADMIN)
        
        try:
            # Update DAO
            dao.update(input_data)
            db.session.commit()
            
            return {
                "action": "updated",
                "dao": dao
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error updating DAO: {error}")
            raise BadRequest(ErrorHandler.DAO_UPDATE)


    @daos_blp.doc(operationId='DeleteDAO')
    @daos_blp.response(404, PagingError, description="DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Error deleting DAO")
    @daos_blp.response(200, DAOSchemaResponse, description="DAO deleted successfully")
    @jwt_required(fresh=True)
    def delete(self, dao_id: str):
        """Delete a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if user is owner
        if auth_user.user_id != dao.owner_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        try:
            # Delete DAO
            db.session.delete(dao)
            db.session.commit()
            return {
                "action": "deleted",
                "dao": dao
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error deleting DAO: {error}")
            raise BadRequest(ErrorHandler.DAO_DELETE)
