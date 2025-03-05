from flask.app import Flask
from api.models.dao import DAO
from api.models.user import User

def test_get_all_daos(client: Flask, victor: User, victor_logged_in: str, dao: DAO):
    res = client.get(
        "/daos/",
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
            'dao_id': dao.dao_id,
            'description': dao.description,
            'is_active': dao.is_active,
            'members': [
                {
                    'user_id': victor.user_id, 'username': victor.username
                }
            ],
            'name': dao.name,
            'owner_id': dao.owner_id
        }
    ] 