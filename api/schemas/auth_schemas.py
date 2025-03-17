from marshmallow import Schema, fields, validate



class LoginResponseSchema(Schema):
    msg = fields.String(metadata={"description": "Message of login"})
    token = fields.String(metadata={"description": "Token of the user"})

    class Meta:
        description = "Token of the user"
        ordered = True


class LogoutResponseSchema(Schema):
    msg = fields.String(metadata={"description": "Message of logout"})

    class Meta:
        description = "Logout details"
        ordered = True


# New schemas for signature-based authentication
class ChallengeRequestSchema(Schema):
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"}, required=True)
    
    class Meta:
        description = "Request to generate authentication challenge"
        ordered = True


class ChallengeResponseSchema(Schema):
    message = fields.String(metadata={"description": "Challenge message to sign"})
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"})
    
    class Meta:
        description = "Challenge message for wallet authentication"
        ordered = True


class VerifySignatureSchema(Schema):
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"}, required=True)
    signature = fields.String(metadata={"description": "Signed message from wallet"}, required=True)
    
    class Meta:
        description = "Verification of wallet signature"
        ordered = True


# Base connection response schema
class SocialConnectionSchema(Schema):
    provider = fields.String(required=True, description="Social provider name (discord, twitter, telegram)")
    provider_user_id = fields.String(required=True, description="User ID from the provider")
    provider_username = fields.String(required=True, description="Username from the provider")
    connected_at = fields.DateTime(description="When the connection was established")
    updated_at = fields.DateTime(description="When the connection was last updated")

# Connection response schemas
class ConnectionResponseSchema(Schema):
    message = fields.String(required=True, description="Success message")
    connection = fields.Nested(SocialConnectionSchema, description="Connection details")

class OAuthResponseSchema(Schema):
    auth_url = fields.String(required=True, description="Authorization URL")
    message = fields.String(required=True, description="Success message")

class DisconnectResponseSchema(Schema):
    message = fields.String(required=True, description="Success message")

class ConnectionsListSchema(Schema):
    connections = fields.List(fields.Nested(SocialConnectionSchema), required=True, description="List of social connections")
    discord_connected = fields.Boolean(required=True, description="Whether Discord is connected")
    twitter_connected = fields.Boolean(required=True, description="Whether Twitter is connected")
    telegram_connected = fields.Boolean(required=True, description="Whether Telegram is connected")

# Telegram specific schemas
class TelegramAuthSchema(Schema):
    id = fields.Integer(required=True, description="Telegram user ID")
    first_name = fields.String(required=True, description="User's first name")
    username = fields.String(required=True, description="Telegram username")
    photo_url = fields.String(description="URL of the user's profile photo")
    auth_date = fields.Integer(required=True, description="Authentication date (Unix time)")
    hash = fields.String(required=True, description="Authentication hash")

# Error schemas
class OAuthErrorSchema(Schema):
    error = fields.String(required=True, description="Error message")
    code = fields.Integer(description="Error code")

# State validation error
class StateValidationErrorSchema(Schema):
    error = fields.String(required=True, description="State validation error")

# Token exchange error
class TokenExchangeErrorSchema(Schema):
    error = fields.String(required=True, description="Token exchange error")

# User info error
class UserInfoErrorSchema(Schema):
    error = fields.String(required=True, description="User info retrieval error")

# Database error
class DatabaseErrorSchema(Schema):
    error = fields.String(required=True, description="Database operation error")

