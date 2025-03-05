from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from api.utils import conditional_jwt_required

from api.models.dao import DAO
from api.models.user import User
from api.schemas.dao_schemas import DAOSchema, DAOMembershipSchema
from api.schemas.communs_schemas import PagingError
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import ErrorHandler, NotFound, Unauthorized, BadRequest


@daos_blp.route("/<int:dao_id>/members")
class DAOMembershipView(MethodView):
    @conditional_jwt_required()
    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, DAOSchema)
    def post(self, membership_data, dao_id):
        """Add a member to a DAO"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        dao = DAO.get_by_id(dao_id, db.session)
        target_user = User.get_by_id(membership_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        if dao.owner_id != auth_user.user_id and auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)

        if not dao.add_member(target_user):
            raise BadRequest(ErrorHandler.DAO_MEMBERSHIP_ALREADY_EXISTS)
        
        db.session.commit()
        return dao
    

    @conditional_jwt_required()
    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, DAOSchema)
    def delete(self, membership_data, dao_id):
        """Remove a member from a DAO"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        dao = DAO.get_by_id(dao_id, db.session)
        target_user = User.get_by_id(membership_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        if dao.owner_id != auth_user.user_id and auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        if not dao.remove_member(target_user):
            raise BadRequest(ErrorHandler.USER_NOT_MEMBER)
        
        db.session.commit()
        return dao


@daos_blp.route("/<int:dao_id>/admins")
class DAOAdminView(MethodView):
    @conditional_jwt_required()
    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, DAOSchema)
    def post(self, admin_data, dao_id):
        """Add an admin to a DAO"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        dao = DAO.get_by_id(dao_id, db.session)
        target_user = User.get_by_id(admin_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        if dao.owner_id != auth_user.user_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        if not dao.add_admin(target_user):
            raise BadRequest(ErrorHandler.DAO_ADMIN_ALREADY_EXISTS)
        
        db.session.commit()
        return dao


    @conditional_jwt_required()
    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, DAOSchema)
    def delete(self, admin_data, dao_id):
        """Remove an admin from a DAO"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        dao = DAO.get_by_id(dao_id, db.session)
        target_user = User.get_by_id(admin_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
            
        if dao.owner_id != auth_user.user_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
            
        if not dao.remove_admin(target_user):
            raise BadRequest(ErrorHandler.DAO_NOT_ADMIN)
        
        db.session.commit()
        return dao