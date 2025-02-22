from flask.app import Flask
from api.models.community import Community
from api.models.user import User
from api.models.pod import POD

def test_get_community_pods(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test listing all PODs in a community"""
    res = client.get(
        f"/communities/{community.community_id}/pods",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert len(data) == 1
    assert data[0]["pod_id"] == pod.pod_id
    assert data[0]["name"] == pod.name
    assert data[0]["community_id"] == community.community_id

def test_get_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test getting a specific POD"""
    res = client.get(
        f"/communities/{community.community_id}/pods/{pod.pod_id}"
    )
    assert res.status_code == 200
    data = res.json
    assert data["pod_id"] == pod.pod_id
    assert data["name"] == pod.name
    assert data["community_id"] == community.community_id

def test_get_pod_members(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test getting POD members"""
    res = client.get(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members"
    )
    assert res.status_code == 200
    data = res.json
    assert len(data) == 0  # Assuming pod starts with no members 