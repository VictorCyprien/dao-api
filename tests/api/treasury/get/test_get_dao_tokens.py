from flask.app import Flask
from unittest.mock import ANY
from api.models.user import User
from api.models.dao import DAO
from api.models.treasury import Token

def test_get_dao_tokens(client: Flask, dao: DAO, token: Token, victor_logged_in: str):
    res = client.get(
        f"/treasury/daos/{dao.dao_id}/tokens",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    
    assert res.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    
    # Check token data
    assert data[0]["token_id"] == token.token_id
    assert data[0]["dao_id"] == dao.dao_id
    assert data[0]["name"] == token.name
    assert data[0]["symbol"] == token.symbol
    assert data[0]["contract"] == token.contract
    assert data[0]["amount"] == token.amount
    assert data[0]["price"] == token.price
    assert data[0]["percentage"] == token.percentage
    assert data[0]["value"] == token.amount * token.price

def test_get_dao_tokens_unauthorized(client: Flask, dao: DAO):
    # Test unauthorized access
    res = client.get(f"/treasury/daos/{dao.dao_id}/tokens")
    assert res.status_code == 401
    
def test_get_dao_tokens_not_found(client: Flask, victor_logged_in: str):
    # Test with non-existent DAO
    res = client.get(
        "/treasury/daos/non_existent_dao/tokens",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404 