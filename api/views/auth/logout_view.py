from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required

from .auth_blp import auth_blp

from ...schemas.communs_schemas import PagingError
from ...schemas.auth_schemas import LogoutResponseSchema

from ...models.user import User
from ...config import config

from helpers.errors_file import ErrorHandler
from helpers.logging_file import Logger


logger = Logger()



@auth_blp.route('/logout')
class LogoutAuthView(MethodView):
    
    @auth_blp.doc(operationId='Logout')
    @auth_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @auth_blp.response(201, LogoutResponseSchema, description="Successfully logged out")
    @jwt_required(fresh=True)
    def post(self):
        """Logout the user"""
        jti = get_jwt()["jti"]
        jwt_redis_blocklist = current_app.extensions['jwt_redis_blocklist']
        jwt_redis_blocklist.set(jti, "", ex=config.JWT_ACCESS_TOKEN_EXPIRES)

        return {"msg": "You have been logout !"}, 201

