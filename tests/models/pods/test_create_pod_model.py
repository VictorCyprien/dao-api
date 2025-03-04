from api.models.pod import POD
from unittest.mock import ANY

def test_model_create_pod(app, dao):
    pod_data = {
        "name": "Backend Learning Group",
        "description": "Learn backend development with Python and Flask",
        "dao_id": dao.dao_id
    }

    pod = POD.create(input_data=pod_data)
    
    assert pod.pod_id == ANY
    assert pod.name == "Backend Learning Group"
    assert pod.description == "Learn backend development with Python and Flask"
    assert pod.dao_id == dao.dao_id
    assert pod.is_active == True
    assert pod.created_at is not None 