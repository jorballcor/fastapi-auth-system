from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_and_users_me():
    # 1. Login
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # 2. Accéder à /users/me
    response2 = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response2.status_code == 200
    assert response2.json()["username"] == "testuser"

    # 2. Accéder à /users
    response2 = client.post("/users", headers={
        "Authorization": f"Bearer {token}"
    }, json={
    "username": "mocktestuser",
    "email": "mocktest@example.com",
    "password": "Mocktestpwd$123"
    })
    assert response2.status_code == 200
    assert response2.json()["username"] == "mocktestuser"