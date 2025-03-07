from flask.views import MethodView
from sqlalchemy.orm import Session

from api.models.user import User
from helpers.errors_file import BadRequest, ErrorHandler

class UserViewHandler(MethodView):
    def check_user_exists(self, input_data: dict, session: Session):

        # Check if username is already used
        if session.query(User).filter(User.username == input_data["username"]).first():
            raise BadRequest(ErrorHandler.USER_USERNAME_ALREADY_USED)

        # Check if email is already used
        if session.query(User).filter(User.email == input_data["email"]).first():
            raise BadRequest(ErrorHandler.USER_EMAIL_ALREADY_USED)
        
        # Check if discord username is already used
        if session.query(User).filter(User.discord_username == input_data["discord_username"]).first():
            raise BadRequest(ErrorHandler.USER_DISCORD_USERNAME_ALREADY_USED)
        
        # Check if wallet address is already used
        if session.query(User).filter(User.wallet_address == input_data["wallet_address"]).first():
            raise BadRequest(ErrorHandler.USER_WALLET_ADDRESS_ALREADY_USED)
        
        
