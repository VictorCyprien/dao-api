from flask.app import Flask
from unittest.mock import ANY

from api.models.user import User
from api.models.wallet_monitor import WalletMonitor
from api.models.dao import DAO

from helpers.errors_file import ErrorHandler

def test_create_dao(client: Flask, victor: User, victor_logged_in: str):
    res = client.post(
        "/daos/",
        json={
            "name": "New DAO",
            "description": "A test DAO",
            "owner_id": victor.user_id,
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 201
    assert data == {
        'action': 'created',
        'dao': {
            'dao_id': ANY,
            'name': 'New DAO',
            'description': 'A test DAO',
            'owner_id': victor.user_id,
            'is_active': True,
            'admins': [
            {
                'user_id': victor.user_id,
                'username': victor.username,
            }
        ],
        'members': [
            {
                'user_id': victor.user_id,
                'username': victor.username,
            }
            ]
        }
    }


def test_create_dao_with_treasury_adds_to_monitor(client: Flask, victor: User, victor_logged_in: str):
    """Test that creating a DAO with a treasury wallet adds it to wallet monitoring"""
    db = client.application.db
    
    # Valid Solana wallet address for testing
    valid_wallet = "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8WJ"
    
    # Make sure the wallet is not already in the monitoring table
    existing = WalletMonitor.get_by_address(valid_wallet, db.session)
    if existing:
        db.session.delete(existing)
        db.session.commit()
    
    # Create a DAO with a treasury wallet
    res = client.post(
        "/daos/",
        json={
            "name": "Treasury DAO",
            "description": "A DAO with treasury for testing",
            "owner_id": victor.user_id,
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    assert res.status_code == 201
    assert data["dao"]["treasury"] == valid_wallet
    
    # Verify that the wallet was added to the monitoring table
    wallet_monitor = WalletMonitor.get_by_address(valid_wallet, db.session)
    assert wallet_monitor is not None
    assert wallet_monitor.wallet_address == valid_wallet
    
    # Clean up
    dao = DAO.get_by_name("Treasury DAO", db.session)
    if dao:
        db.session.delete(dao)
    if wallet_monitor:
        db.session.delete(wallet_monitor)
    db.session.commit()


def test_update_dao_treasury_adds_to_monitor(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test that updating a DAO with a treasury wallet adds it to wallet monitoring"""
    db = client.application.db
    
    # Valid Solana wallet address for testing
    valid_wallet = "87rGx3SZ2S2qUGd6WQWGZj13izuoJJJVXYbzzGi2qkn8"
    
    # Make sure the wallet is not already in the monitoring table
    existing = WalletMonitor.get_by_address(valid_wallet, db.session)
    if existing:
        db.session.delete(existing)
        db.session.commit()
    
    # Update the DAO with a treasury wallet
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    assert res.status_code == 200
    assert data["dao"]["treasury"] == valid_wallet
    
    # Verify that the wallet was added to the monitoring table
    wallet_monitor = WalletMonitor.get_by_address(valid_wallet, db.session)
    assert wallet_monitor is not None
    assert wallet_monitor.wallet_address == valid_wallet
    
    # Clean up
    if wallet_monitor:
        db.session.delete(wallet_monitor)
    db.session.commit()


def test_update_dao_same_treasury_doesnt_duplicate(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test that updating a DAO with the same treasury wallet doesn't create duplicates"""
    db = client.application.db
    
    # Valid Solana wallet address for testing
    valid_wallet = "2BLzCu5w6GCgyvyCzvaE4cw2GNWvCZyJg5TTW5fyd44r"
    
    # First, set the initial treasury
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Get the initial wallet monitor
    initial_monitor = WalletMonitor.get_by_address(valid_wallet, db.session)
    assert initial_monitor is not None
    initial_added_at = initial_monitor.added_at
    
    # Update the DAO with the same treasury wallet
    res = client.put(
        f"/daos/{dao.dao_id}",
        json={
            "name": "Updated name",
            "treasury": valid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    assert res.status_code == 200
    
    # Verify that the wallet in monitoring hasn't changed
    wallet_monitor = WalletMonitor.get_by_address(valid_wallet, db.session)
    assert wallet_monitor is not None
    assert wallet_monitor.wallet_address == valid_wallet
    assert wallet_monitor.added_at == initial_added_at  # Time shouldn't change
    
    # Clean up
    if wallet_monitor:
        db.session.delete(wallet_monitor)
    db.session.commit()


def test_invalid_treasury_wallet_not_added(client: Flask, victor: User, victor_logged_in: str):
    """Test that invalid treasury wallets are not added to monitoring"""
    db = client.application.db
    
    # Invalid wallet address (too short)
    invalid_wallet = "ABCDEFG123"
    
    # Attempt to create a DAO with an invalid treasury wallet
    res = client.post(
        "/daos/",
        json={
            "name": "Invalid Treasury DAO",
            "description": "A DAO with invalid treasury",
            "owner_id": victor.user_id,
            "treasury": invalid_wallet
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    assert res.status_code == 400
    assert res.json["message"] == ErrorHandler.INVALID_WALLET_ADDRESS
    
    # Verify the invalid wallet was not added to monitoring
    wallet_monitor = WalletMonitor.get_by_address(invalid_wallet, db.session)
    assert wallet_monitor is None
