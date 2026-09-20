"""Deterministic CAPS-aligned conceptual Momentum & Impulse questions."""
# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from assessment_platform.core import (
    ExpectedAnswer,
    ExpectedAnswerKind,
    GenerationProvenance,
    GenerationSeed,
    MarkingCriterion,
    MarkingScheme,
    Question,
    QuestionPart,
    ResponseKind,
    ResponseSpecification,
)
from assessment_platform.curriculum.caps.physical_sciences import CurriculumTopic

GENERATOR_ID = "caps-grade-12-momentum-impulse-conceptual-question-generator"
GENERATOR_VERSION = "1"


class ConceptualTemplate(StrEnum):
    DEFINE_MOMENTUM = "momentum.define"
    MOMENTUM_VECTOR = "momentum.vector.explain"
    NEWTON_MOMENTUM = "newton-second-law.momentum-form"
    DEFINE_SYSTEM = "system.define"
    SYSTEM_ENVIRONMENT = "system.environment.distinguish"
    INTERNAL_EXTERNAL = "system.internal-external-forces.distinguish"
    ISOLATED_SYSTEM = "system.isolated.define"
    CONSERVATION = "momentum.conservation.state"
    ELASTIC_INELASTIC = "collision.elastic-inelastic.distinguish"
    IMPULSE_THEOREM = "impulse.theorem.explain"
    SAFETY = "safety.stopping-time.explain"


@dataclass(frozen=True, slots=True)
class ConceptualQuestionOptions:
    include_visuals: bool = False


@dataclass(frozen=True, slots=True)
class _Spec:
    prompt: str
    answer: tuple[str, ...]
    criteria: tuple[tuple[str, str, int], ...]
    response_kind: ResponseKind


_SPECS: dict[ConceptualTemplate, _Spec] = {
    ConceptualTemplate.DEFINE_MOMENTUM: _Spec(
        "Define momentum.", ("momentum is the product of mass and velocity",),
        (("definition", "States that momentum is the product of mass and velocity.", 1),), ResponseKind.SHORT_TEXT,
    ),
    ConceptualTemplate.MOMENTUM_VECTOR: _Spec(
        "Explain why momentum is a vector quantity.", ("has magnitude and direction", "direction follows velocity"),
        (("magnitude", "Identifies a magnitude.", 1), ("direction", "Identifies a direction related to velocity.", 1)), ResponseKind.LONG_TEXT,
    ),
    ConceptualTemplate.NEWTON_MOMENTUM: _Spec(
        "State Newton's second law in terms of momentum.", ("net force is the rate of change of momentum",),
        (("rate", "States that net/resultant force is related to the rate of change of momentum.", 2),), ResponseKind.SHORT_TEXT,
    ),
    ConceptualTemplate.DEFINE_SYSTEM: _Spec(
        "What is meant by a system in mechanics?", ("the objects selected for study",),
        (("selected objects", "Identifies the system as the objects or region selected for study.", 1),), ResponseKind.SHORT_TEXT,
    ),
    ConceptualTemplate.SYSTEM_ENVIRONMENT: _Spec(
        "Distinguish between a system and its environment.", ("system is selected objects", "environment is everything outside system"),
        (("system", "Describes the selected objects as the system.", 1), ("environment", "Describes the environment as what is outside the system.", 1)), ResponseKind.LONG_TEXT,
    ),
    ConceptualTemplate.INTERNAL_EXTERNAL: _Spec(
        "Distinguish between internal and external forces on a system.", ("internal forces act between system objects", "external forces act between system and environment"),
        (("internal", "Identifies forces between objects within the system.", 1), ("external", "Identifies forces involving the system and its environment.", 1)), ResponseKind.LONG_TEXT,
    ),
    ConceptualTemplate.ISOLATED_SYSTEM: _Spec(
        "Explain what is meant by an isolated system.", ("net external force or impulse is zero",),
        (("external interaction", "States that the net external force/impulse on the system is zero.", 2),), ResponseKind.SHORT_TEXT,
    ),
    ConceptualTemplate.CONSERVATION: _Spec(
        "State the law of conservation of linear momentum.", ("total linear momentum remains constant in an isolated system",),
        (("isolated", "Specifies that the statement applies to an isolated system.", 1), ("constant", "States that total linear momentum remains constant/is conserved.", 1)), ResponseKind.SHORT_TEXT,
    ),
    ConceptualTemplate.ELASTIC_INELASTIC: _Spec(
        "Distinguish between elastic and inelastic collisions.", ("elastic conserves kinetic energy", "inelastic does not conserve kinetic energy", "perfectly inelastic bodies stick"),
        (("elastic", "States that kinetic energy is conserved in an elastic collision.", 1), ("inelastic", "States that kinetic energy is not conserved in an inelastic collision.", 1), ("sticking", "Identifies sticking as perfectly inelastic, not as every inelastic collision.", 1)), ResponseKind.LONG_TEXT,
    ),
    ConceptualTemplate.IMPULSE_THEOREM: _Spec(
        "State the impulse-momentum theorem.", ("impulse equals change in momentum",),
        (("relationship", "States that impulse equals the change in momentum.", 2),), ResponseKind.SHORT_TEXT,
    ),
    ConceptualTemplate.SAFETY: _Spec(
        "Explain why an airbag reduces injury during a collision.", ("same change in momentum", "increased stopping time", "smaller average force", "reduced injury"),
        (("momentum change", "Recognises the required change in momentum/impulse.", 1), ("time", "Explains that the airbag increases stopping/contact time.", 1), ("force", "Explains that the same impulse over a longer time reduces average force.", 1), ("safety", "Links the smaller force to reduced injury/damage.", 1)), ResponseKind.LONG_TEXT,
    ),
}


class MomentumConceptualQuestionGenerator:
    """Create conceptual canonical Questions without calculating physics."""

    def __init__(self, topic: CurriculumTopic, options: ConceptualQuestionOptions | None = None) -> None:
        if not isinstance(topic, CurriculumTopic) or topic.identifier != "momentum-and-impulse":
            raise ValueError("generator requires the CAPS Momentum and Impulse topic")
        self.topic = topic
        self.options = options or ConceptualQuestionOptions()

    def generate(self, template: ConceptualTemplate, seed: GenerationSeed | None = None) -> Question:
        if not isinstance(template, ConceptualTemplate):
            raise ValueError("template must be a ConceptualTemplate")
        spec = _SPECS[template]
        question_id = f"momentum-conceptual-v{GENERATOR_VERSION}-{template.value}"
        part_id = f"{template.value}.response"
        marks = sum(item[2] for item in spec.criteria)
        criteria = tuple(MarkingCriterion(f"{template.value}.{key}", description, value) for key, description, value in spec.criteria)
        part = QuestionPart(
            part_id, spec.prompt, marks,
            ResponseSpecification(spec.response_kind, 2 if spec.response_kind is ResponseKind.SHORT_TEXT else 5, False, True),
            ExpectedAnswer(ExpectedAnswerKind.TEXT, spec.answer),
            MarkingScheme(marks, criteria),
        )
        return Question(
            question_id, spec.prompt, (part,),
            provenance=GenerationProvenance(GENERATOR_ID, GENERATOR_VERSION, seed, (template.value,)),
        )
