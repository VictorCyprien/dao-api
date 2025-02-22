from flask.app import Flask
from api.models.community import Community
from api.models.user import User

def test_get_community(client: Flask, victor: User, victor_logged_in: str, community: Community):
    res = client.get(
        f"/communities/{community.community_id}",
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

def test_get_community_not_found(client: Flask, victor: User, victor_logged_in: str):
    res = client.get(
        f"/communities/999999",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
