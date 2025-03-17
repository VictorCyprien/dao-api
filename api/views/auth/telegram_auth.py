from flask import request, redirect, jsonify, current_app
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import hashlib
import hmac
from datetime import datetime
import pytz

from api.models.user import User
from api.models.social_connection import SocialConnection
from .oauth_view_handler import OAuthViewHandler

from api.schemas.auth_schemas import (
    ConnectionResponseSchema,
    DisconnectResponseSchema,
    OAuthErrorSchema,
    TelegramAuthSchema
)
from api.schemas.communs_schemas import PagingError

telegram_auth_blp = Blueprint(
    name='telegram_auth',
    import_name=__name__,
    description='Telegram authentication integration',
    url_prefix='/auth/telegram'
)

@telegram_auth_blp.route('/callback', methods=['POST'])
class TelegramCallbackView(OAuthViewHandler):
    @jwt_required()
    @telegram_auth_blp.arguments(TelegramAuthSchema, location="json")
    @telegram_auth_blp.doc(operationId='TelegramCallback',
                           summary="Process Telegram authentication data",
                           description="Handles the authentication data from the Telegram Login Widget.")
    @telegram_auth_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @telegram_auth_blp.response(400, OAuthErrorSchema, description="Invalid or missing data")
    @telegram_auth_blp.response(500, OAuthErrorSchema, description="Error saving connection")
    @telegram_auth_blp.response(200, ConnectionResponseSchema, description="Account successfully linked")
    def post(self, telegram_data):
        """
        Handle callback data from Telegram Login Widget
        This endpoint processes data sent from the frontend after Telegram Login Widget has been used
        """
        user_id = get_jwt_identity()
        
        self.logger.info(f"Telegram callback received for user_id: {user_id}")
        
        if not telegram_data:
            self.logger.error("Telegram callback - No data provided")
            return jsonify({"error": "No data provided"}), 400
        
        # Verify the authentication data
        verification_result = self.verify_telegram_data(telegram_data)
        if not verification_result:
            self.logger.error("Telegram callback - Invalid authentication data")
            return jsonify({"error": "Invalid authentication data"}), 400
        
        # Save Telegram connection
        db = current_app.db
        result = self.save_telegram_connection(user_id, telegram_data, db.session)
        if not result:
            self.logger.error("Telegram callback - Failed to save connection")
            return jsonify({"error": "Failed to save Telegram connection"}), 500
        
        self.logger.info("Telegram callback - Account linked successfully")
        return jsonify({"message": "Telegram account linked successfully"}), 200


@telegram_auth_blp.route('/disconnect', methods=['DELETE'])
class TelegramDisconnectView(OAuthViewHandler):
    @jwt_required()
    @telegram_auth_blp.doc(operationId='DisconnectTelegram',
                           summary="Disconnect Telegram account",
                           description="Removes the connection between the user's account and their Telegram account.")
    @telegram_auth_blp.response(200, DisconnectResponseSchema, description="Connection successfully removed")
    @telegram_auth_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @telegram_auth_blp.response(404, OAuthErrorSchema, description="No connection found")
    @telegram_auth_blp.response(500, OAuthErrorSchema, description="Error disconnecting account")
    def delete(self):
        """
        Disconnect Telegram account from user account
        """
        user_id = get_jwt_identity()
        
        try:
            # Get database session
            db = current_app.db
            session = db.session
            
            # Find the Telegram connection
            connection = session.query(SocialConnection).filter_by(
                user_id=user_id,
                provider='telegram'
            ).first()
            
            if not connection:
                return jsonify({"error": "No Telegram connection found"}), 404
            
            # Remove Telegram username from user
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.telegram_username = None
            
            # Delete the connection
            session.delete(connection)
            session.commit()
            
            return jsonify({"message": "Telegram connection removed successfully"}), 200
        except Exception as e:
            self.logger.error(f"Error disconnecting Telegram: {str(e)}")
            session.rollback()
            return jsonify({"error": "Failed to disconnect Telegram account"}), 500 