from flask.app import Flask
from api.models.community import Community
from api.models.user import User

def test_update_community(client: Flask, victor: User, victor_logged_in: str, community: Community):
    res = client.put(
        f"/communities/{community.community_id}",
        json={
            "name": "Updated Community",
            "description": "Updated description"
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert data == {
        'community_id': community.community_id,
        'name': community.name,
        'description': community.description,
        'owner_id': community.owner_id,
        'is_active': True,
        'admins': [
            {
                'user_id': victor.user_id,
                'username': victor.username,
            }
        ],
        'members': [
            {
                'user_id': victor.user_id,
                'username': victor.username,
            }
        ]
    }

def test_unauthorized_community_update(client: Flask, victor: User, sayori: User, sayori_logged_in: str, community: Community):
    res = client.put(
        f"/communities/{community.community_id}",
        json={
            "name": "Unauthorized Update",
            "description": "Should fail"
        },
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401

def test_update_community_not_found(client: Flask, victor: User, victor_logged_in: str, community: Community):
    res = client.put(
        f"/communities/999999",
        json={
            "name": "Updated Community",
            "description": "Updated description"
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
