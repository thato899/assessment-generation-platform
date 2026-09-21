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
WORK_ENERGY_POWER_TOPIC_ID: Final[str] = "work-energy-and-power"


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
        WORK_ENERGY_POWER_TOPIC_ID,
        "Work, Energy & Power",
        CurriculumReference(CAPS, phase="FET", grade=GRADE_12, subject=PHYSICAL_SCIENCES,
                            topic=Topic(WORK_ENERGY_POWER_TOPIC_ID)),
        MECHANICS,
        (
            "work as a scalar quantity",
            "work from a force-displacement relationship",
            "positive, negative and zero work",
            "individual work contributions and scalar net work",
            "resultant force along a plane and displacement along the plane",
            "work-energy theorem",
            "kinetic-energy change from net work",
            "horizontal and inclined-plane applications",
            "frictionless and rough-plane applications",
            "conservative and non-conservative forces",
            "mechanical-energy conservation when only conservative forces act",
            "mechanical energy changes with non-conservative forces while total "
            "system energy remains conserved",
            "gravitational force as a conservative force",
            "air resistance, friction, tension and applied force as non-conservative examples",
            "power as the rate of doing work",
            "average power",
            "constant-speed rough horizontal and inclined-plane power",
            "minimum power to pump water from a borehole",
        ),
        (
            "Grade 12 Physics Mechanics Work, Energy & Power in Term 2",
            "work is scalar and net work is the scalar sum of individual contributions",
            "force-displacement angle and along-plane resultant relationships",
            "horizontal and inclined planes, both frictionless and rough",
            "contact-force work depends on remaining in contact over the displacement",
            "mechanical energy is distinguished from total system energy when "
            "non-conservative forces act",
            "constant-speed power on rough horizontal and inclined planes",
            "minimum electric-motor power for a borehole depth and pumping rate",
        ),
        ("Grade 12", "Physics", "Mechanics", "Term 2", "10 hours"),
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
