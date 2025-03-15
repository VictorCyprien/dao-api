from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from typing import List

import random
import sys

from datetime import datetime, timezone

from api import Base



# Association table for POD members
pod_members = Table(
    'pod_members',
    Base.metadata,
    Column('pod_id', String, ForeignKey('pods.pod_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class POD(Base):
    __tablename__ = "pods"
    __table_args__ = {'extend_existing': True}

    pod_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the POD """

    name: Mapped[str] = mapped_column(String, nullable=False)
    """ Name of the POD """

    description: Mapped[str] = mapped_column(String, nullable=False)
    """ Description of the POD """

    dao_id: Mapped[str] = mapped_column(String, ForeignKey('daos.dao_id', ondelete='CASCADE'), nullable=False)
    """ ID of the DAO this POD belongs to """

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    """ Whether the POD is active """

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    """ Timestamp of when the POD was created """

    # Relationships
    members = relationship('User', secondary=pod_members, back_populates='member_pods')
    """ Members of the POD """
    
    dao = relationship('DAO', back_populates='pods')
    """ DAO that the POD belongs to """

    discord_channels = relationship('DiscordChannel', back_populates='pod')
    """ Discord channels associated with this POD """

    @classmethod
    def create(cls, input_data: dict) -> "POD":
        """ Create a new POD instance """
        pod = POD(
            pod_id=cls.generate_pod_id(),
            name=input_data["name"],
            description=input_data["description"],
            dao_id=input_data["dao_id"],
            is_active=True
        )
        return pod

    def update(self, input_data: dict):
        """ Update the current instance of a POD """
        name = input_data.get("name", None)
        description = input_data.get("description", None)
        is_active = input_data.get("is_active", None)
        discord_channel_id = input_data.get("discord_channel_id", None)

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_active is not None:
            self.is_active = is_active
        if discord_channel_id is not None:
            self.discord_channel_id = discord_channel_id


    def add_member(self, user) -> bool:
        """ Add a user as member if they're not already """
        if user not in self.members:
            self.members.append(user)
            return True
        return False

    def remove_member(self, user) -> bool:
        """ Remove a user from members """
        if user in self.members:
            self.members.remove(user)
            return True
        return False

    @classmethod
    def get_by_id(cls, id: int, session: Session) -> "POD":
        """ POD getter with an ID """
        return session.query(POD).filter(POD.pod_id == id).first()
    
    @classmethod
    def get_all(cls, session: Session) -> List["POD"]:
        """ Get all PODs """
        return session.query(cls).all()
    
    @classmethod
    def get_dao_pods(cls, dao_id: int, session: Session):
        """Get all PODs for a DAO using session"""
        return session.query(cls).filter_by(dao_id=dao_id).all()
    
    @classmethod
    def generate_pod_id(cls) -> str:
        """ Generate a random pod_id """
        return str(random.randint(1, sys.maxsize))

    def to_dict(self):
        """Convert POD model to dictionary for Pydantic serialization"""
        result = {
            "pod_id": self.pod_id,
            "dao_id": self.dao_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "members": [{"user_id": member.user_id, "username": member.username} for member in self.members],
            "discord_channels": [channel.to_dict() for channel in self.discord_channels] if hasattr(self, 'discord_channels') and self.discord_channels else []
        }
        return result
        
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "pod_id": self.pod_id,
            "dao_id": self.dao_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "members": [{"user_id": member.user_id, "username": member.username} for member in self.members],
            "discord_channels": [channel.to_dict() for channel in self.discord_channels] if hasattr(self, 'discord_channels') and self.discord_channels else []
        }.items()
