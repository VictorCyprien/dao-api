from typing import Iterator
from unittest.mock import patch

from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from unittest.mock import Mock
import pytest
import freezegun

from api import Base
from api.models.user import User
from api.models.dao import DAO
from api.models.pod import POD

from environs import Env

env = Env()
env.read_env()


@pytest.fixture(scope='session')
def app(request) -> Iterator[Flask]:
    """ Session-wide test `Flask` application. """
    from api.config import config

    config.SECURITY_PASSWORD_SALT = "123456"
    config.JWT_ACCESS_TOKEN_EXPIRES = 60
    config.JWT_SECRET_KEY = "test_secret_key"

    from api.app import create_flask_app
    _app = create_flask_app(config=config)
    _app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    _app.db = SQLAlchemy(_app)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app: Flask) -> Iterator[SQLAlchemy]:
    Base.metadata.create_all(bind=app.db.engine)
    yield app.db
    Base.metadata.drop_all(bind=app.db.engine)


@pytest.fixture(scope='module')
def client(app: Flask) -> Iterator[FlaskClient]:
    app.test_client_class = FlaskClient
    client = app.test_client()
    yield client


#### USERS ####

creation_date = '2000-01-01T00:00:00+00:00'
@pytest.fixture(scope='function')
def victor(app: Flask, db: SQLAlchemy) -> Iterator[User]:
    user_dict = {
        "username": "Victor",
        "email": "victor@example.com",
        "password": "my_password",
        "discord_username": "victor#1234",
        "wallet_address": "0x1234567890",
    }
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            user = User.create(user_dict)
            db.session.add(user)
            db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture(scope='function')
def sayori(app: Flask, db: SQLAlchemy) -> Iterator[User]:
    user_dict = {
        "username": "Sayori",
        "email": "sayori@example.com",
        "password": "my_password",
        "discord_username": "sayori#1234",
        "wallet_address": "0x1234567891",
    }
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            user = User.create(user_dict)
            db.session.add(user)
            db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture(scope='function')
def natsuki(app: Flask, db: SQLAlchemy) -> Iterator[User]:
    user_dict = {
        "username": "Natsuki",
        "email": "natsuki@example.com",
        "password": "my_password",
        "discord_username": "natsuki#1234",
        "wallet_address": "0x1234567892",
    }
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            user = User.create(user_dict)
            db.session.add(user)
            db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


#### MOCKS ####
@pytest.fixture
def mock_redis_queue():
    from helpers.redis_file import RedisQueue
    _original = RedisQueue.enqueue
    RedisQueue.enqueue = Mock()
    yield RedisQueue.enqueue
    RedisQueue.enqueue = _original


# Signature-based auth fixtures
@pytest.fixture
def mock_redis():
    """Mock Redis for signature-based authentication"""
    redis_patcher = patch('api.views.auth.wallet_auth_view.redis_client')
    mock_redis = redis_patcher.start()
    mock_redis.get.return_value = "Test challenge message"
    mock_redis.setex.return_value = True
    yield mock_redis
    redis_patcher.stop()


@pytest.fixture
def mock_verify_signature():
    """Mock signature verification to always succeed"""
    verify_patcher = patch('api.views.auth.wallet_auth_view.User.verify_signature')
    mock_verify = verify_patcher.start()
    mock_verify.return_value = True
    yield mock_verify
    verify_patcher.stop()


@pytest.fixture
def mock_challenge_message():
    """Mock challenge message generation"""
    challenge_patcher = patch('api.views.auth.wallet_auth_view.User.generate_challenge_message')
    mock_challenge = challenge_patcher.start()
    mock_challenge.return_value = "Test challenge message"
    yield mock_challenge
    challenge_patcher.stop()


@pytest.fixture
def victor_logged_in(client, victor, mock_redis, mock_verify_signature):
    """Login Victor using wallet signature authentication"""
    # Signature verification step
    verify_data = {
        "wallet_address": victor.wallet_address,
        "signature": "validSignatureString"
    }
    response = client.post("/auth/wallet/verify", json=verify_data)
    token = response.json["token"]
    yield token


@pytest.fixture
def sayori_logged_in(client, sayori, mock_redis, mock_verify_signature):
    """Login Sayori using wallet signature authentication"""
    # Signature verification step
    verify_data = {
        "wallet_address": sayori.wallet_address,
        "signature": "validSignatureString"
    }
    response = client.post("/auth/wallet/verify", json=verify_data)
    token = response.json["token"]
    yield token


@pytest.fixture
def natsuki_logged_in(client, natsuki, mock_redis, mock_verify_signature):
    """Login Natsuki using wallet signature authentication"""
    # Signature verification step
    verify_data = {
        "wallet_address": natsuki.wallet_address,
        "signature": "validSignatureString"
    }
    response = client.post("/auth/wallet/verify", json=verify_data)
    token = response.json["token"]
    yield token


@pytest.fixture
def dao(app, victor, db: SQLAlchemy) -> Iterator[DAO]:
    dao_data = {
        "name": "Test DAO",
        "description": "A test DAO",
        "owner_id": victor.user_id
    }
    with app.app_context():
        current_victor = db.session.merge(victor)
        with freezegun.freeze_time(creation_date):
            dao = DAO.create(dao_data)
            dao.admins.append(current_victor)
            dao.members.append(current_victor)
            db.session.add(dao)
            db.session.commit()
        yield dao
        db.session.delete(dao)
        db.session.commit()


@pytest.fixture
def pod(app, dao, db: SQLAlchemy) -> Iterator[POD]:
    pod_data = {
        "name": "Backend Learning Group",
        "description": "Learn backend development with Python and Flask",
        "dao_id": dao.dao_id
    }
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            pod = POD.create(input_data=pod_data)
            db.session.add(pod)
            db.session.commit()
        yield pod
        db.session.delete(pod)
        db.session.commit()

