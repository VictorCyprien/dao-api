from werkzeug.exceptions import BadRequest as WerkzeugBadRequest
from werkzeug.exceptions import NotFound as WerkzeugNotFound
from werkzeug.exceptions import Unauthorized as WerkzeugUnauthorized


class BadRequest(WerkzeugBadRequest):
    """ BadRequest error customized for default smorest error handler

    >>> err = BadRequest("An important message")
    >>> err.data
    {'message': 'An important message'}
    """
    def __init__(self, message: str = None) -> None:
        super().__init__()
        if message:
            self.data = {}
            self.data["message"] = message


class NotFound(WerkzeugNotFound):
    """ NotFound error customized for default smorest error handler

    >>> err = NotFound("An important message")
    >>> err.data
    {'message': 'An important message'}
    """
    def __init__(self, message: str = None) -> None:
        super().__init__()
        if message:
            self.data = {}
            self.data["message"] = message


class Unauthorized(WerkzeugUnauthorized):
    """ Unauthorized error customized for default smorest error handler

    >>> err = Unauthorized("An important message")
    >>> err.data
    {'message': 'An important message'}
    """
    def __init__(self, message: str = None) -> None:
        super().__init__()
        if message:
            self.data = {}
            self.data["message"] = message



class ErrorHandler():
    USER_CREATE = "Unable to create the user"
    USER_NOT_FOUND = "This user doesn't exist !"
    USER_UPDATE = "Unable to update the user"
    USER_USERNAME_ALREADY_USED = "This username is already used !"
    USER_EMAIL_ALREADY_USED = "This email is already used !"
    USER_DISCORD_USERNAME_ALREADY_USED = "This discord username is already used !"
    USER_WALLET_ADDRESS_ALREADY_USED = "This wallet address is already used !"
    NOT_AUTHENTICATED = "You must be logged in to perform this action"
    AUTHENTICATION_FAILED = "Authentication failed"
    BAD_CREDENTIALS = "The email or password is incorrect"
    BAD_AUTH_TOKEN = "The token is present but incorrect"
    INVALID_EMAIL = "This email is invalid"
    INVALID_PASSWORD = "This password is invalid"
    INVALID_DATE_FORMAT = "The date format is invalid"
    DAO_CREATE = "Unable to create the DAO"
    DAO_UPDATE = "Unable to update the DAO"
    DAO_DELETE = "Unable to delete the DAO"
    DAO_NOT_FOUND = "This DAO doesn't exist !"
    DAO_ADMIN_ALREADY_EXISTS = "This user is already an admin of this DAO !"
    DAO_NOT_ADMIN = "This user is not an admin of this DAO !"
    DAO_MEMBERSHIP_NOT_FOUND = "This DAO membership doesn't exist !"
    DAO_MEMBERSHIP_ALREADY_EXISTS = "This user is already a member of this DAO !"
    USER_NOT_ADMIN = "You are not an admin of this DAO !"
    USER_NOT_OWNER = "You are not the owner of this DAO !"
    USER_NOT_MEMBER = "This user is not a member of this DAO !"
    CANNOT_REMOVE_OWNER = "The owner cannot be removed as admin"
    POD_CREATE = "Unable to create the POD"
    POD_UPDATE = "Unable to update the POD"
    POD_DELETE = "Unable to delete the POD"
    POD_NOT_FOUND = "This POD doesn't exist !"
    USER_ALREADY_IN_POD = "This user is already in this POD !"
    USER_NOT_IN_POD = "This user is not in this POD !"
    CHALLENGE_EXPIRED = "The Solana authentication challenge has expired, please request a new one"
    INVALID_SIGNATURE = "The provided Solana wallet signature is invalid"
    TOKEN_NOT_FOUND = "This token doesn't exist !"
    TOKEN_CREATE_ERROR = "Unable to create the token"
    TOKEN_UPDATE_ERROR = "Unable to update the token"
    TOKEN_NOT_BELONG_TO_DAO = "The token does not belong to this DAO"
    TRANSFER_NOT_FOUND = "This transfer doesn't exist !"
    TRANSFER_CREATE_ERROR = "Unable to create the transfer"
    INVALID_TRANSFER_AMOUNT = "The transfer amount is invalid"
    DISCORD_CHANNEL_NOT_FOUND = "This Discord channel doesn't exist !"
    DISCORD_CHANNEL_ALREADY_LINKED = "This Discord channel is already linked to a POD !"