from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from rich import print

from unittest.mock import ANY

from api.models.user import User


def test_create_user(client: Flask, db: SQLAlchemy):
    data = {
        "username": "Chara",
        "email": "charadreemurr3571@gmail.com",
        "discord_username": "charadreemurr3571",
        "wallet_address": "8D1234567890",
    }

    res = client.post("/users/", json=data)
    print(res.json)
    assert res.status_code == 201
    data = res.json
    print(data)
    assert data == {
        'action': 'created',
        'user': {
            'discord_username': 'charadreemurr3571',
            'email': 'charadreemurr3571@gmail.com',
            'email_verified': False,
            'is_active': True,
            'last_interaction': ANY,
            'last_login': ANY,
            'member_name': None,
            'telegram_username': None,
            'twitter_username': None,
            'user_id': ANY,
            'username': 'Chara',
            'wallet_address': '8D1234567890'
    }
    }

    user_id = data['user']['user_id']
    user: User = User.get_by_id(id=user_id, session=db.session)
    assert user.user_id == ANY
    assert user.username == "Chara"
    assert user.email == "charadreemurr3571@gmail.com"
    assert user.discord_username == "charadreemurr3571"
    assert user.wallet_address == "8D1234567890"

    db.session.delete(user)
    db.session.commit()


def test_create_user_empty_data(client: Flask):
    res = client.post("/users/", json={})
    print(res.json)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'validation_error': {
            'body_params': [
                {
                    'input': {},
                    'loc': ['username'],
                    'msg': 'Field required',
                    'type': 'missing',
                    'url': 'https://errors.pydantic.dev/2.10/v/missing'
                },
                {
                    'input': {},
                    'loc': ['wallet_address'],
                    'msg': 'Field required',
                    'type': 'missing',
                    'url': 'https://errors.pydantic.dev/2.10/v/missing'
                }
            ]
        }
    }


def test_create_email_already_used(client: Flask, victor: User):
    data = {
        'discord_username': 'victor#1234',
        'email': 'victor@example.com',
        'username': 'Victor123',
        'wallet_address': '0x123456789012'
    }

    res = client.post("/users/", json=data)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'code': 400, 
        'message': 'This email is already used !', 
        'status': 'Bad Request'
    }


def test_create_user_invalid_email(client: Flask):
    data = {
        'discord_username': 'chara#1234',
        'email': 'invalid_email',
        'username': 'Chara',
        'wallet_address': '0x1234567890'
    }

    res = client.post("/users/", json=data)
    print(res.json)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'validation_error': {
            'body_params': [
                {
                    'ctx': {'reason': 'An email address must have an @-sign.'},
                    'input': 'invalid_email',
                    'loc': ['email'],
                    'msg': 'value is not a valid email address: An email address must have an @-sign.',
                    'type': 'value_error'
                }
            ]
        }
    }



def test_create_discord_username_already_used(client: Flask, victor: User):
    data = {
        'discord_username': 'victor#1234',
        'email': 'victor2@example.com',
        'username': 'Victor123',
        'wallet_address': '0x1234567890123'
    }

    res = client.post("/users/", json=data)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'code': 400, 
        'message': 'This discord username is already used !', 
        'status': 'Bad Request'
    }


def test_create_wallet_address_already_used(client: Flask, victor: User):
    data = {
        'discord_username': 'victor3#1234',
        'email': 'victor4@example.com',
        'username': 'Victor123',
        'wallet_address': '0x1234567890'
    }

    res = client.post("/users/", json=data)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'code': 400, 
        'message': 'This wallet address is already used !', 
        'status': 'Bad Request'
    }


def test_create_user_username_already_used(client: Flask, victor: User):
    data = {
        'discord_username': 'victor5#1234',
        'email': 'victor6@example.com',
        'username': victor.username,
        'wallet_address': '0xe5zf1ez5f'
    }

    res = client.post("/users/", json=data)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'code': 400,
        'message': 'This username is already used !',
        'status': 'Bad Request'
    }
