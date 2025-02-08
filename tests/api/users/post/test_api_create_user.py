from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from rich import print

from unittest.mock import ANY

from api.models.user import User


def test_create_user(client: Flask, db: SQLAlchemy):
    data = {
        "username": "Chara",
        "email": "charadreemurr3571@gmail.com",
        "password": "my_password",
        "discord_username": "charadreemurr3571",
        "wallet_address": "8D1234567890",
    }

    res = client.post("/users/", json=data)
    assert res.status_code == 201
    data = res.json
    print(data)
    assert data == {
        'action': 'created',
        'user': {
            "username": "Chara",
            "email": "charadreemurr3571@gmail.com",
            "discord_username": "charadreemurr3571",
            "wallet_address": "8D1234567890",
            "user_id": ANY
        }
    }

    user_id = data['user']['user_id']
    user: User = User.get_by_id(id=user_id, session=db.session)
    assert user.user_id == ANY
    assert user.username == "Chara"
    assert user.email == "charadreemurr3571@gmail.com"
    assert User.check_password("my_password", user.password)
    assert user.discord_username == "charadreemurr3571"
    assert user.wallet_address == "8D1234567890"

    db.session.delete(user)
    db.session.commit()


def test_create_user_empty_data(client: Flask):
    res = client.post("/users/", json={})
    assert res.status_code == 422
    data = res.json
    print(data)
    assert data == {
        'code': 422,
        'errors': {'json': {'_schema': ['Invalid payload']}},
        'status': 'Unprocessable Entity'
    }


def test_create_email_already_used(client: Flask, victor: User):
    data = {
        'discord_username': 'victor#1234',
        'email': 'victor@example.com',
        'password': 'my_password',
        'username': 'Victor',
        'wallet_address': '0x1234567890'
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
        'password': 'my_password', 
        'username': 'Chara',
        'wallet_address': '0x1234567890'
    }

    res = client.post("/users/", json=data)
    assert res.status_code == 400
    data = res.json
    print(data)
    assert data == {
        'code': 400,
        'message': 'This email is invalid',
        'status': 'Bad Request'
    }



def test_create_discord_username_already_used(client: Flask, victor: User):
    data = {
        'discord_username': 'victor#1234',
        'email': 'victor2@example.com',
        'password': 'my_password',
        'username': 'Victor',
        'wallet_address': '0x1234567890'
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
        'password': 'my_password',
        'username': 'Victor',
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

