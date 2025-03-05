from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD


def test_get_nonexistent_pod(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    """Test getting a POD that doesn't exist"""
    res = client.get(
        f"/daos/{dao.dao_id}/pods/999999",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 404

def test_get_pod_wrong_community(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting a POD with wrong dao ID"""
    res = client.get(
        f"/daos/999999/pods/{pod.pod_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 404


def test_get_pods_wrong_community(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting a POD without authentication"""
    res = client.get(
        f"/daos/123456789/pods",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 404


def test_get_pods_unauthorized(client: Flask, sayori: User, sayori_logged_in: str, dao: DAO, pod: POD):
    """Test getting a POD without authentication"""
    res = client.get(
        f"/daos/{dao.dao_id}/pods",
        headers={"Authorization": f"Bearer {sayori_logged_in}"},
        json={"user_who_made_request": sayori.user_id}
    )
    assert res.status_code == 401


def test_get_pod_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting a POD that doesn't exist"""
    res = client.get(
        f"/daos/{dao.dao_id}/pods/999999/members",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 404


def test_get_pod_community_not_found(client: Flask, victor: User, victor_logged_in: str, dao: DAO, pod: POD):
    """Test getting a POD that doesn't exist"""
    res = client.get(
        f"/daos/999999/pods/{pod.pod_id}/members",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json={"user_who_made_request": victor.user_id}
    )
    assert res.status_code == 404

