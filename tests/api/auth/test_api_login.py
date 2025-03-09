import pytest
from unittest.mock import patch, MagicMock



@patch('api.views.auth.wallet_auth_view.User.generate_challenge_message')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_challenge_generation_success(mock_redis, mock_challenge, client, sayori):
    """Test successful challenge generation"""
    # Setup mocks
    mock_challenge.return_value = "Test challenge message"
    mock_redis.set_token.return_value = "Test challenge message"
    
    data = {
        "wallet_address": sayori.wallet_address
    }

    response = client.post("/auth/wallet/challenge", json=data)

    # Verify response
    assert response.status_code == 200
    assert response.json["message"] == "Test challenge message"
    assert response.json["wallet_address"] == sayori.wallet_address
    
    # Verify Redis call
    mock_redis.set_token.assert_called_once_with(
        f"wallet_auth:{sayori.wallet_address}", 
        "Test challenge message", 
        300
    )


def test_challenge_wallet_not_found(client):
    """Test challenge generation with non-existent wallet"""
    data = {
        "wallet_address": "0xNonExistentWallet123456789"
    }

    response = client.post("/auth/wallet/challenge", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "This user doesn't exist !"


@patch('api.views.auth.wallet_auth_view.User.verify_signature')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_signature_verification_success(mock_redis, mock_verify, client, sayori):
    """Test successful signature verification"""
    # Setup mocks
    mock_redis.get_token.return_value = "Test challenge message"
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
    
    # Verify verification was called with correct params
    mock_verify.assert_called_once_with(
        sayori.wallet_address, 
        "Test challenge message", 
        "validSignatureString"
    )
    
    # Verify challenge was deleted
    mock_redis.delete_token.assert_called_once_with(f"wallet_auth:{sayori.wallet_address}")


@patch('api.views.auth.wallet_auth_view.User.verify_signature')
@patch('api.views.auth.wallet_auth_view.redis_client')
def test_signature_verification_invalid(mock_redis, mock_verify, client, sayori):
    """Test signature verification with invalid signature"""
    # Setup mocks
    mock_redis.get_token.return_value = "Test challenge message"
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
def test_signature_verification_expired_challenge(mock_redis, client, sayori):
    """Test signature verification with expired challenge"""
    # Setup mocks
    mock_redis.get_token.return_value = None
    
    data = {
        "wallet_address": sayori.wallet_address,
        "signature": "validSignatureString"
    }

    response = client.post("/auth/wallet/verify", json=data)

    # Verify response
    assert response.status_code == 401
    print(response.json)
    assert response.json["message"] == "The Solana authentication challenge has expired, please request a new one"

