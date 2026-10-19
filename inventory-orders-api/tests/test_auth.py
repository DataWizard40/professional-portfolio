def test_register_and_login(client):
    response = client.post(
        "/auth/register", json={"email": "Sam@Example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "sam@example.com"

    response = client.post(
        "/auth/login", data={"username": "sam@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["is_admin"] is False


def test_register_duplicate_email(client):
    body = {"email": "sam@example.com", "password": "password123"}
    client.post("/auth/register", json=body)
    response = client.post("/auth/register", json=body)
    assert response.status_code == 400


def test_register_short_password(client):
    response = client.post("/auth/register", json={"email": "a@example.com", "password": "123"})
    assert response.status_code == 422


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "sam@example.com", "password": "password123"})
    response = client.post(
        "/auth/login", data={"username": "sam@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_protected_route_needs_valid_token(client):
    assert client.get("/auth/me").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/auth/me", headers=bad).status_code == 401
