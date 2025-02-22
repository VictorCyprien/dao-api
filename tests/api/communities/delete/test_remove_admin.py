from flask.app import Flask
from api.models.community import Community
from api.models.user import User


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
    assert sayori not in community.admins
    assert sayori in community.members


def test_remove_admin_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    res = client.delete(
        f"/communities/{community.community_id}/admins",
        json={"user_id": 1234567890},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This user doesn't exist !"


def test_remove_admin_community_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    res = client.delete(
        f"/communities/1234567890/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This community doesn't exist !"

def test_user_not_in_community(client: Flask, victor: User, sayori: User, victor_logged_in: str, sayori_logged_in: str, community: Community):
    res = client.delete(
        f"/communities/{community.community_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "This user is not a member of this community !"

def test_unauthorized_admin_operations(client: Flask, victor: User, sayori: User, natsuki: User, victor_logged_in: str, natsuki_logged_in: str, community: Community):
    res = client.post(
        f"/communities/{community.community_id}/members",
        json={"user_id": natsuki.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    res = client.delete(
        f"/communities/{community.community_id}/admins",
        json={"user_id": victor.user_id},
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "You are not the owner of this community !"


def test_not_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    res = client.post(
        f"/communities/{community.community_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200

    res = client.delete(
        f"/communities/{community.community_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400
    assert res.json["message"] == "This user is not an admin of this community !"
