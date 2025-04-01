from api.models.treasury import Token
from unittest.mock import ANY
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User

def test_model_create_token(app, dao: DAO):
    token_data = {
        "wallet_address": dao.treasury_address,
        "token_mint": "So11111111111111111111111111111111111111111",
        "balance": 1000.0,
        "symbol": "TEST",
        "decimals": 9
    }

    token = Token.create(input_data=token_data)
    
    assert token.token_id == ANY
    assert token.wallet_address == dao.treasury_address
    assert token.token_mint == "So11111111111111111111111111111111111111111"
    assert token.balance == 1000.0
    assert token.symbol == "TEST"
    assert token.decimals == 9
    
    # Test to_dict() method
    token_dict = token.to_dict()
    assert token_dict["token_id"] == token.token_id
    assert token_dict["wallet_address"] == dao.treasury_address
    assert token_dict["token_mint"] == "So11111111111111111111111111111111111111111"
    assert token_dict["balance"] == 1000.0
    assert token_dict["symbol"] == "TEST"
    assert token_dict["decimals"] == 9

def test_model_update_token(app, db: SQLAlchemy, dao: DAO):
    # Create a token first
    token_data = {
        "wallet_address": dao.treasury_address,
        "token_mint": "So11111111111111111111111111111111111111111",
        "balance": 1000.0,
        "symbol": "TEST",
        "decimals": 9
    }

    token = Token.create(input_data=token_data)
    db.session.add(token)
    db.session.commit()
    
    # Update the token
    update_data = {
        "wallet_address": dao.treasury_address,
        "token_mint": "So22222222222222222222222222222222222222222",
        "balance": 2000.0,
        "symbol": "UPD",
        "decimals": 9
    }
    
    token.update(update_data)
    db.session.commit()
    
    # Retrieve from DB to verify changes
    updated_token = Token.get_by_id(token.token_id, db.session)
    assert updated_token.wallet_address == dao.treasury_address
    assert updated_token.token_mint == "So22222222222222222222222222222222222222222"
    assert updated_token.balance == 2000.0
    assert updated_token.decimals == 9
    
    # Clean up
    db.session.delete(token)
    db.session.commit()

def test_get_tokens_by_dao_id(app, db: SQLAlchemy, dao: DAO):
    # Create multiple tokens for the same DAO
    token1 = Token.create({
        "wallet_address": dao.treasury_address,
        "token_mint": "So11111111111111111111111111111111111111111",
        "balance": 1000.0,
        "symbol": "TK1",
        "decimals": 9
    })
    
    token2 = Token.create({
        "wallet_address": dao.treasury_address,
        "token_mint": "So22222222222222222222222222222222222222222",
        "balance": 2000.0,
        "symbol": "TK2",
        "decimals": 9
    })
    
    db.session.add(token1)
    db.session.add(token2)
    db.session.commit()
    
    # Test get_by_wallet_address
    tokens = Token.get_by_wallet_address(dao.treasury_address, db.session)
    assert len(tokens) == 2
    
    # Verify the tokens are in the list
    token_ids = [token.token_id for token in tokens]
    assert token1.token_id in token_ids
    assert token2.token_id in token_ids
    
    # Clean up
    db.session.delete(token1)
    db.session.delete(token2)
    db.session.commit() 