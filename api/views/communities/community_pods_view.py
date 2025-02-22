from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from api.models.pod import POD
from api.models.community import Community
from api.models.user import User
from api.schemas.pod_schemas import PODMembershipSchema, PODSchema, PODUpdateSchema
from api.schemas.communs_schemas import PagingError
from api.schemas.users_schemas import UserSchema
from api.views.communities.communities_blp import communities_blp

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized


@communities_blp.route("<int:community_id>/pods")
class RootPODView(MethodView):
    @jwt_required()
    @communities_blp.response(404, PagingError)
    @communities_blp.response(200, PODSchema(many=True))
    def get(self, community_id: int):
        """List all PODs in a community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        
        if auth_user not in community.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        return POD.get_community_pods(community_id, db.session)

    @jwt_required()
    @communities_blp.arguments(PODSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(201, PODSchema)
    def post(self, pod_data, community_id):
        """Create a new POD in a community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        # Check if user is admin
        if auth_user not in community.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        try:
            pod = POD.create(pod_data)
            db.session.add(pod)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


@communities_blp.route("<int:community_id>/pods/<int:pod_id>")
class PODView(MethodView):
    @communities_blp.response(404, PagingError)
    @communities_blp.response(200, PODSchema)
    def get(self, community_id: int, pod_id: int):
        """Get a POD"""
        db: SQLAlchemy = current_app.db
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        return pod

    @jwt_required()
    @communities_blp.arguments(PODUpdateSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, PODSchema)
    def put(self, pod_data, community_id: int, pod_id: int):
        """Update a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        # Check if user is a admin of the community
        if auth_user not in community.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        try:
            pod.update(pod_data)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


    @jwt_required()
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, PODSchema)
    def delete(self, community_id, pod_id):
        """Delete a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)

        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        if community.owner_id != auth_user.user_id and auth_user not in community.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        try:
            db.session.delete(pod)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


@communities_blp.route("<int:community_id>/pods/<int:pod_id>/members")
class PODMembersView(MethodView):
    @communities_blp.response(404, PagingError)
    @communities_blp.response(200, UserSchema(many=True))
    def get(self, community_id: int, pod_id: int):
        """Get all participants of a POD"""
        db: SQLAlchemy = current_app.db
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
            
        return pod.participants

    @jwt_required()
    @communities_blp.arguments(PODMembershipSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, PODSchema)
    def post(self, membership_data, community_id, pod_id):
        """Join a POD as a participant"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        target_user = User.get_by_id(membership_data["user_id"], db.session)
        
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        
        # Check if user is a member of the community
        if target_user not in community.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)

        # Check if user is a admin of the community
        if auth_user not in community.admins:
            # If user is not a admin, check if they are the target user
            if target_user != auth_user:
                raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)

        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        if not pod.add_participant(target_user):
            raise BadRequest(ErrorHandler.USER_ALREADY_IN_POD)
        
        db.session.commit()
        return pod


    @jwt_required()
    @communities_blp.arguments(PODMembershipSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, PODSchema)
    def delete(self, membership_data, community_id, pod_id):
        """Leave a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        target_user = User.get_by_id(membership_data["user_id"], db.session)

        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        
        # Check if user is a member of the community
        if target_user not in community.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)

        # Check if user is a admin of the community
        if auth_user not in community.admins:
            # If user is not a admin, check if they are the target user
            if target_user != auth_user:
                raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)

        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)

        if not pod.remove_participant(target_user):
            raise BadRequest(ErrorHandler.USER_NOT_IN_POD)
        
        db.session.commit()
        return pod
