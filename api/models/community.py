from api import Base
from sqlalchemy import BigInteger, String, Boolean, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
import random
import sys


# Association tables for many-to-many relationships
community_admins = Table(
    'community_admins',
    Base.metadata,
    Column('community_id', BigInteger, ForeignKey('communities.community_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

community_members = Table(
    'community_members',
    Base.metadata,
    Column('community_id', BigInteger, ForeignKey('communities.community_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class Community(Base):
    __tablename__ = "communities"
    __table_args__ = {'extend_existing': True}

    community_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    """ ID of the Community """

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    """ Name of the community """

    description: Mapped[str] = mapped_column(String, nullable=False)
    """ Description of the community """

    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    """ ID of the community owner """

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    """ Whether the community is active """

    # Relationships
    admins = relationship('User', secondary=community_admins, back_populates='administered_communities')
    """ Administrators of the community """

    members = relationship('User', secondary=community_members, back_populates='member_communities')
    """ Members of the community """

    # Add explicit relationship to PODs
    pods = relationship('POD', back_populates='community', cascade='all, delete-orphan')
    """ PODs of the community """

    @classmethod
    def create(cls, input_data: dict) -> "Community":
        """ Create a new community instance """
        community = Community(
            community_id=cls.generate_community_id(),
            name=input_data["name"],
            description=input_data["description"],
            owner_id=input_data["owner_id"],
            is_active=True
        )
        
        # Add owner as both admin and member
        if "owner" in input_data:
            community.admins.append(input_data["owner"])
            community.members.append(input_data["owner"])
            
        return community
    

    def update(self, input_data: dict):
        """ Update the current instance of a Community
        """
        name = input_data.get("name", None)
        description = input_data.get("description", None)
        is_active = input_data.get("is_active", None)

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_active is not None:
            self.is_active = is_active


    def add_admin(self, user) -> bool:
        """ Add a user as admin if they're not already """
        if user not in self.admins:
            self.admins.append(user)
            if user not in self.members:
                self.members.append(user)
            return True
        return False

    def remove_admin(self, user) -> bool:
        """ Remove a user from admins """
        if user in self.admins:
            self.admins.remove(user)
            return True
        return False

    def add_member(self, user) -> bool:
        """ Add a user as member if they're not already """
        if user not in self.members:
            self.members.append(user)
            return True
        return False

    def remove_member(self, user) -> bool:
        """ Remove a user from members """
        if user in self.members:
            if user in self.admins:
                self.admins.remove(user)
            self.members.remove(user)
            return True
        return False

    @classmethod
    def get_by_id(cls, id: int, session: Session) -> "Community":
        """ Community getter with an ID """
        return session.query(Community).filter(Community.community_id == id).first()

    @classmethod
    def generate_community_id(cls) -> int:
        """ Generate a random community_id """
        return random.randint(1, sys.maxsize)
