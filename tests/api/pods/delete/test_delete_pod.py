from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.session import make_transient
from api.models.dao import DAO
from api.models.user import User
from api.models.pod import POD

def test_delete_pod(client: Flask, victor: User, victor_logged_in: str, dao: DAO, db: SQLAlchemy):
    """Test deleting a POD"""
    # First add a pod
    pod_data = {
        "name": "Test POD",
        "description": "Test POD description",
        "dao_id": dao.dao_id
    }
    pod = POD.create(pod_data)
    db.session.add(pod)
    db.session.commit()

    membership_data = {
        "user_id": victor.user_id
    }
    pod_id = pod.pod_id
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=membership_data
    )
    print(res.json)
    assert res.status_code == 200
    
    # Verify POD is deleted
    res = client.get(
        f"/daos/{dao.dao_id}/pods/{pod_id}"
    )
    assert res.status_code == 404



def test_remove_pod_member(client: Flask, victor: User, victor_logged_in: str, natsuki: User, natsuki_logged_in: str, dao: DAO, pod: POD, db: SQLAlchemy):
    """Test removing a member from a POD"""
    # First add the member
    res = client.post(
        f"/daos/{dao.dao_id}/members",
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    print(res.json)
    assert res.status_code == 200
    assert natsuki in dao.members

    membership_data = {
        "user_id": natsuki.user_id
    }
    res = client.post(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/members",
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )

    assert res.status_code == 200
    assert natsuki in pod.members
    
    # Then remove them
    res = client.delete(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/members",
        json=membership_data,
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    assert res.status_code == 200
    
    # Verify member was removed
    res = client.get(
        f"/daos/{dao.dao_id}/pods/{pod.pod_id}/members"
    )
    data = res.json
    assert len(data) == 0 

