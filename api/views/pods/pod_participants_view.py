from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy

from api.models.pod import POD
from api.models.community import Community
from api.models.user import User
from api.schemas.communs_schemas import PagingError
from api.schemas.pod_schemas import PODSchema
from api.schemas.users_schemas import UserSchema
from api.views.pods.pod_blp import pod_blp
from helpers.errors_file import ErrorHandler, NotFound, Unauthorized

@pod_blp.route("/community/<int:community_id>/pods/<int:pod_id>/participants")
class PODParticipantsView(MethodView):
    @pod_blp.response(404, PagingError)
    @pod_blp.response(200, UserSchema(many=True))
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
    @pod_blp.response(404, PagingError)
    @pod_blp.response(403, PagingError)
    @pod_blp.response(400, PagingError)
    @pod_blp.response(200, PODSchema)
    def post(self, community_id, pod_id):
        """Join a POD as a participant"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        community = Community.get_by_id(community_id, db.session)
        if not community:
            raise NotFound(ErrorHandler.COMMUNITY_NOT_FOUND)
            
        # Check if user is a member of the community
        if auth_user not in [member.user_id for member in community.members]:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
            
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        try:
            if pod.add_participant(auth_user):
                db.session.commit()
                return pod
            abort(400, message="User is already a participant")
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))

    @jwt_required()
    @pod_blp.response(404, PagingError)
    @pod_blp.response(403, PagingError)
    @pod_blp.response(400, PagingError)
    @pod_blp.response(200, PODSchema)
    def delete(self, community_id, pod_id):
        """Leave a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        pod = POD.get_by_id(pod_id, db.session)
        if not pod or pod.community_id != community_id:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        
        try:
            if pod.remove_participant(auth_user):
                db.session.commit()
                return pod
            abort(400, message="User is not a participant")
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e)) 
