from api.models.treasury import Token
from unittest.mock import ANY
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User

def test_model_create_token(app, dao: DAO):
    token_data = {
        "dao_id": dao.dao_id,
        "name": "Steakhouse USDT",
        "symbol": "USDT",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 14000.0,
        "price": 1.08,
        "percentage": 60
    }

    token = Token.create(input_data=token_data)
    
    assert token.token_id == ANY
    assert token.dao_id == dao.dao_id
    assert token.name == "Steakhouse USDT"
    assert token.symbol == "USDT"
    assert token.contract == "So11111111111111111111111111111111111111111"
    assert token.amount == 14000.0
    assert token.price == 1.08
    assert token.percentage == 60
    
    # Test to_dict() method
    token_dict = token.to_dict()
    assert token_dict["token_id"] == token.token_id
    assert token_dict["dao_id"] == dao.dao_id
    assert token_dict["name"] == "Steakhouse USDT"
    assert token_dict["symbol"] == "USDT"
    assert token_dict["contract"] == "So11111111111111111111111111111111111111111"
    assert token_dict["amount"] == 14000.0
    assert token_dict["price"] == 1.08
    assert token_dict["percentage"] == 60
    assert token_dict["value"] == 14000.0 * 1.08

def test_model_update_token(app, db: SQLAlchemy, dao: DAO):
    # Create a token first
    token_data = {
        "dao_id": dao.dao_id,
        "name": "Original Token",
        "symbol": "ORIG",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 1000.0,
        "price": 1.0,
        "percentage": 50
    }

    token = Token.create(input_data=token_data)
    db.session.add(token)
    db.session.commit()
    
    # Update the token
    update_data = {
        "name": "Updated Token",
        "symbol": "UPD",
        "contract": "So22222222222222222222222222222222222222222",
        "amount": 2000.0,
        "price": 2.0,
        "percentage": 70
    }
    
    token.update(update_data)
    db.session.commit()
    
    # Retrieve from DB to verify changes
    updated_token = Token.get_by_id(token.token_id, db.session)
    assert updated_token.name == "Updated Token"
    assert updated_token.symbol == "UPD"
    assert updated_token.contract == "So22222222222222222222222222222222222222222"
    assert updated_token.amount == 2000.0
    assert updated_token.price == 2.0
    assert updated_token.percentage == 70
    
    # Clean up
    db.session.delete(token)
    db.session.commit()

def test_get_tokens_by_dao_id(app, db: SQLAlchemy, dao: DAO):
    # Create multiple tokens for the same DAO
    token1 = Token.create({
        "dao_id": dao.dao_id,
        "name": "Token 1",
        "symbol": "TK1",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 1000.0,
        "price": 1.0,
        "percentage": 30
    })
    
    token2 = Token.create({
        "dao_id": dao.dao_id,
        "name": "Token 2",
        "symbol": "TK2",
        "contract": "So22222222222222222222222222222222222222222",
        "amount": 2000.0,
        "price": 2.0,
        "percentage": 70
    })
    
    db.session.add(token1)
    db.session.add(token2)
    db.session.commit()
    
    # Test get_by_dao_id
    tokens = Token.get_by_dao_id(dao.dao_id, db.session)
    assert len(tokens) == 2
    
    # Verify the tokens are in the list
    token_ids = [token.token_id for token in tokens]
    assert token1.token_id in token_ids
    assert token2.token_id in token_ids
    
    # Clean up
    db.session.delete(token1)
    db.session.delete(token2)
    db.session.commit() 