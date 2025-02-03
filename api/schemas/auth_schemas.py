from marshmallow import Schema, fields

class LoginParamsSchema(Schema):
    email = fields.String(metadata={"description": "Email of the login"}, required=True)
    password = fields.String(metadata={"description": "Password of the login"}, required=True)

    class Meta:
        description = "Login details"
        ordered = True


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

