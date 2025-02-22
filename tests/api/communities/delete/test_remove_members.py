from flask.app import Flask
from api.models.community import Community
from api.models.user import User


def test_remove_member(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    """Test successfully removing a member from a community"""
    # First add member
    res = client.post(
        f"/communities/{community.community_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    assert sayori in community.members
    
    # Then remove member
    res = client.delete(
        f"/communities/{community.community_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    assert sayori not in community.members


def test_remove_member_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    res = client.delete(
        f"/communities/{community.community_id}/members",
        json={"user_id": 1234567890},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This user doesn't exist !"

def test_remove_member_community_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    res = client.delete(
        f"/communities/1234567890/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This community doesn't exist !"

def test_user_not_member(client: Flask, victor: User, sayori: User, victor_logged_in: str, community: Community):
    res = client.delete(
        f"/communities/{community.community_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400
    assert res.json["message"] == "This user is not a member of this community !"


def test_unauthorized_member_operations(client: Flask, victor: User, sayori: User, 
                                     natsuki: User, natsuki_logged_in: str, community: Community):
    """Test that non-admins cannot add/remove members"""
    res = client.post(
        f"/communities/{community.community_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "You are not an admin of this community !"

    res = client.delete(
        f"/communities/{community.community_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "You are not an admin of this community !"