from flask_jwt_extended import create_access_token

def test_register(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@mail.com",
        "password": "test1234",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.get_json()["msg"] == "User registered successfully. Please check your email to verify your account."


def test_login_success(client):
    client.post("/auth/register", json={
        "username": "testuser2",
        "email": "test2@mail.com",
        "password": "test1234",
        "full_name": "Test User 2"
    })

    response = client.post("/auth/login", json={
        "username": "testuser2",
        "password": "test1234"
    })

    data = response.get_json()
    assert response.status_code == 200
    assert "access_token" in data


def test_login_fail_wrong_password(client):
    client.post("/auth/register", json={
        "username": "testuser3",
        "email": "test3@mail.com",
        "password": "test1234",
        "full_name": "Test User 3"
    })

    response = client.post("/auth/login", json={
        "username": "testuser3",
        "password": "wrongpass"
    })

    assert response.status_code == 401
    assert response.get_json()["msg"] == "Invalid username or password"


def test_verify_email(client, test_app):
    # Simulate user creation with ID = 1 (adjust if needed)
    with test_app.app_context():
        token = create_access_token(
            identity="1",
            expires_delta=False,
            additional_claims={"purpose": "email_verification"}
        )

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/verify-email", headers=headers)

    assert response.status_code in [200, 404]  # 200 if user exists, 404 if not
    assert "msg" in response.get_json()