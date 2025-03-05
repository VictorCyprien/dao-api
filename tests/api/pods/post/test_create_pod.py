from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD

def test_create_pod(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test creating a new POD"""
    pod_data = {
        "name": "Test POD",
        "description": "Test POD description",
        "dao_id": dao.dao_id
    }
    res = client.post(
        f"/daos/{dao.dao_id}/pods",
        json=pod_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 201
    data = res.json
    assert data["name"] == pod_data["name"]
    assert data["description"] == pod_data["description"]
    assert data["dao_id"] == dao.dao_id

def test_add_pod_member(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test adding a member to a POD"""
    membership_data = {
        "user_id": victor.user_id
    }
    res = client.post(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Verify member was added
    res = client.get(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/members"
    )
    data = res.json
    assert len(data) == 1
    assert data[0]["user_id"] == victor.user_id 