from fastapi.testclient import TestClient

from assessment_platform.main import app

client = TestClient(app)

VALID_REQUEST = {
    "curriculum": "CAPS",
    "subject": "physical-sciences",
    "grade": 12,
    "topic": "vertical-projectile-motion-1d",
    "assessment_type": "quiz",
    "question_count": 5,
    "difficulty": "moderate",
    "include_visuals": True,
    "seed": 18472,
}


def test_versioned_generation_contract_is_explicitly_unavailable() -> None:
    response = client.post("/api/v1/assessments/generate", json=VALID_REQUEST)
    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "generation_engine_unavailable",
            "message": "No assessment generation engine is available yet.",
            "details": [],
        }
    }


def test_health_remains_versioned_and_available() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_invalid_request_uses_consistent_safe_error_shape() -> None:
    payload = {**VALID_REQUEST, "curriculum": "OTHER", "seed": -1, "question_count": 0}
    response = client.post("/api/v1/assessments/generate", json=payload)
    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["message"] == "The request did not satisfy the v1 API contract."
    assert body["error"]["details"]
    assert "Traceback" not in response.text
    assert "assessment_platform" not in response.text


def test_extra_request_fields_are_rejected() -> None:
    response = client.post(
        "/api/v1/assessments/generate", json={**VALID_REQUEST, "client": "eduquest"}
    )
    assert response.status_code == 422


def test_supported_topics_and_assessment_types_are_contract_values() -> None:
    for topic in ("momentum-and-impulse", "vertical-projectile-motion-1d", "work-energy-and-power"):
        response = client.post(
            "/api/v1/assessments/generate", json={**VALID_REQUEST, "topic": topic}
        )
        assert response.status_code == 503
    assessment_types = (
        "question", "quiz", "practice_set", "worksheet", "homework", "test", "diagnostic",
        "examination",
    )
    for assessment_type in assessment_types:
        response = client.post(
            "/api/v1/assessments/generate",
            json={**VALID_REQUEST, "assessment_type": assessment_type},
        )
        assert response.status_code == 503


def test_domain_mapping_reuses_stable_identifiers_without_fastapi_in_domain() -> None:
    from assessment_platform.api.v1 import AssessmentGenerationRequest

    domain_request = AssessmentGenerationRequest(**VALID_REQUEST).to_domain()
    assert domain_request.topic.value == "vertical-projectile-motion-1d"
    assert domain_request.seed.value == 18472


def test_openapi_documents_versioned_route_and_boundary_schemas() -> None:
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/assessments/generate"]["post"]
    assert "200" in operation["responses"]
    assert "503" in operation["responses"]
    assert "AssessmentGenerationRequest" in schema["components"]["schemas"]
    assert "AssessmentGenerationResponse" in schema["components"]["schemas"]
    assert "ErrorResponse" in schema["components"]["schemas"]


def test_learner_projection_schema_has_no_answer_or_memo_fields() -> None:
    from assessment_platform.api.v1 import LearnerQuestionPartDto

    fields = set(LearnerQuestionPartDto.model_fields)
    assert {"question_part_id", "prompt", "maximum_marks", "response_specification"} <= fields
    assert not {"expected_answer", "marking_scheme", "memo", "worked_solution"} & fields
