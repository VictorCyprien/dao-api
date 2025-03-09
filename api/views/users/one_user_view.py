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
    UserResponseSchema,
    UserExistResponseSchema
)

from helpers.errors_file import BadRequest, NotFound, ErrorHandler
from helpers.logging_file import Logger


logger = Logger()


@users_blp.route('/@me')
class OneUserWalletView(MethodView):
    @users_blp.doc(operationId='GetAuthUserInfos')
    @users_blp.response(404, schema=PagingError, description="NotFound")
    @users_blp.response(200, schema=UserResponseSchema, description="Get authenticated user informations")
    @jwt_required()
    def get(self):
        """Get authenticated user informations"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        return {
            "user": auth_user
        }


@users_blp.route('/<string:wallet_address>')
class OneUserWalletView(MethodView):

    @users_blp.doc(operationId='GetUserWithWalletAddress')
    @users_blp.response(404, schema=PagingError, description="NotFound")
    @users_blp.response(200, schema=UserExistResponseSchema, description="Check if user with the wallet address exists")
    def get(self, wallet_address: str):
        """Check if user with the wallet address exists"""
        db: SQLAlchemy = current_app.db
        
        exists = False
        user = User.get_by_wallet_address(wallet_address, db.session)
        if user is not None:
            exists = True

        return {
            "exists": exists
        }



@users_blp.route('/<string:user_id>')
class OneUserView(MethodView):

    @users_blp.doc(operationId='UpdateUser')
    @users_blp.arguments(InputUpdateUserSchema)
    @users_blp.response(400, schema=PagingError, description="BadRequest")
    @users_blp.response(404, schema=PagingError, description="NotFound")
    @users_blp.response(200, schema=UserResponseSchema, description="Update one user")
    @jwt_required(fresh=True)
    def put(self, input_dict: Dict, user_id: str):
        """Update an existing user"""
        db: SQLAlchemy = current_app.db
        
        # Only attempt to get the auth user if authentication is not disabled
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
