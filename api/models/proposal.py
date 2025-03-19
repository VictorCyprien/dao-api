from datetime import datetime
from typing import List, Optional
import random
import sys

from sqlalchemy import String, DateTime, Integer, ForeignKey, JSON, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

from api import Base

# Association tables for users who voted
proposal_for_votes = Table(
    'proposal_for_votes',
    Base.metadata,
    Column('proposal_id', String, ForeignKey('proposals.proposal_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

proposal_against_votes = Table(
    'proposal_against_votes',
    Base.metadata,
    Column('proposal_id', String, ForeignKey('proposals.proposal_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = {'extend_existing': True}

    proposal_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the proposal """

    name: Mapped[str] = mapped_column(String, nullable=False)
    """ Name of the proposal """

    description: Mapped[str] = mapped_column(String, nullable=False)
    """ Description of the proposal """

    dao_id: Mapped[str] = mapped_column(String, ForeignKey('daos.dao_id', ondelete='CASCADE'), nullable=False)
    """ ID of the DAO this proposal belongs to """

    pod_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('pods.pod_id', ondelete='CASCADE'), nullable=True)
    """ ID of the POD this proposal belongs to (optional) """

    created_by: Mapped[str] = mapped_column(String, ForeignKey('users.user_id'), nullable=False)
    """ ID of the user who created the proposal """

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    """ Start time of the voting period """

    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    """ End time of the voting period """

    actions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    """ Optional actions to be executed if proposal passes (add wallet, remove wallet, withdraw tokens) """

    for_votes_count: Mapped[int] = mapped_column(Integer, default=0)
    """ Number of votes in favor of the proposal """

    against_votes_count: Mapped[int] = mapped_column(Integer, default=0)
    """ Number of votes against the proposal """

    # Relationships
    dao = relationship('DAO', back_populates='proposals')
    """ The DAO this proposal belongs to """

    pod = relationship('POD', backref='proposals')
    """ The POD this proposal belongs to (if any) """

    creator = relationship('User', foreign_keys=[created_by], backref='created_proposals')
    """ The user who created this proposal """

    for_voters = relationship('User', secondary=proposal_for_votes, backref='for_votes')
    """ Users who voted in favor of the proposal """

    against_voters = relationship('User', secondary=proposal_against_votes, backref='against_votes')
    """ Users who voted against the proposal """

    @classmethod
    def create(cls, input_data: dict) -> "Proposal":
        """ Create a new Proposal instance """
        proposal = Proposal(
            proposal_id=cls.generate_proposal_id(),
            name=input_data["name"],
            description=input_data["description"],
            dao_id=input_data["dao_id"],
            pod_id=input_data.get("pod_id"),  # Optional pod_id
            created_by=input_data["created_by"],
            start_time=input_data["start_time"],
            end_time=input_data["end_time"],
            actions=input_data.get("actions"),  # Optional
            for_votes_count=0,
            against_votes_count=0
        )
            
        return proposal
    
    def update(self, input_data: dict):
        """ Update the current instance of a Proposal """
        name = input_data.get("name")
        description = input_data.get("description")
        start_time = input_data.get("start_time")
        end_time = input_data.get("end_time")
        actions = input_data.get("actions")
        pod_id = input_data.get("pod_id")

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if actions is not None:
            self.actions = actions
        if pod_id is not None:
            self.pod_id = pod_id

    def can_vote(self, user) -> bool:
        """ Check if a user is allowed to vote on this proposal """
        # If the proposal is linked to a POD, only POD members can vote
        if self.pod_id is not None:
            return user in self.pod.members
        # Otherwise, any DAO member can vote (assuming this check happens elsewhere)
        return True

    def vote_for(self, user) -> bool:
        """ Register a vote in favor of the proposal """
        if not self.can_vote(user):
            return False
            
        if user not in self.for_voters and user not in self.against_voters:
            self.for_voters.append(user)
            self.for_votes_count += 1
            return True
        return False

    def vote_against(self, user) -> bool:
        """ Register a vote against the proposal """
        if not self.can_vote(user):
            return False
            
        if user not in self.for_voters and user not in self.against_voters:
            self.against_voters.append(user)
            self.against_votes_count += 1
            return True
        return False

    def remove_vote(self, user) -> bool:
        """ Remove a user's vote """
        if user in self.for_voters:
            self.for_voters.remove(user)
            self.for_votes_count -= 1
            return True
        elif user in self.against_voters:
            self.against_voters.remove(user)
            self.against_votes_count -= 1
            return True
        return False

    def is_active(self) -> bool:
        """ Check if the proposal is currently active """
        now = datetime.now()
        return self.start_time <= now <= self.end_time

    def has_passed(self) -> bool:
        """ Check if the proposal has passed (more for votes than against) """
        return self.for_votes_count > self.against_votes_count

    @classmethod
    def get_by_id(cls, id: str, session: Session) -> "Proposal":
        """ Proposal getter with an ID """
        return session.query(Proposal).filter(Proposal.proposal_id == id).first()
    
    @classmethod
    def get_by_dao_id(cls, dao_id: str, session: Session) -> List["Proposal"]:
        """ Get all proposals for a specific DAO """
        return session.query(Proposal).filter(Proposal.dao_id == dao_id).all()
    
    @classmethod
    def get_by_pod_id(cls, pod_id: str, session: Session) -> List["Proposal"]:
        """ Get all proposals for a specific POD """
        return session.query(Proposal).filter(Proposal.pod_id == pod_id).all()
    
    @classmethod
    def get_dao_only_proposals(cls, dao_id: str, session: Session) -> List["Proposal"]:
        """ Get all DAO-level proposals (proposals without a pod_id) for a specific DAO """
        return session.query(Proposal).filter(
            Proposal.dao_id == dao_id,
            Proposal.pod_id == None
        ).all()
    
    @classmethod
    def get_dao_only_pods_proposals(cls, dao_id: str, pod_id: str, session: Session) -> List["Proposal"]:
        """ Get all POD-level proposals (proposals with a pod_id) for a specific POD """
        return session.query(Proposal).filter(
            Proposal.pod_id == pod_id,
            Proposal.dao_id == dao_id
        ).all()
    
    @classmethod
    def get_all(cls, session: Session) -> List["Proposal"]:
        """ Get all proposals """
        return session.query(Proposal).all()
    
    @classmethod
    def get_active(cls, session: Session) -> List["Proposal"]:
        """ Get all currently active proposals """
        now = datetime.now()
        return session.query(Proposal).filter(
            Proposal.start_time <= now,
            Proposal.end_time >= now
        ).all()

    @classmethod
    def generate_proposal_id(cls) -> str:
        """ Generate a random proposal_id """
        return str(random.randint(1, sys.maxsize))

    def to_dict(self):
        """Convert Proposal model to dictionary for Pydantic serialization"""
        result = {
            "proposal_id": self.proposal_id,
            "name": self.name,
            "description": self.description,
            "dao_id": self.dao_id,
            "pod_id": self.pod_id,
            "created_by": self.created_by,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "actions": self.actions,
            "for_votes_count": self.for_votes_count,
            "against_votes_count": self.against_votes_count,
            "for_voters": [{"user_id": voter.user_id, "username": voter.username} for voter in self.for_voters],
            "against_voters": [{"user_id": voter.user_id, "username": voter.username} for voter in self.against_voters],
            "is_active": self.is_active(),
            "has_passed": self.has_passed()
        }
        return result
        
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "proposal_id": self.proposal_id,
            "name": self.name,
            "description": self.description,
            "dao_id": self.dao_id,
            "pod_id": self.pod_id,
            "created_by": self.created_by,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "actions": self.actions,
            "for_votes_count": self.for_votes_count,
            "against_votes_count": self.against_votes_count,
            "for_voters": [{"user_id": voter.user_id, "username": voter.username} for voter in self.for_voters],
            "against_voters": [{"user_id": voter.user_id, "username": voter.username} for voter in self.against_voters],
            "is_active": self.is_active(),
            "has_passed": self.has_passed()
        }.items() 