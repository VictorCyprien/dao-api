from api.models.treasury import Token, Transfer
from unittest.mock import ANY
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy
from api.models.dao import DAO
from api.models.user import User

def test_model_create_transfer(app, db: SQLAlchemy, dao: DAO, victor: User):
    # Create a token first
    token = Token.create({
        "dao_id": dao.dao_id,
        "name": "Test Token",
        "symbol": "TEST",
        "amount": 1000.0,
        "price": 1.0,
        "percentage": 100
    })
    db.session.add(token)
    db.session.commit()
    
    # Create a transfer
    transfer_data = {
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": "0xExternalAddress",
        "to_address": victor.wallet_address,
        "amount": 500.0
    }

    transfer = Transfer.create(input_data=transfer_data)
    
    assert transfer.transfer_id == ANY
    assert transfer.dao_id == dao.dao_id
    assert transfer.token_id == token.token_id
    assert transfer.from_address == "0xExternalAddress"
    assert transfer.to_address == victor.wallet_address
    assert transfer.amount == 500.0
    assert transfer.timestamp is not None
    
    # Test to_dict() method
    transfer_dict = transfer.to_dict()
    assert transfer_dict["transfer_id"] == transfer.transfer_id
    assert transfer_dict["dao_id"] == dao.dao_id
    assert transfer_dict["token_id"] == token.token_id
    assert transfer_dict["from_address"] == "0xExternalAddress"
    assert transfer_dict["to_address"] == victor.wallet_address
    assert transfer_dict["amount"] == 500.0
    assert "timestamp" in transfer_dict
    
    # Clean up
    db.session.delete(token)
    db.session.commit()

def test_get_transfers_by_dao_id(app, db: SQLAlchemy, dao: DAO, victor: User):
    # Create a token first
    token = Token.create({
        "dao_id": dao.dao_id,
        "name": "Test Token",
        "symbol": "TEST",
        "amount": 1000.0,
        "price": 1.0,
        "percentage": 100
    })
    db.session.add(token)
    db.session.commit()
    
    # Create multiple transfers
    transfer1 = Transfer.create({
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": "0xExternalAddress1",
        "to_address": victor.wallet_address,
        "amount": 500.0
    })
    
    transfer2 = Transfer.create({
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": victor.wallet_address,
        "to_address": "0xExternalAddress2",
        "amount": 200.0
    })
    
    db.session.add(transfer1)
    db.session.add(transfer2)
    db.session.commit()
    
    # Test get_by_dao_id
    transfers = Transfer.get_by_dao_id(dao.dao_id, db.session)
    assert len(transfers) == 2
    
    # Verify the transfers are in the list ordered by timestamp (desc)
    assert transfers[0].transfer_id == transfer2.transfer_id  # Most recent first
    assert transfers[1].transfer_id == transfer1.transfer_id
    
    # Clean up
    db.session.delete(transfer1)
    db.session.delete(transfer2)
    db.session.delete(token)
    db.session.commit()

def test_get_transfers_by_token_id(app, db: SQLAlchemy, dao: DAO, victor: User):
    # Create two tokens
    token1 = Token.create({
        "dao_id": dao.dao_id,
        "name": "Token 1",
        "symbol": "TK1",
        "amount": 1000.0,
        "price": 1.0,
        "percentage": 50
    })
    
    token2 = Token.create({
        "dao_id": dao.dao_id,
        "name": "Token 2",
        "symbol": "TK2",
        "amount": 1000.0,
        "price": 2.0,
        "percentage": 50
    })
    
    db.session.add(token1)
    db.session.add(token2)
    db.session.commit()
    
    # Create transfers for each token
    transfer1 = Transfer.create({
        "dao_id": dao.dao_id,
        "token_id": token1.token_id,
        "from_address": "0xExternalAddress",
        "to_address": victor.wallet_address,
        "amount": 500.0
    })
    
    transfer2 = Transfer.create({
        "dao_id": dao.dao_id,
        "token_id": token2.token_id,
        "from_address": "0xExternalAddress",
        "to_address": victor.wallet_address,
        "amount": 300.0
    })
    
    db.session.add(transfer1)
    db.session.add(transfer2)
    db.session.commit()
    
    # Test get_by_token_id for the first token
    transfers = Transfer.get_by_token_id(token1.token_id, db.session)
    assert len(transfers) == 1
    assert transfers[0].transfer_id == transfer1.transfer_id
    
    # Test get_by_token_id for the second token
    transfers = Transfer.get_by_token_id(token2.token_id, db.session)
    assert len(transfers) == 1
    assert transfers[0].transfer_id == transfer2.transfer_id
    
    # Clean up
    db.session.delete(transfer1)
    db.session.delete(transfer2)
    db.session.delete(token1)
    db.session.delete(token2)
    db.session.commit() 