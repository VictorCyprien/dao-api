from flask import request, redirect, jsonify, current_app, session
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import secrets
import time
from datetime import datetime, timedelta
import pytz
from urllib.parse import urlencode
import base64
import hashlib
import secrets

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

twitter_oauth_blp = Blueprint(
    name='twitter_oauth',
    import_name=__name__,
    description='Twitter OAuth integration',
    url_prefix='/auth/twitter'
)

@twitter_oauth_blp.route('/connect', methods=['GET'])
class TwitterConnectView(OAuthViewHandler):
    @jwt_required()
    @twitter_oauth_blp.doc(operationId='ConnectTwitter',
                           summary="Initiate Twitter OAuth flow",
                           description="Redirects the user to Twitter's authorization page to begin the OAuth 2.0 PKCE flow.")
    @twitter_oauth_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @twitter_oauth_blp.response(200, OAuthResponseSchema, description="Return Twitter authorization URL")
    def get(self):
        """
        Initiate Twitter OAuth flow for linking a Twitter account
        Using OAuth 2.0 PKCE flow
        """
        config = current_app.config
        user_id = get_jwt_identity()
        
        # Generate code verifier and challenge for PKCE
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Generate state token
        state_token = secrets.token_urlsafe(32)
        
        # Combine state token with user_id for stateless validation
        # Format: "random_token:user_id"
        state = f"{state_token}:{user_id}"
        
        # Store code verifier and state token in Redis with 1 hour expiry
        redis_token = RedisToken()
        redis_token.set_token(f'twitter_oauth_state_{user_id}', state_token, 3600)
        redis_token.set_token(f'twitter_code_verifier_{user_id}', code_verifier, 3600)
        
        # Define Twitter OAuth parameters
        params = {
            'response_type': 'code',
            'client_id': config['TWITTER_CLIENT_ID'],
            'redirect_uri': config['TWITTER_REDIRECT_URI'],
            'scope': 'users.read tweet.read',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Return the URL for the frontend to use
        auth_url = f"{self.TWITTER_AUTHORIZE_URL}?{urlencode(params)}"
        return {
            "auth_url": auth_url,
            "message": "Use this URL to redirect the user to Twitter's authorization page"
        }

@twitter_oauth_blp.route('/callback', methods=['GET'])
class TwitterCallbackView(OAuthViewHandler):
    # Remove JWT requirement
    @twitter_oauth_blp.doc(operationId='TwitterCallback',
                           summary="Handle Twitter OAuth callback",
                           description="Processes the callback from Twitter after user authorization.")
    @twitter_oauth_blp.response(400, StateValidationErrorSchema, description="Invalid state")
    @twitter_oauth_blp.response(400, TokenExchangeErrorSchema, description="Token exchange failed")
    @twitter_oauth_blp.response(400, UserInfoErrorSchema, description="User info retrieval failed")
    @twitter_oauth_blp.response(500, OAuthErrorSchema, description="Database error")
    @twitter_oauth_blp.response(302, description="Redirect to frontend with success or error status")
    def get(self):
        """
        Handle callback from Twitter OAuth
        """
        error = request.args.get('error')
        if error:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=twitter_auth_error&message={error}")
        
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
        
        # Initialize Redis token manager
        redis_token = RedisToken()
        
        # Verify state using Redis
        stored_state_token = redis_token.get_token(f'twitter_oauth_state_{user_id}')
        if not stored_state_token or state_token != stored_state_token:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=invalid_state")
        
        # Get stored code verifier from Redis
        code_verifier = redis_token.get_token(f'twitter_code_verifier_{user_id}')
        if not code_verifier:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=missing_verifier")
        
        # Clear Redis data
        redis_token.delete_token(f'twitter_oauth_state_{user_id}')
        redis_token.delete_token(f'twitter_code_verifier_{user_id}')
        
        # Exchange code for token
        token_response = self.exchange_twitter_token(code, code_verifier)
        if not token_response:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=token_error")
        
        # Get Twitter user information
        user_info = self.get_twitter_user_info(token_response['access_token'])
        if not user_info:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=user_info_error")
        
        # Save Twitter connection to database
        db = current_app.db
        result = self.save_twitter_connection(user_id, token_response, user_info, db.session)
        if not result:
            return redirect(f"{current_app.config['FRONTEND_URL']}/profile?error=db_error")
        
        # Success - redirect to frontend
        return redirect(f"{current_app.config['FRONTEND_URL']}/profile?success=twitter_connected")

@twitter_oauth_blp.route('/disconnect', methods=['DELETE'])
class TwitterDisconnectView(OAuthViewHandler):
    @jwt_required()
    @twitter_oauth_blp.doc(operationId='DisconnectTwitter',
                           summary="Disconnect Twitter account",
                           description="Removes the connection between the user's account and their Twitter account.")
    @twitter_oauth_blp.response(401, OAuthErrorSchema, description="Unauthorized")
    @twitter_oauth_blp.response(404, OAuthErrorSchema, description="No connection found")
    @twitter_oauth_blp.response(500, OAuthErrorSchema, description="Error disconnecting account")
    @twitter_oauth_blp.response(200, DisconnectResponseSchema, description="Connection successfully removed")
    def delete(self):
        """
        Disconnect Twitter account from user account
        """
        user_id = get_jwt_identity()
        
        try:
            # Get database session
            db = current_app.db
            session = db.session
            
            # Find the Twitter connection
            connection = session.query(SocialConnection).filter_by(
                user_id=user_id,
                provider='twitter'
            ).first()
            
            if not connection:
                return jsonify({"error": "No Twitter connection found"}), 404
            
            # Remove Twitter username from user
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.twitter_username = None
            
            # Delete the connection
            session.delete(connection)
            session.commit()
            
            return jsonify({"message": "Twitter connection removed successfully"}), 200
        except Exception as e:
            self.logger.error(f"Error disconnecting Twitter: {str(e)}")
            session.rollback()
            return jsonify({"error": "Failed to disconnect Twitter account"}), 500 