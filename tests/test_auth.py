from fastapi.testclient import TestClient
from tests.testing_db import client
from tests.testing_db import FIRST_SUPERUSER_USERNAME, FIRST_SUPERUSER_PASSWORD   


def test_users_me_protected_and_success(client: TestClient):
    # 1. Sans token → 401 Unauthorized
    response = client.get("/users/me")
    assert response.status_code == 401

    # 2. Login pour obtenir un token
    login_response = client.post("/login", data={
        "username": FIRST_SUPERUSER_USERNAME,
        "password": FIRST_SUPERUSER_PASSWORD
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Appel protégé avec token → 200 OK
    response = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "username" in response.json()
    
     # 4. Appel protégé avec token → 401 Unauthorized
    response = client.get("/users/me")
    assert response.status_code == 401


def test_create_user(client: TestClient):
    # Login pour token
    login = client.post("/login", data={
        "username": FIRST_SUPERUSER_USERNAME,
        "password": FIRST_SUPERUSER_PASSWORD
    })
    token = login.json()["access_token"]

    # Création d’un utilisateur
    response = client.post("/users", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Newpass123$"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    #assert "id" in data


def test_login_fail_wrong_password(client: TestClient):
    response = client.post("/login", data={
        "username": FIRST_SUPERUSER_USERNAME,
        "password": "wrongpass"
    })
    assert response.status_code == 401
