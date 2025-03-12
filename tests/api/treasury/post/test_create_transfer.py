from flask.app import Flask
from unittest.mock import ANY
from api.models.dao import DAO
from api.models.treasury import Token
from api.models.user import User

def test_create_transfer(client: Flask, dao: DAO, token: Token, victor: User, victor_logged_in: str):
    transfer_data = {
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": "0xExternalWallet",
        "to_address": victor.wallet_address,
        "amount": 500.0
    }
    
    # Get the token amount before the transfer
    initial_token_amount = token.amount
    
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/transfers",
        json=transfer_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    
    assert res.status_code == 201
    
    # Check transfer data
    assert data["action"] == "created"
    assert data["transfer"]["transfer_id"] == ANY
    assert data["transfer"]["dao_id"] == dao.dao_id
    assert data["transfer"]["token_id"] == token.token_id
    assert data["transfer"]["from_address"] == "0xExternalWallet"
    assert data["transfer"]["to_address"] == victor.wallet_address
    assert data["transfer"]["amount"] == 500.0
    assert "timestamp" in data["transfer"]
    

def test_create_outgoing_transfer(client: Flask, dao: DAO, token: Token, victor: User, victor_logged_in: str):
    transfer_data = {
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": victor.wallet_address,
        "to_address": "0xExternalWallet",
        "amount": 200.0
    }
    
    # Get the token amount before the transfer
    initial_token_amount = token.amount
    
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/transfers",
        json=transfer_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 201


def test_create_transfer_unauthorized(client: Flask, dao: DAO, token: Token, victor: User):
    transfer_data = {
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": "0xExternalWallet",
        "to_address": victor.wallet_address,
        "amount": 500.0
    }
    
    # Test unauthorized access
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/transfers",
        json=transfer_data
    )
    assert res.status_code == 401
    
def test_create_transfer_dao_not_found(client: Flask, token: Token, victor: User, victor_logged_in: str):
    transfer_data = {
        "dao_id": "non_existent_dao",
        "token_id": token.token_id,
        "from_address": "0xExternalWallet",
        "to_address": victor.wallet_address,
        "amount": 500.0
    }
    
    # Test with non-existent DAO
    res = client.post(
        "/treasury/daos/non_existent_dao/transfers",
        json=transfer_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

def test_create_transfer_token_not_found(client: Flask, dao: DAO, victor: User, victor_logged_in: str):
    transfer_data = {
        "dao_id": dao.dao_id,
        "token_id": "non_existent_token",
        "from_address": "0xExternalWallet",
        "to_address": victor.wallet_address,
        "amount": 500.0
    }
    
    # Test with non-existent token
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/transfers",
        json=transfer_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404 