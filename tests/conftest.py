
from typing import Iterator
from flask import Flask
from flask.testing import FlaskClient

from mongoengine.connection import disconnect
from unittest.mock import Mock
import mongomock
import pytest
import freezegun

from api.models.user import User


@pytest.fixture(scope='session')
def app(request) -> Iterator[Flask]:
    """ Session-wide test `Flask` application. """
    disconnect()    # force close potential existing mongo connection
    from api.config import config
    config.MONGODB_URI = "mongomock://localhost"
    config.MONGODB_DATABASE = "test"
    config.MONGODB_CONNECT = False

    config.SECURITY_PASSWORD_SALT = "123456"

    from mongoengine import connect
    connect('mydatabase', host='mongodb://localhost', mongo_client_class=mongomock.MongoClient)

    from api.app import create_flask_app
    _app = create_flask_app(config=config)
    yield _app


@pytest.fixture(scope='module')
def client(app: Flask) -> Iterator[FlaskClient]:
    app.test_client_class = FlaskClient
    client = app.test_client()
    yield client

#### USERS ####

creation_date = '2000-01-01T00:00:00+00:00'

@pytest.fixture(scope='function')
def victor(app) -> Iterator[User]:
    user_dict = {
        "username": "Victor",
        "email": "victor@example.com",
        "password": "my_password",
        "discord_username": "victor#1234",
        "wallet_address": "0x1234567890",
        "github_username": "victor",
    }
    with freezegun.freeze_time(creation_date):
        user = User.create(user_dict)
        user.save()
    yield user
    user.delete()


@pytest.fixture(scope='function')
def sayori(app) -> Iterator[User]:
    user_dict = {
        "username": "Sayori",
        "email": "sayori@example.com",
        "password": "my_password",
        "discord_username": "sayori#1234",
        "wallet_address": "0x1234567891",
        "github_username": "sayori",
    }
    with freezegun.freeze_time(creation_date):
        user = User.create(user_dict)
        user.save()
    yield user
    user.delete()


#### MOCKS ####

@pytest.fixture
def mock_save_user_document():
    from api.models.user import User
    from mongoengine.errors import ValidationError
    _original = User.save
    User.save = Mock()
    User.save.side_effect = ValidationError
    yield User.save
    User.save = _original
