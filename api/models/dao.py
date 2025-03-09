from typing import List
import random
import sys

from sqlalchemy import BigInteger, String, Boolean, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

from api import Base

# Association tables for many-to-many relationships
dao_admins = Table(
    'dao_admins',
    Base.metadata,
    Column('dao_id', String, ForeignKey('daos.dao_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

dao_members = Table(
    'dao_members',
    Base.metadata,
    Column('dao_id', String, ForeignKey('daos.dao_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class DAO(Base):
    __tablename__ = "daos"
    __table_args__ = {'extend_existing': True}

    dao_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the DAO """

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    """ Name of the DAO """

    description: Mapped[str] = mapped_column(String, nullable=False)
    """ Description of the DAO """

    owner_id: Mapped[str] = mapped_column(String, ForeignKey('users.user_id'), nullable=False)
    """ ID of the DAO owner """

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    """ Whether the DAO is active """

    # Relationships
    admins = relationship('User', secondary=dao_admins, back_populates='administered_daos')
    """ Administrators of the DAO """

    members = relationship('User', secondary=dao_members, back_populates='member_daos')
    """ Members of the DAO """

    # Add explicit relationship to PODs
    pods = relationship('POD', back_populates='dao', cascade='all, delete-orphan')
    """ PODs of the DAO """

    @classmethod
    def create(cls, input_data: dict) -> "DAO":
        """ Create a new DAO instance """
        dao = DAO(
            dao_id=cls.generate_dao_id(),
            name=input_data["name"],
            description=input_data["description"],
            owner_id=input_data["owner_id"],
            is_active=True
        )
            
        return dao
    

    def update(self, input_data: dict):
        """ Update the current instance of a DAO
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
    def get_by_id(cls, id: str, session: Session) -> "DAO":
        """ DAO getter with an ID """
        return session.query(DAO).filter(DAO.dao_id == id).first()
    
    @classmethod
    def get_by_name(cls, name: str, session: Session) -> "DAO":
        """ DAO getter with a name """
        return session.query(DAO).filter(DAO.name == name).first()
    
    @classmethod
    def get_all(cls, session: Session) -> List["DAO"]:
        """ Get all DAOs """
        return session.query(DAO).all()

    @classmethod
    def generate_dao_id(cls) -> str:
        """ Generate a random dao_id """
        return str(random.randint(1, sys.maxsize))
