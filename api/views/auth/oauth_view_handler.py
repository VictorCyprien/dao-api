from flask.views import MethodView
from flask import current_app
from datetime import datetime, timedelta
import requests
import secrets
import pytz
import hashlib
import base64
import hmac

from api.models.user import User
from api.models.social_connection import SocialConnection



class OAuthViewHandler(MethodView):
    """Base handler for OAuth operations"""
    
    # Discord API constants
    DISCORD_API_URL = 'https://discord.com/api/v10'
    
    # Twitter API constants
    TWITTER_API_URL = 'https://api.twitter.com'
    TWITTER_AUTHORIZE_URL = 'https://twitter.com/i/oauth2/authorize'
    TWITTER_TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
    
    def __init__(self):
        self.logger = current_app.logger
    
    def get_session(self):
        """Get the database session"""
        return current_app.db.session
    
    def generate_code_verifier(self):
        """Generate PKCE code verifier for OAuth 2.0 flows"""
        code_verifier = secrets.token_urlsafe(64)
        # PKCE verifier should be between 43-128 characters
        if len(code_verifier) > 128:
            code_verifier = code_verifier[:128]
        return code_verifier
    
    def exchange_discord_token(self, code):
        """Exchange Discord authorization code for access token"""
        config = current_app.config
        
        # Prepare token request
        token_url = f"{self.DISCORD_API_URL}/oauth2/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'client_id': config['DISCORD_CLIENT_ID'],
            'client_secret': config['DISCORD_CLIENT_SECRET'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': config['DISCORD_REDIRECT_URI']
        }
        
        # Log request parameters (excluding secret)
        self.logger.info(f"Discord token exchange - URL: {token_url}")
        self.logger.info(f"Discord token exchange - client_id: {config['DISCORD_CLIENT_ID']}")
        self.logger.info(f"Discord token exchange - redirect_uri: {config['DISCORD_REDIRECT_URI']}")
        
        # Make token request
        try:
            response = requests.post(token_url, headers=headers, data=data)
            # Log raw response for debugging
            self.logger.info(f"Discord token exchange - Raw response: {response.text}")
            response.raise_for_status()
            token_data = response.json()
            
            # Log token data (safely excluding sensitive parts)
            safe_token_data = {k: v if k not in ['access_token', 'refresh_token'] else f"{v[:5]}...{v[-5:]}" 
                            for k, v in token_data.items() if v is not None and isinstance(v, str)}
            self.logger.info(f"Discord token exchange successful. Keys received: {list(token_data.keys())}")
            self.logger.info(f"Discord token data: {safe_token_data}")
            
            return token_data
        except requests.RequestException as e:
            self.logger.error(f"Discord token exchange error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            return None
    
    def get_discord_user_info(self, access_token):
        """Get Discord user information using access token"""
        user_url = f"{self.DISCORD_API_URL}/users/@me"
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        
        self.logger.info(f"Fetching Discord user info from: {user_url}")
        
        try:
            response = requests.get(user_url, headers=headers)
            self.logger.info(f"Discord user info - Raw response: {response.text}")
            response.raise_for_status()
            user_data = response.json()
            self.logger.info(f"Discord user info - User ID: {user_data.get('id')}, Username: {user_data.get('username')}")
            return user_data
        except requests.RequestException as e:
            self.logger.error(f"Discord user info error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            return None
    
    def save_discord_connection(self, user_id, token_data, user_info, session):
        """Save Discord connection to database"""
        try:
            self.logger.info(f"Saving Discord connection for user_id: {user_id}")
            
            # Check if this Discord account is already linked to another user
            discord_id = str(user_info['id'])
            self.logger.info(f"Discord user ID: {discord_id}")
            
            existing_connection = session.query(SocialConnection).filter_by(
                provider='discord', 
                provider_user_id=discord_id
            ).first()
            
            if existing_connection:
                self.logger.info(f"Existing Discord connection found: {existing_connection.id} for user: {existing_connection.user_id}")
                
            if existing_connection and existing_connection.user_id != user_id:
                # This Discord account is already linked to another user
                self.logger.warning(f"Discord account {discord_id} already linked to another user: {existing_connection.user_id}")
                return False
            
            # Check if user already has a Discord connection
            user_connection = session.query(SocialConnection).filter_by(
                user_id=user_id,
                provider='discord'
            ).first()
            
            if user_connection:
                self.logger.info(f"User {user_id} already has Discord connection: {user_connection.id}")
            
            # Calculate token expiration time
            expires_in = token_data.get('expires_in', 604800)
            expires_at = datetime.now(pytz.UTC) + timedelta(seconds=expires_in)
            self.logger.info(f"Token expires in {expires_in} seconds (at {expires_at.isoformat()})")
            
            # Prepare username (tag may not exist in newer Discord API)
            username = user_info.get('username', '')
            if user_info.get('discriminator') and user_info.get('discriminator') != '0':
                username = f"{username}#{user_info['discriminator']}"
            
            self.logger.info(f"Discord username: {username}")
            
            if not user_connection:
                # Create new connection
                self.logger.info("Creating new Discord connection")
                connection = SocialConnection.create(
                    user_id=user_id,
                    provider='discord',
                    provider_user_id=discord_id,
                    provider_username=username,
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    token_expires_at=expires_at
                )
                self.logger.info(f"New Discord connection created with ID: {connection.id}")
                session.add(connection)
            else:
                # Update existing connection
                self.logger.info(f"Updating existing Discord connection: {user_connection.id}")
                user_connection.provider_user_id = discord_id
                user_connection.provider_username = username
                user_connection.set_access_token(token_data['access_token'])
                if token_data.get('refresh_token'):
                    user_connection.set_refresh_token(token_data['refresh_token'])
                user_connection.token_expires_at = expires_at
                user_connection.updated_at = datetime.now(pytz.UTC)
            
            # Update user's Discord username field
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                self.logger.info(f"Updating Discord username for user {user_id}: {username}")
                user.discord_username = username
            else:
                self.logger.warning(f"User {user_id} not found when updating Discord username")
            
            session.commit()
            self.logger.info(f"Discord connection saved successfully for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving Discord connection: {str(e)}")
            if hasattr(e, "__traceback__"):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                self.logger.error(f"Traceback: {trace}")
            session.rollback()
            return False
    
    def generate_code_challenge(self, verifier):
        """Generate a code challenge for PKCE from a code verifier"""
        sha256 = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256).decode().rstrip('=')
    
    def exchange_twitter_token(self, code, code_verifier):
        """Exchange Twitter authorization code for access token"""
        config = current_app.config
        
        # Prepare token request with basic auth
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': config['TWITTER_REDIRECT_URI'],
            'code_verifier': code_verifier
        }
        
        # Set up auth tuple for requests (client_id, client_secret)
        # This will be converted to the proper Authorization header by requests
        auth = (config['TWITTER_CLIENT_ID'], config['TWITTER_CLIENT_SECRET'])
        
        # Log request parameters (excluding secret)
        self.logger.info(f"Twitter token exchange - URL: {self.TWITTER_TOKEN_URL}")
        self.logger.info(f"Twitter token exchange - client_id: {config['TWITTER_CLIENT_ID']}")
        self.logger.info(f"Twitter token exchange - redirect_uri: {config['TWITTER_REDIRECT_URI']}")
        self.logger.info(f"Twitter token exchange - code_verifier length: {len(code_verifier)}")
        self.logger.info(f"Twitter token exchange - Using Basic Authentication")
        
        # Make token request
        try:
            response = requests.post(self.TWITTER_TOKEN_URL, headers=headers, data=data, auth=auth)
            # Log raw response
            self.logger.info(f"Twitter token exchange - Raw response: {response.text}")
            response.raise_for_status()
            token_data = response.json()
            
            # Log token data (safely excluding sensitive parts)
            safe_token_data = {k: v if k not in ['access_token', 'refresh_token'] else f"{v[:5]}...{v[-5:]}" 
                            for k, v in token_data.items() if v is not None and isinstance(v, str)}
            self.logger.info(f"Twitter token exchange successful. Keys received: {list(token_data.keys())}")
            self.logger.info(f"Twitter token data: {safe_token_data}")
            
            return token_data
        except requests.RequestException as e:
            self.logger.error(f"Twitter token exchange error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            return None
    
    def get_twitter_user_info(self, access_token):
        """Get Twitter user information using access token"""
        user_url = f"{self.TWITTER_API_URL}/2/users/me"
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        params = {
            'user.fields': 'id,name,username'
        }
        
        self.logger.info(f"Fetching Twitter user info from: {user_url}")
        self.logger.info(f"Twitter user info - User fields: {params['user.fields']}")
        
        try:
            response = requests.get(user_url, headers=headers, params=params)
            self.logger.info(f"Twitter user info - Raw response: {response.text}")
            response.raise_for_status()
            user_data = response.json()
            
            # Log the user data
            twitter_user = user_data.get('data', {})
            if twitter_user:
                self.logger.info(f"Twitter user info - User ID: {twitter_user.get('id')}, Username: {twitter_user.get('username')}")
            else:
                self.logger.warning("Twitter user info - No user data in response")
                
            return user_data
        except requests.RequestException as e:
            self.logger.error(f"Twitter user info error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response body: {e.response.text}")
            return None
    
    def save_twitter_connection(self, user_id, token_data, user_info, session):
        """Save Twitter connection to database"""
        try:
            self.logger.info(f"Saving Twitter connection for user_id: {user_id}")
            
            # Get user data from response (Twitter API v2 structure)
            twitter_user = user_info.get('data', {})
            if not twitter_user or 'id' not in twitter_user:
                self.logger.error("Twitter user info - Missing user ID in response")
                return False
            
            # Check if this Twitter account is already linked to another user
            twitter_id = twitter_user['id']
            self.logger.info(f"Twitter user ID: {twitter_id}")
            
            existing_connection = session.query(SocialConnection).filter_by(
                provider='twitter', 
                provider_user_id=twitter_id
            ).first()
            
            if existing_connection:
                self.logger.info(f"Existing Twitter connection found: {existing_connection.id} for user: {existing_connection.user_id}")
                
            if existing_connection and existing_connection.user_id != user_id:
                # This Twitter account is already linked to another user
                self.logger.warning(f"Twitter account {twitter_id} already linked to another user: {existing_connection.user_id}")
                return False
            
            # Check if user already has a Twitter connection
            user_connection = session.query(SocialConnection).filter_by(
                user_id=user_id,
                provider='twitter'
            ).first()
            
            if user_connection:
                self.logger.info(f"User {user_id} already has Twitter connection: {user_connection.id}")
            
            # Calculate token expiration time
            expires_in = token_data.get('expires_in', 7200)
            expires_at = datetime.now(pytz.UTC) + timedelta(seconds=expires_in)
            self.logger.info(f"Token expires in {expires_in} seconds (at {expires_at.isoformat()})")
            
            # Get username
            username = twitter_user.get('username', '')
            self.logger.info(f"Twitter username: {username}")
            
            if not user_connection:
                # Create new connection
                self.logger.info("Creating new Twitter connection")
                connection = SocialConnection.create(
                    user_id=user_id,
                    provider='twitter',
                    provider_user_id=twitter_id,
                    provider_username=username,
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    token_expires_at=expires_at
                )
                self.logger.info(f"New Twitter connection created with ID: {connection.id}")
                session.add(connection)
            else:
                # Update existing connection
                self.logger.info(f"Updating existing Twitter connection: {user_connection.id}")
                user_connection.provider_user_id = twitter_id
                user_connection.provider_username = username
                user_connection.set_access_token(token_data['access_token'])
                if token_data.get('refresh_token'):
                    user_connection.set_refresh_token(token_data['refresh_token'])
                user_connection.token_expires_at = expires_at
                user_connection.updated_at = datetime.now(pytz.UTC)
            
            # Update user's Twitter username field
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                self.logger.info(f"Updating Twitter username for user {user_id}: {username}")
                user.twitter_username = username
            else:
                self.logger.warning(f"User {user_id} not found when updating Twitter username")
            
            session.commit()
            self.logger.info(f"Twitter connection saved successfully for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving Twitter connection: {str(e)}")
            if hasattr(e, "__traceback__"):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                self.logger.error(f"Traceback: {trace}")
            session.rollback()
            return False
    
    def verify_telegram_data(self, auth_data):
        """Verify the authentication data from Telegram"""
        self.logger.info("Starting Telegram data verification")
        
        if not auth_data or not isinstance(auth_data, dict):
            self.logger.error("Telegram verification - Invalid data format")
            return False
        
        # Required fields from Telegram login widget
        missing_fields = [field for field in ['id', 'auth_date', 'hash'] if field not in auth_data]
        
        if missing_fields:
            self.logger.error(f"Telegram verification - Missing required fields: {missing_fields}")
            return False
        
        # Get the hash from the data
        received_hash = auth_data.pop('hash')
        self.logger.info(f"Telegram verification - Received hash: {received_hash[:5]}...{received_hash[-5:]}")
        
        # Check if the auth_date is not too old (86400 seconds = 24 hours)
        auth_date = int(auth_data['auth_date'])
        now = int(datetime.now().timestamp())
        time_diff = now - auth_date
        
        self.logger.info(f"Telegram verification - Auth date: {auth_date}, Current time: {now}, Difference: {time_diff}s")
        
        if time_diff > 86400:
            self.logger.error(f"Telegram verification - Auth date too old: {time_diff}s > 86400s")
            return False
        
        # Sort the data alphabetically
        data_check_string = '\n'.join(f"{key}={value}" for key, value in sorted(auth_data.items()))
        self.logger.info(f"Telegram verification - Data check string created, length: {len(data_check_string)}")
        
        # Create the secret key using HMAC-SHA256
        bot_token = current_app.config['TELEGRAM_BOT_TOKEN']
        if not bot_token:
            self.logger.error("Telegram verification - Bot token not configured")
            return False
            
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate the hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.logger.info(f"Telegram verification - Calculated hash: {calculated_hash[:5]}...{calculated_hash[-5:]}")
        
        # Compare the hashes
        hash_match = calculated_hash == received_hash
        self.logger.info(f"Telegram verification - Hash match: {hash_match}")
        
        return hash_match
    
    def save_telegram_connection(self, user_id, telegram_data, session):
        """Save Telegram connection to database"""
        try:
            self.logger.info(f"Saving Telegram connection for user_id: {user_id}")
            
            # Check if this Telegram account is already linked to another user
            telegram_id = str(telegram_data['id'])
            self.logger.info(f"Telegram user ID: {telegram_id}")
            
            existing_connection = session.query(SocialConnection).filter_by(
                provider='telegram', 
                provider_user_id=telegram_id
            ).first()
            
            if existing_connection:
                self.logger.info(f"Existing Telegram connection found: {existing_connection.id} for user: {existing_connection.user_id}")
                
            if existing_connection and existing_connection.user_id != user_id:
                # This Telegram account is already linked to another user
                self.logger.warning(f"Telegram account {telegram_id} already linked to another user: {existing_connection.user_id}")
                return False
            
            # Check if user already has a Telegram connection
            user_connection = session.query(SocialConnection).filter_by(
                user_id=user_id,
                provider='telegram'
            ).first()
            
            if user_connection:
                self.logger.info(f"User {user_id} already has Telegram connection: {user_connection.id}")
            
            # Prepare username
            username = telegram_data.get('username', '')
            self.logger.info(f"Telegram username: {username}")
            
            # Construct display name from first_name and last_name
            display_name = telegram_data.get('first_name', '')
            if telegram_data.get('last_name'):
                display_name += f" {telegram_data.get('last_name')}"
            
            self.logger.info(f"Telegram display name: {display_name}")
            
            if not user_connection:
                # Create new connection
                self.logger.info("Creating new Telegram connection")
                connection = SocialConnection.create(
                    user_id=user_id,
                    provider='telegram',
                    provider_user_id=telegram_id,
                    provider_username=username
                    # No access token or refresh token for Telegram
                )
                self.logger.info(f"New Telegram connection created with ID: {connection.id}")
                session.add(connection)
            else:
                # Update existing connection
                self.logger.info(f"Updating existing Telegram connection: {user_connection.id}")
                user_connection.provider_user_id = telegram_id
                user_connection.provider_username = username
                user_connection.updated_at = datetime.now(pytz.UTC)
            
            # Update user's Telegram username field
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                self.logger.info(f"Updating Telegram username for user {user_id}: {username}")
                user.telegram_username = username
            else:
                self.logger.warning(f"User {user_id} not found when updating Telegram username")
            
            session.commit()
            self.logger.info(f"Telegram connection saved successfully for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving Telegram connection: {str(e)}")
            if hasattr(e, "__traceback__"):
                import traceback
                trace = ''.join(traceback.format_tb(e.__traceback__))
                self.logger.error(f"Traceback: {trace}")
            session.rollback()
            return False 