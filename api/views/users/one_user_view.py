from typing import Dict

from flask import current_app
from flask.views import MethodView

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask_jwt_extended import get_jwt_identity, jwt_required

from .users_blp import users_blp
from ...models.user import User

from ...schemas.communs_schemas import PagingError
from ...schemas.users_schemas import (
    InputUpdateUserSchema,
    UserResponseSchema
)

from helpers.errors_file import BadRequest, NotFound, ErrorHandler
from helpers.logging_file import Logger


logger = Logger()



@users_blp.route('/<int:user_id>')
class OneUserView(MethodView):

    @users_blp.doc(operationId='GetUser')
    @users_blp.response(404, schema=PagingError, description="NotFound")
    @users_blp.response(200, schema=UserResponseSchema, description="Get one user")
    @jwt_required(fresh=True)
    def get(self, user_id: int):
        """Get an existing user"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        user = User.get_by_id(id=user_id, session=db.session)
        if user is None:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # We raise a NotFound if the user is not the same as the authenticated user
        if auth_user.user_id != user.user_id:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)

        return {
            "user": user
        }


    @users_blp.doc(operationId='UpdateUser')
    @users_blp.arguments(InputUpdateUserSchema)
    @users_blp.response(400, schema=PagingError, description="BadRequest")
    @users_blp.response(404, schema=PagingError, description="NotFound")
    @users_blp.response(200, schema=UserResponseSchema, description="Update one user")
    @jwt_required(fresh=True)
    def put(self, input_dict: Dict, user_id: int):
        """Update an existing user"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        user = User.get_by_id(id=user_id, session=db.session)
        if user is None:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # We raise a NotFound if the user is not the same as the authenticated user
        if auth_user.user_id != user.user_id:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        user.update(input_dict)

        try:
            db.session.commit()
        except IntegrityError as error:
            logger.error(f"Error updating user: {error}")
            raise BadRequest(ErrorHandler.USER_UPDATE)

        return {
            "action": "updated",
            "user": user
        }
