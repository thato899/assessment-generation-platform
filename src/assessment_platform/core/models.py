"""Stable, framework-independent concepts shared by assessment engines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import Any


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


class Difficulty(StrEnum):
    INTRODUCTORY = "introductory"
    MODERATE = "moderate"
    ADVANCED = "advanced"


class AssessmentType(StrEnum):
    QUESTION = "question"
    QUIZ = "quiz"
    PRACTICE_SET = "practice_set"
    WORKSHEET = "worksheet"
    HOMEWORK = "homework"
    TEST = "test"
    DIAGNOSTIC = "diagnostic"
    EXAMINATION = "examination"


class ResponseKind(StrEnum):
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    NUMERIC = "numeric"
    CALCULATION = "calculation"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    EQUATION = "equation"
    DRAWING = "drawing"
    GRAPH = "graph"
    TABLE = "table"


class ExpectedAnswerKind(StrEnum):
    TEXT = "text"
    NUMERIC = "numeric"
    CHOICE = "choice"
    CALCULATION = "calculation"
    EQUATION = "equation"


class MarkingStatus(StrEnum):
    UNMARKED = "unmarked"
    AUTO_MARKED = "auto_marked"
    REQUIRES_REVIEW = "requires_review"
    MANUALLY_MARKED = "manually_marked"


@dataclass(frozen=True, slots=True)
class GenerationSeed:
    """A portable non-negative seed for reproducible generation."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise ValueError("generation seed must be an integer")
        if not 0 <= self.value <= 2**63 - 1:
            raise ValueError("generation seed must be between 0 and 2**63 - 1")


@dataclass(frozen=True, slots=True)
class Subject:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _required_text(self.value, "subject"))


@dataclass(frozen=True, slots=True)
class Topic:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _required_text(self.value, "topic"))


@dataclass(frozen=True, slots=True)
class Grade:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise ValueError("grade must be an integer")
        if not 1 <= self.value <= 12:
            raise ValueError("grade must be between 1 and 12")


@dataclass(frozen=True, slots=True)
class CurriculumReference:
    curriculum: str
    phase: str | None = None
    grade: Grade | None = None
    subject: Subject | None = None
    topic: Topic | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "curriculum", _required_text(self.curriculum, "curriculum"))
        if self.phase is not None:
            object.__setattr__(self, "phase", _required_text(self.phase, "phase"))


@dataclass(frozen=True, slots=True)
class QuestionPartId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _required_text(self.value, "question part ID"))


@dataclass(frozen=True, slots=True)
class ResponseSpecification:
    kind: ResponseKind
    suggested_line_count: int = 0
    expects_working: bool = False
    expects_final_answer: bool = False
    expects_units: bool = False
    required_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ResponseKind):
            raise ValueError("response kind must be supported")
        if isinstance(self.suggested_line_count, bool) or self.suggested_line_count < 0:
            raise ValueError("suggested line count must be a non-negative integer")
        fields = tuple(
            _required_text(field_name, "required field") for field_name in self.required_fields
        )
        if len(fields) != len(set(fields)):
            raise ValueError("required response fields must be unique")
        object.__setattr__(self, "required_fields", fields)


AnswerValue = str | float | tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExpectedAnswer:
    kind: ExpectedAnswerKind
    value: AnswerValue
    unit: str | None = None
    tolerance: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ExpectedAnswerKind):
            raise ValueError("expected answer kind must be supported")
        if isinstance(self.value, float) and not isfinite(self.value):
            raise ValueError("numeric expected answers must be finite")
        if self.tolerance is not None:
            if not isfinite(self.tolerance) or self.tolerance < 0:
                raise ValueError("answer tolerance must be finite and non-negative")
        if self.unit is not None:
            object.__setattr__(self, "unit", _required_text(self.unit, "answer unit"))


@dataclass(frozen=True, slots=True)
class MarkingCriterion:
    identifier: str
    description: str
    marks: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _required_text(self.identifier, "criterion ID"))
        object.__setattr__(
            self, "description", _required_text(self.description, "criterion description")
        )
        if isinstance(self.marks, bool) or not isinstance(self.marks, int) or self.marks < 1:
            raise ValueError("criterion marks must be a positive integer")


@dataclass(frozen=True, slots=True)
class MarkingScheme:
    maximum_marks: int
    criteria: tuple[MarkingCriterion, ...]

    def __post_init__(self) -> None:
        if isinstance(self.maximum_marks, bool) or not isinstance(self.maximum_marks, int):
            raise ValueError("maximum marks must be an integer")
        if self.maximum_marks < 1 or not self.criteria:
            raise ValueError("marking scheme must have positive maximum marks and criteria")
        identifiers = tuple(criterion.identifier for criterion in self.criteria)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("marking criterion IDs must be unique")
        if sum(criterion.marks for criterion in self.criteria) != self.maximum_marks:
            raise ValueError("criterion marks must equal maximum marks")


@dataclass(frozen=True, slots=True)
class LearnerResponse:
    question_part_id: QuestionPartId
    value: AnswerValue


@dataclass(frozen=True, slots=True)
class LearnerSubmission:
    responses: tuple[LearnerResponse, ...]

    def __post_init__(self) -> None:
        ids = tuple(response.question_part_id for response in self.responses)
        if len(ids) != len(set(ids)):
            raise ValueError("learner responses must have unique question part IDs")

    def validate_against(self, assessment: Assessment) -> ValidationResult:
        valid_ids = {
            part.identifier for question in assessment.questions for part in question.parts
        }
        errors = tuple(
            f"unknown question part ID: {response.question_part_id.value}"
            for response in self.responses
            if response.question_part_id.value not in valid_ids
        )
        return ValidationResult(not errors, errors)


@dataclass(frozen=True, slots=True)
class CriterionResult:
    criterion_id: str
    marks_awarded: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "criterion_id", _required_text(self.criterion_id, "criterion ID"))
        if not isfinite(self.marks_awarded) or self.marks_awarded < 0:
            raise ValueError("awarded criterion marks must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class MarkingResult:
    question_part_id: QuestionPartId
    marks_awarded: float
    maximum_marks: int
    status: MarkingStatus
    criterion_results: tuple[CriterionResult, ...] = ()
    feedback: str | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.marks_awarded) or self.marks_awarded < 0:
            raise ValueError("awarded marks must be finite and non-negative")
        if self.maximum_marks < 1 or self.marks_awarded > self.maximum_marks:
            raise ValueError("awarded marks must not exceed maximum marks")
        if not isinstance(self.status, MarkingStatus):
            raise ValueError("marking status must be supported")
        identifiers = tuple(result.criterion_id for result in self.criterion_results)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("criterion result IDs must be unique")
        if sum(result.marks_awarded for result in self.criterion_results) > self.marks_awarded:
            raise ValueError("criterion results cannot exceed total marks awarded")


@dataclass(frozen=True, slots=True)
class MemoEntry:
    question_part_id: QuestionPartId
    expected_answer: ExpectedAnswer
    marking_scheme: MarkingScheme
    worked_solution: str | None = None

    def __post_init__(self) -> None:
        if self.worked_solution is not None:
            object.__setattr__(
                self, "worked_solution", _required_text(self.worked_solution, "worked solution")
            )


@dataclass(frozen=True, slots=True)
class AssessmentRequest:
    curriculum: str
    subject: Subject
    grade: Grade
    topic: Topic
    assessment_type: AssessmentType
    question_count: int
    difficulty: Difficulty
    include_visuals: bool = True
    seed: GenerationSeed | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "curriculum", _required_text(self.curriculum, "curriculum"))
        if isinstance(self.question_count, bool) or not isinstance(self.question_count, int):
            raise ValueError("question_count must be an integer")
        if not 1 <= self.question_count <= 100:
            raise ValueError("question_count must be between 1 and 100")
        if not isinstance(self.include_visuals, bool):
            raise ValueError("include_visuals must be a boolean")


@dataclass(frozen=True, slots=True)
class Scenario:
    identifier: str
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _required_text(self.identifier, "scenario identifier")
        )
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


@dataclass(frozen=True, slots=True)
class QuestionPart:
    identifier: str
    prompt: str
    marks: int
    response_specification: ResponseSpecification | None = None
    expected_answer: ExpectedAnswer | None = None
    marking_scheme: MarkingScheme | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _required_text(self.identifier, "part identifier"))
        object.__setattr__(self, "prompt", _required_text(self.prompt, "prompt"))
        if isinstance(self.marks, bool) or not isinstance(self.marks, int) or self.marks < 1:
            raise ValueError("marks must be a positive integer")
        if (
            self.response_specification is None
            or self.expected_answer is None
            or self.marking_scheme is None
        ):
            raise ValueError(
                "assessable question parts need response, answer, and marking definitions"
            )
        if self.marking_scheme.maximum_marks != self.marks:
            raise ValueError("question part marks must equal marking scheme maximum")


@dataclass(frozen=True, slots=True)
class Solution:
    answer: Any
    explanation: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "explanation", _required_text(self.explanation, "explanation"))


@dataclass(frozen=True, slots=True)
class MarkingRubric:
    criteria: tuple[str, ...]

    def __post_init__(self) -> None:
        criteria = tuple(_required_text(item, "rubric criterion") for item in self.criteria)
        if not criteria:
            raise ValueError("rubric must contain at least one criterion")
        object.__setattr__(self, "criteria", criteria)


@dataclass(frozen=True, slots=True)
class Question:
    identifier: str
    prompt: str
    parts: tuple[QuestionPart, ...]
    scenario: Scenario | None = None
    solution: Solution | None = None
    rubric: MarkingRubric | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _required_text(self.identifier, "question identifier")
        )
        object.__setattr__(self, "prompt", _required_text(self.prompt, "prompt"))
        if not self.parts:
            raise ValueError("question must contain at least one part")


@dataclass(frozen=True, slots=True)
class Assessment:
    identifier: str
    assessment_type: AssessmentType
    curriculum: CurriculumReference
    questions: tuple[Question, ...]
    seed: GenerationSeed | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _required_text(self.identifier, "assessment identifier")
        )
        if not self.questions:
            raise ValueError("assessment must contain at least one question")
        identifiers = [part.identifier for question in self.questions for part in question.parts]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("question part IDs must be unique within an assessment")

    @property
    def memorandum(self) -> tuple[MemoEntry, ...]:
        entries: list[MemoEntry] = []
        for question in self.questions:
            for part in question.parts:
                assert part.expected_answer is not None
                assert part.marking_scheme is not None
                entries.append(
                    MemoEntry(
                        QuestionPartId(part.identifier), part.expected_answer, part.marking_scheme
                    )
                )
        return tuple(entries)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        errors = tuple(_required_text(error, "validation error") for error in self.errors)
        if self.valid and errors:
            raise ValueError("a valid result cannot contain errors")
        if not self.valid and not errors:
            raise ValueError("an invalid result must contain errors")
        object.__setattr__(self, "errors", errors)
