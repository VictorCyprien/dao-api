from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User

def test_add_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    res = client.post(
        f"/daos/{dao.dao_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    assert sayori in dao.members
    assert sayori in dao.admins


def test_add_admin_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    res = client.post(
        f"/daos/{dao.dao_id}/admins",
        json={"user_id": 1234567890},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This user doesn't exist !"


def test_add_admin_dao_not_found(client: Flask, victor: User, sayori: User, victor_logged_in: str):
    res = client.post(
        f"/daos/1234567890/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
    assert res.json["message"] == "This DAO doesn't exist !"


def test_add_admin_not_owner(client: Flask, victor: User, sayori: User, natsuki: User, victor_logged_in: str, natsuki_logged_in: str, dao: DAO):
    res = client.post(
        f"/daos/{dao.dao_id}/admins",
        json={"user_id": sayori.user_id},
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    assert res.status_code == 401
    assert res.json["message"] == "You are not the owner of this DAO !"


def test_add_admin_already_admin(client: Flask, victor: User, sayori: User, victor_logged_in: str, dao: DAO):
    res = client.post(
        f"/daos/{dao.dao_id}/admins",
        json={"user_id": victor.user_id},
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 400
    assert res.json["message"] == "This user is already an admin of this DAO !"


