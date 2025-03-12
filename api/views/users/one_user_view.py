from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_pydantic import validate

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from flask_jwt_extended import get_jwt_identity, jwt_required

from .users_blp import users_blp
from ...models.user import User

from ...schemas.pydantic_schemas import (
    User as UserModel,
    UserResponse,
    UserExistResponse,
    InputUpdateUser,
    PagingError
)

from helpers.errors_file import BadRequest, NotFound, ErrorHandler
from helpers.logging_file import Logger


logger = Logger()


@users_blp.route('/@me')
class OneUserWalletView(MethodView):
    @users_blp.doc(operationId='GetAuthUserInfos')
    @jwt_required(fresh=True)
    def get(self):
        """Get authenticated user informations"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Create response using Pydantic model
        response = UserModel.model_validate(auth_user.to_dict())
        return response.model_dump()


@users_blp.route('/<string:wallet_address>')
class OneUserWalletView(MethodView):

    @users_blp.doc(operationId='GetUserWithWalletAddress')
    def get(self, wallet_address: str):
        """Check if user with the wallet address exists"""
        db: SQLAlchemy = current_app.db
        
        exists = False
        user = User.get_by_wallet_address(wallet_address, db.session)
        if user is not None:
            exists = True

        # Create response using Pydantic model
        response = UserExistResponse(exists=exists)
        return response.model_dump()


@users_blp.route('/<string:user_id>')
class OneUserView(MethodView):

    @users_blp.doc(operationId='UpdateUser')
    @jwt_required(fresh=True)
    @validate(body=InputUpdateUser)
    def put(self, body: InputUpdateUser, user_id: str):
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

        user.update(body.model_dump(exclude_unset=True))

        try:
            db.session.commit()
        except IntegrityError as error:
            logger.error(f"Error updating user: {error}")
            raise BadRequest(ErrorHandler.USER_UPDATE)

        # Create response using Pydantic model
        response = UserResponse(
            action="updated",
            user=user.to_dict()
        )
        return response.model_dump()
