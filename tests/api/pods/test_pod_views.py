from flask.app import Flask
from unittest.mock import ANY
from api.models.pod import POD
from api.models.user import User
from api.models.community import Community

def test_create_pod(client: Flask, victor: User, victor_logged_in: str, community: Community):
    res = client.post(
        f"/communities/{community.community_id}/pods",
        json={
            "name": "New POD",
            "description": "A test POD",
            "community_id": community.community_id
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 201
    assert data == {
        'pod_id': ANY,
        'name': 'New POD',
        'description': 'A test POD',
        'community_id': community.community_id,
        'is_active': True,
        'created_at': ANY,
    }

def test_get_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    res = client.get(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 200
    assert data == {
        'pod_id': pod.pod_id,
        'name': pod.name,
        'description': pod.description,
        'community_id': pod.community_id,
        'is_active': True,
        'created_at': ANY
    }

def test_update_pod(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    res = client.put(
        f"/communities/{community.community_id}/pods/{pod.pod_id}",
        json={
            "name": "Updated POD",
            "description": "Updated description"
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert data == {
        'pod_id': pod.pod_id,
        'name': 'Updated POD',
        'description': 'Updated description',
        'community_id': pod.community_id,
        'is_active': True,
        'created_at': ANY,
    }

def test_add_participant(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    res = client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json={"user_id": victor.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 200
    assert victor in pod.participants

def test_remove_participant(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community, pod: POD):
    # First add participant
    res = client.post(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json={"user_id": victor.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    res = client.delete(
        f"/communities/{community.community_id}/pods/{pod.pod_id}/members",
        json={"user_id": victor.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert sayori not in pod.participants

def test_list_community_pods(client: Flask, victor: User, victor_logged_in: str, community: Community, pod: POD):
    res = client.get(
        f"/communities/{community.community_id}/pods",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    print(data)
    assert len(data) >= 1
    assert data[0]['pod_id'] == pod.pod_id

def test_unauthorized_pod_access(client: Flask, victor: User, sayori: User, sayori_logged_in: str, community: Community):
    # Assuming POD access requires community membership
    res = client.get(
        f"/communities/{community.community_id}/pods",
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401
