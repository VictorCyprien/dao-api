from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from api.models.pod import POD
from api.models.dao import DAO
from api.models.user import User
from api.schemas.pod_schemas import (
    PODMembershipResponseSchema,
    PODMembershipSchema,
    PODSchema, 
    InputCreatePODSchema,
    PODSchemaResponse,
    PODUpdateSchema,
)
from api.schemas.communs_schemas import PagingError
from api.schemas.users_schemas import UserSchema
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized
from helpers.logging_file import Logger

logger = Logger()


@daos_blp.route("<string:dao_id>/pods")
class RootPODView(MethodView):

    @daos_blp.doc(operationId='GetAllPODsForDAO')
    @daos_blp.response(404, PagingError, description="User or DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(200, PODSchema(many=True), description="List of all PODs for the DAO")
    @jwt_required(fresh=True)
    def get(self, dao_id: str):
        """Get all PODs for a DAO"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        pods = POD.get_dao_pods(dao_id, db.session)
        return pods


    @daos_blp.arguments(InputCreatePODSchema)
    @daos_blp.doc(operationId='CreatePOD')
    @daos_blp.response(404, PagingError, description="User or DAO not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @daos_blp.response(201, PODSchemaResponse, description="POD created successfully")
    @jwt_required(fresh=True)
    def post(self, input_data: Dict, dao_id: str):
        """Create a new POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Check if user is admin
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        try:
            # Ensure dao_id in the body matches the URL parameter
            pod = POD.create(input_data)
            pod.add_member(auth_user)
            db.session.add(pod)
            db.session.commit()
            
            return {
                "action": "created",
                "pod": pod
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error creating POD: {error}")
            raise BadRequest(ErrorHandler.POD_CREATE)


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>")
class PODView(MethodView):
    @daos_blp.doc(operationId='GetPODById')
    @daos_blp.response(404, PagingError, description="DAO or POD not found")
    @daos_blp.response(200, PODSchema, description="POD retrieved successfully")
    def get(self, dao_id: str, pod_id: str):
        """Get a POD by ID"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        return pod


    @daos_blp.arguments(PODUpdateSchema)
    @daos_blp.doc(operationId='UpdatePOD')
    @daos_blp.response(404, PagingError, description="User, DAO or POD not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @daos_blp.response(200, PODSchemaResponse, description="POD updated successfully")
    @jwt_required(fresh=True)
    def put(self, input_data: Dict, dao_id: str, pod_id: str):
        """Update a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Check if user is admin
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        # Get POD
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        try:
            # Update POD
            pod.update(input_data)
            db.session.commit()
            
            return {
                "action": "updated",
                "pod": pod
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error updating POD: {error}")
            raise BadRequest(ErrorHandler.POD_UPDATE)


    @daos_blp.doc(operationId='DeletePOD')
    @daos_blp.response(404, PagingError, description="User, DAO or POD not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Error deleting POD")
    @daos_blp.response(200, PODSchemaResponse, description="POD deleted successfully")
    @jwt_required(fresh=True)
    def delete(self, dao_id, pod_id):
        """Delete a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Check if user is admin
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        # Get POD
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        if dao.owner_id != auth_user.user_id and auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        try:
            # Delete POD
            db.session.delete(pod)
            db.session.commit()
            return {
                "action": "deleted",
                "pod": pod
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error deleting POD: {error}")
            raise BadRequest(ErrorHandler.POD_DELETE)


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/members")
class PODMembersView(MethodView):
    @daos_blp.doc(operationId='GetAllMembersOfPOD')
    @daos_blp.response(404, PagingError, description="DAO or POD not found")
    @daos_blp.response(200, UserSchema(many=True), description="List of all members in the POD")
    def get(self, dao_id: str, pod_id: str):
        """Get all members of a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Get POD
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        return pod.members


    @daos_blp.doc(operationId='AddMemberToPOD')
    @daos_blp.response(404, PagingError, description="User, DAO or POD not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - User already in POD")
    @daos_blp.response(200, PODMembershipResponseSchema, description="User added to POD successfully")
    @jwt_required(fresh=True)
    def post(self, dao_id: str, pod_id: str):
        """Add a member to a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Get POD
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        # Add user to POD
        if not pod.add_member(auth_user):
            raise BadRequest(ErrorHandler.USER_ALREADY_IN_POD)
        
        db.session.commit()
        return {
            "action": "added",
            "pod": pod
        }


    @daos_blp.arguments(PODMembershipSchema)
    @daos_blp.doc(operationId='RemoveMemberFromPOD')
    @daos_blp.response(404, PagingError, description="User, DAO or POD not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - User not in POD")
    @daos_blp.response(200, PODMembershipResponseSchema, description="User removed from POD successfully")
    @jwt_required(fresh=True)
    def delete(self, input_data: Dict, dao_id: str, pod_id: str):
        """Remove a member from a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Get POD
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        # Get user to remove
        user_to_remove = User.get_by_id(input_data["user_id"], db.session)
        if not user_to_remove:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if user_to_remove.user_id != auth_user.user_id:
            if dao.owner_id != auth_user.user_id and auth_user not in dao.admins:
                raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)

        # Remove user from POD
        if not pod.remove_member(user_to_remove):
            raise BadRequest(ErrorHandler.USER_NOT_MEMBER)
        
        db.session.commit()
        return {
            "action": "removed",
            "pod": pod
        }

