import pytest

from assessment_platform.core import (
    Assessment,
    AssessmentRequest,
    AssessmentType,
    CurriculumReference,
    Difficulty,
    GenerationSeed,
    Grade,
    MarkingRubric,
    Question,
    QuestionPart,
    Scenario,
    Solution,
    Subject,
    Topic,
    ValidationResult,
)


def test_request_and_value_objects_construct_and_normalize_text() -> None:
    request = AssessmentRequest(
        curriculum=" CAPS ", subject=Subject(" physical-sciences "), grade=Grade(12),
        topic=Topic(" mechanics "), assessment_type=AssessmentType.QUIZ,
        question_count=1, difficulty=Difficulty.MODERATE, seed=GenerationSeed(0),
    )
    assert request.curriculum == "CAPS"
    assert request.subject.value == "physical-sciences"
    assert request.seed == GenerationSeed(0)


@pytest.mark.parametrize("value", [-1, 2**63, True, "1"])
def test_seed_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError):
        GenerationSeed(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, 13, True, "12"])
def test_grade_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError):
        Grade(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["subject", "topic", "curriculum"])
def test_required_text_rejects_blank_values(field: str) -> None:
    constructor = {"subject": Subject, "topic": Topic, "curriculum": CurriculumReference}[field]
    with pytest.raises(ValueError):
        constructor("   ")


def test_scenario_data_is_snapshot_and_read_only() -> None:
    source = {"height_m": 10}
    scenario = Scenario("scenario-1", source)
    source["height_m"] = 20
    assert scenario.data["height_m"] == 10
    with pytest.raises(TypeError):
        scenario.data["height_m"] = 20  # type: ignore[index]


def test_assessment_requires_questions_and_question_requires_parts() -> None:
    curriculum = CurriculumReference("CAPS", grade=Grade(12), subject=Subject("physics"))
    with pytest.raises(ValueError):
        Assessment("a", AssessmentType.QUIZ, curriculum, ())
    with pytest.raises(ValueError):
        Question("q", "Prompt", ())


def test_nested_models_and_validation_result() -> None:
    part = QuestionPart("a", "Calculate", 2)
    question = Question(
        "q", "A question", (part,), Scenario("s"), Solution(4, "Substitute values"),
        MarkingRubric(("method",)),
    )
    assessment = Assessment(
        "a", AssessmentType.QUESTION, CurriculumReference("CAPS"), (question,), GenerationSeed(42)
    )
    assert assessment.questions[0].parts[0].marks == 2
    assert ValidationResult(True).errors == ()
    assert ValidationResult(False, ("invalid scenario",)).valid is False


def test_validation_result_requires_consistent_errors() -> None:
    with pytest.raises(ValueError):
        ValidationResult(True, ("error",))
    with pytest.raises(ValueError):
        ValidationResult(False)
