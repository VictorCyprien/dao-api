from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from api.models.community import Community
from api.models.user import User
from api.schemas.community_schemas import CommunitySchema, CommunityMembershipSchema
from api.schemas.communs_schemas import PagingError
from api.views.communities.communities_blp import communities_blp

from helpers.errors_file import ErrorHandler, NotFound, Unauthorized, BadRequest


@communities_blp.route("/<int:community_id>/members")
class CommunityMembershipView(MethodView):
    @jwt_required()
    @communities_blp.arguments(CommunityMembershipSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, CommunitySchema)
    def post(self, membership_data, community_id):
        """Add a member to the community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        target_user = User.get_by_id(membership_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user.user_id and auth_user not in community.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)

        if not community.add_member(target_user):
            raise BadRequest(ErrorHandler.COMMUNITY_MEMBERSHIP_ALREADY_EXISTS)
        
        db.session.commit()
        return community


    @jwt_required()
    @communities_blp.arguments(CommunityMembershipSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, CommunitySchema)
    def delete(self, membership_data, community_id):
        """Remove a member from the community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        target_user = User.get_by_id(membership_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user.user_id and auth_user not in community.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        if not community.remove_member(target_user):
            raise BadRequest(ErrorHandler.USER_NOT_MEMBER)
        
        db.session.commit()
        return community


@communities_blp.route("/<int:community_id>/admins")
class CommunityAdminView(MethodView):
    @jwt_required()
    @communities_blp.arguments(CommunityMembershipSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, CommunitySchema)
    def post(self, admin_data, community_id):
        """Add an admin to the community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        target_user = User.get_by_id(admin_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user.user_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        if not community.add_admin(target_user):
            raise BadRequest(ErrorHandler.COMMUNITY_ADMIN_ALREADY_EXISTS)
        
        db.session.commit()
        return community


    @jwt_required()
    @communities_blp.arguments(CommunityMembershipSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, CommunitySchema)
    def delete(self, admin_data, community_id):
        """Remove an admin from the community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        target_user = User.get_by_id(admin_data["user_id"], db.session)

        if not target_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        
        if auth_user not in community.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
            
        if community.owner_id != auth_user.user_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
            
        if not community.remove_admin(target_user):
            raise BadRequest(ErrorHandler.COMMUNITY_NOT_ADMIN)
        
        db.session.commit()
        return community
