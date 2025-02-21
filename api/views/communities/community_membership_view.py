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

from helpers.errors_file import ErrorHandler, NotFound, Unauthorized


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
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user and auth_user not in [admin.user_id for admin in community.admins]:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        user = User.get_by_id(membership_data["user_id"], db.session)
        if not user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        try:
            if community.add_member(user):
                db.session.commit()
                return community
            abort(400, message=ErrorHandler.COMMUNITY_MEMBERSHIP_ALREADY_EXISTS)
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


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
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user and auth_user not in [admin.user_id for admin in community.admins]:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        user = User.get_by_id(membership_data["user_id"], db.session)
        if not user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
            
        try:
            if community.remove_member(user):
                db.session.commit()
                return community
            abort(400, message=ErrorHandler.USER_NOT_MEMBER)
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))

