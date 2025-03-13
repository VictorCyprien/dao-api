from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from typing import List, Optional
from datetime import datetime, timezone
import json

from api import Base


class DiscordMessage(Base):
    __tablename__ = "discord_messages"
    __table_args__ = {'extend_existing': True}

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    """Discord message ID"""

    channel_id: Mapped[str] = mapped_column(String, ForeignKey('discord_channels.channel_id', ondelete='CASCADE'), nullable=False)
    """ID of the channel this message belongs to"""

    username: Mapped[str] = mapped_column(String, nullable=False)
    """Discord username of the sender"""

    user_id: Mapped[str] = mapped_column(String, nullable=False)
    """Discord user ID of the sender"""


    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    """When the message was sent on Discord"""

    text: Mapped[str] = mapped_column(Text, nullable=True)
    """Message text content"""

    media_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """JSON-serialized list of media URLs"""

    has_media: Mapped[bool] = mapped_column(Boolean, default=False)
    """Whether the message contains media"""
    
    indexed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    """When we indexed this message"""

    # Relationships
    channel = relationship("DiscordChannel", back_populates="messages")

    @classmethod
    def get_by_id(cls, message_id: str, session: Session) -> Optional["DiscordMessage"]:
        """Get message by Discord ID"""
        return session.query(cls).filter(cls.message_id == message_id).first()

    @classmethod
    def get_by_channel(cls, channel_id: str, session: Session, limit: int = 100) -> List["DiscordMessage"]:
        """Get messages from a specific channel"""
        return session.query(cls).filter(cls.channel_id == channel_id).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_pod(cls, pod_id: str, session: Session, limit: int = 100) -> List["DiscordMessage"]:
        """Get messages from all channels associated with a specific POD"""
        from api.models.discord_channel import DiscordChannel
        
        channels = session.query(DiscordChannel).filter(DiscordChannel.pod_id == pod_id).all()
        channel_ids = [channel.channel_id for channel in channels]
        
        if not channel_ids:
            return []
            
        return session.query(cls).filter(cls.channel_id.in_(channel_ids)).order_by(cls.created_at.desc()).limit(limit).all()

    def to_dict(self):
        """Convert model to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "channel_id": self.channel_id,
            "username": self.username,
            "user_id": self.user_id,
            "text": self.text,
            "has_media": self.has_media,
            "media_urls": json.loads(self.media_urls) if self.media_urls else [],
            "created_at": self.created_at,
            "indexed_at": self.indexed_at
        }
    
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "message_id": self.message_id,
            "channel_id": self.channel_id,
            "username": self.username,
            "user_id": self.user_id,
            "text": self.text,
            "has_media": self.has_media,
            "media_urls": json.loads(self.media_urls) if self.media_urls else [],
            "created_at": self.created_at,
            "indexed_at": self.indexed_at
        }.items() 