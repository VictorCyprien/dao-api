from mongoengine import Document, fields
from mongoengine.errors import ValidationError

from datetime import datetime


class User(Document):
    user_id: int = fields.IntField(db_field="user_id", min_value=0, required=True, primary_key=True)
    """ ID of the User
    """

    username = fields.StringField(required=True, unique=True)
    """ Username of the user
    """

    email = fields.StringField(required=True, unique=True)
    """ Email of the user
    """

    discord_username = fields.StringField(required=True, unique=True)
    """ Discord username of the user
    """

    wallet_address = fields.StringField(required=True, unique=True)
    """ Wallet address of the user
    """

    github_username = fields.StringField(required=True, unique=True)
    """ Github username of the user
    """


    @classmethod
    def create(cls, input_data: dict) -> "User":
        """ Create a new user instance
        """
        user = User()
        user.user_id = User.generate_user_id()
        user.username = input_data["username"]
        user.email = input_data["email"]
        user.discord_username = input_data["discord_username"]
        user.wallet_address = input_data["wallet_address"]
        user.github_username = input_data["github_username"]
        return user

    
    def update(self, input_data: dict):
        """ Update the current instance of a User
        """
        username = input_data.get("username", None)
        email = input_data.get("email", None)
        discord_username = input_data.get("discord_username", None)
        wallet_address = input_data.get("wallet_address", None)
        github_username = input_data.get("github_username", None)

        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if discord_username is not None:
            self.discord_username = discord_username
        if wallet_address is not None:
            self.wallet_address = wallet_address
        if github_username is not None:
            self.github_username = github_username


    @classmethod
    def get_by_id(cls, id: int) -> "User":
        """ User getter with a ID
        """
        try:
            user_id = int(id)
        except ValueError:
            raise ValidationError('The user ID should be an int')
        _query = User.objects(user_id=user_id)
        user = _query.get()
        return user
    

    @classmethod
    def generate_user_id(cls) -> int:
        """ Generate a random user_id between 1 and integer limit
        """
        import random
        import sys

        # Get max integer value for this system
        max_int = sys.maxsize

        # Generate random ID between 1 and max_int
        user_id = random.randint(1, max_int)

        # Keep generating if ID already exists
        while User.objects(user_id=user_id):
            user_id = random.randint(1, max_int)

        return user_id
