from flask.app import Flask
from unittest.mock import ANY
from api.models.dao import DAO

def test_create_token(client: Flask, dao: DAO, victor_logged_in: str):
    token_data = {
        "dao_id": dao.dao_id,
        "name": "New Token",
        "symbol": "NEW",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 2000.0,
    }
    
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/tokens",
        json=token_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 201
    
    # Check token data
    assert data["action"] == "created"
    assert data["token"]["token_id"] == ANY
    assert data["token"]["dao_id"] == dao.dao_id
    assert data["token"]["name"] == "New Token"
    assert data["token"]["symbol"] == "NEW"
    assert data["token"]["contract"] == "So11111111111111111111111111111111111111111"
    assert data["token"]["amount"] == 2000.0

def test_create_token_unauthorized(client: Flask, dao: DAO):
    token_data = {
        "dao_id": dao.dao_id,
        "name": "New Token",
        "symbol": "NEW",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 2000.0,
    }
    
    # Test unauthorized access
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/tokens",
        json=token_data
    )
    assert res.status_code == 401
    
def test_create_token_dao_not_found(client: Flask, victor_logged_in: str):
    token_data = {
        "dao_id": "non_existent_dao",
        "name": "New Token",
        "symbol": "NEW",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 2000.0,
    }
    
    # Test with non-existent DAO
    res = client.post(
        "/treasury/daos/non_existent_dao/tokens",
        json=token_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

def test_create_token_invalid_data(client: Flask, dao: DAO, victor_logged_in: str):
    # Missing required fields
    token_data = {
        "dao_id": dao.dao_id,
        "name": "New Token",
        # missing symbol
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 2000.0,
    }
    
    res = client.post(
        f"/treasury/daos/{dao.dao_id}/tokens",
        json=token_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    print(res.json)
    assert res.status_code == 422  # Validation error 