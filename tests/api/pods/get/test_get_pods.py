from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD

def test_get_community_pods(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test listing all PODs in a dao"""
    res = client.get(
        f"/daos/{dao.dao_id}/pods",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 200
    data = res.json
    assert len(data) == 1
    assert data[0]["pod_id"] == pod.pod_id
    assert data[0]["name"] == pod.name
    assert data[0]["dao_id"] == dao.dao_id

def test_get_pod(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting a specific POD"""
    res = client.get(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}",
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 200
    data = res.json
    assert data["pod_id"] == pod.pod_id
    assert data["name"] == pod.name
    assert data["dao_id"] == dao.dao_id

def test_get_pod_members(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting POD members"""
    res = client.get(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/members",
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 200
    data = res.json
    assert len(data) == 0  # Assuming pod starts with no members 