from fastapi.testclient import TestClient

from assessment_platform.application import AssessmentGenerationService
from assessment_platform.core import (
    AssessmentRequest,
    AssessmentType,
    Difficulty,
    GenerationSeed,
    Grade,
    Subject,
    Topic,
)
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

NEWTON_REQUEST = {
    **VALID_REQUEST,
    "grade": 11,
    "topic": "newtons-laws",
    "difficulty": "moderate",
    "include_visuals": True,
    "seed": 0,
}

WORK_ENERGY_REQUEST = {
    **VALID_REQUEST,
    "topic": "work-energy-and-power",
    "seed": 0,
}


def _recursive_keys(value):
    if isinstance(value, dict):
        yield from value.keys()
        for child in value.values():
            yield from _recursive_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _recursive_keys(child)


def test_exact_grade_topic_routing_matrix() -> None:
    cases = (
        (11, "newtons-laws", 200, None),
        (12, "newtons-laws", 422, "unsupported_topic"),
        (12, "vertical-projectile-motion-1d", 200, None),
        (12, "momentum-and-impulse", 200, None),
        (12, "work-energy-and-power", 200, None),
        (11, "work-energy-and-power", 422, "unsupported_topic"),
        (10, "work-energy-and-power", 422, "unsupported_grade"),
        (11, "vertical-projectile-motion-1d", 422, "unsupported_topic"),
        (11, "momentum-and-impulse", 422, "unsupported_topic"),
        (10, "newtons-laws", 422, "unsupported_grade"),
    )
    for grade, topic, status, code in cases:
        response = client.post(
            "/api/v1/assessments/generate",
            json={**NEWTON_REQUEST, "grade": grade, "topic": topic},
        )
        assert response.status_code == status
        if code is None:
            assert response.json()["questions"]
        else:
            assert response.json()["error"]["code"] == code
            assert "questions" not in response.json()


def test_work_energy_conceptual_generation_is_deterministic_and_token_safe() -> None:
    first = client.post("/api/v1/assessments/generate", json=WORK_ENERGY_REQUEST)
    second = client.post("/api/v1/assessments/generate", json=WORK_ENERGY_REQUEST)

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert body["api_version"] == "v1"
    assert body["grade"] == 12
    assert body["topic"] == "work-energy-and-power"
    assert body["effective_seed"] == 0
    assert body["questions"][0]["question_id"].startswith("wep-conceptual-v1-")
    assert body["visuals"] == []
    forbidden = {
        "expected_answer",
        "marking_scheme",
        "rubric",
        "criteria",
        "memo",
        "memorandum",
        "solution",
        "solver",
        "scenario",
        "provenance",
        "concepts",
        "correct_choice",
        "worked_solution",
    }
    assert not forbidden & set(_recursive_keys(body))

    internal = AssessmentGenerationService().generate(
        AssessmentRequest(
            "CAPS",
            Subject("physical-sciences"),
            Grade(12),
            Topic("work-energy-and-power"),
            AssessmentType.QUESTION,
            1,
            Difficulty.MODERATE,
            True,
            GenerationSeed(0),
        )
    )
    tokens = internal.questions[0].parts[0].expected_answer.value
    assert all(token not in first.text for token in tokens)
    assert internal.memorandum


def test_work_energy_calculation_generation_is_learner_safe_and_visual_capable() -> None:
    payload = {**WORK_ENERGY_REQUEST, "seed": 1, "include_visuals": True}
    response = client.post("/api/v1/assessments/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["questions"][0]["question_id"].startswith("wep-question-v1-")
    assert body["questions"][0]["parts"][0]["response_specification"]["kind"] == "calculation"
    assert body["visuals"]
    assert not {"expected_answer", "marking_scheme", "scenario", "provenance"} & set(
        _recursive_keys(body)
    )

    without_visuals = client.post(
        "/api/v1/assessments/generate",
        json={**payload, "include_visuals": False},
    )
    assert without_visuals.status_code == 200
    assert without_visuals.json()["visuals"] == []


def test_work_energy_average_power_may_legitimately_have_no_visual() -> None:
    response = client.post(
        "/api/v1/assessments/generate",
        json={**WORK_ENERGY_REQUEST, "seed": 19, "include_visuals": True},
    )

    assert response.status_code == 200
    assert response.json()["questions"][0]["question_id"].startswith("wep-question-v1-")
    assert response.json()["visuals"] == []


def test_newton_generation_is_canonical_deterministic_and_learner_safe() -> None:
    first = client.post("/api/v1/assessments/generate", json=NEWTON_REQUEST)
    second = client.post("/api/v1/assessments/generate", json=NEWTON_REQUEST)

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert body["api_version"] == "v1"
    assert body["effective_seed"] == 0
    assert body["grade"] == 11
    assert body["topic"] == "newtons-laws"
    assert len(body["questions"]) == 1
    assert body["questions"][0]["parts"]
    assert body["visuals"]
    forbidden = {
        "expected_answer",
        "marking_scheme",
        "rubric",
        "criteria",
        "memo",
        "memorandum",
        "solution",
        "solver",
        "scenario",
        "provenance",
        "concepts",
        "correct_choice",
        "worked_solution",
    }

    def keys(value):
        if isinstance(value, dict):
            yield from value.keys()
            for child in value.values():
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    assert not forbidden & set(keys(body))
    assert "equal_magnitude" not in first.text
    assert "same_interaction" not in first.text


def test_newton_calculation_route_has_no_internal_answers_or_hidden_svg_values() -> None:
    payload = {**NEWTON_REQUEST, "seed": 1}
    response = client.post("/api/v1/assessments/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["questions"][0]["question_id"].startswith("newton-question-")
    assert "expected_answer" not in response.text
    assert "marking_scheme" not in response.text
    assert "solver" not in response.text.lower()
    assert all("?" in visual["content"] or "F" in visual["content"] for visual in body["visuals"])

    internal = AssessmentGenerationService().generate(
        AssessmentRequest(
            "CAPS",
            Subject("physical-sciences"),
            Grade(11),
            Topic("newtons-laws"),
            AssessmentType.QUESTION,
            1,
            Difficulty.MODERATE,
            True,
            GenerationSeed(1),
        )
    )
    answer = internal.questions[0].parts[0].expected_answer
    assert answer is not None
    assert str(answer.value) not in body["visuals"][0]["content"]


def test_newton_omitted_seed_and_visual_preference_are_stable() -> None:
    payload = {key: value for key, value in NEWTON_REQUEST.items() if key != "seed"}
    first = client.post("/api/v1/assessments/generate", json=payload)
    second = client.post("/api/v1/assessments/generate", json=payload)
    no_visuals = client.post(
        "/api/v1/assessments/generate", json={**payload, "include_visuals": False}
    )

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["effective_seed"] == 0
    assert no_visuals.json()["visuals"] == []


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
        ("grade", 11, "unsupported_topic"),
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
