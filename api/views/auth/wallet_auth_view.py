from flask import current_app, jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import secrets
import redis
from flask_pydantic import validate

from .auth_blp import auth_blp

from ...schemas.communs_schemas import PagingError
from ...schemas.pydantic_schemas import (
    ChallengeRequest, 
    ChallengeResponse, 
    VerifySignature, 
    LoginResponse,
    PagingError as PydanticPagingError
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
    @validate(body=ChallengeRequest)
    def post(self, body: ChallengeRequest):
        """Generate a challenge message for Solana wallet signature authentication"""
        wallet_address = body.wallet_address
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

        # Create response using Pydantic model
        response = ChallengeResponse(
            message=message,
            wallet_address=wallet_address
        )
        
        return response.model_dump()


@auth_blp.route('/wallet/verify')
class WalletVerifyView(MethodView):
    
    @auth_blp.doc(operationId='VerifyWalletSignature')
    @validate(body=VerifySignature)
    def post(self, body: VerifySignature):
        """Verify a Solana wallet signature and authenticate the user"""
        wallet_address = body.wallet_address
        signature = body.signature
        
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
        
        # Create response using Pydantic model
        response = LoginResponse(
            msg="Logged in with Solana wallet signature",
            token=token
        )
        
        return jsonify(response.model_dump()), 201
