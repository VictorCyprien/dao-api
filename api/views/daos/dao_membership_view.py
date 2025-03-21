from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from typing import Dict

from api.models.dao import DAO
from api.models.user import User
from api.schemas.dao_schemas import DAOMembershipResponseSchema, DAOSchema, DAOMembershipSchema
from api.schemas.communs_schemas import PagingError
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized
from helpers.logging_file import Logger

logger = Logger()


@daos_blp.route("/<string:dao_id>/members")
class DAOMembershipView(MethodView):
    
    @daos_blp.doc(operationId='AddMemberToDAO')
    @daos_blp.response(404, PagingError, description="User or DAO not found")
    @daos_blp.response(400, PagingError, description="Bad Request")
    @daos_blp.response(200, DAOMembershipResponseSchema, description="User added to DAO successfully")
    @jwt_required(fresh=True)
    def post(self, dao_id: str):
        """Add a member to a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Check if user is a member of the DAO
        if not dao.add_member(auth_user):
            raise BadRequest(ErrorHandler.DAO_MEMBERSHIP_ALREADY_EXISTS)
        
        # Add user to DAO
        db.session.commit()
        
        return {
            "action": "added",
            "dao": dao
        }

            
    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.doc(operationId='RemoveMemberFromDAO')
    @daos_blp.response(404, PagingError, description="User or DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized")
    @daos_blp.response(400, PagingError, description="Bad Request")
    @daos_blp.response(200, DAOMembershipResponseSchema, description="User removed from DAO successfully")
    @jwt_required(fresh=True)
    def delete(self, input_data: Dict, dao_id: str):
        """Remove a member from a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        target_user = User.get_by_id(input_data["user_id"], db.session)
        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if target_user.user_id == dao.owner_id:
            raise BadRequest(ErrorHandler.CANNOT_REMOVE_OWNER)
        
        if target_user.user_id != auth_user.user_id:
            if dao.owner_id != auth_user.user_id and auth_user not in dao.admins:
                raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        if not dao.remove_member(target_user):
            raise BadRequest(ErrorHandler.USER_NOT_MEMBER)
        
        db.session.commit()
        return {
            "action": "removed",
            "dao": dao
        }


@daos_blp.route("/<string:dao_id>/admins")
class DAOAdminView(MethodView):
    
    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.doc(operationId='AddAdminToDAO')
    @daos_blp.response(404, PagingError, description="User or DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized")
    @daos_blp.response(400, PagingError, description="Bad Request")
    @daos_blp.response(200, DAOMembershipResponseSchema, description="User added to DAO successfully")
    @jwt_required(fresh=True)
    def post(self, input_data: Dict, dao_id: str):
        """Add an admin to a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Only the owner can add admins
        if auth_user.user_id != dao.owner_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
        
        target_user = User.get_by_id(input_data["user_id"], db.session)
        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not dao.add_admin(target_user):
            raise BadRequest(ErrorHandler.DAO_ADMIN_ALREADY_EXISTS)
        
        db.session.commit()
        return {
            "action": "added",
            "dao": dao
        }


    @daos_blp.arguments(DAOMembershipSchema)
    @daos_blp.doc(operationId='RemoveAdminFromDAO')
    @daos_blp.response(404, PagingError, description="User or DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized")
    @daos_blp.response(400, PagingError, description="Bad Request")
    @daos_blp.response(200, DAOMembershipResponseSchema, description="User removed from DAO successfully")
    @jwt_required(fresh=True)
    def delete(self, input_data: Dict, dao_id: str):
        """Remove an admin from a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Get user to remove as admin
        user_to_remove = User.get_by_id(input_data["user_id"], db.session)
        if not user_to_remove:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Check permissions
        if auth_user.user_id != user_to_remove.user_id:  # If not removing self
            if auth_user.user_id != dao.owner_id:
                raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
                
        # Cannot remove the owner as admin
        if user_to_remove.user_id == dao.owner_id:
            raise BadRequest(ErrorHandler.CANNOT_REMOVE_OWNER)
            
        # Remove user as admin
        if not dao.remove_admin(user_to_remove):
            raise BadRequest(ErrorHandler.USER_NOT_ADMIN)
        
        db.session.commit()
        return {
            "action": "removed",
            "dao": dao
        }
