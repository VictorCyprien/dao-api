from typing import Dict

from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

from .users_blp import users_blp
from ...models.user import User

from ...schemas.users_schemas import UserResponseSchema, InputCreateUserSchema
from ...schemas.communs_schemas import PagingError

from helpers.errors_file import BadRequest, ErrorHandler
from helpers.logging_file import Logger

from .user_view_handler import UserViewHandler

logger = Logger()


@users_blp.route('/')
class RootUsersView(UserViewHandler):
    @users_blp.arguments(InputCreateUserSchema)
    @users_blp.doc(operationId='CreateUser')
    @users_blp.response(400, PagingError, description="Bad Request")
    @users_blp.response(201, UserResponseSchema, description="User successfully created")
    def post(self, input_data: Dict):
        """Create a new user"""
        db: SQLAlchemy = current_app.db

        # Check if email, discord username, wallet address or github username are already used
        try:
            self.check_user_exists(input_data=input_data, session=db.session)
        except BadRequest as error:
            raise error

        # Create user
        user = User.create(input_data=input_data)

        # Save user
        db.session.add(user)

        try:
            db.session.commit()
        except Exception as error:
            logger.error(f"Error creating user: {error}")
            raise BadRequest(ErrorHandler.USER_CREATE)

        return {
            "action": "created",
            "user": user
        }
