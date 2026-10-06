from fastapi.testclient import TestClient

from app.main import app


def test_health():
    # Lifespan is not entered here; the endpoint itself has no DB dependency.
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
