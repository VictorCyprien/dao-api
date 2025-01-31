from marshmallow import Schema, fields, validates_schema, ValidationError, post_dump
from marshmallow.validate import Range

from ..models.user import User


class UserSchema(Schema):
    # If the value is None or the list if empty, we don't display this in the user schema
    EMPTY_VALUES = [None, []]

    user_id = fields.Integer(
        attribute='user_id',
        metadata={"description": "Unique user identifier"}
    )
    username = fields.String(metadata={"description": "Username of the user"})
    email = fields.String(metadata={"description": "Email of the user"})
    discord_username = fields.String(metadata={"description": "Discord username of the user"})
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"})
    github_username = fields.String(metadata={"description": "Github username of the user"})


    class Meta:
        ordered = True
        description = "User informations."



class UserResponseSchema(Schema):
    action = fields.String()
    user = fields.Nested(UserSchema)

    class Meta:
        ordered = True
        description = "Create/Update a user."


class InputCreateUserSchema(Schema):
    username = fields.String(metadata={"description": "Username of the user"})
    email = fields.String(metadata={"description": "Email of the user"})
    discord_username = fields.String(metadata={"description": "Discord username of the user"})
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"})
    github_username = fields.String(metadata={"description": "Github username of the user"})

    @validates_schema
    def validation_payload(self, data, **kwargs):
        email: str = data.get("email", None)
        discord_username: str = data.get("discord_username", None)
        wallet_address: str = data.get("wallet_address", None)
        github_username: str = data.get("github_username", None)

        if not email:
            raise ValidationError("The email cannot be null")
        if not discord_username:
            raise ValidationError("The discord username cannot be null")
        if not wallet_address:
            raise ValidationError("The wallet address cannot be null")
        if not github_username:
            raise ValidationError("The github username cannot be null")


    class Meta:
        description = "Input informations need to create user."
        ordered = True


class InputUpdateUserSchema(Schema):
    username = fields.String(metadata={"description": "New Username of the user"})
    email = fields.String(metadata={"description": "New Email of the user"})
    discord_username = fields.String(metadata={"description": "New Discord username of the user"})
    wallet_address = fields.String(metadata={"description": "New Wallet address of the user"})
    github_username = fields.String(metadata={"description": "New Github username of the user"})


    class Meta:
        description = "New user information"
        ordered = True
