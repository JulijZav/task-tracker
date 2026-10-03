from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)

def test_create_task():
    response = client.post("/tasks/", json={"title": "Test task"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["completed"] is False

def test_get_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_task():
    create = client.post("/tasks/", json={"title": "Another task"})
    task_id = create.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Another task"

def test_update_task():
    create = client.post("/tasks/", json={"title": "Update me"})
    task_id = create.json()["id"]
    response = client.put(f"/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True

def test_delete_task():
    create = client.post("/tasks/", json={"title": "Delete me"})
    task_id = create.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204


def test_get_nonexistent_task():
    response = client.get("/tasks/99999")
    assert response.status_code == 404