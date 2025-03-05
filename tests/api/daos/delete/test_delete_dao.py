from flask.app import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.session import make_transient

from api.models.dao import DAO
from api.models.user import User

def test_delete_dao(client: Flask, victor: User, victor_logged_in: str, dao: DAO, db: SQLAlchemy):
    res = client.delete(
        f"/daos/{dao.dao_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Make the DAO transient to avoid SQLAlchemy error for other tests
    make_transient(dao)
    db.session.add(dao)
    db.session.commit()

def test_delete_dao_not_found(client: Flask, victor: User, victor_logged_in: str):
    res = client.delete(
        f"/daos/1234567890",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

def test_unauthorized_dao_delete(client: Flask, victor: User, sayori: User, sayori_logged_in: str, dao: DAO):
    res = client.delete(
        f"/daos/{dao.dao_id}",
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401
