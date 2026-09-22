"""Tests for project CRUD operations."""


def test_create_project(client):
    """Test creating a new project."""
    response = client.post("/api/projects", json={
        "name": "Test Batch",
        "target_images": 500,
        "description": "Test project",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Batch"
    assert data["target_images"] == 500
    assert data["status"] == "active"
    assert "id" in data
    assert "stats" in data


def test_create_duplicate_project(client):
    """Test that duplicate project names are rejected."""
    client.post("/api/projects", json={"name": "Unique Name", "target_images": 100})
    response = client.post("/api/projects", json={"name": "Unique Name", "target_images": 200})
    assert response.status_code == 409


def test_list_projects(client):
    """Test listing projects."""
    client.post("/api/projects", json={"name": "Project A", "target_images": 100})
    client.post("/api/projects", json={"name": "Project B", "target_images": 200})

    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["projects"]) == 2


def test_get_project(client):
    """Test getting a single project."""
    create_resp = client.post("/api/projects", json={"name": "Get Me", "target_images": 300})
    project_id = create_resp.json()["id"]

    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Me"


def test_get_nonexistent_project(client):
    """Test getting a project that doesn't exist."""
    response = client.get("/api/projects/9999")
    assert response.status_code == 404


def test_project_validation(client):
    """Test validation constraints."""
    # Empty name
    response = client.post("/api/projects", json={"name": "", "target_images": 100})
    assert response.status_code == 422

    # Target too high
    response = client.post("/api/projects", json={"name": "Valid", "target_images": 99999})
    assert response.status_code == 422
