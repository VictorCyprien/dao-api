from flask.app import Flask
from unittest.mock import ANY
from api.models.community import Community
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
    print(data)
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
    

def test_update_community(client: Flask, victor: User, victor_logged_in: str, community: Community):
    print("aled")
    print(community)
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


def test_add_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    res = client.post(
        f"/communities/{community.community_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    assert sayori in community.members
    assert sayori in community.admins

def test_remove_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    # First add admin
    res = client.post(
        f"/communities/{community.community_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    res = client.delete(
        f"/communities/{community.community_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    data = res.json
    assert sayori not in community.admins
    assert sayori in community.members

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

