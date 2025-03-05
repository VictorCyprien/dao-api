from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from api.utils import conditional_jwt_required

from api.models.dao import DAO
from api.models.user import User
from api.schemas.dao_schemas import DAOSchema, DAOUpdateSchema, DAOMembershipSchema
from api.schemas.communs_schemas import PagingError
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import ErrorHandler, NotFound, Unauthorized


@daos_blp.route("/<string:dao_name>")
class OneDAOByNameView(MethodView):
    @conditional_jwt_required()
    @daos_blp.response(404, PagingError)
    @daos_blp.response(200, DAOSchema)
    def get(self, dao_name: str):
        """Get a DAO by name"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_name(dao_name, db.session)
        if not dao:
            raise NotFound(f"DAO with name '{dao_name}' not found")
        return dao


@daos_blp.route("/<int:dao_id>")
class OneDAOView(MethodView):
    @conditional_jwt_required()
    @daos_blp.response(404, PagingError)
    @daos_blp.response(200, DAOSchema)
    def get(self, dao_id: int):
        """Get a DAO by ID"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(f"DAO with ID {dao_id} not found")
        return dao


    @daos_blp.arguments(DAOUpdateSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, DAOSchema)
    @conditional_jwt_required()
    def put(self, update_data, dao_id):
        """Update a DAO"""
        db: SQLAlchemy = current_app.db
        if not current_app.config.get('AUTH_DISABLED', False):
            auth_user = User.get_by_id(get_jwt_identity(), db.session)
        else:
            auth_user = User.get_by_id(update_data["user_who_made_request"], db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        if dao.owner_id != auth_user.user_id or auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        try:
            dao.update(update_data)
            db.session.commit()
            return dao
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200)
    @conditional_jwt_required()
    def delete(self, user_data: dict, dao_id: int):
        """Delete a DAO"""
        db: SQLAlchemy = current_app.db
        if not current_app.config.get('AUTH_DISABLED', False):
            auth_user = User.get_by_id(get_jwt_identity(), db.session)
        else:
            auth_user = User.get_by_id(user_data["user_who_made_request"], db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)

        dao = DAO.get_by_id(dao_id, db.session)
        
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        if dao.owner_id != auth_user.user_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
            
        try:
            db.session.delete(dao)
            db.session.commit()
            return {"message": "DAO deleted"}
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))

