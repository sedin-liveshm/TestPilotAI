from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that GET /health returns HTTP 200 and expected payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "service": "testpilot-backend",
    }


def test_health_db_endpoint_structure():
    """Test that GET /health/db returns structured response without leaking secrets."""
    response = client.get("/health/db")
    # Response code can be 200 (if connected) or 503 (if dummy/unreachable connection)
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data
    # Ensure sensitive credentials are never leaked
    response_text = response.text.lower()
    assert "supabase_key" not in response_text
    assert "secret" not in response_text
