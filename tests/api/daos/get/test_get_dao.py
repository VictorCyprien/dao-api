from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User

def test_get_dao(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    res = client.get(
        f"/daos/{dao.dao_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    print(res.json)
    assert res.status_code == 200
    data = res.json
    assert data == {
        'dao_id': dao.dao_id,
        'name': dao.name,
        'description': dao.description,
        'owner_id': dao.owner_id,
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

def test_get_dao_not_found(client: Flask, victor: User, victor_logged_in: str):
    res = client.get(
        f"/daos/999999",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404
