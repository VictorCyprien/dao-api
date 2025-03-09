from pytest import raises
from marshmallow import ValidationError

from api.schemas.users_schemas import InputCreateUserSchema

def test_input_create_user_schema(app):
    schema = InputCreateUserSchema()
    
    # Test valid data
    data = {
        "username": "Chara",
        "wallet_address": "8D1234567890",
    }
    result = schema.load(data)
    assert result == data

    # Test missing username
    invalid_data = {
        "wallet_address": "8D1234567890", 
    }
    with raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert "{'username': ['Missing data for required field.']}" in str(exc.value)

    # Test missing wallet address
    invalid_data = {
        "username": "Chara",
    }
    with raises(ValidationError) as exc:
        schema.load(invalid_data)
    assert "{'wallet_address': ['Missing data for required field.']}" in str(exc.value)

