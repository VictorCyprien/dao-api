from flask import jsonify, current_app
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

from api.models.user import User
from api.models.social_connection import SocialConnection
from flask.views import MethodView

from api.schemas.auth_schemas import ConnectionsListSchema, OAuthErrorSchema
from api.schemas.communs_schemas import PagingError

social_connections_blp = Blueprint(
    name='social_connections',
    import_name=__name__,
    description='Social Connections Management',
    url_prefix='/auth/connections'
)

@social_connections_blp.route('', methods=['GET'])
class SocialConnectionsView(MethodView):
    @jwt_required()
    @social_connections_blp.doc(operationId='GetSocialConnections',
                               summary="Get user's social connections",
                               description="Returns all social connections for the authenticated user.")
    @social_connections_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @social_connections_blp.response(404, OAuthErrorSchema, description="User not found")
    @social_connections_blp.response(500, OAuthErrorSchema, description="Server error")
    @social_connections_blp.response(200, ConnectionsListSchema, description="List of social connections")
    def get(self):
        """
        Get all social connections for the authenticated user
        """
        user_id = get_jwt_identity()
        
        try:
            # Get database session
            db = current_app.db
            session = db.session
            
            # Get user with social connections
            user = session.query(User).options(
                joinedload(User.social_connections)
            ).filter_by(user_id=user_id).first()
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Return connections
            connections = [connection.to_dict() for connection in user.social_connections]
            
            return jsonify({
                "connections": connections,
                "discord_connected": any(c.provider == "discord" for c in user.social_connections),
                "twitter_connected": any(c.provider == "twitter" for c in user.social_connections),
                "telegram_connected": any(c.provider == "telegram" for c in user.social_connections)
            }), 200
        except Exception as e:
            current_app.logger.error(f"Error getting social connections: {str(e)}")
            return jsonify({"error": "Failed to get social connections"}), 500 