from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

from .auth_blp import auth_blp

from ...schemas.communs_schemas import PagingError
from ...schemas.auth_schemas import (
    LoginParamsSchema,
    LoginResponseSchema
)

from ...models.user import User
from helpers.errors_file import Unauthorized, ErrorHandler
from helpers.logging_file import Logger

from api.config import config


logger = Logger()


@auth_blp.route('/login')
class LoginAuthView(MethodView):
    
    @auth_blp.doc(operationId='Login')
    @auth_blp.arguments(LoginParamsSchema)
    @auth_blp.response(401, schema=PagingError, description="Invalid credentials")
    @auth_blp.response(201, schema=LoginResponseSchema, description="Log the user")
    def post(self, user_login: dict):
        """Login the user"""
        logger.debug(f"Authenticate user with email: {user_login.get('email')}")
        email = user_login.get("email")
        password = user_login.get("password")
  
        if not User.is_valid_email(email):
            raise Unauthorized(ErrorHandler.BAD_CREDENTIALS)

        db: SQLAlchemy = current_app.db
        user = db.session.query(User).filter(User.email == email).first()
        if user is None:
            raise Unauthorized(ErrorHandler.BAD_CREDENTIALS)
            
        if not user.check_password(password=password, hashed_password=user.password):
            raise Unauthorized(ErrorHandler.BAD_CREDENTIALS)
        
        token = create_access_token(
            identity=user.user_id, 
            fresh=True, 
            expires_delta=timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRES)
        )

        return {
            "msg": "Logged",
            "token": token
        }
