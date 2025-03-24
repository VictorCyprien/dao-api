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

    # Required fields without defaults (must be first)
    dao_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the DAO """

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    """ Name of the DAO """

    description: Mapped[str] = mapped_column(String, nullable=False)
    """ Description of the DAO """

    owner_id: Mapped[str] = mapped_column(String, ForeignKey('users.user_id'), nullable=False)
    """ ID of the DAO owner """
    
    # Fields with defaults or nullable=True (must be after required fields)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    """ Whether the DAO is active """
    
    # Social media and website attributes (all optional)
    discord_server: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Discord server of the DAO (optional) """
    
    twitter: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Twitter account of the DAO (optional) """
    
    telegram: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Telegram channel/group of the DAO (optional) """
    
    instagram: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Instagram account of the DAO (optional) """
    
    tiktok: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ TikTok account of the DAO (optional) """
    
    website: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Website of the DAO (optional) """
    
    # Profile and banner pictures (optional)
    profile_picture: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Path to profile picture in S3 bucket (optional) """
    
    banner_picture: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """ Path to banner picture in S3 bucket (optional) """

    # Relationships
    admins = relationship('User', secondary=dao_admins, back_populates='administered_daos')
    """ Administrators of the DAO """

    members = relationship('User', secondary=dao_members, back_populates='member_daos')
    """ Members of the DAO """

    # Add explicit relationship to PODs
    pods = relationship('POD', back_populates='dao', cascade='all, delete-orphan')
    """ PODs of the DAO """
    
    # Add relationship to tokens (Treasury)
    tokens = relationship('Token', back_populates='dao', cascade='all, delete-orphan')
    """ Tokens in the DAO's treasury """
    
    # Add relationship to transfers
    transfers = relationship('Transfer', back_populates='dao', cascade='all, delete-orphan')
    """ Transfers in the DAO's treasury """
    
    # Add relationship to proposals
    proposals = relationship('Proposal', back_populates='dao', cascade='all, delete-orphan')
    """ Proposals in the DAO """

    @classmethod
    def create(cls, input_data: dict) -> "DAO":
        """ Create a new DAO instance """
        dao_id = cls.generate_dao_id()
        
        # Set default paths for profile and banner pictures if not provided
        profile_picture = input_data.get("profile_picture")
        banner_picture = input_data.get("banner_picture")
        
        dao = DAO(
            dao_id=dao_id,
            name=input_data["name"],
            description=input_data["description"],
            owner_id=input_data["owner_id"],
            is_active=True,
            discord_server=input_data.get("discord_server"),
            twitter=input_data.get("twitter"),
            telegram=input_data.get("telegram"),
            instagram=input_data.get("instagram"),
            tiktok=input_data.get("tiktok"),
            website=input_data.get("website"),
            profile_picture=profile_picture,
            banner_picture=banner_picture
        )
            
        return dao
    

    def update(self, input_data: dict):
        """ Update the current instance of a DAO
        """
        name = input_data.get("name")
        description = input_data.get("description")
        is_active = input_data.get("is_active")
        discord_server = input_data.get("discord_server")
        twitter = input_data.get("twitter")
        telegram = input_data.get("telegram")
        instagram = input_data.get("instagram")
        tiktok = input_data.get("tiktok")
        website = input_data.get("website")
        profile_picture = input_data.get("profile_picture")
        banner_picture = input_data.get("banner_picture")

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if is_active is not None:
            self.is_active = is_active
        if discord_server is not None:
            self.discord_server = discord_server
        if twitter is not None:
            self.twitter = twitter
        if telegram is not None:
            self.telegram = telegram
        if instagram is not None:
            self.instagram = instagram
        if tiktok is not None:
            self.tiktok = tiktok
        if website is not None:
            self.website = website
        if profile_picture is not None:
            self.profile_picture = profile_picture
        if banner_picture is not None:
            self.banner_picture = banner_picture


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

    def to_dict(self):
        """Convert DAO model to dictionary for Pydantic serialization"""
        result = {
            "dao_id": self.dao_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "is_active": self.is_active,
            "discord_server": self.discord_server,
            "twitter": self.twitter,
            "telegram": self.telegram,
            "instagram": self.instagram,
            "tiktok": self.tiktok,
            "website": self.website,
            "profile_picture": self.profile_picture,
            "banner_picture": self.banner_picture,
            "admins": [{"user_id": admin.user_id, "username": admin.username} for admin in self.admins],
            "members": [{"user_id": member.user_id, "username": member.username} for member in self.members]
        }
        return result
        
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "dao_id": self.dao_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "is_active": self.is_active,
            "discord_server": self.discord_server,
            "twitter": self.twitter,
            "telegram": self.telegram,
            "instagram": self.instagram,
            "tiktok": self.tiktok,
            "website": self.website,
            "profile_picture": self.profile_picture,
            "banner_picture": self.banner_picture,
            "admins": [{"user_id": admin.user_id, "username": admin.username} for admin in self.admins],
            "members": [{"user_id": member.user_id, "username": member.username} for member in self.members]
        }.items()
