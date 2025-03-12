from flask.app import Flask
from unittest.mock import ANY
from api.models.user import User
from api.models.dao import DAO
from api.models.treasury import Token, Transfer

def test_get_dao_treasury(client: Flask, dao: DAO, token: Token, transfer: Transfer, victor_logged_in: str):
    res = client.get(
        f"/treasury/daos/{dao.dao_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    
    assert res.status_code == 200
    assert "total_value" in data
    assert "daily_change" in data
    assert "daily_change_percentage" in data
    assert "tokens" in data
    assert "recent_transfers" in data
    
    # Check tokens data
    assert len(data["tokens"]) == 1
    assert data["tokens"][0]["token_id"] == token.token_id
    assert data["tokens"][0]["name"] == token.name
    assert data["tokens"][0]["symbol"] == token.symbol
    assert data["tokens"][0]["contract"] == token.contract
    assert data["tokens"][0]["amount"] == token.amount
    assert data["tokens"][0]["price"] == token.price
    assert data["tokens"][0]["percentage"] == token.percentage
    assert data["tokens"][0]["value"] == token.amount * token.price
    
    # Check transfers data
    assert len(data["recent_transfers"]) == 1
    assert data["recent_transfers"][0]["transfer_id"] == transfer.transfer_id
    assert data["recent_transfers"][0]["dao_id"] == dao.dao_id
    assert data["recent_transfers"][0]["token_id"] == token.token_id
    assert data["recent_transfers"][0]["from_address"] == transfer.from_address
    assert data["recent_transfers"][0]["to_address"] == transfer.to_address
    assert data["recent_transfers"][0]["amount"] == transfer.amount

def test_get_dao_treasury_unauthorized(client: Flask, dao: DAO):
    # Test unauthorized access
    res = client.get(f"/treasury/daos/{dao.dao_id}")
    assert res.status_code == 401
    
def test_get_dao_treasury_not_found(client: Flask, victor_logged_in: str):
    # Test with non-existent DAO
    res = client.get(
        "/treasury/daos/non_existent_dao",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404 