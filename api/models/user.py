from mongoengine import Document, fields
from mongoengine.errors import ValidationError

import bcrypt

from helpers.logging_file import Logger
from helpers.smtp_file import send_email


logger = Logger()



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

    email_verified = fields.BooleanField(default=False)
    """ Is the email verified
    """

    password = fields.StringField(required=True)
    """ Password of the user
    """

    discord_username = fields.StringField(required=True, unique=True)
    """ Discord username of the user
    """

    wallet_address = fields.StringField(required=True, unique=True)
    """ Wallet address of the user
    """


    @classmethod
    def create(cls, input_data: dict) -> "User":
        """ Create a new user instance
        """
        user = User()
        user.user_id = User.generate_user_id()
        user.username = input_data["username"]
        user.email = input_data["email"]
        user.email_verified = False
        user.password = User.hash_password(input_data["password"])
        user.discord_username = input_data["discord_username"]
        user.wallet_address = input_data["wallet_address"]
        return user

    
    def update(self, input_data: dict):
        """ Update the current instance of a User
        """
        username = input_data.get("username", None)
        email = input_data.get("email", None)
        password = input_data.get("password", None)
        discord_username = input_data.get("discord_username", None)
        wallet_address = input_data.get("wallet_address", None)

        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
            self.email_verified = False
        if password is not None:
            self.password = User.hash_password(password)
        if discord_username is not None:
            self.discord_username = discord_username
        if wallet_address is not None:
            self.wallet_address = wallet_address


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
    

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if an email address is valid
        
        Args:
            email: The email address to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        import re
        
        # Regular expression pattern for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Check if email matches pattern
        if re.match(pattern, email):
            return True
        return False
    

    def send_email_to_user(self):
        """ Send an email to the user to check if it's real
        """
        logger.info(f"Sending email to {self.email}...")
        subject = "Welcome to DAO.io"
        msg_to_send = "Welcome to DAO.io"

        try:
            send_email(self.email, subject, msg_to_send)
        except Exception:
            logger.error(f"Failed to send email to {self.email}")
            raise

    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt
        
        Args:
            password: The plain text password to hash
            
        Returns:
            str: The hashed password
        """
        # Convert password to bytes and generate salt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        
        # Hash password with salt
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return string representation
        return hashed.decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Check a password against a hashed password
        
        Args:
            password: The plain text password to check
            hashed_password: The hashed password to check against
            
        Returns:
            bool: True if the password is correct, False otherwise
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        # Convert hashed password to bytes
        hashed_password_bytes = hashed_password.encode('utf-8')
        # Check if the password is correct
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
