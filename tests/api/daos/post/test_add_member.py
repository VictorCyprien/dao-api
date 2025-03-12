from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User

def test_add_member(client: Flask, victor: User, sayori: User, sayori_logged_in: str, dao: DAO):
    """Test successfully adding a member to a DAO"""
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        json={},
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    data = res.json
    print(data)
    assert res.status_code == 200
    assert sayori in dao.members



def test_add_member_as_admin(client: Flask, victor: User, sayori: User, natsuki: User, victor_logged_in: str, sayori_logged_in: str, dao: DAO):
    """Test that an admin can't add members"""
    # First add sayori as a member
    assert sayori not in dao.members
    
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    data = res.json
    print(data)
    assert res.status_code == 400
    assert sayori not in dao.members
    assert data["message"] == "This user is already a member of this DAO !"


def test_add_member_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": "1234567890"},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400
    assert res.json["message"] == "This user is already a member of this DAO !"


def test_add_member_dao_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    res = client.post(
        f"/daos/1234567890/members",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This DAO doesn't exist !"


def test_user_already_member(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        json={"user_id": victor.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400
    assert res.json["message"] == "This user is already a member of this DAO !"

 