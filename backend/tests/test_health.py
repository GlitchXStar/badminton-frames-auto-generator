"""Tests for health endpoint."""


def test_health_endpoint(client):
    """Test that health endpoint returns expected structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "database" in data
    assert "ffmpeg" in data
    assert "ytdlp" in data


def test_swagger_docs(client):
    """Test that Swagger docs are available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json(client):
    """Test that OpenAPI JSON is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "Badminton Dataset Generator" in data.get("info", {}).get("title", "")
