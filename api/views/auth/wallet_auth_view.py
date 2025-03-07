from flask import current_app, jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import secrets
import redis

from .auth_blp import auth_blp

from ...schemas.communs_schemas import PagingError
from ...schemas.auth_schemas import (
    LoginResponseSchema,
    ChallengeRequestSchema,
    ChallengeResponseSchema,
    VerifySignatureSchema
)

from ...models.user import User
from helpers.errors_file import Unauthorized, ErrorHandler, NotFound
from helpers.logging_file import Logger
from helpers.redis_file import RedisToken

from api.config import config


logger = Logger()
redis_client = RedisToken()


@auth_blp.route('/wallet/challenge')
class WalletChallengeView(MethodView):
    
    @auth_blp.doc(operationId='GetWalletChallenge')
    @auth_blp.arguments(ChallengeRequestSchema)
    @auth_blp.response(404, schema=PagingError, description="User not found")
    @auth_blp.response(200, schema=ChallengeResponseSchema, description="Challenge message")
    def post(self, challenge_request: dict):
        """Generate a challenge message for Solana wallet signature authentication"""
        wallet_address = challenge_request.get("wallet_address")
        logger.debug(f"Generating challenge for Solana wallet: {wallet_address}")
        
        # Check if user exists
        db: SQLAlchemy = current_app.db
        user = db.session.query(User).filter(User.wallet_address == wallet_address).first()
        if user is None:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Generate challenge message
        message = User.generate_challenge_message(wallet_address)
        
        # Store challenge in Redis with expiration (5 minutes)
        redis_key = f"wallet_auth:{wallet_address}"
        redis_client.set_token(redis_key, message, 300)

        
        return {
            "message": message,
            "wallet_address": wallet_address
        }


@auth_blp.route('/wallet/verify')
class WalletVerifyView(MethodView):
    
    @auth_blp.doc(operationId='VerifyWalletSignature')
    @auth_blp.arguments(VerifySignatureSchema)
    @auth_blp.response(401, schema=PagingError, description="Invalid signature")
    @auth_blp.response(201, schema=LoginResponseSchema, description="Login successful")
    def post(self, verify_data: dict):
        """Verify a Solana wallet signature and authenticate the user"""
        wallet_address = verify_data.get("wallet_address")
        signature = verify_data.get("signature")
        
        logger.debug(f"Verifying Solana signature for wallet: {wallet_address}")
        
        # Retrieve challenge from Redis
        redis_key = f"wallet_auth:{wallet_address}"
        message = redis_client.get_token(redis_key)
        
        if message is None:
            raise Unauthorized(ErrorHandler.CHALLENGE_EXPIRED)
        
        # Convert from bytes to string if needed
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        
        # Verify the signature
        if not User.verify_signature(wallet_address, message, signature):
            raise Unauthorized(ErrorHandler.INVALID_SIGNATURE)
        
        # Delete the challenge from Redis after verification
        redis_client.delete_token(redis_key)
        
        # Get user
        db: SQLAlchemy = current_app.db
        user = db.session.query(User).filter(User.wallet_address == wallet_address).first()
        if user is None:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Update last login timestamp
        user.update_last_login()
        db.session.commit()
        
        # Generate JWT token
        token = create_access_token(
            identity=user.user_id, 
            fresh=True, 
            expires_delta=timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRES)
        )
        
        return {
            "msg": "Logged in with Solana wallet signature",
            "token": token
        } 