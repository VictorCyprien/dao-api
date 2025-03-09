from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy


from api.models.pod import POD
from api.models.dao import DAO
from api.models.user import User
from api.schemas.pod_schemas import PODMembershipSchema, PODSchema, PODUpdateSchema
from api.schemas.communs_schemas import PagingError
from api.schemas.users_schemas import UserSchema
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized


@daos_blp.route("<string:dao_id>/pods")
class RootPODView(MethodView):

    @daos_blp.doc(operationId='GetAllPODsForDAO')
    @jwt_required(fresh=True)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(200, PODSchema(many=True))
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
        
        return POD.get_dao_pods(dao_id, db.session)


    @daos_blp.doc(operationId='CreatePOD')
    @jwt_required(fresh=True)
    @daos_blp.arguments(PODSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(201, PODSchema)
    def post(self, pod_data, dao_id: str):
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
            pod = POD.create(pod_data)
            db.session.add(pod)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>")
class PODView(MethodView):
    @daos_blp.doc(operationId='GetPODById')
    @daos_blp.response(404, PagingError)
    @daos_blp.response(200, PODSchema)
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


    @daos_blp.doc(operationId='UpdatePOD')
    @jwt_required(fresh=True)
    @daos_blp.arguments(PODUpdateSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, PODSchema)
    def put(self, pod_data, dao_id: str, pod_id: str):
        """Update a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        # Check if user is a admin of the DAO
        if auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        try:
            pod.update(pod_data)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


    @daos_blp.doc(operationId='DeletePOD')
    @jwt_required(fresh=True)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, PODSchema)
    def delete(self, dao_id, pod_id):
        """Delete a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)

        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        if dao.owner_id != auth_user.user_id and auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        try:
            db.session.delete(pod)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/members")
class PODMembersView(MethodView):
    @daos_blp.doc(operationId='GetAllMembersOfPOD')
    @daos_blp.response(404, PagingError)
    @daos_blp.response(200, UserSchema(many=True))
    def get(self, dao_id: str, pod_id: str):
        """Get all members of a POD"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        return pod.members


    @daos_blp.doc(operationId='AddMemberToPOD')
    @jwt_required(fresh=True)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, PODSchema)
    def post(self, dao_id: str, pod_id: str):
        """Add a member to a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)

        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        if not pod.add_member(auth_user):
            raise BadRequest(ErrorHandler.USER_ALREADY_IN_POD)
        
        db.session.commit()
        return pod


    @daos_blp.doc(operationId='RemoveMemberFromPOD')
    @jwt_required(fresh=True)
    @daos_blp.arguments(PODMembershipSchema)
    @daos_blp.response(404, PagingError)
    @daos_blp.response(403, PagingError)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(200, PODSchema)
    def delete(self, member_data, dao_id: str, pod_id: str):
        """Remove a member from a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        target_user = User.get_by_id(member_data["user_id"], db.session)
        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)

        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        if target_user not in dao.members:
            raise BadRequest(ErrorHandler.USER_NOT_MEMBER)
        
        # Check if user is a member of the DAO
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        if auth_user.user_id != target_user.user_id:
            if auth_user not in dao.admins and auth_user.user_id != dao.owner_id:
                raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)

        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.dao_id != dao_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)

        if not pod.remove_member(target_user):
            raise BadRequest(ErrorHandler.USER_NOT_IN_POD)
        
        db.session.commit()
        return pod
