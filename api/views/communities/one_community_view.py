from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from api.models.community import Community
from api.models.user import User
from api.schemas.community_schemas import CommunitySchema, CommunityUpdateSchema, CommunityMembershipSchema
from api.schemas.communs_schemas import PagingError
from api.views.communities.communities_blp import communities_blp

from helpers.errors_file import ErrorHandler, NotFound, Unauthorized

@communities_blp.route("/<int:community_id>")
class OneCommunityView(MethodView):
    @jwt_required()
    @communities_blp.response(404, PagingError)
    @communities_blp.response(200, CommunitySchema)
    def get(self, community_id: int):
        """Get a specific community"""
        db: SQLAlchemy = current_app.db
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        return community

    @communities_blp.arguments(CommunityUpdateSchema)
    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200, CommunitySchema)
    @jwt_required()
    def put(self, update_data, community_id):
        """Update a community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user.user_id or auth_user not in community.admins:
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        try:
            community.update(update_data)
            db.session.commit()
            return community
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


    @communities_blp.response(404, PagingError)
    @communities_blp.response(403, PagingError)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(200)
    @jwt_required()
    def delete(self, community_id: int):
        """Delete a community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        if community.owner_id != auth_user.user_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
            
        try:
            db.session.delete(community)
            db.session.commit()
            return {"message": "Community deleted"}
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))

