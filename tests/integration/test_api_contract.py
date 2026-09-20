from fastapi.testclient import TestClient

from assessment_platform.main import app

client = TestClient(app)

VALID_REQUEST = {
    "curriculum": "CAPS",
    "subject": "physical-sciences",
    "grade": 12,
    "topic": "vertical-projectile-motion-1d",
    "assessment_type": "question",
    "question_count": 1,
    "difficulty": "moderate",
    "include_visuals": True,
    "seed": 18472,
}

MOMENTUM_REQUEST = {
    **VALID_REQUEST,
    "topic": "momentum-and-impulse",
    "seed": 7,
}


def test_momentum_topic_is_supported_and_learner_safe() -> None:
    response = client.post("/api/v1/assessments/generate", json=MOMENTUM_REQUEST)

    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "momentum-and-impulse"
    assert body["questions"]
    assert "expected_answer" not in response.text
    assert "marking_scheme" not in response.text


def test_momentum_requests_are_deterministic_and_visual_preference_is_honoured() -> None:
    first = client.post("/api/v1/assessments/generate", json=MOMENTUM_REQUEST)
    second = client.post("/api/v1/assessments/generate", json=MOMENTUM_REQUEST)
    without_visuals = client.post(
        "/api/v1/assessments/generate",
        json={**MOMENTUM_REQUEST, "seed": 9, "include_visuals": False},
    )

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert without_visuals.json()["visuals"] == []


def test_supported_generation_returns_a_learner_safe_v1_response() -> None:
    response = client.post("/api/v1/assessments/generate", json=VALID_REQUEST)

    assert response.status_code == 200
    body = response.json()
    assert body["api_version"] == "v1"
    assert body["effective_seed"] == 18472
    assert body["curriculum"] == "CAPS"
    assert body["subject"] == "physical-sciences"
    assert body["grade"] == 12
    assert body["topic"] == "vertical-projectile-motion-1d"
    assert body["assessment_type"] == "question"
    assert len(body["questions"]) == 1
    assert len(body["questions"][0]["parts"]) >= 2
    assert body["visuals"]


def test_identical_supported_requests_are_reproducible() -> None:
    first = client.post("/api/v1/assessments/generate", json=VALID_REQUEST)
    second = client.post("/api/v1/assessments/generate", json=VALID_REQUEST)

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_omitted_seed_uses_documented_deterministic_default() -> None:
    payload = {key: value for key, value in VALID_REQUEST.items() if key != "seed"}

    first = client.post("/api/v1/assessments/generate", json=payload)
    second = client.post("/api/v1/assessments/generate", json=payload)

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["effective_seed"] == 0


def test_visual_preference_is_honoured() -> None:
    response = client.post(
        "/api/v1/assessments/generate", json={**VALID_REQUEST, "include_visuals": False}
    )

    assert response.status_code == 200
    assert response.json()["visuals"] == []


def test_learner_projection_contains_no_answer_or_memo_data() -> None:
    response = client.post("/api/v1/assessments/generate", json=VALID_REQUEST)
    body = response.json()

    for forbidden in (
        "expected_answer",
        "marking_scheme",
        "memo",
        "worked_solution",
        "correct_choice",
    ):
        assert forbidden not in response.text
        assert forbidden not in body["questions"][0]
        assert all(forbidden not in part for part in body["questions"][0]["parts"])

    visual_content = body["visuals"][0]["content"]
    assert "t = " not in visual_content
    assert "v = " not in visual_content
    assert "g = " not in visual_content


def test_unsupported_configuration_returns_stable_safe_errors() -> None:
    cases = (
        ("curriculum", "OTHER", "unsupported_curriculum"),
        ("subject", "mathematics", "unsupported_subject"),
        ("grade", 11, "unsupported_grade"),
        ("assessment_type", "quiz", "unsupported_assessment_type"),
        ("assessment_type", "examination", "unsupported_assessment_type"),
        ("assessment_type", "diagnostic", "unsupported_assessment_type"),
        ("assessment_type", "test", "unsupported_assessment_type"),
        ("assessment_type", "homework", "unsupported_assessment_type"),
        ("assessment_type", "worksheet", "unsupported_assessment_type"),
        ("question_count", 2, "unsupported_question_count"),
    )
    for field, value, code in cases:
        response = client.post("/api/v1/assessments/generate", json={**VALID_REQUEST, field: value})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == code
        assert "Traceback" not in response.text
        assert "assessment_platform" not in response.text


def test_invalid_request_uses_consistent_safe_error_shape() -> None:
    payload = {**VALID_REQUEST, "seed": -1, "question_count": 0}

    response = client.post("/api/v1/assessments/generate", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert response.json()["error"]["details"]
    assert "Traceback" not in response.text
    assert "assessment_platform" not in response.text


def test_extra_request_fields_are_rejected() -> None:
    response = client.post(
        "/api/v1/assessments/generate", json={**VALID_REQUEST, "client": "eduquest"}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_unexpected_application_failures_are_sanitized(monkeypatch) -> None:
    from assessment_platform.api import v1

    class BrokenService:
        def generate(self, _request):
            raise RuntimeError("private implementation detail")

    monkeypatch.setattr(v1, "generation_service", BrokenService())
    isolated_client = TestClient(app, raise_server_exceptions=False)
    response = isolated_client.post("/api/v1/assessments/generate", json=VALID_REQUEST)

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "generation_failed",
            "message": "Assessment generation failed.",
            "details": [],
        }
    }
    assert "private implementation detail" not in response.text


def test_health_remains_versioned_and_available() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_domain_mapping_reuses_stable_identifiers_without_fastapi_in_domain() -> None:
    from assessment_platform.api.v1 import AssessmentGenerationRequest

    domain_request = AssessmentGenerationRequest(**VALID_REQUEST).to_domain()

    assert domain_request.topic.value == "vertical-projectile-motion-1d"
    assert domain_request.seed.value == 18472


def test_openapi_documents_the_supported_generation_path() -> None:
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/assessments/generate"]["post"]

    assert "200" in operation["responses"]
    assert "422" in operation["responses"]
    assert "503" not in operation["responses"]
    assert "AssessmentGenerationResponse" in schema["components"]["schemas"]
    assert "ErrorResponse" in schema["components"]["schemas"]


def test_learner_projection_schema_has_no_answer_or_memo_fields() -> None:
    from assessment_platform.api.v1 import LearnerQuestionPartDto

    fields = set(LearnerQuestionPartDto.model_fields)

    assert {"question_part_id", "prompt", "maximum_marks", "response_specification"} <= fields
    assert not {"expected_answer", "marking_scheme", "memo", "worked_solution"} & fields
