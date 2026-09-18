import pytest

from assessment_platform.core import (
    Assessment,
    AssessmentType,
    CriterionResult,
    CurriculumReference,
    ExpectedAnswer,
    ExpectedAnswerKind,
    LearnerResponse,
    LearnerSubmission,
    MarkingCriterion,
    MarkingResult,
    MarkingScheme,
    MarkingStatus,
    Question,
    QuestionPart,
    QuestionPartId,
    ResponseKind,
    ResponseSpecification,
)


def part(identifier: str = "2.1", marks: int = 2) -> QuestionPart:
    return QuestionPart(
        identifier,
        "Calculate the answer.",
        marks,
        ResponseSpecification(
            ResponseKind.CALCULATION, suggested_line_count=4,
            expects_working=True, expects_final_answer=True, expects_units=True,
        ),
        ExpectedAnswer(ExpectedAnswerKind.NUMERIC, 9.81, "m/s²", 0.01),
        MarkingScheme(marks, (MarkingCriterion("method", "Correct method", marks),)),
    )


def assessment() -> Assessment:
    question = Question("2", "Mechanics", (part("2.1"), part("2.2", 3)))
    return Assessment("assessment-1", AssessmentType.TEST, CurriculumReference("CAPS"), (question,))


def test_question_part_carries_typed_response_answer_and_consistent_scheme() -> None:
    question_part = part()
    assert question_part.response_specification.kind is ResponseKind.CALCULATION
    assert question_part.expected_answer.kind is ExpectedAnswerKind.NUMERIC
    assert question_part.marking_scheme.maximum_marks == question_part.marks


def test_marking_scheme_rejects_duplicate_criteria_and_inconsistent_totals() -> None:
    criterion = MarkingCriterion("method", "Correct method", 1)
    with pytest.raises(ValueError, match="unique"):
        MarkingScheme(2, (criterion, criterion))
    with pytest.raises(ValueError, match="equal"):
        MarkingScheme(2, (MarkingCriterion("method", "Correct method", 1),))


def test_expected_answer_rejects_invalid_numeric_tolerance() -> None:
    with pytest.raises(ValueError):
        ExpectedAnswer(ExpectedAnswerKind.NUMERIC, float("nan"))
    with pytest.raises(ValueError):
        ExpectedAnswer(ExpectedAnswerKind.NUMERIC, 1.0, tolerance=-0.1)


def test_assessment_rejects_duplicate_ids_independent_of_display_order() -> None:
    question = Question("2", "Mechanics", (part("2.1"), part("2.1")))
    with pytest.raises(ValueError, match="unique"):
        Assessment("assessment-1", AssessmentType.TEST, CurriculumReference("CAPS"), (question,))


def test_memo_is_derived_from_question_part_ids() -> None:
    memo = assessment().memorandum
    assert [entry.question_part_id.value for entry in memo] == ["2.1", "2.2"]
    assert memo[1].marking_scheme.maximum_marks == 3


def test_learner_responses_are_separate_and_validate_ids() -> None:
    submission = LearnerSubmission((LearnerResponse(QuestionPartId("2.1"), 9.8),))
    assert submission.validate_against(assessment()).valid
    unknown = LearnerSubmission((LearnerResponse(QuestionPartId("9.9"), "answer"),))
    result = unknown.validate_against(assessment())
    assert not result.valid
    assert "9.9" in result.errors[0]


def test_marking_result_supports_partial_credit_but_not_over_award() -> None:
    result = MarkingResult(
        QuestionPartId("2.1"), 1.0, 2, MarkingStatus.MANUALLY_MARKED,
        (CriterionResult("method", 1.0),), "Correct method; calculation incomplete",
    )
    assert result.marks_awarded == 1.0
    with pytest.raises(ValueError, match="exceed"):
        MarkingResult(QuestionPartId("2.1"), 3.0, 2, MarkingStatus.AUTO_MARKED)


def test_response_specification_rejects_duplicate_fields_and_negative_space() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ResponseSpecification(ResponseKind.TABLE, suggested_line_count=-1)
    with pytest.raises(ValueError, match="unique"):
        ResponseSpecification(ResponseKind.TABLE, required_fields=("rows", "rows"))
