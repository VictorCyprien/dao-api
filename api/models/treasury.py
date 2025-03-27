from typing import List, Dict
import random
import sys
from datetime import datetime
import pytz

from sqlalchemy import String, Float, ForeignKey, DateTime, Integer, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship

from api import Base
from api.models.wallet_monitor import WalletMonitor

class Token(Base):
    __tablename__ = "token_accounts"
    __table_args__ = {'extend_existing': True}

    token_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ Unique identifier for the token account """
    
    wallet_address: Mapped[str] = mapped_column(String, ForeignKey('wallets_to_monitor.wallet_address'), nullable=True)
    """ Wallet address that holds the token """
    
    token_mint: Mapped[str] = mapped_column(String, nullable=False)
    """ Token mint address (contract) """
    
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False)
    """ Token balance """
    
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    """ When the token account was last updated """
    
    symbol: Mapped[str] = mapped_column(String, nullable=True)
    """ Symbol of the token """
    
    decimals: Mapped[int] = mapped_column(Integer, nullable=True)
    """ Number of decimal places for the token """
    
    # Relationships
    wallet = relationship('WalletMonitor', foreign_keys=[wallet_address], back_populates='tokens')

    @classmethod
    def create(cls, input_data: dict) -> "Token":
        """ Create a new Token instance """
        token_id = cls.generate_token_id()
        token = Token(
            token_id=token_id,
            wallet_address=input_data.get("wallet_address"),
            token_mint=input_data["token_mint"],
            balance=input_data["balance"],
            last_updated=input_data.get("last_updated", datetime.now(pytz.utc)),
            symbol=input_data.get("symbol"),
            decimals=input_data.get("decimals")
        )
            
        return token

    def update(self, input_data: dict):
        """ Update the current instance of a Token """
        wallet_address = input_data.get("wallet_address")
        token_mint = input_data.get("token_mint")
        balance = input_data.get("balance")
        symbol = input_data.get("symbol")
        decimals = input_data.get("decimals")

        if wallet_address is not None:
            self.wallet_address = wallet_address
        if token_mint is not None:
            self.token_mint = token_mint
        if balance is not None:
            self.balance = balance
        if symbol is not None:
            self.symbol = symbol
        if decimals is not None:
            self.decimals = decimals
            
        # Update the last_updated timestamp automatically
        self.last_updated = datetime.now(pytz.utc)

    @classmethod
    def generate_token_id(cls) -> str:
        """ Generate a random token_id """
        return str(random.randint(1, sys.maxsize))

    @classmethod
    def get_by_id(cls, token_id: str, session: Session) -> "Token":
        """ Token getter with an ID """
        return session.query(Token).filter(Token.token_id == token_id).first()
    
    @classmethod
    def get_by_wallet_address(cls, wallet_address: str, session: Session) -> List[Dict]:
        """ Get all tokens for a specific wallet """
        tokens = session.query(Token).filter(Token.wallet_address == wallet_address).all()
        tokens_list = []
        for token in tokens:
            token_info = Token.get_more_token_info(token.token_mint, session)
            tokens_list.append(
                {
                    "token_id": token.token_id,
                    "wallet_address": token.wallet_address,
                    "token_mint": token.token_mint,
                    "balance": token.balance,
                    "last_updated": token.last_updated,
                    "symbol": token.symbol,
                    "price": token_info.get("price", None),
                    "price_change_percentage": token_info.get("price_24h_change", None),
                    "photo_url": token_info.get("image_url", None)
                }
            )
        return tokens_list
    
    @classmethod
    def get_by_wallet_and_mint(cls, wallet_address: str, token_mint: str, session: Session) -> "Token":
        """ Get token by wallet address and token mint """
        return session.query(Token).filter(
            Token.wallet_address == wallet_address,
            Token.token_mint == token_mint
        ).first()
    
    @classmethod
    def get_more_token_info(cls, token_mint: str, session: Session) -> Dict:
        """ Get more token info """
        query = text(
        """
        SELECT 
            ta.*,
            te.symbol,
            te.price,
            te.price_24h_change,
            te.image_url
        FROM 
            token_accounts ta
        JOIN 
            token_entity te ON ta.token_mint = te.token_id
        WHERE 
            ta.token_mint = :token_mint
        """)
        result = session.execute(query, {"token_mint": token_mint})
        return result.fetchone()._asdict()

    def to_dict(self):
        """Convert Token model to dictionary for Pydantic serialization"""
        return {
            "token_id": self.token_id,
            "wallet_address": self.wallet_address,
            "token_mint": self.token_mint,
            "balance": self.balance,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "symbol": self.symbol,
            "decimals": self.decimals
        }
        
    def __iter__(self):
        """Make the model iterable for dict() conversion"""
        yield from {
            "token_id": self.token_id,
            "wallet_address": self.wallet_address,
            "token_mint": self.token_mint,
            "balance": self.balance,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "symbol": self.symbol,
            "decimals": self.decimals
        }.items()


class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = {'extend_existing': True}

    transfer_id: Mapped[str] = mapped_column(String, primary_key=True)
    """ ID of the transfer """

    dao_id: Mapped[str] = mapped_column(String, ForeignKey('daos.dao_id', ondelete='CASCADE'), nullable=False)
    """ ID of the DAO this transfer belongs to """

    token_id: Mapped[str] = mapped_column(String, nullable=False)
    """ ID of the token being transferred (token mint address) """

    from_address: Mapped[str] = mapped_column(String, nullable=False)
    """ Wallet address that sent the tokens """

    to_address: Mapped[str] = mapped_column(String, nullable=False)
    """ Wallet address that received the tokens """
    
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    """ Amount of tokens transferred """
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(pytz.utc))
    """ When the transfer occurred """

    # Relationships
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
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
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
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }.items() 