def test_register(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@mail.com",
        "password": "test123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.get_json()["msg"] == "User registered successfully"


def test_login(client):
    # Register first
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@mail.com",
        "password": "test123",
        "full_name": "Test User"
    })

    # Login
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "test123"
    })

    data = response.get_json()
    assert response.status_code == 200
    assert "access_token" in data
