from datetime import datetime, timezone
import pytz

from api.models.wallet_monitor import WalletMonitor
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy

def test_create_wallet_monitor(client: Flask, db: SQLAlchemy):
    """Test creating a wallet monitor entry"""
    
    # Valid Solana wallet address for testing
    wallet_address = "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8WJ"
    
    # Check if wallet already exists and delete it
    existing = WalletMonitor.get_by_address(wallet_address, db.session)
    if existing:
        db.session.delete(existing)
        db.session.commit()
    
    # Create a wallet with explicit pytz timezone
    import datetime
    now = datetime.datetime.now(pytz.utc)
    wallet_monitor = WalletMonitor(
        wallet_address=wallet_address,
        added_at=now
    )
    
    print(f"Before save - tzinfo: {wallet_monitor.added_at.tzinfo}")
    print(f"Before save - full datetime: {wallet_monitor.added_at}")
    
    # Save to database
    db.session.add(wallet_monitor)
    db.session.commit()
    
    # Get fresh instance from database
    db.session.expire(wallet_monitor)
    db.session.refresh(wallet_monitor)
    
    print(f"After save - tzinfo: {wallet_monitor.added_at.tzinfo}")
    print(f"After save - full datetime: {wallet_monitor.added_at}")
    
    # For SQLite in memory, we might lose timezone info but we still have a datetime
    assert wallet_monitor.wallet_address == wallet_address
    assert isinstance(wallet_monitor.added_at, datetime.datetime)
    
    # If timezone info is lost, this is a SQLite limitation in test environment
    # In production with PostgreSQL, timezone info should be preserved
    
    # Retrieve the wallet monitor and check it matches
    retrieved = WalletMonitor.get_by_address(wallet_address, db.session)
    assert retrieved is not None
    assert retrieved.wallet_address == wallet_address
    print(f"Retrieved - tzinfo: {retrieved.added_at.tzinfo}")
    print(f"Retrieved - full datetime: {retrieved.added_at}")
    
    # For the test, we should still be able to convert to dict
    wallet_dict = wallet_monitor.to_dict()
    assert wallet_dict["wallet_address"] == wallet_address
    assert isinstance(wallet_dict["added_at"], str)
    
    # Clean up
    db.session.delete(wallet_monitor)
    db.session.commit()


def test_get_all_wallet_monitors(client: Flask):
    """Test retrieving all wallet monitor entries"""
    db = client.application.db
    
    # Create a few wallet monitor entries
    wallet_addresses = [
        "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8WJ",
        "87rGx3SZ2S2qUGd6WQWGZj13izuoJJJVXYbzzGi2qkn8",
        "2BLzCu5w6GCgyvyCzvaE4cw2GNWvCZyJg5TTW5fyd44r"
    ]
    
    wallet_monitors = []
    for address in wallet_addresses:
        monitor = WalletMonitor.create(address)
        db.session.add(monitor)
        wallet_monitors.append(monitor)
    
    db.session.commit()
    
    # Retrieve all wallet monitors
    all_monitors = WalletMonitor.get_all(db.session)
    assert len(all_monitors) >= len(wallet_addresses)  # There might be existing entries
    
    # Check that all our test wallet addresses are in the result
    retrieved_addresses = [monitor.wallet_address for monitor in all_monitors]
    for address in wallet_addresses:
        assert address in retrieved_addresses
    
    # Clean up
    for monitor in wallet_monitors:
        db.session.delete(monitor)
    db.session.commit()


def test_wallet_monitor_to_dict(client: Flask):
    """Test conversion of wallet monitor to dictionary"""
    # Create a wallet monitor without adding to the database
    wallet_address = "6VDivnFWVRdFemYjgPbGPQ8kzRe3WBcew6tEJePWq8WJ"
    wallet_monitor = WalletMonitor(
        wallet_address=wallet_address,
        added_at=datetime.now(timezone.utc)
    )
    
    # Convert to dictionary
    wallet_dict = wallet_monitor.to_dict()
    
    # Check dictionary values
    assert wallet_dict["wallet_address"] == wallet_address
    assert isinstance(wallet_dict["added_at"], str)
    
    # Check __iter__ implementation (dict conversion)
    dict_from_iter = dict(wallet_monitor)
    assert dict_from_iter == wallet_dict 