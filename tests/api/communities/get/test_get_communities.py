from flask.app import Flask
from api.models.community import Community
from api.models.user import User

def test_get_all_communities(client: Flask, victor: User, victor_logged_in: str, community: Community):
    res = client.get(
        "/communities/",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert data == [
        {
            'admins': [
                {
                    'user_id': victor.user_id, 'username': victor.username
                }
            ],
            'community_id': community.community_id,
            'description': community.description,
            'is_active': community.is_active,
            'members': [
                {
                    'user_id': victor.user_id, 'username': victor.username
                }
            ],
            'name': community.name,
            'owner_id': community.owner_id
        }
    ] 