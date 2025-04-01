from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User
from helpers.errors_file import ErrorHandler

def test_update_dao(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "Updated DAO",
            "description": "Updated description",
            
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert data == {
        'action': 'updated',
        'dao': {
            'dao_id': dao.dao_id,
            'name': dao.name,
            'description': dao.description,
            'owner_id': dao.owner_id,
            'is_active': True,
            'admins': [
            {
                'user_id': victor.user_id,
                'username': victor.username,
            }
        ],
        'members': [
            {
                'user_id': victor.user_id,
                'username': victor.username,
            }
            ]
        }
    }

def test_update_dao_with_valid_treasury(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test updating a DAO with a valid Solana wallet address as treasury"""
    # Valid Solana wallet address for testing
    valid_wallet = "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8WJ"
    
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "DAO with Treasury",
            "description": "A DAO with a valid treasury wallet",
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    assert res.status_code == 200
    assert data["dao"]["treasury_address"] == valid_wallet
    assert data["action"] == "updated"

def test_update_dao_with_invalid_treasury(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test updating a DAO with an invalid Solana wallet address"""
    # Invalid wallet address (too short)
    invalid_wallet = "ABCDEFG123"
    
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "DAO with Invalid Treasury",
            "description": "A DAO with an invalid treasury wallet",
            "treasury": invalid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    assert res.status_code == 400
    assert data["message"] == ErrorHandler.INVALID_WALLET_ADDRESS

def test_update_dao_with_invalid_treasury_chars(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test updating a DAO with a wallet address containing invalid characters"""
    # Valid length but invalid characters (contains 'O' and '0' which aren't in base58)
    invalid_wallet = "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8O0"
    
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "DAO with Invalid Treasury Chars",
            "description": "A DAO with an invalid treasury wallet characters",
            "treasury": invalid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    assert res.status_code == 400
    assert data["message"] == ErrorHandler.INVALID_WALLET_ADDRESS

def test_update_dao_with_same_treasury(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test updating a DAO with the same treasury wallet address"""
    # First update with a valid wallet
    valid_wallet = "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8WJ"
    
    # Set initial treasury
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Now update with same treasury
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "Updated Name",
            "description": "Updated with same treasury",
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    assert res.status_code == 200
    assert data["dao"]["treasury_address"] == valid_wallet
    assert data["action"] == "updated"


def test_unauthorized_dao_update(client: Flask, victor: User, sayori: User, sayori_logged_in: str, dao: DAO):
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "Unauthorized Update",
            "description": "Should fail",
            
        },
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401

def test_update_dao_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    res = client.put(
        f"/daos/999999",
        json={
            "name": "Updated DAO",
            "description": "Updated description",
            
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
