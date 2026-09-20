"""Deterministic solver-backed calculation questions for Momentum & Impulse."""
# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from assessment_platform.core import (
    ExpectedAnswer,
    ExpectedAnswerKind,
    GenerationProvenance,
    MarkingCriterion,
    MarkingScheme,
    Question,
    QuestionPart,
    ResponseKind,
    ResponseSpecification,
    Scenario,
    VisualReference,
)
from assessment_platform.curriculum.caps.physical_sciences import CurriculumTopic
from assessment_platform.domains.physical_sciences.mechanics.momentum_constrained_solver import (
    ConstrainedMomentumSolver,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_generation import (
    GeneratedCollisionProblem,
    GeneratedContactTimeProblem,
    GeneratedForceFromMomentumChangeProblem,
    GeneratedImpulseForceTimeProblem,
    GeneratedInitialMomentumProblem,
    GeneratedMomentumChangeProblem,
    MomentumGeneratedProblem,
    MomentumGenerationFamily,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse_relationships import (
    MomentumImpulseRelationshipSolver,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse_solver import (
    MomentumImpulseSolver,
)
from assessment_platform.rendering.svg.momentum import MomentumDiagramOptions, MomentumSvgRenderer

GENERATOR_ID = "caps-grade-12-momentum-impulse-question-generator"
GENERATOR_VERSION = "1"
NUMERIC_TOLERANCE = 0.01


class MomentumQuestionTemplate(StrEnum):
    BODY_MOMENTUM = "momentum.body.calculate"
    SYSTEM_MOMENTUM = "momentum.system.total"
    MOMENTUM_CHANGE = "momentum.change.calculate"
    IMPULSE = "impulse.calculate"
    FORCE = "force.average.calculate"
    CONTACT_TIME = "contact-time.calculate"
    FINAL_VELOCITY = "collision.final-velocity.calculate"
    STICKING_VELOCITY = "collision.sticking.common-velocity"
    CLASSIFICATION = "collision.classification.calculate"


@dataclass(frozen=True, slots=True)
class MomentumQuestionOptions:
    include_visuals: bool = True


class MomentumQuestionGenerator:
    """Author canonical questions from already generated, solvable problems."""

    def __init__(self, topic: CurriculumTopic, options: MomentumQuestionOptions | None = None) -> None:
        if not isinstance(topic, CurriculumTopic):
            raise ValueError("topic must be a CurriculumTopic")
        if topic.identifier != "momentum-and-impulse":
            raise ValueError("generator requires the CAPS Momentum and Impulse topic")
        self.topic = topic
        self.options = options or MomentumQuestionOptions()
        self._renderer = MomentumSvgRenderer()

    def generate(self, problem: MomentumGeneratedProblem) -> Question:
        metadata = problem.metadata
        family = metadata.family
        parts: list[QuestionPart] = []
        templates: list[str] = []
        result: Any
        solution: Any
        if isinstance(problem, GeneratedInitialMomentumProblem):
            solution = MomentumImpulseSolver(problem.scenario).solve()
            body = problem.scenario.bodies[0]
            result = next(item for item in solution.body_momenta if item.body_identifier == body.identifier)
            parts.append(self._part("body", MomentumQuestionTemplate.BODY_MOMENTUM, f"Calculate the momentum of body {body.identifier}.", result.momentum.value, "kg·m·s⁻¹", 2))
            parts.append(self._part("system", MomentumQuestionTemplate.SYSTEM_MOMENTUM, "Calculate the total momentum of the system.", solution.initial_total_momentum.value, "kg·m·s⁻¹", 3))
            templates.extend((MomentumQuestionTemplate.BODY_MOMENTUM, MomentumQuestionTemplate.SYSTEM_MOMENTUM))
            scenario = problem.scenario
            interaction = None
        elif isinstance(problem, GeneratedMomentumChangeProblem):
            result = MomentumImpulseRelationshipSolver().calculate_momentum_change(problem.input_data)
            parts.append(self._part("change", MomentumQuestionTemplate.MOMENTUM_CHANGE, "Calculate the signed change in momentum.", result.momentum_change.value, "kg·m·s⁻¹", 3))
            parts.append(self._part("impulse", MomentumQuestionTemplate.IMPULSE, "Calculate the impulse on the body.", MomentumImpulseRelationshipSolver().calculate_impulse_from_momentum_change(result).impulse.value, "N·s", 2))
            templates.extend((MomentumQuestionTemplate.MOMENTUM_CHANGE, MomentumQuestionTemplate.IMPULSE))
            scenario = None
            interaction = None
        elif isinstance(problem, GeneratedImpulseForceTimeProblem):
            result = MomentumImpulseRelationshipSolver().calculate_impulse_from_force_time(problem.input_data)
            parts.append(self._part("impulse", MomentumQuestionTemplate.IMPULSE, "Calculate the impulse delivered during contact.", result.impulse.value, "N·s", 2))
            templates.append(MomentumQuestionTemplate.IMPULSE)
            scenario = None
            interaction = None
        elif isinstance(problem, GeneratedForceFromMomentumChangeProblem):
            solver = MomentumImpulseRelationshipSolver()
            change = solver.calculate_momentum_change(problem.momentum_change_input)
            result = solver.calculate_force_from_momentum_change(change, problem.contact_time)
            parts.append(self._part("force", MomentumQuestionTemplate.FORCE, "Calculate the signed average resultant force.", result.force.value, "N", 3))
            templates.append(MomentumQuestionTemplate.FORCE)
            scenario = None
            interaction = None
        elif isinstance(problem, GeneratedContactTimeProblem):
            result = MomentumImpulseRelationshipSolver().calculate_contact_time_from_impulse(problem.impulse, problem.force, problem.positive_axis)
            parts.append(self._part("time", MomentumQuestionTemplate.CONTACT_TIME, "Calculate the contact time.", result.contact_time.value, "s", 3))
            templates.append(MomentumQuestionTemplate.CONTACT_TIME)
            scenario = None
            interaction = None
        elif isinstance(problem, GeneratedCollisionProblem):
            solution = ConstrainedMomentumSolver(problem.interaction).solve()
            scenario = problem.scenario
            interaction = problem.interaction
            if family is MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION:
                constraint = problem.interaction.constraint
                unknown = next(state for state in solution.final_states if state.body_identifier != constraint.body_identifier)  # type: ignore[union-attr]
                parts.append(self._part("final-velocity", MomentumQuestionTemplate.FINAL_VELOCITY, f"Calculate the final velocity of body {unknown.body_identifier}.", unknown.final_velocity.value, "m·s⁻¹", 4))
                templates.append(MomentumQuestionTemplate.FINAL_VELOCITY)
            elif family is MomentumGenerationFamily.STICKING_COLLISION:
                state = solution.final_states[0]
                parts.append(self._part("common-velocity", MomentumQuestionTemplate.STICKING_VELOCITY, "The bodies stick together. Calculate their common final velocity.", state.final_velocity.value, "m·s⁻¹", 4))
                templates.append(MomentumQuestionTemplate.STICKING_VELOCITY)
            else:
                if solution.classification is None:
                    raise ValueError("classification requires an authoritative isolated solution")
                parts.append(self._text_part("classification", MomentumQuestionTemplate.CLASSIFICATION, "Classify the collision using the validated final state.", solution.classification.value, 2))
                templates.append(MomentumQuestionTemplate.CLASSIFICATION)
        else:
            raise ValueError("unsupported Momentum generated problem")

        identifier = f"momentum-question-v{GENERATOR_VERSION}-{metadata.identifier}"
        visuals: tuple[VisualReference, ...] = ()
        if self.options.include_visuals and scenario is not None:
            document = self._renderer.render(
                scenario,
                interaction,
                solution if isinstance(problem, GeneratedCollisionProblem) else None,
                MomentumDiagramOptions(show_after_panel=isinstance(problem, GeneratedCollisionProblem)),
            )
            visuals = (VisualReference(f"{identifier}-diagram", "image/svg+xml", document.markup, document.width, document.height),)
        prompt = self._prompt(scenario, problem)
        return Question(
            identifier,
            prompt,
            tuple(parts),
            Scenario(metadata.identifier),
            provenance=GenerationProvenance(GENERATOR_ID, GENERATOR_VERSION, metadata.provenance.seed, tuple(templates)),
            visuals=visuals,
        )

    @staticmethod
    def _part(key: str, template: MomentumQuestionTemplate, prompt: str, value: float, unit: str, marks: int) -> QuestionPart:
        return QuestionPart(
            f"{template.value}.{key}", prompt, marks,
            ResponseSpecification(ResponseKind.CALCULATION, 3, True, True, True, ("working", "final")),
            ExpectedAnswer(ExpectedAnswerKind.NUMERIC, value, unit, NUMERIC_TOLERANCE),
            MarkingScheme(marks, (MarkingCriterion(f"{template.value}.{key}.method", "Correct physical relationship and signed result with unit.", marks),)),
        )

    @staticmethod
    def _text_part(key: str, template: MomentumQuestionTemplate, prompt: str, value: str, marks: int) -> QuestionPart:
        return QuestionPart(
            f"{template.value}.{key}", prompt, marks,
            ResponseSpecification(ResponseKind.SHORT_TEXT, 1, False, True),
            ExpectedAnswer(ExpectedAnswerKind.TEXT, value),
            MarkingScheme(marks, (MarkingCriterion(f"{template.value}.{key}.answer", "Correct classification.", marks),)),
        )

    @staticmethod
    def _prompt(scenario: Any, problem: MomentumGeneratedProblem) -> str:
        if scenario is None:
            return "Use SI units and the signed quantities supplied in the problem data to answer the calculation parts."
        axis = "right" if scenario.positive_axis.value == "right" else "left"
        givens = "; ".join(f"{body.identifier}: {body.mass.value:g} kg, {body.initial_velocity.value:g} m·s⁻¹" for body in scenario.bodies)
        return f"Take motion to the {axis} as positive. The initial data are {givens}. Answer the calculation parts using signed SI quantities."
