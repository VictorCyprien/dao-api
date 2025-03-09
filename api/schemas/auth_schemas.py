from marshmallow import Schema, fields



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

