from fastapi.testclient import TestClient

from assessment_platform.main import app


def test_health() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}

def test_generation_schema_rejects_invalid_grade() -> None:
    response = TestClient(app).post("/api/v1/assessments/generate", json={"grade": 9})
    assert response.status_code == 422
