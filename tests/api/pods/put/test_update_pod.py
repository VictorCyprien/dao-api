from flask.app import Flask
from api.models.community import Community
from api.models.user import User
from api.models.pod import POD

def test_update_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    """Test updating a POD"""
    update_data = {
        "name": "Updated POD",
        "description": "Updated description"
    }
    res = client.put(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"] 