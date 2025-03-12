from flask import current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_pydantic import validate

from sqlalchemy.exc import IntegrityError

from .users_blp import users_blp
from ...models.user import User

from ...schemas.communs_schemas import PagingError
from ...schemas.pydantic_schemas import (
    InputCreateUser,
    UserResponse,
    PagingError as PydanticPagingError
)

from helpers.errors_file import BadRequest, ErrorHandler
from helpers.logging_file import Logger

from .user_view_handler import UserViewHandler

logger = Logger()


@users_blp.route('/')
class RootUsersView(UserViewHandler):
    @users_blp.doc(operationId='CreateUser')
    @validate(body=InputCreateUser)
    def post(self, body: InputCreateUser):
        """Create a new user"""
        db: SQLAlchemy = current_app.db
        input_data = body.model_dump(exclude_unset=True)

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
        except IntegrityError as error:
            logger.error(f"Error creating user: {error}")
            raise BadRequest(ErrorHandler.USER_CREATE)

        # Create response using Pydantic model
        response = UserResponse(
            action='created',
            user=user.to_dict()
        )

        return jsonify(response.model_dump()), 201
