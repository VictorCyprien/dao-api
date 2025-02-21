from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from api.models.pod import POD
from api.models.community import Community
from api.models.user import User
from api.schemas.pod_schemas import PODSchema
from api.schemas.communs_schemas import PagingError
from api.views.pods.pod_blp import pod_blp

from helpers.errors_file import ErrorHandler, NotFound, Unauthorized

@pod_blp.route("/community/<int:community_id>/pods")
class RootPODView(MethodView):
    @jwt_required()
    @pod_blp.response(404, PagingError)
    @pod_blp.response(200, PODSchema(many=True))
    def get(self, community_id: int):
        """List all PODs in a community"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
        
        if auth_user not in community.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        return POD.query.filter_by(community_id=community_id).all()

    @jwt_required()
    @pod_blp.arguments(PODSchema)
    @pod_blp.response(404, PagingError)
    @pod_blp.response(403, PagingError)
    @pod_blp.response(400, PagingError)
    @pod_blp.response(201, PODSchema)
    def post(self, pod_data, community_id):
        """Create a new POD in a community"""
        db: SQLAlchemy = current_app.db
        current_user_id = get_jwt_identity()
        
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        # Check if user is admin or owner
        if (community.owner_id != current_user_id and 
            current_user_id not in [admin.user_id for admin in community.admins]):
            raise Unauthorized(ErrorHandler.USER_NOT_ADMIN)
            
        try:
            pod = POD.create(pod_data)
            db.session.add(pod)
            db.session.commit()
            return pod
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e)) 