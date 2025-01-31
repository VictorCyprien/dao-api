from pytest import raises
from marshmallow import ValidationError

from api.schemas.users_schemas import InputCreateUserSchema

def test_input_create_user_schema(app):
    schema = InputCreateUserSchema()
    
    # Test valid data
    data = {
        "username": "Chara",
        "email": "charadreemurr3571@gmail.com", 
        "discord_username": "charadreemurr3571",
        "wallet_address": "8D1234567890",
        "github_username": "CharaDreemurr"
    }
    result = schema.load(data)
    assert result == data

    # Test missing email
    invalid_data = {
        "username": "Chara",
        "discord_username": "charadreemurr3571",
        "wallet_address": "8D1234567890",
        "github_username": "CharaDreemurr"
    }
    with raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert "The email cannot be null" in str(exc.value)

    # Test missing discord username
    invalid_data = {
        "username": "Chara",
        "email": "charadreemurr3571@gmail.com",
        "wallet_address": "8D1234567890", 
        "github_username": "CharaDreemurr"
    }
    with raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert "The discord username cannot be null" in str(exc.value)

    # Test missing wallet address
    invalid_data = {
        "username": "Chara",
        "email": "charadreemurr3571@gmail.com",
        "discord_username": "charadreemurr3571",
        "github_username": "CharaDreemurr"
    }
    with raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert "The wallet address cannot be null" in str(exc.value)

    # Test missing github username
    invalid_data = {
        "username": "Chara",
        "email": "charadreemurr3571@gmail.com",
        "discord_username": "charadreemurr3571",
        "wallet_address": "8D1234567890"
    }
    with raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert "The github username cannot be null" in str(exc.value)
