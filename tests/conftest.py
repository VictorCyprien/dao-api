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
from api.models.proposal import Proposal
from api.models.treasury import Token, Transfer
from api.models.discord_channel import DiscordChannel
from api.models.discord_message import DiscordMessage

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
def proposal(app, dao, victor, db: SQLAlchemy) -> Iterator["Proposal"]:
    """Create a test proposal for testing"""
    from api.models.proposal import Proposal
    from datetime import datetime, timedelta
    
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "Test Proposal",
        "description": "A test proposal for the DAO",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time,
        "actions": {"action_type": "add_wallet", "target_address": "0xNewWallet"}
    }
    
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            proposal = Proposal.create(proposal_data)
            db.session.add(proposal)
            db.session.commit()
        yield proposal
        db.session.delete(proposal)
        db.session.commit()


@pytest.fixture
def inactive_proposal(app, dao, victor, db: SQLAlchemy) -> Iterator["Proposal"]:
    """Create an inactive test proposal (past end time) for testing"""
    from api.models.proposal import Proposal
    from datetime import datetime, timedelta
    
    start_time = datetime.now() - timedelta(days=10)
    end_time = datetime.now() - timedelta(days=5)
    
    proposal_data = {
        "name": "Inactive Proposal",
        "description": "An inactive test proposal for the DAO",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time,
        "actions": {"action_type": "remove_wallet", "target_address": "0xOldWallet"}
    }
    
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            proposal = Proposal.create(proposal_data)
            db.session.add(proposal)
            db.session.commit()
        yield proposal
        db.session.delete(proposal)
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


# Add Treasury fixtures
@pytest.fixture
def token(app, dao, db: SQLAlchemy) -> Iterator[Token]:
    token_data = {
        "dao_id": dao.dao_id,
        "name": "Test Token",
        "symbol": "TEST",
        "contract": "So11111111111111111111111111111111111111111",
        "amount": 1000.0,
        "price": 1.0,
        "percentage": 100
    }
    
    with app.app_context():
        token = Token.create(token_data)
        db.session.add(token)
        db.session.commit()
        yield token
        db.session.delete(token)
        db.session.commit()

@pytest.fixture
def transfer(app, dao, token, victor, db: SQLAlchemy) -> Iterator[Transfer]:
    transfer_data = {
        "dao_id": dao.dao_id,
        "token_id": token.token_id,
        "from_address": "0xExternalAddress",
        "to_address": victor.wallet_address,
        "amount": 500.0
    }
    
    with app.app_context():
        transfer = Transfer.create(transfer_data)
        db.session.add(transfer)
        db.session.commit()
        yield transfer
        db.session.delete(transfer)
        db.session.commit()


@pytest.fixture
def discord_channel(app, pod, db: SQLAlchemy) -> Iterator[DiscordChannel]:
    with app.app_context():
        channel = DiscordChannel(
            channel_id="123456789",
            name="general",
            pod_id=pod.pod_id,
            created_at=freezegun.freeze_time(creation_date).time_to_freeze
        )
        db.session.add(channel)
        db.session.commit()
        yield channel
        db.session.delete(channel)
        db.session.commit()


@pytest.fixture
def unlinked_discord_channel(app, db: SQLAlchemy) -> Iterator[DiscordChannel]:
    with app.app_context():
        channel = DiscordChannel(
            channel_id="987654321",
            name="announcements",
            pod_id=None,
            created_at=freezegun.freeze_time(creation_date).time_to_freeze
        )
        db.session.add(channel)
        db.session.commit()
        yield channel
        db.session.delete(channel)
        db.session.commit()


@pytest.fixture
def discord_message(app, discord_channel, db: SQLAlchemy) -> Iterator[DiscordMessage]:
    with app.app_context():
        message = DiscordMessage(
            message_id="123456789012345",
            channel_id=discord_channel.channel_id,
            username="testuser",
            user_id="98765432101",
            text="Hello, world!",
            has_media=False,
            media_urls=None,
            created_at=freezegun.freeze_time(creation_date).time_to_freeze,
            indexed_at=freezegun.freeze_time(creation_date).time_to_freeze
        )
        db.session.add(message)
        db.session.commit()
        yield message
        db.session.delete(message)
        db.session.commit()


@pytest.fixture
def discord_messages(app, discord_channel, db: SQLAlchemy) -> Iterator[list]:
    with app.app_context():
        messages = []
        for i in range(5):
            message = DiscordMessage(
                message_id=f"12345678901234{i}",
                channel_id=discord_channel.channel_id,
                username="testuser",
                user_id="98765432101",
                text=f"Test message {i}",
                has_media=False,
                media_urls=None,
                created_at=freezegun.freeze_time(creation_date).time_to_freeze,
                indexed_at=freezegun.freeze_time(creation_date).time_to_freeze
            )
            db.session.add(message)
            messages.append(message)
        
        db.session.commit()
        yield messages
        
        for message in messages:
            db.session.delete(message)
        db.session.commit()


@pytest.fixture
def pod_proposal(app, dao, pod, victor, db: SQLAlchemy) -> Iterator["Proposal"]:
    """Create a test proposal for a POD"""
    from api.models.proposal import Proposal
    from datetime import datetime, timedelta
    
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "POD Test Proposal",
        "description": "A test proposal for the POD",
        "dao_id": dao.dao_id,
        "pod_id": pod.pod_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time,
        "actions": {"action_type": "add_wallet", "target_address": "0xPodWallet"}
    }
    
    with app.app_context():
        with freezegun.freeze_time(creation_date):
            proposal = Proposal.create(proposal_data)
            db.session.add(proposal)
            db.session.commit()
        yield proposal
        db.session.delete(proposal)
        db.session.commit()


@pytest.fixture
def victor_in_pod(app, db, pod, victor):
    """Add Victor to the POD as a member"""
    with app.app_context():
        current_pod = db.session.merge(pod)
        current_victor = db.session.merge(victor)
        current_pod.add_member(current_victor)
        db.session.commit()
        yield
        current_pod.remove_member(current_victor)
        db.session.commit()

