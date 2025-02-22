from flask.app import Flask
from api.models.community import Community
from api.models.user import User
from api.models.pod import POD

def test_delete_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test deleting a POD"""
    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Verify POD is deleted
    res = client.get(
        f"/communities/{community.community_id}/pods/{pod.pod_id}"
    )
    assert res.status_code == 404

def test_remove_pod_member(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test removing a member from a POD"""
    # First add the member
    membership_data = {
        "user_id": victor.user_id
    }
    client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Then remove them
    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Verify member was removed
    res = client.get(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members"
    )
    data = res.json
    assert len(data) == 0 

