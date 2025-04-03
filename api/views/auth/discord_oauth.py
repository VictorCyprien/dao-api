from flask import request, redirect, jsonify, current_app, session
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import secrets
import time
from datetime import datetime, timedelta
import pytz
from urllib.parse import urlencode

from api.models.user import User
from api.models.social_connection import SocialConnection
from .oauth_view_handler import OAuthViewHandler
from helpers.redis_file import RedisToken

from api.schemas.auth_schemas import (
    ConnectionResponseSchema,
    DisconnectResponseSchema,
    OAuthErrorSchema,
    OAuthResponseSchema,
    StateValidationErrorSchema,
    TokenExchangeErrorSchema,
    UserInfoErrorSchema
)
from api.schemas.communs_schemas import PagingError

discord_oauth_blp = Blueprint(
    name='discord_oauth',
    import_name=__name__,
    description='Discord OAuth integration',
    url_prefix='/auth/discord'
)

@discord_oauth_blp.route('/connect', methods=['GET'])
class DiscordConnectView(OAuthViewHandler):
    @jwt_required()
    @discord_oauth_blp.doc(operationId='ConnectDiscord',
                           summary="Initiate Discord OAuth flow",
                           description="Redirects the user to Discord's authorization page to begin the OAuth flow.")
    @discord_oauth_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @discord_oauth_blp.response(200, OAuthResponseSchema, description="Return Discord authorization URL")
    def get(self):
        """
        Initiate Discord OAuth flow for linking a Discord account
        """
        config = current_app.config
        user_id = get_jwt_identity()
        
        # Generate and store state token to prevent CSRF
        state_token = secrets.token_urlsafe(32)
        
        # Combine state token with user_id for stateless validation
        # Format: "random_token:user_id"
        state = f"{state_token}:{user_id}"
        
        # Store token in Redis with 1 hour expiry
        redis_token = RedisToken()
        redis_token.set_token(f'discord_oauth_state_{user_id}', state_token, 3600)
        
        # Define Discord OAuth parameters
        params = {
            'client_id': config['DISCORD_CLIENT_ID'],
            'redirect_uri': config['DISCORD_REDIRECT_URI'],
            'response_type': 'code',
            'state': state,
            'scope': 'identify',  # We only need basic user info
            'prompt': 'consent'
        }
        
        # Instead of redirecting, return the URL for the frontend to use
        auth_url = f"{self.DISCORD_API_URL}/oauth2/authorize?{urlencode(params)}"
        return {
            "auth_url": auth_url,
            "message": "Use this URL to redirect the user to Discord's authorization page"
        }


@discord_oauth_blp.route('/callback', methods=['GET'])
class DiscordCallbackView(OAuthViewHandler):
    @discord_oauth_blp.doc(operationId='DiscordCallback',
                       summary="Handle Discord OAuth callback",
                       description="Processes the callback from Discord after user authorization.")
    @discord_oauth_blp.response(400, StateValidationErrorSchema, description="Invalid state")
    @discord_oauth_blp.response(400, TokenExchangeErrorSchema, description="Token exchange failed")
    @discord_oauth_blp.response(400, UserInfoErrorSchema, description="User info retrieval failed")
    @discord_oauth_blp.response(500, OAuthErrorSchema, description="Database error")
    @discord_oauth_blp.response(302, description="Redirect to frontend with success or error status")
    def get(self):
        """
        Handle callback from Discord OAuth
        """
        error = request.args.get('error')
        if error:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=discord_auth_error&message={error}")
        
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not state or not code:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=missing_parameters")
        
        # Retrieve user_id from state
        # The state should be in the format: "random_token:user_id"
        state_parts = state.split(':', 1)
        if len(state_parts) != 2:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=invalid_state_format")
            
        state_token, user_id = state_parts
        
        # Verify state using Redis instead of session
        redis_token = RedisToken()
        stored_state_token = redis_token.get_token(f'discord_oauth_state_{user_id}')
        if not stored_state_token or state_token != stored_state_token:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=invalid_state")
        
        # Clear state from Redis
        redis_token.delete_token(f'discord_oauth_state_{user_id}')
        
        # Exchange code for token
        token_response = self.exchange_discord_token(code)
        if not token_response:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=token_error")
        
        # Get Discord user information
        user_info = self.get_discord_user_info(token_response['access_token'])
        if not user_info:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=user_info_error")
        
        # Save Discord connection to database
        db = current_app.db
        result = self.save_discord_connection(user_id, token_response, user_info, db.session)
        if not result:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=db_error")
        
        # Success - redirect to frontend
        return redirect(f"{current_app.config['FRONTEND_URL']}/profile?success=discord_connected")

@discord_oauth_blp.route('/disconnect', methods=['DELETE'])
class DiscordDisconnectView(OAuthViewHandler):
    @jwt_required()
    @discord_oauth_blp.doc(operationId='DisconnectDiscord',
                           summary="Disconnect Discord account",
                           description="Removes the connection between the user's account and their Discord account.")
    @discord_oauth_blp.response(500, OAuthErrorSchema, description="Error disconnecting account")
    @discord_oauth_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @discord_oauth_blp.response(404, OAuthErrorSchema, description="No connection found")
    @discord_oauth_blp.response(200, DisconnectResponseSchema, description="Connection successfully removed")
    def delete(self):
        """
        Disconnect Discord account from user account
        """
        user_id = get_jwt_identity()
        
        try:
            # Get database session
            db = current_app.db
            session = db.session
            
            # Find the Discord connection
            connection = session.query(SocialConnection).filter_by(
                user_id=user_id,
                provider='discord'
            ).first()
            
            if not connection:
                return jsonify({"error": "No Discord connection found"}), 404
            
            # Remove Discord username from user
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.discord_username = None
            
            # Delete the connection
            session.delete(connection)
            session.commit()
            
            return jsonify({"message": "Discord connection removed successfully"}), 200
        except Exception as e:
            self.logger.error(f"Error disconnecting Discord: {str(e)}")
            session.rollback()
            return jsonify({"error": "Failed to disconnect Discord account"}), 500
