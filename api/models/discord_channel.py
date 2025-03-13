from sqlalchemy import String, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from typing import List, Optional
from datetime import datetime, timezone

from api import Base


class DiscordChannel(Base):
    __tablename__ = "discord_channels"
    __table_args__ = {'extend_existing': True}

    channel_id: Mapped[str] = mapped_column(String, primary_key=True)
    """Discord channel ID"""

    name: Mapped[str] = mapped_column(String, nullable=False)
    """Name of the Discord channel"""

    pod_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('pods.pod_id', ondelete='SET NULL'), nullable=True)
    """Optional connection to a POD"""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    """When this channel was added to our system"""

    last_synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    """When messages were last synced from this channel"""

    # Relationships
    messages = relationship("DiscordMessage", back_populates="channel", cascade="all, delete-orphan")
    pod = relationship("POD", back_populates="discord_channels")

    @classmethod
    def get_by_id(cls, channel_id: str, session: Session) -> Optional["DiscordChannel"]:
        """Get channel by Discord ID"""
        return session.query(cls).filter(cls.channel_id == channel_id).first()
    
    @classmethod
    def get_by_pod_id(cls, pod_id: str, session: Session) -> List["DiscordChannel"]:
        """Get all channels associated with a specific POD"""
        return session.query(cls).filter(cls.pod_id == pod_id).all()

    def to_dict(self):
        """Convert model to dictionary for serialization"""
        return {
            "channel_id": self.channel_id,
            "name": self.name,
            "pod_id": self.pod_id,
            "created_at": self.created_at,
            "last_synced_at": self.last_synced_at,
            "message_count": len(self.messages) if self.messages else 0
        }
    
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "channel_id": self.channel_id,
            "name": self.name,
            "pod_id": self.pod_id,
            "created_at": self.created_at,
            "last_synced_at": self.last_synced_at,
            "message_count": len(self.messages) if self.messages else 0
        }.items() 