import pytest

from assessment_platform.core import (
    Assessment,
    AssessmentRequest,
    AssessmentType,
    CurriculumReference,
    Difficulty,
    ExpectedAnswer,
    ExpectedAnswerKind,
    GenerationProvenance,
    GenerationSeed,
    Grade,
    MarkingCriterion,
    MarkingRubric,
    MarkingScheme,
    Question,
    QuestionPart,
    ResponseKind,
    ResponseSpecification,
    Scenario,
    Solution,
    Subject,
    Topic,
    ValidationResult,
    VisualReference,
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
    part = QuestionPart(
        "a", "Calculate", 2,
        ResponseSpecification(ResponseKind.NUMERIC),
        ExpectedAnswer(ExpectedAnswerKind.NUMERIC, 4.0, "m/s"),
        MarkingScheme(2, (MarkingCriterion("method", "Use the method", 2),)),
    )
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


def test_visual_references_and_provenance_are_immutable_and_validated() -> None:
    visual = VisualReference("diagram", "image/svg+xml", "<svg />", 640, 480)
    provenance = GenerationProvenance("generator", "1", GenerationSeed(7), ("template-a",))
    question_part = QuestionPart(
        "p",
        "State the answer",
        1,
        ResponseSpecification(ResponseKind.SHORT_TEXT),
        ExpectedAnswer(ExpectedAnswerKind.TEXT, "downward"),
        MarkingScheme(1, (MarkingCriterion("answer", "States the answer", 1),)),
    )
    question = Question(
        "q", "A question", (question_part,), visuals=[visual], provenance=provenance
    )
    assert question.visuals == (visual,)
    assert question.provenance == provenance
    with pytest.raises(ValueError, match="positive integer"):
        VisualReference("diagram", "image/svg+xml", "<svg />", 0, 480)
    with pytest.raises(ValueError, match="unique"):
        GenerationProvenance("generator", "1", template_ids=("a", "a"))
    with pytest.raises(ValueError, match="visual IDs"):
        Question("q", "A question", (question_part,), visuals=(visual, visual))


def test_validation_result_requires_consistent_errors() -> None:
    with pytest.raises(ValueError):
        ValidationResult(True, ("error",))
    with pytest.raises(ValueError):
        ValidationResult(False)
