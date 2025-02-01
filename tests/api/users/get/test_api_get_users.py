from flask.app import Flask
from rich import print
from unittest.mock import ANY

from api.models.user import User


def test_get_one_user(client: Flask, victor: User):
    res = client.get(f"/users/{victor.user_id}")
    assert res.status_code == 200
    data = res.json
    print(data)
    assert data == {
        'user': {
            'discord_username': 'victor#1234',
            'email': 'victor@example.com',
            'github_username': 'victor',
            'user_id': ANY,
            'username': 'Victor',
            'wallet_address': '0x1234567890'
        }
    }


def test_get_one_user_not_found(client: Flask, victor: User):
    res = client.get("/users/123")
    assert res.status_code == 404
    data = res.json
    print(data)
    assert data == {
        'code': 404, 
        'message': "This user doesn't exist !", 
        'status': 'Not Found'
    }
