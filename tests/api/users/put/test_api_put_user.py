from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
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
            'discord_username': 'victor#1234',
            'email': 'victor@example.com',
            'email_verified': False,
            'is_active': True,
            'last_interaction': ANY,
            'last_login': ANY,
            'user_id': ANY,
            'username': 'VicCrypto',
            'wallet_address': '0x1234567890'
        }
    }


def test_user_update_email(client: Flask, victor: User, victor_logged_in: str):
    data_put = {
        "username": "VicCrypto",
        "email": "viccrypto13@gmail.com",
    }

    res = client.put(f"/users/{victor.user_id}", json=data_put, headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'action': 'updated',
        'user': {
            'discord_username': 'victor#1234',
            'email': 'viccrypto13@gmail.com',
            'email_verified': False,
            'is_active': True,
            'last_interaction': ANY,
            'last_login': ANY,
            'user_id': ANY,
            'username': 'VicCrypto',
            'wallet_address': '0x1234567890'
        }
    }


def test_user_update_wallet_address(client: Flask, victor: User, victor_logged_in: str):
    data_put = {
        "username": "VicCrypto",
        "wallet_address": "0x987654321",
    }

    res = client.put(f"/users/{victor.user_id}", json=data_put, headers={"Authorization": f"Bearer {victor_logged_in}"})
    print(res.json)
    assert res.status_code == 422
    data = res.json
    print(data)
    assert data == {
        'code': 422,
        'errors': {'json': {'wallet_address': ['Unknown field.']}},
        'status': 'Unprocessable Entity'
    }

    assert victor.wallet_address != "0x987654321" and victor.wallet_address == "0x1234567890"
    

def test_user_update_no_payload(client: Flask, victor: User, victor_logged_in: str):
    res = client.put(f"/users/{victor.user_id}", json={}, headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'action': 'updated',
        'user': {
            'discord_username': 'victor#1234',
            'email': 'victor@example.com',
            'email_verified': False,
            'is_active': True,
            'last_interaction': ANY,
            'last_login': ANY,
            'user_id': ANY,
            'username': 'Victor',
            'wallet_address': '0x1234567890'
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


def test_put_one_user_not_authorized(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    data_put = {
        "username": "Sayori 2",
    }

    res = client.put(f"/users/{sayori.user_id}", headers={"Authorization": f"Bearer {victor_logged_in}"}, json=data_put)
    assert res.status_code == 404
    data = res.json
    print(data)
    assert data == {
        'code': 404, 
        'message': "This user doesn't exist !",
        'status': 'Not Found',
    }

