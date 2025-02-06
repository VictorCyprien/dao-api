from flask.views import MethodView
from mongoengine.errors import NotUniqueError, DoesNotExist

from helpers.redis_file import RedisQueue

from .users_blp import users_blp
from ...models.user import User

from ...schemas.communs_schemas import PagingError
from ...schemas.users_schemas import (
    InputCreateUserSchema,
    UserResponseSchema
)

from helpers.errors_file import BadRequest, ErrorHandler
from helpers.logging_file import Logger

from .user_view_handler import UserViewHandler

logger = Logger()


@users_blp.route('/')
class RootUsersView(UserViewHandler):
    @users_blp.doc(operationId='CreateUser')
    @users_blp.arguments(InputCreateUserSchema)
    @users_blp.response(400, schema=PagingError, description="BadRequest")
    @users_blp.response(201, schema=UserResponseSchema, description="Infos of new user")
    def post(self, input_data: dict):
        """Create a new user"""
        # Check if email is valid
        if not User.is_valid_email(input_data['email']):
            raise BadRequest(ErrorHandler.INVALID_EMAIL)

        # Check if email, discord username, wallet address or github username are already used
        try:
            self.check_user_exists(input_data=input_data)
        except BadRequest as error:
            raise error

        # Create user
        user = User.create(input_data=input_data)

        # Send email to user to check if it's real
        redis_queue = RedisQueue()
        redis_queue.enqueue(user.send_email_to_user)

        # Save user
        user.save()

        return {
            'action': 'created',
            'user': user
        }
