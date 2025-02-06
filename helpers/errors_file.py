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
