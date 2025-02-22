from flask.app import Flask
from api.models.community import Community
from api.models.user import User
from api.models.pod import POD

def test_update_pod_unauthorized(client: Flask, community: Community, pod: POD):
    """Test updating a POD without authentication"""
    update_data = {
        "name": "Updated POD",
        "description": "Updated description"
    }
    res = client.put(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        json=update_data
    )
    assert res.status_code == 401

def test_update_nonexistent_pod(client: Flask, victor: User, victor_logged_in: str, community: Community):
    """Test updating a POD that doesn't exist"""
    update_data = {
        "name": "Updated POD",
        "description": "Updated description"
    }
    res = client.put(
        f"/communities/{community.community_id}/pods/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

def test_update_pod_invalid_data(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test updating a POD with invalid data"""
    update_data = {
        "name": "",  # Empty name should be invalid
        "description": "Updated description"
    }
    res = client.put(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 422


def test_update_pod_not_admin(client: Flask, sayori: User, sayori_logged_in: str, community: Community, pod: POD):
    """Test updating a POD without being an admin"""
    update_data = {
        "name": "Updated POD",
        "description": "Updated description"
    }
    res = client.put(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401


def test_update_pod_wrong_community(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test updating a POD with wrong community ID"""
    update_data = {
        "name": "Updated POD",
        "description": "Updated description"
    }
    res = client.put(
        f"/communities/999999/pods/{pod.pod_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

