import pytest
from flask.app import Flask
from unittest.mock import patch

from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD
from api.models.discord_channel import DiscordChannel


def test_get_pod_discord_channels(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel):
    """Test getting Discord channels for a POD"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_pod_discord_channels"
        assert len(data["channels"]) == 1
        
        # Verify channel fields
        channel = data["channels"][0]
        assert channel["channel_id"] == discord_channel.channel_id
        assert channel["name"] == discord_channel.name
        assert channel["pod_id"] == pod.pod_id


def test_get_pod_discord_channels_empty(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting Discord channels for a POD with no channels"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_pod_discord_channels"
        assert len(data["channels"]) == 0


def test_get_pod_discord_channels_dao_not_found(client: Flask, victor: User, victor_logged_in: str, pod: POD):
    """Test getting Discord channels with non-existent DAO"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/999999/pods/{pod.pod_id}/discord-channels",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 404


def test_get_pod_discord_channels_pod_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test getting Discord channels with non-existent POD"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/999999/discord-channels",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 404


def test_get_pod_discord_channels_unauthorized(client: Flask, sayori: User, sayori_logged_in: str, dao: DAO, pod: POD):
    """Test getting Discord channels when user is not member of the DAO"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels",
            headers={"Authorization": f"Bearer {sayori_logged_in}"},
            json={}
        )
        
        assert res.status_code == 401


def test_get_channel_messages(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel, discord_messages: list):
    """Test getting messages for a specific Discord channel"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/{discord_channel.channel_id}/messages",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_channel_messages"
        assert len(data["messages"]) == 5


def test_get_channel_messages_with_limit(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel, discord_messages: list):
    """Test getting messages for a specific Discord channel with limit"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/{discord_channel.channel_id}/messages?limit=2",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 200
        data = res.json
        assert data["action"] == "get_channel_messages"
        assert len(data["messages"]) == 2


def test_get_channel_messages_channel_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting messages for a non-existent Discord channel"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/999999/messages",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 404


def test_get_channel_messages_not_linked_to_pod(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, unlinked_discord_channel: DiscordChannel):
    """Test getting messages for a Discord channel not linked to the POD"""
    with patch('helpers.cache_decorator.cached_view', lambda *args, **kwargs: lambda f: f):
        res = client.get(
            f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/{unlinked_discord_channel.channel_id}/messages",
            headers={"Authorization": f"Bearer {victor_logged_in}"},
            json={}
        )
        
        assert res.status_code == 400 