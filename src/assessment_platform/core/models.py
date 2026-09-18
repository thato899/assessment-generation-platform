"""Stable, framework-independent concepts shared by assessment engines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
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

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _required_text(self.identifier, "part identifier"))
        object.__setattr__(self, "prompt", _required_text(self.prompt, "prompt"))
        if isinstance(self.marks, bool) or not isinstance(self.marks, int) or self.marks < 1:
            raise ValueError("marks must be a positive integer")


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
