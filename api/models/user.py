from api import Base

from sqlalchemy import BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
import bcrypt
from datetime import datetime
import pytz
import secrets
import base58

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from helpers.logging_file import Logger
from helpers.smtp_file import send_email

logger = Logger()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the User
    """

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    """ Username of the user
    """

    wallet_address: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    """ Wallet address of the user
    """
    
    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    """ Email of the user
    """

    member_name: Mapped[str] = mapped_column(String, nullable=True)
    """ Display name of the user
    """

    discord_username: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    """ Discord username of the user
    """

    twitter_username: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    """ Twitter username of the user
    """

    telegram_username: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    """ Telegram username of the user
    """

    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    """ Last login timestamp """

    last_interaction: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    """ Last interaction timestamp """

    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    """ Is the email verified
    """

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    """ Whether the user is active """


    # Add these relationship definitions
    administered_daos = relationship('DAO', secondary='dao_admins', back_populates='admins')
    """ DAOs that the user is an admin of """

    member_daos = relationship('DAO', secondary='dao_members', back_populates='members')
    """ DAOs that the user is a member of """

    member_pods = relationship('POD', secondary='pod_members', back_populates='members')
    """ PODs that the user is a member of """


    @classmethod
    def create(cls, input_data: dict) -> "User":
        """ Create a new user instance
        """
        user = User(
            user_id=User.generate_user_id(),
            username=input_data["username"],
            wallet_address=input_data["wallet_address"],
            email=input_data.get("email", None),
            email_verified=False,
            discord_username=input_data.get("discord_username", None),
            member_name=input_data.get("member_name", None),
            twitter_username=input_data.get("twitter_username", None),
            telegram_username=input_data.get("telegram_username", None),
            last_login=datetime.now(pytz.utc),
            last_interaction=datetime.now(pytz.utc)
        )
        return user

    
    def update(self, input_data: dict):
        """ Update the current instance of a User
        """
        username = input_data.get("username", None)
        email = input_data.get("email", None)
        discord_username = input_data.get("discord_username", None)
        member_name = input_data.get("member_name", None)
        twitter_username = input_data.get("twitter_username", None)
        telegram_username = input_data.get("telegram_username", None)

        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
            self.email_verified = False
        if discord_username is not None:
            self.discord_username = discord_username
        if member_name is not None:
            self.member_name = member_name
        if twitter_username is not None:
            self.twitter_username = twitter_username
        if telegram_username is not None:
            self.telegram_username = telegram_username


    @classmethod
    def get_by_id(cls, id: str, session: Session) -> "User":
        """ User getter with a ID
        """
        return session.query(User).filter(User.user_id == id).first()
    

    @classmethod
    def get_by_wallet_address(cls, wallet_address: str, session: Session) -> "User":
        """ User getter with a wallet address
        """
        return session.query(User).filter(User.wallet_address == wallet_address).first()


    @classmethod
    def generate_user_id(cls) -> str:
        """ Generate a random user_id between 1 and integer limit
        """
        import random
        import sys

        # Get max integer value for this system
        max_int = sys.maxsize

        # Generate random ID between 1 and max_int
        return str(random.randint(1, max_int))
    

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


    def update_last_login(self):
        """ Update the last login timestamp to current time
        """
        self.last_login = datetime.now(pytz.utc)

    def update_last_interaction(self):
        """ Update the last interaction timestamp to current time
        """
        self.last_interaction = datetime.now(pytz.utc)

    @staticmethod
    def generate_challenge_message(wallet_address: str) -> str:
        """Generate a unique challenge message for wallet signature authentication
        
        Args:
            wallet_address: The wallet address of the user
            
        Returns:
            str: The challenge message to be signed
        """
        # Generate a random nonce
        nonce = secrets.token_hex(16)
        
        # Create a message including the wallet address and nonce
        timestamp = datetime.now(pytz.utc).isoformat()
        message = f"Sign this message to authenticate with your Solana wallet.\nWallet: {wallet_address}\nNonce: {nonce}\nTimestamp: {timestamp}"
        
        return message
    
    @staticmethod
    def verify_signature(wallet_address: str, message: str, signature: str) -> bool:
        """Verify if a signature was created by the owner of a Solana wallet address
        
        Args:
            wallet_address: The Solana wallet address to verify against
            message: The original message that was signed
            signature: The signature to verify (base58 encoded)
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # For Solana verification we'll use PyNaCl directly without Solana-specific libraries
            # First, we need to convert the wallet address from base58 to bytes
            try:
                pubkey_bytes = base58.b58decode(wallet_address)
                if len(pubkey_bytes) != 32:  # Solana public keys are 32 bytes
                    logger.error(f"Invalid public key length: {len(pubkey_bytes)}")
                    return False
            except Exception as e:
                logger.error(f"Failed to decode wallet address: {str(e)}")
                return False
                
            # Decode the base58 signature
            try:
                signature_bytes = base58.b58decode(signature)
                if len(signature_bytes) < 64:  # Ed25519 signatures are 64 bytes
                    logger.error(f"Invalid signature length: {len(signature_bytes)}")
                    return False
            except Exception as e:
                logger.error(f"Failed to decode signature: {str(e)}")
                return False
                
            # Use PyNaCl for Ed25519 verification
            try:
                # Create a VerifyKey from the public key bytes
                verify_key = VerifyKey(pubkey_bytes)
                
                # The actual signature is the first 64 bytes
                sig = signature_bytes[:64]
                
                # Verify the signature
                verify_key.verify(message.encode(), sig)
                return True
            except BadSignatureError:
                logger.error("Bad signature")
                return False
            except Exception as e:
                logger.error(f"Verification error: {str(e)}")
                return False
                
        except Exception as e:
            # Log the error
            logger.error(f"Solana signature verification failed: {str(e)}")
            return False
