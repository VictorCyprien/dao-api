from typing import List
import random
import sys
from datetime import datetime
import pytz

from sqlalchemy import String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

from api import Base

class Token(Base):
    __tablename__ = "tokens"
    __table_args__ = {'extend_existing': True}

    token_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the token """

    dao_id: Mapped[str] = mapped_column(String, ForeignKey('daos.dao_id', ondelete='CASCADE'), nullable=False)
    """ ID of the DAO this token belongs to """

    name: Mapped[str] = mapped_column(String, nullable=False)
    """ Name of the token (e.g., Steakhouse USDT) """

    symbol: Mapped[str] = mapped_column(String, nullable=False)
    """ Symbol of the token (e.g., USDT, SOL) """
    
    contract: Mapped[str] = mapped_column(String, nullable=True)
    """ Contract address of the token on the blockchain (e.g., Solana: So11111111111111111111111111111111111111111) """

    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    """ Amount of tokens owned """

    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    """ Current price of the token """
    
    percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    """ Percentage of the treasury this token represents (0-100) """

    # Relationships
    dao = relationship('DAO', back_populates='tokens')
    transfers = relationship('Transfer', back_populates='token', cascade='all, delete-orphan')

    @classmethod
    def create(cls, input_data: dict) -> "Token":
        """ Create a new Token instance """
        token = Token(
            token_id=cls.generate_token_id(),
            dao_id=input_data["dao_id"],
            name=input_data["name"],
            symbol=input_data["symbol"],
            contract=input_data.get("contract"),
            amount=input_data.get("amount", 0.0),
            price=input_data.get("price", 0.0),
            percentage=input_data.get("percentage", 0)
        )
            
        return token

    def update(self, input_data: dict):
        """ Update the current instance of a Token """
        name = input_data.get("name")
        symbol = input_data.get("symbol")
        contract = input_data.get("contract")
        amount = input_data.get("amount")
        price = input_data.get("price")
        percentage = input_data.get("percentage")

        if name is not None:
            self.name = name
        if symbol is not None:
            self.symbol = symbol
        if contract is not None:
            self.contract = contract
        if amount is not None:
            self.amount = amount
        if price is not None:
            self.price = price
        if percentage is not None:
            self.percentage = percentage

    @classmethod
    def get_by_id(cls, id: str, session: Session) -> "Token":
        """ Token getter with an ID """
        return session.query(Token).filter(Token.token_id == id).first()
    
    @classmethod
    def get_by_dao_id(cls, dao_id: str, session: Session) -> List["Token"]:
        """ Get all tokens for a specific DAO """
        return session.query(Token).filter(Token.dao_id == dao_id).all()
    
    @classmethod
    def generate_token_id(cls) -> str:
        """ Generate a random token_id """
        return str(random.randint(1, sys.maxsize))

    def to_dict(self):
        """Convert Token model to dictionary for Pydantic serialization"""
        return {
            "token_id": self.token_id,
            "dao_id": self.dao_id,
            "name": self.name,
            "symbol": self.symbol,
            "contract": self.contract,
            "amount": self.amount,
            "price": self.price,
            "percentage": self.percentage,
            "value": self.amount * self.price
        }
        
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "token_id": self.token_id,
            "dao_id": self.dao_id,
            "name": self.name,
            "symbol": self.symbol,
            "contract": self.contract,
            "amount": self.amount,
            "price": self.price,
            "percentage": self.percentage,
            "value": self.amount * self.price
        }.items()


class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = {'extend_existing': True}

    transfer_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the transfer """

    dao_id: Mapped[str] = mapped_column(String, ForeignKey('daos.dao_id', ondelete='CASCADE'), nullable=False)
    """ ID of the DAO this transfer belongs to """

    token_id: Mapped[str] = mapped_column(String, ForeignKey('tokens.token_id', ondelete='CASCADE'), nullable=False)
    """ ID of the token being transferred """

    from_address: Mapped[str] = mapped_column(String, nullable=False)
    """ Wallet address that sent the tokens """

    to_address: Mapped[str] = mapped_column(String, nullable=False)
    """ Wallet address that received the tokens """
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    """ Amount of tokens transferred """
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(pytz.utc))
    """ When the transfer occurred """

    # Relationships
    token = relationship('Token', back_populates='transfers')
    dao = relationship('DAO', back_populates='transfers')

    @classmethod
    def create(cls, input_data: dict) -> "Transfer":
        """ Create a new Transfer instance """
        transfer = Transfer(
            transfer_id=cls.generate_transfer_id(),
            dao_id=input_data["dao_id"],
            token_id=input_data["token_id"],
            from_address=input_data["from_address"],
            to_address=input_data["to_address"],
            amount=input_data["amount"],
            timestamp=input_data.get("timestamp", datetime.utcnow())
        )
            
        return transfer

    @classmethod
    def get_by_id(cls, id: str, session: Session) -> "Transfer":
        """ Transfer getter with an ID """
        return session.query(Transfer).filter(Transfer.transfer_id == id).first()
    
    @classmethod
    def get_by_token_id(cls, token_id: str, session: Session) -> List["Transfer"]:
        """ Get all transfers for a specific token """
        return session.query(Transfer).filter(Transfer.token_id == token_id).order_by(Transfer.timestamp.desc()).all()
    
    @classmethod
    def get_by_dao_id(cls, dao_id: str, session: Session) -> List["Transfer"]:
        """ Get all transfers for a specific DAO """
        return session.query(Transfer).filter(Transfer.dao_id == dao_id).order_by(Transfer.timestamp.desc()).all()
    
    @classmethod
    def generate_transfer_id(cls) -> str:
        """ Generate a random transfer_id """
        return str(random.randint(1, sys.maxsize))

    def to_dict(self):
        """Convert Transfer model to dictionary for Pydantic serialization"""
        return {
            "transfer_id": self.transfer_id,
            "dao_id": self.dao_id,
            "token_id": self.token_id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "token": self.token.to_dict() if self.token else None
        }
        
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "transfer_id": self.transfer_id,
            "dao_id": self.dao_id,
            "token_id": self.token_id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "token": self.token.to_dict() if self.token else None
        }.items() 