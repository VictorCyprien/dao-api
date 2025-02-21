from typing import Dict

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
from helpers.errors_file import ErrorHandler, NotFound


@communities_blp.route("/")
class RootCommunitiesView(MethodView):
    @communities_blp.response(200, CommunitySchema(many=True))
    def get(self):
        """List all communities"""
        db: SQLAlchemy = current_app.db
        return Community.get_all(db.session)

    @jwt_required()
    @communities_blp.arguments(CommunitySchema)
    @communities_blp.response(400, PagingError)
    @communities_blp.response(201, CommunitySchema)
    def post(self, community_data: Dict):
        """Create a new community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
            
        try:
            community = Community.create(community_data)
            community.admins.append(auth_user)
            community.members.append(auth_user)
            db.session.add(community)
            db.session.commit()
            return community
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))
