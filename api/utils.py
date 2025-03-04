from functools import wraps
from flask import current_app
from flask_jwt_extended import jwt_required as flask_jwt_required


def conditional_jwt_required(fresh=False):
    """
    A decorator that conditionally enforces JWT authentication.
    When AUTH_DISABLED is True, authentication is skipped.
    
    Args:
        fresh (bool, optional): Whether a fresh token is required. Defaults to False.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Check if authentication is disabled in the config
            if current_app.config.get('AUTH_DISABLED', False):
                # Skip authentication and directly call the function
                return fn(*args, **kwargs)
            else:
                # Apply the JWT required decorator with specified parameters
                jwt_decorator = flask_jwt_required(fresh=fresh)
                return jwt_decorator(fn)(*args, **kwargs)
        return wrapper
    return decorator 