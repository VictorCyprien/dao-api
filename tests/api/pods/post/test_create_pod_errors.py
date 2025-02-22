from flask.app import Flask
from api.models.community import Community
from api.models.user import User
from api.models.pod import POD

def test_create_pod_unauthorized(client: Flask, community: Community):
    """Test creating a POD without authentication"""
    pod_data = {
        "name": "Test POD",
        "description": "Test POD description"
    }
    res = client.post(
        f"/communities/{community.community_id}/pods",
        json=pod_data
    )
    assert res.status_code == 401

def test_create_pod_invalid_data(client: Flask, victor: User, victor_logged_in: str, community: Community):
    """Test creating a POD with invalid data"""
    pod_data = {
        # Missing required 'name' field
        "description": "Test POD description"
    }
    res = client.post(
        f"/communities/{community.community_id}/pods",
        json=pod_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 422

def test_add_duplicate_pod_member(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test adding the same member twice"""
    membership_data = {
        "user_id": victor.user_id
    }
    # First addition
    client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Second addition should fail
    res = client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400 


def test_create_pod_wrong_community(client: Flask, victor: User, victor_logged_in: str, community: Community):
    """Test creating a POD with wrong community ID"""
    pod_data = {
        "name": "Test POD",
        "description": "Test POD description",
        "community_id": community.community_id
    }
    res = client.post(
        f"/communities/999999/pods",
        json=pod_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 404


def test_create_pod_not_admin(client: Flask, sayori: User, sayori_logged_in: str, community: Community):
    """Test creating a POD without being an admin"""
    pod_data = {
        "name": "Test POD",
        "description": "Test POD description",
        "community_id": community.community_id
    }
    res = client.post(
        f"/communities/{community.community_id}/pods",
        json=pod_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401


def test_add_user_to_nonexistent_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test adding a user to a POD that doesn't exist"""
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.post(
        f"/communities/{community.community_id}/pods/999999/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404


def test_add_user_to_pod_not_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, sayori_logged_in: str, community: Community, pod: POD):
    """Test adding a user to a POD that they are not an admin of""" 
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401


def test_add_user_to_pod_not_member(client: Flask, victor: User, sayori: User, victor_logged_in: str, sayori_logged_in: str, community: Community, pod: POD):
    """Test adding a user to a POD that they are not a member of"""
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401


def test_add_user_to_pod_not_in_community(client: Flask, victor: User, victor_logged_in: str, sayori: User, community: Community, pod: POD):
    """Test adding a user to a POD but they are not a member of the community"""
    membership_data = {
        "user_id": sayori.user_id
    }
    res = client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 401


def test_add_user_to_pod_community_not_found(client: Flask, victor: User, victor_logged_in: str, sayori: User, community: Community, pod: POD):
    """Test adding a user to a POD but the community is not found"""
    membership_data = {
        "user_id": sayori.user_id
    }
    res = client.post(
        f"/communities/999999/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

