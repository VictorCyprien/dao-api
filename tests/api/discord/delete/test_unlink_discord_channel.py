import pytest
from flask.app import Flask

from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD
from api.models.discord_channel import DiscordChannel


def test_unlink_discord_channel(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel):
    """Test unlinking a Discord channel from a POD"""
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/{discord_channel.channel_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={}
    )
    
    assert res.status_code == 200
    data = res.json
    assert data["action"] == "unlink_discord_channel"
    assert data["channel"]["channel_id"] == discord_channel.channel_id
    assert data["channel"]["pod_id"] is None


def test_unlink_discord_channel_not_linked(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD, unlinked_discord_channel: DiscordChannel):
    """Test unlinking a Discord channel that's not linked to any POD"""
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/{unlinked_discord_channel.channel_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={}
    )
    
    assert res.status_code == 400  # Should fail since channel is not linked to this POD


def test_unlink_discord_channel_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test unlinking a non-existent Discord channel"""
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/nonexistent_channel",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={}
    )
    
    assert res.status_code == 404


def test_unlink_discord_channel_pod_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO, discord_channel: DiscordChannel):
    """Test unlinking a Discord channel from a non-existent POD"""
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/999999/discord-channels/{discord_channel.channel_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={}
    )
    
    assert res.status_code == 404


def test_unlink_discord_channel_dao_not_found(client: Flask, victor: User, victor_logged_in: str, pod: POD, discord_channel: DiscordChannel):
    """Test unlinking a Discord channel with a non-existent DAO"""
    res = client.delete(
        f"/daos/999999/pods/{pod.pod_id}/discord-channels/{discord_channel.channel_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={}
    )
    
    assert res.status_code == 404


def test_unlink_discord_channel_unauthorized(client: Flask, sayori: User, sayori_logged_in: str, dao: DAO, pod: POD, discord_channel: DiscordChannel):
    """Test unlinking a Discord channel when user is not member of the DAO"""
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/discord-channels/{discord_channel.channel_id}",
        headers={"Authorization": f"Bearer {sayori_logged_in}"},
        json={}
    )
    
    assert res.status_code == 401 