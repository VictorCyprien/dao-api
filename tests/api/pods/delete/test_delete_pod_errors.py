from flask.app import Flask
from api.models.community import Community
from api.models.user import User
from api.models.pod import POD

def test_delete_pod_unauthorized(client: Flask, community: Community, pod: POD):
    """Test deleting a POD without authentication"""
    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}"
    )
    assert res.status_code == 401

def test_delete_nonexistent_pod(client: Flask, victor: User, victor_logged_in: str, community: Community):
    """Test deleting a POD that doesn't exist"""
    res = client.delete(
        f"/communities/{community.community_id}/pods/999999",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

def test_remove_nonexistent_pod_member(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test removing a member that isn't in the POD"""
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 400

   
def test_remove_pod_member_not_in_community(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community, pod: POD):
    """Test removing a member that isn't in the community"""
    membership_data = {
        "user_id": sayori.user_id
    }
    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 401


def test_delete_pod_wrong_community(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test deleting a POD with wrong community ID"""
    res = client.delete(
        f"/communities/999999/pods/{pod.pod_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404


def test_leave_pod_not_in_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test leaving a POD that the user isn't in"""
    membership_data = {
        "user_id": victor.user_id
    }

    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400


def test_leave_pod_user_not_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, sayori_logged_in: str, community: Community, pod: POD):
    """Test make leave a user on a POD without being an admin"""
    membership_data = {
        "user_id": victor.user_id
    }

    client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )

    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401


def test_remove_pod_member_pod_not_found(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test removing a member from a POD that doesn't exist"""
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.delete(
        f"/communities/{community.community_id}/pods/999999/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404


def test_leave_pod_community_not_found(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test leaving a POD but community not found"""
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.delete(
        f"/communities/999999/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404


def test_delete_pod_not_admin(client: Flask, victor: User, victor_logged_in: str, sayori: User, sayori_logged_in: str, community: Community, pod: POD):
    """Test leaving a POD but the user is not an admin"""
    membership_data = {
        "user_id": victor.user_id
    }
    
    client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )

    client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )

    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        json=membership_data,
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )

    assert res.status_code == 401
    
