from api.models.pod import POD

def test_update_pod(app, pod: POD):
    update_data = {
        "name": "Updated Group Name",
        "description": "Updated description",
        "is_active": False
    }
    
    pod.update(input_data=update_data)
    
    assert pod.name == "Updated Group Name"
    assert pod.description == "Updated description"
    assert pod.is_active == False

def test_partial_update_pod(app, pod: POD):
    # Test updating only name
    pod.update(input_data={"name": "New Name Only"})
    assert pod.name == "New Name Only"
    assert pod.description == "Learn backend development with Python and Flask"
    assert pod.is_active == True
    
    # Test updating only description
    pod.update(input_data={"description": "New Description Only"})
    assert pod.name == "New Name Only"
    assert pod.description == "New Description Only"
    assert pod.is_active == True
    
    # Test updating only is_active
    pod.update(input_data={"is_active": False})
    assert pod.name == "New Name Only"
    assert pod.description == "New Description Only"
    assert pod.is_active == False 