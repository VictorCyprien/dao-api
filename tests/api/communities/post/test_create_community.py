from flask.app import Flask
from unittest.mock import ANY
from api.models.user import User

def test_create_community(client: Flask, victor: User, victor_logged_in: str):
    res = client.post(
        "/communities/",
        json={
            "name": "New Community",
            "description": "A test community",
            "owner_id": victor.user_id
        },
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    data = res.json
    assert res.status_code == 201
    assert data == {
        'community_id': ANY,
        'name': 'New Community',
        'description': 'A test community',
        'owner_id': victor.user_id,
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