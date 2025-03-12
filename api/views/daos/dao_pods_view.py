from flask import current_app, jsonify
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from flask_pydantic import validate


from api.models.pod import POD
from api.models.dao import DAO
from api.models.user import User
from api.schemas.pydantic_schemas import (
    POD as PODModel,
    InputCreatePOD,
    PODUpdate,
    PODMembership,
    User as UserModel,
    PagingError
)
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized


@daos_blp.route("<string:dao_id>/pods")
class RootPODView(MethodView):

    @daos_blp.doc(operationId='GetAllPODsForDAO')
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
        
        # Convert to Pydantic models using POD's serialization method
        pod_models = [PODModel.model_validate(pod.to_dict()) for pod in pods]
        return [pod_model.model_dump() for pod_model in pod_models]


    @daos_blp.doc(operationId='CreatePOD')
    @jwt_required(fresh=True)
    @validate(body=InputCreatePOD)
    def post(self, body: InputCreatePOD, dao_id: str):
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
            pod_data = body.model_dump(exclude_unset=True)
            pod = POD.create(pod_data)
            db.session.add(pod)
            db.session.commit()
            
            # Convert to Pydantic model
            pod_model = PODModel.model_validate(pod.to_dict())
            return jsonify(pod_model.model_dump()), 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>")
class PODView(MethodView):
    @daos_blp.doc(operationId='GetPODById')
    def get(self, dao_id: str, pod_id: str):
        """Get a POD by ID"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        # Convert to Pydantic model
        pod_model = PODModel.model_validate(pod.to_dict())
        return pod_model.model_dump()


    @daos_blp.doc(operationId='UpdatePOD')
    @jwt_required(fresh=True)
    @validate(body=PODUpdate)
    def put(self, body: PODUpdate, dao_id: str, pod_id: str):
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
            pod.update(body.model_dump(exclude_unset=True))
            db.session.commit()
            
            # Convert to Pydantic model
            pod_model = PODModel.model_validate(pod.to_dict())
            return pod_model.model_dump()
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


    @daos_blp.doc(operationId='DeletePOD')
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
            return {}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/members")
class PODMembersView(MethodView):
    @daos_blp.doc(operationId='GetAllMembersOfPOD')
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
            
        # Convert members to Pydantic models
        member_models = [UserModel.model_validate(member.to_dict()) for member in pod.members]
        return [member_model.model_dump() for member_model in member_models]


    @daos_blp.doc(operationId='AddMemberToPOD')
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
        pod_model = PODModel.model_validate(pod.to_dict())
        return pod_model.model_dump()


    @daos_blp.doc(operationId='RemoveMemberFromPOD')
    @jwt_required(fresh=True)
    @validate(body=PODMembership)
    def delete(self, body: PODMembership, dao_id: str, pod_id: str):
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
            
        # Check if user is admin
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        # Get POD
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        # Get user to remove
        user_to_remove = User.get_by_id(body.user_id, db.session)
        if not user_to_remove:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        # Remove user from POD
        if not pod.remove_member(user_to_remove):
            raise BadRequest(ErrorHandler.USER_NOT_MEMBER)
        
        db.session.commit()
        pod_model = PODModel.model_validate(pod.to_dict())
        return pod_model.model_dump()

