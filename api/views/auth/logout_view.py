from flask import current_app, jsonify
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_pydantic import validate

from .auth_blp import auth_blp

from ...schemas.communs_schemas import PagingError
from ...schemas.pydantic_schemas import LogoutResponse, PagingError as PydanticPagingError

from ...models.user import User
from ...config import config

from helpers.errors_file import ErrorHandler
from helpers.logging_file import Logger


logger = Logger()



@auth_blp.route('/logout')
class LogoutAuthView(MethodView):
    
    @auth_blp.doc(operationId='Logout')
    @jwt_required(fresh=True)
    def post(self):
        """Logout the user"""
        jti = get_jwt()["jti"]
        jwt_redis_blocklist = current_app.extensions['jwt_redis_blocklist']
        jwt_redis_blocklist.set(jti, "", ex=config.JWT_ACCESS_TOKEN_EXPIRES)

        # Create response using Pydantic model
        response = LogoutResponse(msg="You have been logout !")
        return jsonify(response.model_dump()), 201

