


def test_login_success(client, sayori):
    """Test successful login returns token"""
    data = {
        "email": sayori.email,
        "password": "my_password"
    }

    response = client.post("/auth/login", json=data)

    
    assert response.status_code == 201
    assert "token" in response.json
    assert response.json["msg"] == "Logged"


def test_login_invalid_email(client):
    """Test login with invalid email returns error"""
    data = {
        "email": "invalid_email",
        "password": "my_password"
    }

    response = client.post("/auth/login", json=data)

    assert response.status_code == 401
    assert response.json["message"] == "The email or password is incorrect"


def test_login_invalid_password(client, sayori):
    """Test login with invalid password returns error"""
    data = {
        "email": sayori.email,
        "password": "invalid_password"
    }

    response = client.post("/auth/login", json=data)
    assert response.status_code == 401
    assert response.json["message"] == "The email or password is incorrect"


def test_user_not_found(client):
    """Test login with non-existent user returns error"""
    data = {
        "email": "nonexistent@example.com",
        "password": "my_password"
    }

    response = client.post("/auth/login", json=data)

    assert response.status_code == 401
    assert response.json["message"] == "The email or password is incorrect"

