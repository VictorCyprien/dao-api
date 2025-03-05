from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User


def test_remove_member(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    """Test successfully removing a member from a dao"""
    # First add member
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    assert sayori in dao.members
    
    # Then remove member
    res = client.delete(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    assert sayori not in dao.members


def test_remove_member_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    res = client.delete(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": 1234567890},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This user doesn't exist !"

def test_remove_member_community_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    res = client.delete(
        f"/daos/1234567890/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This DAO doesn't exist !"

def test_user_not_member(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    res = client.delete(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400
    assert res.json["message"] == "This user is not a member of this DAO !"


def test_unauthorized_member_operations(client: Flask, victor: User, sayori: User, 
                                     natsuki: User, natsuki_logged_in: str, dao: DAO):
    """Test that non-admins cannot add/remove members"""
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "You are not an admin of this DAO !"

    res = client.delete(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "You are not an admin of this DAO !"