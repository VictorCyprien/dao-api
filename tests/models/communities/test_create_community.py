from api.models.community import Community
from unittest.mock import ANY

from api.models.user import User

def test_model_create_community(app, victor: User):
    community_data = {
        "name": "Python Developers",
        "description": "A community for Python enthusiasts",
        "owner_id": victor.user_id,
        "is_private": False,
        "tags": ["python", "programming"]
    }

    community = Community.create(input_data=community_data)
    community.add_member(victor)
    community.add_admin(victor)
    
    assert community.community_id == ANY
    assert community.name == "Python Developers"
    assert community.description == "A community for Python enthusiasts"
    assert community.owner_id == victor.user_id
    assert community.is_active == True
    assert victor in community.members
    assert victor in community.admins
    