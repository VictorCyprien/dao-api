from marshmallow import Schema, fields, validates_schema, ValidationError

from api.models.user import User


class UserSchema(Schema):
    user_id = fields.Integer(
        attribute='user_id',
        metadata={"description": "Unique user identifier"}
    )
    username = fields.String(metadata={"description": "Username of the user"})
    wallet_address = fields.String(metadata={"description": "Wallet address of the user"})
    email = fields.String(metadata={"description": "Email of the user"})
    member_name = fields.String(metadata={"description": "Display name of the user"})
    discord_username = fields.String(metadata={"description": "Discord username of the user"})
    twitter_username = fields.String(metadata={"description": "Twitter username of the user"})
    telegram_username = fields.String(metadata={"description": "Telegram username of the user"})
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
    discord_username = fields.String(metadata={"description": "Discord username of the user"})
    twitter_username = fields.String(metadata={"description": "Twitter username of the user"})
    telegram_username = fields.String(metadata={"description": "Telegram username of the user"})

    @validates_schema
    def validation_payload(self, data, **kwargs):
        email: str = data.get("email", None)
        discord_username: str = data.get("discord_username", None)

        if email is not None and not User.is_valid_email(email):
            raise ValidationError("Email format invalid.", field_name="email")

        if discord_username is None or len(discord_username) < 3:
            raise ValidationError("The discord username must be at least 3 characters.", field_name="discord_username")

    class Meta:
        description = "Input information needed to create user."
        ordered = True


class InputUpdateUserSchema(Schema):
    username = fields.String(metadata={"description": "New username of the user"})
    email = fields.String(metadata={"description": "New email of the user"})
    member_name = fields.String(metadata={"description": "New display name of the user"})
    discord_username = fields.String(metadata={"description": "New Discord username of the user"})
    twitter_username = fields.String(metadata={"description": "New Twitter username of the user"})
    telegram_username = fields.String(metadata={"description": "New Telegram username of the user"})
    wallet_address = fields.String(metadata={"description": "New wallet address of the user"})

    class Meta:
        description = "New user information"
        ordered = True
