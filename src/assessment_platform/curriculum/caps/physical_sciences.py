"""The initial CAPS Grade 12 Physical Sciences curriculum slice."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from assessment_platform.core import CurriculumReference, Grade, Subject, Topic

CAPS: Final[str] = "CAPS"
PHYSICAL_SCIENCES: Final[Subject] = Subject("physical-sciences")
GRADE_11: Final[Grade] = Grade(11)
GRADE_12: Final[Grade] = Grade(12)
NEWTONS_LAWS_TOPIC_ID: Final[str] = "newtons-laws"


@dataclass(frozen=True, slots=True)
class Domain:
    identifier: str
    name: str


@dataclass(frozen=True, slots=True)
class CurriculumTopic:
    identifier: str
    name: str
    reference: CurriculumReference
    domain: Domain
    concepts: tuple[str, ...]
    constraints: tuple[str, ...]
    assessment_metadata: tuple[str, ...]


MECHANICS: Final[Domain] = Domain("mechanics", "Mechanics")

_TOPICS: tuple[CurriculumTopic, ...] = (
    CurriculumTopic(
        NEWTONS_LAWS_TOPIC_ID,
        "Newton's Laws and Application of Newton's Laws",
        CurriculumReference(CAPS, phase="FET", grade=GRADE_11, subject=PHYSICAL_SCIENCES,
                            topic=Topic(NEWTONS_LAWS_TOPIC_ID)),
        MECHANICS,
        (
            "Newton's first, second and third laws",
            "Newton's law of universal gravitation",
            "weight, normal, frictional, applied and tension forces",
            "force diagrams and free-body diagrams",
            "equilibrium and non-equilibrium applications",
            "resultant forces and two-dimensional force components",
            "horizontal, inclined-plane, vertical-motion and two-body applications",
            "mass and weight distinction, including apparent weight",
        ),
        (
            "one- and two-dimensional force systems",
            "light/negligible-mass string for the bounded two-body case",
            "static and kinetic friction relationships on horizontal and inclined planes",
            "explicit gravitational field data",
        ),
        (
            "Grade 11 core instruction",
            "Grade 12 consolidation",
            "selected Grade 11 content examinable in the Grade 12 final examination",
            "Mechanics",
        ),
    ),
    CurriculumTopic(
        "momentum-and-impulse",
        "Momentum and Impulse",
        CurriculumReference(CAPS, phase="FET", grade=GRADE_12, subject=PHYSICAL_SCIENCES,
                            topic=Topic("momentum-and-impulse")),
        MECHANICS,
        ("momentum", "Newton's second law expressed in terms of momentum",
         "conservation of momentum", "elastic and inelastic collisions", "impulse"),
        (),
        ("Grade 12", "Mechanics"),
    ),
    CurriculumTopic(
        "vertical-projectile-motion-1d",
        "Vertical projectile motion in one dimension (1D)",
        CurriculumReference(CAPS, phase="FET", grade=GRADE_12, subject=PHYSICAL_SCIENCES,
                            topic=Topic("vertical-projectile-motion-1d")),
        MECHANICS,
        ("vertical projectile motion represented in words, diagrams, equations and graphs",
         "position, velocity and displacement at any given time",
         "position versus time, velocity versus time and acceleration versus time graphs",
         "time symmetry"),
        ("near the surface of the Earth", "in the absence of air friction",
         "one-dimensional vertical motion"),
        ("Grade 12", "Mechanics", "5 hours"),
    ),
    CurriculumTopic(
        "work-energy-and-power",
        "Work, Energy & Power",
        CurriculumReference(CAPS, phase="FET", grade=GRADE_12, subject=PHYSICAL_SCIENCES,
                            topic=Topic("work-energy-and-power")),
        MECHANICS,
        ("work", "work-energy theorem",
         "conservation of energy with non-conservative forces present", "power"),
        (),
        ("Grade 12", "Mechanics"),
    ),
)


class CapsCurriculum:
    """Read-only indexed access to the supported CAPS curriculum slice."""

    def __init__(self, topics: tuple[CurriculumTopic, ...] = _TOPICS) -> None:
        identifiers = [topic.identifier for topic in topics]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("curriculum topic identifiers must be unique")
        self._topics = MappingProxyType({topic.identifier: topic for topic in topics})

    @property
    def topics(self) -> tuple[CurriculumTopic, ...]:
        return tuple(self._topics.values())

    def topic(self, identifier: str) -> CurriculumTopic:
        try:
            return self._topics[identifier]
        except KeyError as error:
            raise KeyError(f"unknown CAPS Physical Sciences topic: {identifier}") from error

    def topics_for(self, grade: Grade, subject: Subject) -> tuple[CurriculumTopic, ...]:
        return tuple(topic for topic in self._topics.values()
                     if topic.reference.grade == grade and topic.reference.subject == subject)


def get_caps_physical_sciences() -> CapsCurriculum:
    return CapsCurriculum()
