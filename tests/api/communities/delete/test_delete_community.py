from flask.app import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.session import make_transient

from api.models.community import Community
from api.models.user import User

def test_delete_community(client: Flask, victor: User, victor_logged_in: str, community: Community, db: SQLAlchemy):
    res = client.delete(
        f"/communities/{community.community_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Make the community transient to avoid SQLAlchemy error for other tests
    make_transient(community)
    db.session.add(community)
    db.session.commit()

def test_delete_community_not_found(client: Flask, victor: User, victor_logged_in: str):
    res = client.delete(
        f"/communities/1234567890",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 404

def test_unauthorized_community_delete(client: Flask, victor: User, sayori: User, sayori_logged_in: str, community: Community):
    res = client.delete(
        f"/communities/{community.community_id}",
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    assert res.status_code == 401
