from fastapi.testclient import TestClient
from tests.conftest import client, auth_headers
from uuid import uuid4


def make_unique_todo(title_prefix: str = "Test Todo", **overrides) -> dict:
    data = {
        "title": f"{title_prefix} {uuid4().hex[:8]}",
        "description": "Some description",
        "done": False,
        # "owner_id": 1,  # décommente si ton API l’exige au POST
    }
    data.update(overrides)
    return data


def test_create_todo_success(client: TestClient, auth_headers: dict):
    TEST_TODO = make_unique_todo()
    
    response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    #assert data["title"] == TEST_TODO["title"]
    #assert data["description"] == TEST_TODO["description"]
    #assert data["done"] == TEST_TODO["done"]
    #assert "owner_id" in data

def test_create_todo_duplicate_title(client: TestClient, auth_headers: dict):
    TEST_TODO = make_unique_todo()
    
    client.post("/todos", json=TEST_TODO, headers=auth_headers)
    # Try to create again with same title
    response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    assert response.status_code == 400
    #assert "Todo with this title already exists" in response.json()["detail"]

def test_create_todo_unauthenticated(client: TestClient):
    TEST_TODO = make_unique_todo()
    
    response = client.post("/todos", json=TEST_TODO)
    assert response.status_code == 401

#def test_get_todos_empty(client: TestClient, auth_headers: dict):
# Ensure no todos exist    
  #  response = client.get("/todos", headers=auth_headers)
  #  assert response.status_code == 200
  #  assert response.json() == []

def test_get_todos_with_data(client: TestClient, auth_headers: dict):
    TEST_TODO = make_unique_todo()
    create_response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    
    # Get all todos
    response = client.get("/todos", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_get_single_todo(client: TestClient, auth_headers: dict):
    TEST_TODO = make_unique_todo()
    create_response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Get the todo
    response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200
    #data = response.json()
    #assert data["id"] == todo_id
    #assert data["title"] == TEST_TODO["title"]

def test_get_nonexistent_todo(client: TestClient, auth_headers: dict):
    response = client.get("/todos/9999", headers=auth_headers)
    assert response.status_code == 404
   # assert "Todo not found" in response.json()["detail"]

def test_update_todo(client: TestClient, auth_headers: dict):
    # Create a todo first
    TEST_TODO = make_unique_todo()
    UPDATED_TODO = {
        "title": "Updated Todo Title",
        "description": "Updated description",
        "done": True
    }
    
    create_response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Update the todo
    response = client.put(
        f"/todos/{todo_id}",
        json=UPDATED_TODO,
        headers=auth_headers
    )
    assert response.status_code == 200
    #data = response.json()
    #assert data["title"] == UPDATED_TODO["title"]
    #assert data["description"] == UPDATED_TODO["description"]
    #assert data["done"] == UPDATED_TODO["done"]

def test_partial_update_todo(client: TestClient, auth_headers: dict):
    TEST_TODO = make_unique_todo(done=False)
    create_response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Partial update - only change done status
    partial_update = {"done": True}
    response = client.put(
        f"/todos/{todo_id}",
        json=partial_update,
        headers=auth_headers
    )
    assert response.status_code == 200
    #data = response.json()
    #assert data["title"] == TEST_TODO["title"]  # unchanged
    #assert data["done"] is True  # changed

def test_update_nonexistent_todo(client: TestClient, auth_headers: dict):
    UPDATED_TODO = {
        "title": "Updated Todo Title",
        "description": "Updated description",
        "done": True
    }
    response = client.put(
        "/todos/9999",
        json=UPDATED_TODO,
        headers=auth_headers
    )
    assert response.status_code == 404
    #assert "Todo not found" in response.json()["detail"]

def test_delete_todo(client: TestClient, auth_headers: dict):
    TEST_TODO = make_unique_todo()
    # Create a todo first
    create_response = client.post("/todos", json=TEST_TODO, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Delete the todo
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200
    assert f"Todo {todo_id} deleted successfully" in response.json()["message"]
    
    # Verify it's gone
    get_response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_nonexistent_todo(client: TestClient, auth_headers: dict):
    response = client.delete("/todos/9999", headers=auth_headers)
    assert response.status_code == 404
   # assert "Todo not found" in response.json()["detail"]