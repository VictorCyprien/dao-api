from flask.views import MethodView
from api.models.user import User
from helpers.errors_file import BadRequest, ErrorHandler

class UserViewHandler(MethodView):
    def check_user_exists(self, input_data: dict):
        if User.objects(email=input_data["email"]):
            raise BadRequest(ErrorHandler.USER_EMAIL_ALREADY_USED)
        
        # Check if discord username is already used
        if User.objects(discord_username=input_data["discord_username"]):
            raise BadRequest(ErrorHandler.USER_DISCORD_USERNAME_ALREADY_USED)
        
        # Check if wallet address is already used
        if User.objects(wallet_address=input_data["wallet_address"]):
            raise BadRequest(ErrorHandler.USER_WALLET_ADDRESS_ALREADY_USED)
        
        # Check if github username is already used
        if User.objects(github_username=input_data["github_username"]):
            raise BadRequest(ErrorHandler.USER_GITHUB_USERNAME_ALREADY_USED)
