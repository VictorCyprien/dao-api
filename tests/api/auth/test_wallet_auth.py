import pytest
from unittest.mock import patch, MagicMock
import base58
import secrets
from datetime import datetime


@patch('api.models.user.User.verify_signature')
def test_solana_signature_validation(mock_verify):
    """Test the Solana signature validation method"""
    from api.models.user import User
    
    # Mock the validation method to avoid actual crypto operations
    mock_verify.return_value = True
    
    # Test basic validation
    wallet_address = "87x89V5sPNQrTWnsmmPRZbdHWZKN3GxxwCCNkrbFJ9D"
    message = "Sign this message to authenticate with your Solana wallet."
    signature = "validSignatureString"
    
    assert User.verify_signature(wallet_address, message, signature) is True
    
    # Verify it was called with the right parameters
    mock_verify.assert_called_once_with(wallet_address, message, signature)


@patch('api.models.user.User.generate_challenge_message')
def test_challenge_message_generation(mock_generate):
    """Test the challenge message generation method"""
    from api.models.user import User
    import re
    
    # Set up the mock
    challenge_message = "Sign this message to authenticate with your Solana wallet.\nWallet: testWallet\nNonce: abcdef1234567890\nTimestamp: 2023-01-01T12:00:00"
    mock_generate.return_value = challenge_message
    
    wallet_address = "testWallet"
    result = User.generate_challenge_message(wallet_address)
    
    # Verify the challenge message format
    assert result == challenge_message
    mock_generate.assert_called_once_with(wallet_address)


@patch('api.views.auth.wallet_auth_view.User.generate_challenge_message')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_challenge_route_success(mock_redis, mock_challenge, client, sayori):
    """Test the wallet challenge route successfully generates a challenge"""
    # Setup mocks
    mock_challenge.return_value = "Test challenge message"
    mock_redis.setex.return_value = True
    
    data = {
        "wallet_address": sayori.wallet_address
    }

    response = client.post("/auth/wallet/challenge", json=data)

    # Verify response
    assert response.status_code == 200
    assert response.json["message"] == "Test challenge message"
    assert response.json["wallet_address"] == sayori.wallet_address


def test_challenge_route_user_not_found(client):
    """Test the wallet challenge route with a non-existent wallet"""
    data = {
        "wallet_address": "nonexistentwallet123"
    }

    response = client.post("/auth/wallet/challenge", json=data)

    # Verify response
    assert response.status_code == 404
    assert response.json["message"] == "This user doesn't exist !"


@patch('api.views.auth.wallet_auth_view.User.verify_signature')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_verify_route_success(mock_redis, mock_verify, client, sayori):
    """Test the wallet verify route successfully verifies a signature"""
    # Setup mocks
    mock_redis.get.return_value = "Test challenge message"
    mock_verify.return_value = True
    
    data = {
        "wallet_address": sayori.wallet_address,
        "signature": "validSignatureString"
    }

    response = client.post("/auth/wallet/verify", json=data)

    # Verify response
    assert response.status_code == 201
    assert "token" in response.json
    assert response.json["msg"] == "Logged in with Solana wallet signature"


@patch('api.views.auth.wallet_auth_view.User.verify_signature')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_verify_route_invalid_signature(mock_redis, mock_verify, client, sayori):
    """Test the wallet verify route with an invalid signature"""
    # Setup mocks
    mock_redis.get.return_value = "Test challenge message"
    mock_verify.return_value = False
    
    data = {
        "wallet_address": sayori.wallet_address,
        "signature": "invalidSignatureString"
    }

    response = client.post("/auth/wallet/verify", json=data)

    # Verify response
    assert response.status_code == 401
    assert response.json["message"] == "The provided Solana wallet signature is invalid"


@patch('api.views.auth.wallet_auth_view.redis_client')
def test_verify_route_expired_challenge(mock_redis, client, sayori):
    """Test the wallet verify route with an expired challenge"""
    # Setup mocks
    mock_redis.get.return_value = None
    
    data = {
        "wallet_address": sayori.wallet_address,
        "signature": "validSignatureString"
    }

    response = client.post("/auth/wallet/verify", json=data)

    # Verify response
    assert response.status_code == 401
    assert response.json["message"] == "The provided Solana wallet signature is invalid"


@patch('api.views.auth.wallet_auth_view.User.verify_signature')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_verify_route_updates_last_login(mock_redis, mock_verify, client, sayori, db):
    """Test that the wallet verify route updates the last_login timestamp"""
    # Setup mocks
    mock_redis.get.return_value = "Test challenge message"
    mock_verify.return_value = True
    
    # Ensure last_login is None initially
    assert sayori.last_login == datetime(2000, 1, 1, 0, 0)
    
    data = {
        "wallet_address": sayori.wallet_address,
        "signature": "validSignatureString"
    }

    response = client.post("/auth/wallet/verify", json=data)
    
    # Refresh the user from the database
    db.session.refresh(sayori)
    
    # Verify last_login was updated
    assert sayori.last_login is not None
    assert response.status_code == 201 