from api import Base
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import pytz
from cryptography.fernet import Fernet
import os
from api.config import Config


class SocialConnection(Base):
    __tablename__ = "social_connections"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the social connection """

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.user_id"), nullable=False)
    """ ID of the user this connection belongs to """

    provider: Mapped[str] = mapped_column(String, nullable=False)
    """ The provider (discord, twitter, telegram) """

    provider_user_id: Mapped[str] = mapped_column(String, nullable=False)
    """ User ID from the provider """

    provider_username: Mapped[str] = mapped_column(String, nullable=False)
    """ Username from the provider """

    access_token: Mapped[str] = mapped_column(String, nullable=True)
    """ Encrypted access token """

    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    """ Encrypted refresh token """

    token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    """ When the token expires """

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    """ When this connection was created """

    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    """ When this connection was last updated """

    # Relationship to User model
    user = relationship("User", back_populates="social_connections")

    @classmethod
    def create(cls, user_id, provider, provider_user_id, provider_username, 
               access_token=None, refresh_token=None, token_expires_at=None):
        """Create a new social connection"""
        from api.models.user import User
        import secrets
        import base58

        # Generate a unique ID
        connection_id = base58.b58encode(secrets.token_bytes(16)).decode('utf-8')
        
        # Set current timestamp for created_at and updated_at
        current_time = datetime.now(pytz.UTC)
        
        # Create a new connection
        connection = cls(
            id=connection_id,
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=provider_username,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            created_at=current_time,
            updated_at=current_time
        )
        
        # Add tokens if provided
        if access_token:
            connection.set_access_token(access_token)
        
        if refresh_token:
            connection.set_refresh_token(refresh_token)
            
        if token_expires_at:
            connection.token_expires_at = token_expires_at
            
        return connection
    
    def set_access_token(self, token):
        """Encrypt and store access token"""
        config = Config()
        cipher_suite = Fernet(config.OAUTH_ENCRYPTION_KEY.encode())
        self.access_token = cipher_suite.encrypt(token.encode()).decode()
    
    def get_access_token(self):
        """Decrypt and return access token"""
        if not self.access_token:
            return None
        
        config = Config()
        cipher_suite = Fernet(config.OAUTH_ENCRYPTION_KEY.encode())
        return cipher_suite.decrypt(self.access_token.encode()).decode()
    
    def set_refresh_token(self, token):
        """Encrypt and store refresh token"""
        config = Config()
        cipher_suite = Fernet(config.OAUTH_ENCRYPTION_KEY.encode())
        self.refresh_token = cipher_suite.encrypt(token.encode()).decode()
    
    def get_refresh_token(self):
        """Decrypt and return refresh token"""
        if not self.refresh_token:
            return None
        
        config = Config()
        cipher_suite = Fernet(config.OAUTH_ENCRYPTION_KEY.encode())
        return cipher_suite.decrypt(self.refresh_token.encode()).decode()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "provider": self.provider,
            "provider_user_id": self.provider_user_id,
            "provider_username": self.provider_username,
            "connected_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.updated_at.isoformat() if self.updated_at else None
        } 