from api.models.user import User
from unittest.mock import ANY

def test_model_create_user(app):

    user_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "my_password",
        "discord_username": "john.doe#1234",
        "wallet_address": "0x1234567890",
        "github_username": "john.doe",
    }

    user = User().create(input_data=user_data)
    
    assert user.user_id == ANY
    assert user.username == "John Doe"
    assert user.email == "john.doe@example.com"
    assert user.discord_username == "john.doe#1234"
    assert user.wallet_address == "0x1234567890"
    assert user.github_username == "john.doe"
    assert User.check_password("my_password", user.password)
    