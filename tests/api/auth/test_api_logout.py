from freezegun import freeze_time


def test_logout_success(client, sayori, sayori_logged_in):
    """Test successful logout"""
    headers = {"Authorization": f"Bearer {sayori_logged_in}"}
    response = client.post("/auth/logout", headers=headers)

    assert response.status_code == 201
    assert response.json["msg"] == "You have been logout !"


def test_logout_no_token(client):
    """Test logout without token returns error"""
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert "Not Authenticated" in response.json["message"]


def test_logout_invalid_token(client):
    """Test logout with invalid token returns error"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/auth/logout", headers=headers)

    assert response.status_code == 401
    assert "Invalid token" in response.json["message"]


def test_logout_expired_token(client, sayori):
    """Test logout with expired token returns error"""
    # First login to get token
    login_data = {
        "email": sayori.email,
        "password": "my_password"
    }
    with freeze_time("2000-01-01"):
        login_response = client.post("/auth/login", json=login_data)
        token = login_response.json["token"]

    # Test logout with expired token
    with freeze_time("2000-01-02"):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/logout", headers=headers)

        assert response.status_code == 401
        assert "Token expired" in response.json["message"]
