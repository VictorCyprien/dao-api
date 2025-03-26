from typing import List
import datetime
import pytz
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

from api import Base

class WalletMonitor(Base):
    __tablename__ = "wallets_to_monitor"
    __table_args__ = {'extend_existing': True}

    # Required fields without defaults
    wallet_address: Mapped[str] = mapped_column(String, primary_key=True)
    """ Wallet address to monitor """

    # Explicitly use timezone=True to ensure timezone information is preserved
    added_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),  # This is critical for preserving timezone info
        nullable=False, 
        default=lambda: datetime.datetime.now(pytz.utc)
    )
    """ Timestamp when the wallet was added for monitoring """
    
    # Relationship back to DAO
    dao = relationship(
        'DAO', 
        primaryjoin="WalletMonitor.wallet_address == foreign(DAO.treasury_address)",
        back_populates='treasury', 
        uselist=False
    )
    """ The DAO that uses this wallet as treasury """
    
    # Relationship to tokens
    tokens = relationship('Token', back_populates='wallet', cascade='all, delete-orphan')
    """ Tokens in this wallet """
    
    @classmethod
    def create(cls, wallet_address: str) -> "WalletMonitor":
        """Create a new wallet monitoring entry with explicit timezone"""
        now = datetime.datetime.now(pytz.utc)
        print(now)
        return WalletMonitor(
            wallet_address=wallet_address,
            added_at=now
        )
    
    @classmethod
    def get_by_address(cls, wallet_address: str, session: Session) -> "WalletMonitor":
        """Get a wallet monitor entry by its address"""
        return session.query(WalletMonitor).filter(WalletMonitor.wallet_address == wallet_address).first()
    
    @classmethod
    def get_all(cls, session: Session) -> List["WalletMonitor"]:
        """Get all monitored wallets"""
        return session.query(WalletMonitor).all()
    
    def to_dict(self):
        """Convert the model to a dictionary"""
        return {
            "wallet_address": self.wallet_address,
            "added_at": self.added_at.isoformat() if self.added_at else None
        }
    
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "wallet_address": self.wallet_address,
            "added_at": self.added_at.isoformat() if self.added_at else None
        }.items() 