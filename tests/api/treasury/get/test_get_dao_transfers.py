from flask.app import Flask
from unittest.mock import ANY
from api.models.dao import DAO
from api.models.treasury import Token, Transfer

def test_get_dao_transfers(client: Flask, dao: DAO, token: Token, transfer: Transfer, victor_logged_in: str):
    res = client.get(
        f"/treasury/daos/{dao.dao_id}/transfers",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    
    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    
    # Check transfer data
    assert data[0]["transfer_id"] == transfer.transfer_id
    assert data[0]["dao_id"] == dao.dao_id
    assert data[0]["token_id"] == token.token_id
    assert data[0]["from_address"] == transfer.from_address
    assert data[0]["to_address"] == transfer.to_address
    assert data[0]["amount"] == transfer.amount
    assert "timestamp" in data[0]
    
    # Transfer should include token information
    assert "token" in data[0]
    assert data[0]["token"]["token_id"] == token.token_id
    assert data[0]["token"]["name"] == token.name

def test_get_dao_transfers_unauthorized(client: Flask, dao: DAO):
    # Test unauthorized access
    res = client.get(f"/treasury/daos/{dao.dao_id}/transfers")
    assert res.status_code == 401
    
def test_get_dao_transfers_not_found(client: Flask, victor_logged_in: str):
    # Test with non-existent DAO
    res = client.get(
        "/treasury/daos/non_existent_dao/transfers",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404 