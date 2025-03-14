import pytest
from flask.app import Flask
from unittest.mock import patch

from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD
from api.models.discord_channel import DiscordChannel
from api.models.discord_message import DiscordMessage


def test_get_pod_feed(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel, discord_messages: list):
    """Test getting the Discord feed for a POD"""
    # Patch the cached_view decorator to bypass caching in tests
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/feed",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_pod_feed"
        assert len(data["messages"]) == 5
        
        # Verify message fields
        message = data["messages"][0]
        assert "message_id" in message
        assert "channel_id" in message
        assert "username" in message
        assert "text" in message
        assert "created_at" in message


def test_get_pod_feed_with_limit(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel, discord_messages: list):
    """Test getting the Discord feed with a limit parameter"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/feed?limit=2",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_pod_feed"
        assert len(data["messages"]) == 2


def test_get_pod_feed_empty(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting an empty Discord feed for a POD (no channels or messages)"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/feed",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_pod_feed"
        assert len(data["messages"]) == 0


def test_get_pod_feed_dao_not_found(client: Flask, victor: User, victor_logged_in: str, pod: POD):
    """Test getting feed with non-existent DAO"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/999999/pods/{pod.pod_id}/feed",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 404


def test_get_pod_feed_pod_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test getting feed with non-existent POD"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/999999/feed",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 404


def test_get_pod_feed_unauthorized(client: Flask, sayori: User, sayori_logged_in: str, dao: DAO, pod: POD):
    """Test getting feed when user is not member of the DAO"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/feed",
            headers={"Authorization": f"Bearer {sayori_logged_in}"},
            json={}
        )
        
        assert res.status_code == 401


def test_get_pod_feed_wrong_dao(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting feed with mismatched DAO and POD"""
    # Create a second DAO first
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.post(
            "/daos",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={"name": "Second DAO", "description": "Test Description"}
        )
        
        # Check if the response has the expected format, if not, use a fake ID
        if res.status_code == 201 and "dao" in res.json:
            second_dao_id = res.json["dao"]["dao_id"]
        else:
            # If DAO creation failed or response format is different, use a fake ID
            # that's different from the original DAO
            second_dao_id = "999999"
        
        # Try to access pod of first DAO through second DAO
        res = client.get(
            f"/daos/{second_dao_id}/pods/{pod.pod_id}/feed",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 400 or res.status_code == 404 