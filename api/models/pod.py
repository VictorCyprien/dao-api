from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

import random
import sys

from datetime import datetime, timezone

from api import Base

# Association table for POD participants
pod_participants = Table(
    'pod_participants',
    Base.metadata,
    Column('pod_id', BigInteger, ForeignKey('pod.pod_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class POD(Base):
    __tablename__ = "pod"
    __table_args__ = {'extend_existing': True}

    pod_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    """ ID of the POD """

    community_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('communities.community_id', ondelete='CASCADE'), nullable=False)
    """ ID of the community this POD belongs to """

    name: Mapped[str] = mapped_column(String, nullable=False)
    """ Name of the POD group """

    description: Mapped[str] = mapped_column(String, nullable=False)
    """ Description of what needs to be learned """

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    """ Whether the POD is active """

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    """ Timestamp of when the POD was created """

    # Relationships
    community = relationship('Community', back_populates='pods')
    """ Community that the POD belongs to """

    participants = relationship('User', secondary=pod_participants, back_populates='participating_pods')
    """ Participants of the POD """

    @classmethod
    def create(cls, input_data: dict) -> "POD":
        """ Create a new POD instance """
        pod = POD(
            pod_id=cls.generate_pod_id(),
            community_id=input_data["community_id"],
            name=input_data["name"],
            description=input_data["description"],
            is_active=True
        )
        return pod

    def update(self, input_data: dict):
        """ Update the current instance of a POD """
        name = input_data.get("name", None)
        description = input_data.get("description", None)
        is_active = input_data.get("is_active", None)

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_active is not None:
            self.is_active = is_active

    def add_participant(self, user) -> bool:
        """ Add a user as participant if they're not already """
        if user not in self.participants:
            self.participants.append(user)
            return True
        return False

    def remove_participant(self, user) -> bool:
        """ Remove a user from participants """
        if user in self.participants:
            self.participants.remove(user)
            return True
        return False

    @classmethod
    def get_by_id(cls, id: int, session: Session) -> "POD":
        """ POD getter with an ID """
        return session.query(cls).filter(cls.pod_id == id).first()
    
    @classmethod
    def get_community_pods(cls, community_id: int, session: Session):
        """Get all PODs for a community using session"""
        return session.query(cls).filter_by(community_id=community_id).all()

    @classmethod
    def generate_pod_id(cls) -> int:
        """ Generate a random POD ID """
        return random.randint(1, sys.maxsize)
