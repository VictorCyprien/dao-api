from typing import Dict

from flask import current_app
from flask.views import MethodView

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask_jwt_extended import get_jwt_identity, jwt_required

from .users_blp import users_blp
from ...models.user import User

from ...schemas.users_schemas import InputUpdateUserSchema, UserSchema, UserResponseSchema, UserExistResponseSchema
from ...schemas.communs_schemas import PagingError

from helpers.errors_file import BadRequest, NotFound, ErrorHandler
from helpers.logging_file import Logger


logger = Logger()


@users_blp.route('/@me')
class OneUserWalletView(MethodView):
    @users_blp.doc(operationId='GetAuthUserInfos')
    @users_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @users_blp.response(200, UserSchema, description="User information retrieved successfully")
    @jwt_required(fresh=True)
    def get(self):
        """Get authenticated user informations"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        return auth_user


@users_blp.route('/<string:wallet_address>')
class OneUserWalletView(MethodView):

    @users_blp.doc(operationId='GetUserWithWalletAddress')
    @users_blp.response(200, UserExistResponseSchema, description="Check if user exists completed successfully")
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

    @users_blp.arguments(InputUpdateUserSchema)
    @users_blp.doc(operationId='UpdateUser')
    @users_blp.response(404, PagingError, description="User not found")
    @users_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @users_blp.response(400, PagingError, description="Bad Request - Error updating user")
    @users_blp.response(200, UserResponseSchema, description="User updated successfully")
    @jwt_required(fresh=True)
    def put(self, input_data: Dict, user_id: str):
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

        user.update(input_data)

        try:
            db.session.commit()
        except Exception as error:
            logger.error(f"Error updating user: {error}")
            raise BadRequest(ErrorHandler.USER_UPDATE)

        return {
            "action": "updated",
            "user": user
        }
