from flask.app import Flask
from rich import print
from unittest.mock import ANY

from api.models.user import User


def test_get_auth_user(client: Flask, victor: User, victor_logged_in: str):
    res = client.get(f"/users/@me", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'discord_username': 'victor#1234',
        'email': 'victor@example.com',
        'email_verified': False,
        'is_active': True,
        'last_login': ANY,
        'last_interaction': ANY,
        'user_id': ANY,
        'username': 'Victor',
        'wallet_address': '0x1234567890'
    }
    


def test_get_one_user_not_logged(client: Flask, victor: User):
    res = client.get(f"/users/@me")
    assert res.status_code == 401
    data = res.json
    print(data)
    assert data == {
        'code': 401,
        'message': "Not Authenticated",
        'status': 'Unauthorized',
    }


def test_check_user_exists(client: Flask, victor: User, victor_logged_in: str):
    res = client.get(f"/users/{victor.wallet_address}", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'exists': True
    }


def test_check_user_does_not_exist(client: Flask):
    res = client.get(f"/users/0xz56f1ez56f1")
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'exists': False
    }
