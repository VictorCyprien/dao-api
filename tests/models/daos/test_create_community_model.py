from api.models.dao import DAO
from unittest.mock import ANY

from api.models.user import User

def test_model_create_community(app, victor: User):
    community_data = {
        "name": "Python Developers",
        "description": "A dao for Python enthusiasts",
        "owner_id": victor.user_id,
        "is_private": False,
        "tags": ["python", "programming"]
    }

    dao = DAO.create(input_data=community_data)
    dao.add_member(victor)
    dao.add_admin(victor)
    
    assert dao.dao_id == ANY
    assert dao.name == "Python Developers"
    assert dao.description == "A dao for Python enthusiasts"
    assert dao.owner_id == victor.user_id
    assert dao.is_active == True
    assert victor in dao.members
    assert victor in dao.admins
    