from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD

def test_update_pod(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test updating a POD"""
    update_data = {
        "name": "Updated POD",
        "description": "Updated description",
        "user_who_made_request": victor.user_id
    }
    res = client.put(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"] 