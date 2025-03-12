from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


### Common schemas ###

class Error(BaseModel):
    """Error response model"""
    code: int = Field(..., description="Error code")
    status: str = Field(..., description="Error name")
    message: str = Field(..., description="Error message")
    errors: Optional[Dict[str, Any]] = Field(None, description="Errors")


class PaginationMetadata(BaseModel):
    """Pagination metadata"""
    total: int
    total_pages: int
    first_page: int
    last_page: int
    page: int
    previous_page: Optional[int]
    next_page: Optional[int]


class PagingError(BaseModel):
    """Error information"""
    code: int = Field(..., description="Error status code")
    message: str = Field(..., description="Error message")
    status: str = Field(..., description="Error status")


### Auth schemas ###

class LogoutResponse(BaseModel):
    """Logout details"""
    msg: str = Field(..., description="Message of logout")


class ChallengeRequest(BaseModel):
    """Request to generate authentication challenge"""
    wallet_address: str = Field(..., description="Wallet address of the user")


class ChallengeResponse(BaseModel):
    """Challenge message for wallet authentication"""
    message: str = Field(..., description="Challenge message to sign")
    wallet_address: str = Field(..., description="Wallet address of the user")


class VerifySignature(BaseModel):
    """Verification of wallet signature"""
    wallet_address: str = Field(..., description="Wallet address of the user")
    signature: str = Field(..., description="Signed message from wallet")


class LoginResponse(BaseModel):
    """Token of the user"""
    msg: str = Field(..., description="Message of login")
    token: str = Field(..., description="Token of the user")


### User schemas ###

class InputCreateUser(BaseModel):
    """Input information needed to create user"""
    username: str = Field(..., description="Username of the user")
    wallet_address: str = Field(..., description="Wallet address of the user")
    email: Optional[EmailStr] = Field(None, description="Email of the user")
    member_name: Optional[str] = Field(None, description="Display name of the user")
    discord_username: Optional[str] = Field(None, description="Discord username of the user")
    twitter_username: Optional[str] = Field(None, description="Twitter username of the user")
    telegram_username: Optional[str] = Field(None, description="Telegram username of the user")


class User(BaseModel):
    """User information"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username of the user")
    wallet_address: str = Field(..., description="Wallet address of the user")
    email: Optional[str] = Field(None, description="Email of the user")
    member_name: Optional[str] = Field(None, description="Display name of the user")
    discord_username: Optional[str] = Field(None, description="Discord username of the user")
    twitter_username: Optional[str] = Field(None, description="Twitter username of the user")
    telegram_username: Optional[str] = Field(None, description="Telegram username of the user")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    last_interaction: Optional[datetime] = Field(None, description="Last interaction timestamp")
    email_verified: Optional[bool] = Field(None, description="Whether the email is verified")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")


class UserResponse(BaseModel):
    """Create/Update a user response"""
    action: Optional[str] = Field(None, description="Action performed")
    user: User = Field(..., description="User information")


class UserExistResponse(BaseModel):
    """Check if user with the wallet address exists"""
    exists: bool = Field(..., description="Whether the user exists")


class InputUpdateUser(BaseModel):
    """New user information"""
    username: Optional[str] = Field(None, description="New username of the user")
    email: Optional[EmailStr] = Field(None, description="New email of the user")
    member_name: Optional[str] = Field(None, description="New display name of the user")
    discord_username: Optional[str] = Field(None, description="New Discord username of the user")
    twitter_username: Optional[str] = Field(None, description="New Twitter username of the user")
    telegram_username: Optional[str] = Field(None, description="New Telegram username of the user")


class UserBasic(BaseModel):
    """Basic user information"""
    user_id: str
    username: str


### DAO models ###

class DAOMembership(BaseModel):
    """DAO membership"""
    user_id: Optional[str] = Field(None, description="User ID")


class InputCreateDAO(BaseModel):
    """Input information needed to create a DAO"""
    name: str = Field(..., description="DAO name")
    description: str = Field(..., description="DAO description")
    owner_id: str = Field(..., description="Owner ID")


class DAO(BaseModel):
    """DAO information"""
    dao_id: str = Field(..., description="DAO ID")
    name: str = Field(..., description="DAO name")
    description: str = Field(..., description="DAO description")
    owner_id: str = Field(..., description="Owner ID")
    is_active: bool = Field(..., description="Whether the DAO is active")
    admins: List[UserBasic] = Field(..., description="List of admins")
    members: List[UserBasic] = Field(..., description="List of members")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Example DAO",
                "description": "This is an example DAO",
                "owner_id": "user_123",
                "is_active": True
            }
        }


class DAOUpdate(BaseModel):
    """DAO update information"""
    name: Optional[str] = Field(None, min_length=1, description="DAO name")
    description: Optional[str] = Field(None, min_length=1, description="DAO description")
    is_active: Optional[bool] = Field(None, description="Whether the DAO is active")


### POD schemas ###

class PODMembership(BaseModel):
    """POD membership"""
    user_id: Optional[str] = Field(None, description="User ID")


class InputCreatePOD(BaseModel):
    """Input information needed to create a POD"""
    dao_id: str = Field(..., description="DAO ID")
    name: str = Field(..., description="POD name")
    description: str = Field(..., description="POD description")


class POD(BaseModel):
    """POD information"""
    pod_id: Optional[str] = Field(None, description="POD ID")
    dao_id: str = Field(..., description="DAO ID")
    name: str = Field(..., description="POD name")
    description: str = Field(..., description="POD description")
    is_active: Optional[bool] = Field(None, description="Whether the POD is active")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class PODUpdate(BaseModel):
    """POD update information"""
    name: Optional[str] = Field(None, min_length=1, description="POD name")
    description: Optional[str] = Field(None, min_length=1, description="POD description")
    is_active: Optional[bool] = Field(None, description="Whether the POD is active")


### Data schemas ### (need to be reworked for new data model)

class Item(BaseModel):
    """Information about the data from SQLite"""
    id: Optional[int] = None
    cid: Optional[str] = None
    type: str
    source: Union[str, Dict[str, Any]]
    title: Optional[str] = None
    text: str
    link: Optional[str] = None
    topics: Optional[str] = None
    date: int
    metadata: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "cid": "QmExample",
                "type": "article",
                "source": "news",
                "title": "Example Title",
                "text": "Example text content",
                "link": "https://example.com",
                "topics": "example,topic",
                "date": 1620000000,
                "metadata": "{}"
            }
        }


class ItemsResponse(BaseModel):
    """Items response schema"""
    data: List[Item]


class SummaryResponse(BaseModel):
    """Summary response schema"""
    summary: List[Dict[str, List[Item]]]


class QueryParams(BaseModel):
    """Query parameters for data filtering"""
    date_start: str = Field(..., description="Start date in YYYY-MM-DD format")
    date_end: str = Field(..., description="End date in YYYY-MM-DD format")
    source: Optional[str] = Field(None, description="Optional source filter")


# Create models for validators with custom rules
class CreateItemRequest(BaseModel):
    """Request model for creating a new item"""
    type: str = Field(..., description="Type of the item")
    source: str = Field(..., description="Source of the item")
    title: Optional[str] = Field(None, description="Title of the item")
    text: str = Field(..., description="Content text", min_length=10)
    link: Optional[str] = Field(None, description="URL link")
    topics: Optional[str] = Field(None, description="Comma-separated topics")
    
    @field_validator('type')
    def type_must_be_valid(cls, v):
        valid_types = ['article', 'tweet', 'forum', 'news']
        if v not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "type": "article",
                "source": "news",
                "title": "New Article",
                "text": "This is a new article with at least 10 characters",
                "link": "https://example.com",
                "topics": "crypto,blockchain,dao"
            }
        }

# Treasury-related schemas
class TokenBase(BaseModel):
    """Base Token model"""
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    contract: Optional[str] = Field(None, description="Contract address of the token on the blockchain")
    amount: float = Field(0.0, description="Amount of tokens")
    price: float = Field(0.0, description="Current price of the token")
    percentage: int = Field(0, description="Percentage of treasury this token represents", ge=0, le=100)

class InputCreateToken(TokenBase):
    """Input information needed to create a Token"""
    dao_id: str = Field(..., description="DAO ID this token belongs to")

class TokenModel(TokenBase):
    """Token information"""
    token_id: str = Field(..., description="Token ID")
    dao_id: str = Field(..., description="DAO ID this token belongs to")
    value: float = Field(..., description="Total value of the token holding (amount * price)")

    class Config:
        schema_extra = {
            "example": {
                "token_id": "123456789",
                "dao_id": "987654321",
                "name": "Steakhouse USDT",
                "symbol": "USDT",
                "amount": 14000.0,
                "price": 1.08,
                "percentage": 60,
                "value": 15120.0
            }
        }

class TokenUpdate(BaseModel):
    """Token update information"""
    name: Optional[str] = Field(None, min_length=1, description="Token name")
    symbol: Optional[str] = Field(None, min_length=1, description="Token symbol")
    contract: Optional[str] = Field(None, description="Contract address of the token on the blockchain")
    amount: Optional[float] = Field(None, description="Amount of tokens")
    price: Optional[float] = Field(None, description="Current price of the token")
    percentage: Optional[int] = Field(None, description="Percentage of treasury this token represents", ge=0, le=100)

class TransferBase(BaseModel):
    """Base Transfer model"""
    from_address: str = Field(..., description="Wallet address that sent the tokens")
    to_address: str = Field(..., description="Wallet address that received the tokens")
    amount: float = Field(..., description="Amount of tokens transferred")
    timestamp: Optional[datetime] = Field(None, description="When the transfer occurred")

class InputCreateTransfer(TransferBase):
    """Input information needed to create a Transfer"""
    dao_id: str = Field(..., description="DAO ID this transfer belongs to")
    token_id: str = Field(..., description="Token ID")

class TransferModel(TransferBase):
    """Transfer information"""
    transfer_id: str = Field(..., description="Transfer ID")
    dao_id: str = Field(..., description="DAO ID this transfer belongs to")
    token_id: str = Field(..., description="Token ID")
    token: Optional[TokenModel] = Field(None, description="Token information")

    class Config:
        schema_extra = {
            "example": {
                "transfer_id": "123456789",
                "dao_id": "987654321",
                "token_id": "987654321",
                "from_address": "0x123456789abcdef",
                "to_address": "0xfedcba987654321",
                "amount": 1000.0,
                "timestamp": "2023-08-15T14:30:00Z",
                "token": {
                    "token_id": "987654321",
                    "dao_id": "123456789",
                    "name": "Steakhouse USDT",
                    "symbol": "USDT",
                    "amount": 14000.0,
                    "price": 1.08,
                    "percentage": 60,
                    "value": 15120.0
                }
            }
        }

class TreasuryModel(BaseModel):
    """Treasury information"""
    total_value: float = Field(..., description="Total value of all tokens")
    daily_change: float = Field(..., description="Value change in the last 24 hours")
    daily_change_percentage: float = Field(..., description="Percentage change in the last 24 hours")
    tokens: List[TokenModel] = Field(..., description="Tokens in the treasury")
    recent_transfers: List[TransferModel] = Field(..., description="Recent transfers")

    class Config:
        schema_extra = {
            "example": {
                "total_value": 26632122.28,
                "daily_change": 111172.70,
                "daily_change_percentage": 0.42,
                "tokens": [
                    {
                        "token_id": "123456789",
                        "dao_id": "987654321",
                        "name": "Steakhouse USDT",
                        "symbol": "USDT",
                        "amount": 14000000.0,
                        "price": 1.08,
                        "percentage": 60,
                        "value": 15120000.0
                    },
                    {
                        "token_id": "987654321",
                        "dao_id": "987654321",
                        "name": "Steakhouse ETH",
                        "symbol": "ETH",
                        "amount": 5413.96,
                        "price": 1951.42,
                        "percentage": 40,
                        "value": 10564891.66
                    }
                ],
                "recent_transfers": [
                    {
                        "transfer_id": "123456789",
                        "token_id": "123456789",
                        "from_address": "0x123456789abcdef",
                        "to_address": "0xfedcba987654321",
                        "amount": 14000.0,
                        "timestamp": "2023-08-15T14:30:00Z"
                    }
                ]
            }
        } 