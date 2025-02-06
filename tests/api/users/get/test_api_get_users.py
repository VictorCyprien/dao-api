from flask.app import Flask
from rich import print
from unittest.mock import ANY

from api.models.user import User


def test_get_one_user(client: Flask, victor: User, victor_logged_in: str):
    res = client.get(f"/users/{victor.user_id}", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'user': {
            'discord_username': 'victor#1234',
            'email': 'victor@example.com',
            'user_id': ANY,
            'username': 'Victor',
            'wallet_address': '0x1234567890'
        }
    }


def test_get_one_user_not_found(client: Flask, victor: User, victor_logged_in: str):
    res = client.get("/users/123", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 404
    data = res.json
    print(data)
    assert data == {
        'code': 404, 
        'message': "This user doesn't exist !", 
        'status': 'Not Found'
    }


def test_get_one_user_not_authorized(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    res = client.get(f"/users/{sayori.user_id}", headers={"Authorization": f"Bearer {victor_logged_in}"})
    assert res.status_code == 404
    data = res.json
    print(data)
    assert data == {
        'code': 404, 
        'message': "This user doesn't exist !",
        'status': 'Not Found',
    }


def test_get_one_user_not_logged(client: Flask, victor: User):
    res = client.get(f"/users/{victor.user_id}")
    assert res.status_code == 401
    data = res.json
    print(data)
    assert data == {
        'code': 401,
        'message': "Not Authenticated",
        'status': 'Unauthorized',
    }
