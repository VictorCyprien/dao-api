from flask.app import Flask
from rich import print

from unittest.mock import ANY

from api.models.user import User

def test_user_update(client: Flask, victor: User, victor_logged_in: str):
    data_put = {
        "username": "VicCrypto",
    }

    res = client.put(f"/users/{victor.user_id}", json=data_put, headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'action': 'updated',
        'user': {
            "username": "VicCrypto",
            "email": "victor@example.com",
            "discord_username": "victor#1234",
            "wallet_address": "0x1234567890",
            "github_username": "victor",
            "user_id": ANY        
        }
    }


def test_user_update_no_payload(client: Flask, victor: User, victor_logged_in: str):
    res = client.put(f"/users/{victor.user_id}", json={}, headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'action': 'updated',
        'user': {
            "username": "Victor",
            "email": "victor@example.com",
            "discord_username": "victor#1234",
            "wallet_address": "0x1234567890",
            "github_username": "victor",
            "user_id": ANY        
        }
    }


def test_user_update_not_found(client: Flask, victor: User, victor_logged_in: str):
    data_put = {
        "username": "VicCrypto",
    }

    res = client.put("/users/86489686484864", json=data_put, headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 404
    data = res.json
    print(data)
    assert data == {
        'code': 404,
        'message': "This user doesn't exist !",
        'status': 'Not Found'
    }


def test_user_update_not_logged(client: Flask, victor: User):
    data_put = {
        "username": "VicCrypto",
    }

    res = client.put(f"/users/{victor.user_id}", json=data_put)
    assert res.status_code == 401
    data = res.json
    print(data)
    assert data == {
        'code': 401,
        'message': "Not Authenticated",
        'status': 'Unauthorized'
    }


def test_user_update_error_during_save(client: Flask, victor: User, victor_logged_in: str, mock_save_user_document):
    data_put = {
        "username": "VicCrypto",
    }

    res = client.put(f"/users/{victor.user_id}", json=data_put, headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'code': 400, 
        'message': 'Unable to update the user', 
        'status': 'Bad Request'
    }

    mock_save_user_document.assert_called()
