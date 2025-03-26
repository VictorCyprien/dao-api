from marshmallow import Schema, fields, validates_schema, ValidationError

from api.models.user import User
from helpers.schemas_file import OmitNoneField


class UserSchema(Schema):
    user_id = fields.String(
        attribute='user_id',
        metadata={"description": "Unique user identifier"}
    )
    username = fields.String(metadata={"description": "Username of the user"})
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"})
    email = OmitNoneField(metadata={"description": "Email of the user"})
    member_name = OmitNoneField(metadata={"description": "Display name of the user"})
    profile_picture = OmitNoneField(metadata={"description": "Profile picture of the user"})
    discord_username = OmitNoneField(metadata={"description": "Discord username of the user"})
    twitter_username = OmitNoneField(metadata={"description": "Twitter username of the user"})
    telegram_username = OmitNoneField(metadata={"description": "Telegram username of the user"})
    last_login = fields.DateTime(metadata={"description": "Last login timestamp"})
    last_interaction = fields.DateTime(metadata={"description": "Last interaction timestamp"})
    email_verified = fields.Boolean(metadata={"description": "Whether the email is verified"})
    is_active = fields.Boolean(metadata={"description": "Whether the user is active"})

    class Meta:
        ordered = True
        description = "User informations."



class UserResponseSchema(Schema):
    action = fields.String()
    user = fields.Nested(UserSchema)

    class Meta:
        ordered = True
        description = "Create/Update a user."


class UserExistResponseSchema(Schema):
    exists = fields.Boolean()

    class Meta:
        ordered = True
        description = "Check if user with the wallet address exists."


class InputCreateUserSchema(Schema):
    username = fields.String(metadata={"description": "Username of the user"}, required=True)
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"}, required=True)
    email = fields.Email(metadata={"description": "Email of the user"})
    member_name = fields.String(metadata={"description": "Display name of the user"})
    profile_picture = fields.Raw(metadata={"description": "Profile picture of the user", 'type': 'string', 'format': 'binary'})
    discord_username = fields.String(metadata={"description": "Discord username of the user"})
    twitter_username = fields.String(metadata={"description": "Twitter username of the user"})
    telegram_username = fields.String(metadata={"description": "Telegram username of the user"})

    @validates_schema
    def validation_payload(self, data, **kwargs):
        username: str = data.get("username", None)
        wallet_address: str = data.get("wallet_address", None)

        if username is None:
            raise ValidationError("Invalid payload", field_name="username")

        if wallet_address is None:
            raise ValidationError("Invalid payload", field_name="wallet_address")

    class Meta:
        description = "Input information needed to create user."
        ordered = True


class InputUpdateUserSchema(Schema):
    username = fields.String(metadata={"description": "New username of the user"})
    email = fields.String(metadata={"description": "New email of the user"})
    member_name = fields.String(metadata={"description": "New display name of the user"})
    profile_picture = fields.Raw(metadata={"description": "New profile picture of the user", 'type': 'string', 'format': 'binary'})
    discord_username = fields.String(metadata={"description": "New Discord username of the user"})
    twitter_username = fields.String(metadata={"description": "New Twitter username of the user"})
    telegram_username = fields.String(metadata={"description": "New Telegram username of the user"})

    class Meta:
        description = "New user information"
        ordered = True
