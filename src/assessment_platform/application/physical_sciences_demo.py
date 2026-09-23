"""Trusted end-to-end demonstration for the supported Physical Sciences routes.

This module deliberately keeps the teacher memorandum separate from the
learner projection. It is intended for local demonstrations and trusted
application callers, not for the learner-facing API boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from assessment_platform.application.assessment_generation import (
    AssessmentGenerationService,
)
from assessment_platform.core import (
    Assessment,
    AssessmentRequest,
    AssessmentType,
    Difficulty,
    GenerationSeed,
    Grade,
    MemoEntry,
    Subject,
    Topic,
)

VERTICAL_PROJECTILE_TOPIC_ID = "vertical-projectile-motion-1d"
MOMENTUM_TOPIC_ID = "momentum-and-impulse"
NEWTON_TOPIC_ID = "newtons-laws"
WORK_ENERGY_POWER_TOPIC_ID = "work-energy-and-power"
SUPPORTED_DEMO_TOPICS = (
    VERTICAL_PROJECTILE_TOPIC_ID,
    MOMENTUM_TOPIC_ID,
    NEWTON_TOPIC_ID,
    WORK_ENERGY_POWER_TOPIC_ID,
)


@dataclass(frozen=True, slots=True)
class PhysicalSciencesDemoRequest:
    """The small request contract used by the trusted demonstration path."""

    topic: str
    seed: int = 42
    difficulty: Difficulty = Difficulty.MODERATE
    include_visuals: bool = True

    def __post_init__(self) -> None:
        if self.topic not in SUPPORTED_DEMO_TOPICS:
            raise ValueError("topic is not supported by the Physical Sciences demo")
        GenerationSeed(self.seed)
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("difficulty must be a supported Difficulty")
        if not isinstance(self.include_visuals, bool):
            raise ValueError("include_visuals must be a boolean")

    @property
    def grade(self) -> int:
        return 11 if self.topic == NEWTON_TOPIC_ID else 12

    def to_domain(self) -> AssessmentRequest:
        return AssessmentRequest(
            curriculum="CAPS",
            subject=Subject("physical-sciences"),
            grade=Grade(self.grade),
            topic=Topic(self.topic),
            assessment_type=AssessmentType.QUESTION,
            question_count=1,
            difficulty=self.difficulty,
            include_visuals=self.include_visuals,
            seed=GenerationSeed(self.seed),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "curriculum": "CAPS",
            "subject": "physical-sciences",
            "grade": self.grade,
            "topic": self.topic,
            "assessment_type": "question",
            "question_count": 1,
            "difficulty": self.difficulty.value,
            "include_visuals": self.include_visuals,
            "seed": self.seed,
        }


def generate_demo(
    request: PhysicalSciencesDemoRequest,
    service: AssessmentGenerationService | None = None,
) -> dict[str, object]:
    """Generate one learner view and one trusted teacher memorandum.

    The returned mapping contains separate ``learner`` and ``teacher_memo``
    sections. The learner section is built from the same allowlisted fields as
    the v1 API and never contains expected answers, rubrics, scenarios,
    solutions, provenance, or solver data.
    """

    assessment = (service or AssessmentGenerationService()).generate(request.to_domain())
    return {
        "request": request.as_dict(),
        "effective_seed": assessment.seed.value if assessment.seed is not None else None,
        "learner": learner_projection(assessment),
        "teacher_memo": teacher_memo_projection(assessment),
    }


def learner_projection(assessment: Assessment) -> dict[str, object]:
    """Build a learner-safe projection without importing the web framework."""

    if not isinstance(assessment, Assessment) or len(assessment.questions) != 1:
        raise ValueError("demo requires an assessment containing exactly one question")
    question = assessment.questions[0]
    parts: list[dict[str, object]] = []
    for part in question.parts:
        specification = part.response_specification
        if specification is None:
            raise ValueError("generated question part is missing a response specification")
        parts.append(
            {
                "question_part_id": part.identifier,
                "prompt": part.prompt,
                "maximum_marks": part.marks,
                "response_specification": {
                    "kind": specification.kind.value,
                    "suggested_line_count": specification.suggested_line_count,
                    "expects_working": specification.expects_working,
                    "expects_final_answer": specification.expects_final_answer,
                    "expects_units": specification.expects_units,
                    "required_fields": specification.required_fields,
                },
            }
        )
    return {
        "assessment_id": assessment.identifier,
        "curriculum": assessment.curriculum.curriculum,
        "grade": assessment.curriculum.grade.value if assessment.curriculum.grade else None,
        "topic": assessment.curriculum.topic.value if assessment.curriculum.topic else None,
        "questions": [
            {
                "question_id": question.identifier,
                "prompt": question.prompt,
                "parts": parts,
            }
        ],
        "visuals": [
            {
                "asset_id": visual.identifier,
                "media_type": visual.media_type,
                "content": visual.content,
            }
            for visual in question.visuals
        ],
    }


def teacher_memo_projection(assessment: Assessment) -> list[dict[str, object]]:
    """Serialize canonical memorandum data for a trusted teacher-side caller."""

    return [_memo_entry(entry) for entry in assessment.memorandum]


def _memo_entry(entry: MemoEntry) -> dict[str, object]:
    expected = entry.expected_answer
    scheme = entry.marking_scheme
    return {
        "question_part_id": entry.question_part_id.value,
        "expected_answer": {
            "kind": expected.kind.value,
            "value": _json_value(expected.value),
            "unit": expected.unit,
            "tolerance": expected.tolerance,
        },
        "marking_scheme": {
            "maximum_marks": scheme.maximum_marks,
            "criteria": [
                {
                    "identifier": criterion.identifier,
                    "description": criterion.description,
                    "marks": criterion.marks,
                }
                for criterion in scheme.criteria
            ],
        },
        "worked_solution": entry.worked_solution,
    }


def _json_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value
