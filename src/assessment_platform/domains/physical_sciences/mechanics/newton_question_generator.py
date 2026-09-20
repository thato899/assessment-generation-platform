"""Solver-backed canonical calculation questions for Newton's Laws.

The generator owns wording, applicability and assessment packaging.  Numerical
answers are obtained exclusively from :class:`NewtonSolver`.
"""

from __future__ import annotations

import re
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
from assessment_platform.curriculum.caps.physical_sciences import (
    GRADE_11,
    PHYSICAL_SCIENCES,
    CurriculumTopic,
)
from assessment_platform.domains.physical_sciences.mechanics.newton_generation import (
    GeneratedConnectedBodiesProblem,
    GeneratedContactProblem,
    GeneratedEquilibriumProblem,
    GeneratedGravitationProblem,
    GeneratedNewtonIIProblem,
    GeneratedUnknownForceProblem,
    GeneratedWeightProblem,
    NewtonGeneratedProblem,
    NewtonGenerationFamily,
)
from assessment_platform.domains.physical_sciences.mechanics.newton_solver import (
    ContactResult,
    NewtonSolveError,
    NewtonSolver,
)
from assessment_platform.domains.physical_sciences.mechanics.newtons_laws import (
    CartesianDirection,
    Force,
    Newtons,
    NewtonScenario,
    SurfaceCoordinates,
    SurfaceDirection,
    UnknownValue,
)
from assessment_platform.rendering.svg.newton import (
    NewtonDiagramKind,
    NewtonRenderOptions,
    NewtonSvgRenderer,
)

GENERATOR_ID = "caps-grade-11-newton-calculation-question-generator"
GENERATOR_VERSION = "1"
NUMERIC_TOLERANCE = 0.01
NEWTONS_LAWS_TOPIC_ID = "newtons-laws"


class NewtonCalculationTemplate(StrEnum):
    RESULTANT_FORCE = "newton.resultant-force.calculate"
    ACCELERATION = "newton.acceleration.calculate"
    UNKNOWN_FORCE = "newton.unknown-force.calculate"
    WEIGHT = "newton.weight.calculate"
    NORMAL_FORCE = "newton.normal-force.calculate"
    APPARENT_WEIGHT = "newton.apparent-weight.calculate"
    STATIC_FRICTION = "newton.static-friction.calculate"
    LIMITING_STATIC_FRICTION = "newton.limiting-static-friction.calculate"
    KINETIC_FRICTION = "newton.kinetic-friction.calculate"
    INCLINED_NORMAL_FORCE = "newton.incline-normal-force.calculate"
    CONNECTED_ACCELERATION = "newton.connected-acceleration.calculate"
    TENSION = "newton.tension.calculate"
    UNIVERSAL_GRAVITATION = "newton.universal-gravitation.calculate"
    EQUILIBRIUM_RESULTANT = "newton.equilibrium-resultant.calculate"


@dataclass(frozen=True, slots=True)
class NewtonQuestionOptions:
    """Immutable options for learner-safe question generation."""

    include_visuals: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.include_visuals, bool):
            raise ValueError("include_visuals must be a boolean")


class NewtonCalculationQuestionGenerator:
    """Create canonical numeric Newton questions from solver-valid problems."""

    def __init__(
        self,
        topic: CurriculumTopic,
        options: NewtonQuestionOptions | None = None,
    ) -> None:
        if not isinstance(topic, CurriculumTopic):
            raise ValueError("topic must be a CurriculumTopic")
        if topic.identifier != NEWTONS_LAWS_TOPIC_ID:
            raise ValueError("generator requires the CAPS Newton's Laws topic")
        if topic.reference.grade != GRADE_11 or topic.reference.subject != PHYSICAL_SCIENCES:
            raise ValueError("generator requires Grade 11 CAPS Physical Sciences metadata")
        self.topic = topic
        self.options = options or NewtonQuestionOptions()
        self._renderer = NewtonSvgRenderer()

    def generate(self, problem: NewtonGeneratedProblem) -> Question:
        if not isinstance(problem, NewtonGeneratedProblem):
            raise ValueError("problem must be a generated Newton problem")
        scenario = problem.scenario
        solver = NewtonSolver(scenario)
        question_id = f"newton-question-v{GENERATOR_VERSION}-{self._slug(problem.identifier)}"
        parts: list[QuestionPart] = []
        templates: list[str] = []

        if isinstance(problem, GeneratedNewtonIIProblem):
            body_id = scenario.bodies[0].identifier
            dynamics = self._solve(lambda: solver.body_dynamics(body_id))
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.RESULTANT_FORCE,
                    "Calculate the signed resultant force on the body.",
                    dynamics.resultant.components[0].value,
                    "N",
                    3,
                )
            )
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.ACCELERATION,
                    "Calculate the signed acceleration of the body.",
                    dynamics.acceleration.components[0].value,
                    "m·s⁻²",
                    3,
                )
            )
            templates.extend(
                (
                    NewtonCalculationTemplate.RESULTANT_FORCE.value,
                    NewtonCalculationTemplate.ACCELERATION.value,
                )
            )
        elif isinstance(problem, GeneratedEquilibriumProblem):
            body_id = scenario.bodies[0].identifier
            dynamics = self._solve(lambda: solver.body_dynamics(body_id))
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.EQUILIBRIUM_RESULTANT,
                    "Calculate the signed resultant force on the body.",
                    dynamics.resultant.components[0].value,
                    "N",
                    2,
                )
            )
            templates.append(NewtonCalculationTemplate.EQUILIBRIUM_RESULTANT.value)
        elif isinstance(problem, GeneratedUnknownForceProblem):
            result = self._solve(lambda: solver.solve_force(problem.force_id))
            for index, component in enumerate(result.vector.components, start=1):
                parts.append(
                    self._numeric_part(
                        question_id,
                        NewtonCalculationTemplate.UNKNOWN_FORCE,
                        f"Calculate the signed component {index} of the unknown force.",
                        component.value,
                        "N",
                        3,
                        suffix=str(index),
                    )
                )
            templates.append(NewtonCalculationTemplate.UNKNOWN_FORCE.value)
        elif isinstance(problem, GeneratedWeightProblem):
            result = self._solve(
                lambda: solver.weight(scenario.bodies[0].identifier, problem.field_source)
            )
            component = self._answer_component(result.vector.components)
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.WEIGHT,
                    "Calculate the signed weight component in the authored field direction.",
                    component,
                    "N",
                    3,
                )
            )
            templates.append(NewtonCalculationTemplate.WEIGHT.value)
        elif isinstance(problem, GeneratedContactProblem):
            result = self._solve(lambda: solver.contact_forces(problem.contact_id))
            template, prompt, value = self._contact_quantity(problem.family, result)
            parts.append(self._numeric_part(question_id, template, prompt, value, "N", 3))
            templates.append(template.value)
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.APPARENT_WEIGHT,
                    "Calculate the apparent weight of the body from the validated contact result.",
                    result.apparent_weight.value,
                    "N",
                    2,
                )
            )
            templates.append(NewtonCalculationTemplate.APPARENT_WEIGHT.value)
        elif isinstance(problem, GeneratedConnectedBodiesProblem):
            result = self._solve(lambda: solver.connected_bodies(problem.request))
            first = result.bodies[0]
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.CONNECTED_ACCELERATION,
                    "Calculate the common signed acceleration of the connected bodies.",
                    first.acceleration.components[0].value,
                    "m·s⁻²",
                    4,
                )
            )
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.TENSION,
                    "Calculate the tension in the light string.",
                    result.tension.value,
                    "N",
                    3,
                )
            )
            templates.extend(
                (
                    NewtonCalculationTemplate.CONNECTED_ACCELERATION.value,
                    NewtonCalculationTemplate.TENSION.value,
                )
            )
        elif isinstance(problem, GeneratedGravitationProblem):
            result = self._solve(lambda: solver.gravitational_force(problem.interaction_id))
            parts.append(
                self._numeric_part(
                    question_id,
                    NewtonCalculationTemplate.UNIVERSAL_GRAVITATION,
                    "Calculate the magnitude of the gravitational force between the bodies.",
                    result.magnitude.value,
                    "N",
                    4,
                )
            )
            templates.append(NewtonCalculationTemplate.UNIVERSAL_GRAVITATION.value)
        else:
            # Newton III validation is not a numerical derivation and belongs to #60 concept work.
            raise ValueError("generated family has no supported Issue #59 calculation template")

        if not parts:
            raise ValueError("no applicable calculation template for generated problem")
        visuals: tuple[VisualReference, ...] = ()
        if self.options.include_visuals:
            document = self._renderer.render(
                scenario,
                NewtonRenderOptions(diagram_kind=NewtonDiagramKind.FORCE_DIAGRAM),
            )
            visuals = (
                VisualReference(
                    f"{question_id}-diagram",
                    "image/svg+xml",
                    document.markup,
                    document.width,
                    document.height,
                ),
            )
        return Question(
            identifier=question_id,
            prompt=self._prompt(scenario, problem),
            parts=tuple(parts),
            scenario=Scenario(scenario.identifier, self._scenario_data(scenario, problem)),
            visuals=visuals,
            provenance=GenerationProvenance(
                GENERATOR_ID,
                GENERATOR_VERSION,
                problem.provenance.seed,
                tuple(templates),
            ),
        )

    @staticmethod
    def _solve(operation: Any) -> Any:
        try:
            return operation()
        except NewtonSolveError as error:
            raise ValueError(
                f"Newton calculation is not applicable: {error.reason.value}"
            ) from error

    @staticmethod
    def _answer_component(
        components: tuple[Newtons | UnknownValue, ...],
    ) -> float:
        known = [component.value for component in components if isinstance(component, Newtons)]
        if not known:
            raise ValueError("solver returned no answer component")
        return next((value for value in reversed(known) if value != 0), known[-1])

    @staticmethod
    def _contact_quantity(
        family: NewtonGenerationFamily, result: ContactResult
    ) -> tuple[NewtonCalculationTemplate, str, float]:
        if family is NewtonGenerationFamily.CONTACT_NORMAL:
            return (
                NewtonCalculationTemplate.NORMAL_FORCE,
                "Calculate the signed normal-force component.",
                NewtonCalculationQuestionGenerator._answer_component(
                    result.normal.vector.components
                ),
            )
        if family is NewtonGenerationFamily.INCLINED_PLANE:
            return (
                NewtonCalculationTemplate.INCLINED_NORMAL_FORCE,
                "Calculate the signed normal-force component perpendicular to the incline.",
                NewtonCalculationQuestionGenerator._answer_component(
                    result.normal.vector.components
                ),
            )
        if result.friction is None:
            raise ValueError("contact solver returned no friction result")
        if family is NewtonGenerationFamily.STATIC_FRICTION:
            if result.friction.force is None:
                raise ValueError("static friction did not produce a signed force")
            return (
                NewtonCalculationTemplate.STATIC_FRICTION,
                "Calculate the signed static-friction force required for balance.",
                NewtonCalculationQuestionGenerator._answer_component(
                    result.friction.force.vector.components
                ),
            )
        if family is NewtonGenerationFamily.LIMITING_STATIC_FRICTION:
            return (
                NewtonCalculationTemplate.LIMITING_STATIC_FRICTION,
                "Calculate the limiting static-friction magnitude.",
                result.friction.magnitude.value,
            )
        if family is NewtonGenerationFamily.KINETIC_FRICTION:
            return (
                NewtonCalculationTemplate.KINETIC_FRICTION,
                "Calculate the kinetic-friction magnitude.",
                result.friction.magnitude.value,
            )
        raise ValueError("unsupported contact calculation family")

    @staticmethod
    def _numeric_part(
        question_id: str,
        template: NewtonCalculationTemplate,
        prompt: str,
        value: float,
        unit: str,
        marks: int,
        suffix: str = "",
    ) -> QuestionPart:
        part_id = f"{question_id}.{template.value}{f'.{suffix}' if suffix else ''}"
        criteria: tuple[MarkingCriterion, ...]
        if marks == 1:
            criteria = (
                MarkingCriterion(
                    f"{part_id}.answer",
                    f"States the correct signed numerical answer with unit {unit}.",
                    1,
                ),
            )
        else:
            criteria = (
                MarkingCriterion(
                    f"{part_id}.method",
                    "Uses the supplied physical data and sign convention correctly.",
                    marks - 1,
                ),
                MarkingCriterion(
                    f"{part_id}.answer",
                    f"States the correct signed numerical answer with unit {unit}.",
                    1,
                ),
            )
        return QuestionPart(
            identifier=part_id,
            prompt=prompt,
            marks=marks,
            response_specification=ResponseSpecification(
                ResponseKind.CALCULATION,
                suggested_line_count=3,
                expects_working=True,
                expects_final_answer=True,
                expects_units=True,
                required_fields=("working", "final"),
            ),
            expected_answer=ExpectedAnswer(
                ExpectedAnswerKind.NUMERIC, value, unit, NUMERIC_TOLERANCE
            ),
            marking_scheme=MarkingScheme(marks, criteria),
        )

    @staticmethod
    def _prompt(scenario: NewtonScenario, problem: NewtonGeneratedProblem) -> str:
        direction = NewtonCalculationQuestionGenerator._positive_direction(scenario)
        body_data = "; ".join(
            f"{body.identifier} has mass {body.mass.value:g} kg" for body in scenario.bodies
        )
        forces = "; ".join(
            NewtonCalculationQuestionGenerator._force_given(force) for force in scenario.forces
        )
        fields = "; ".join(
            f"the authored field from {field.source.identifier} has acceleration "
            f"{', '.join(f'{component.value:g}' for component in field.acceleration.components)} "
            "m·s⁻²"
            for field in scenario.gravitational_fields
        )
        details = ". ".join(item for item in (body_data, forces, fields) if item)
        if scenario.contacts:
            contact = scenario.contacts[0]
            details += f". The contact uses {contact.friction.regime.value} friction"
            if contact.friction.coefficient is not None and not isinstance(
                contact.friction.coefficient, UnknownValue
            ):
                details += f" with coefficient {contact.friction.coefficient.value:g}"
        if scenario.strings:
            details += ". The connecting string is light, taut and inextensible"
        if scenario.gravitation:
            interaction = scenario.gravitation[0]
            details += f". The centre-to-centre separation is {interaction.separation.value:g} m"
            details += ". Use G = 6.67e-11 N·m²·kg⁻²"
        return (
            f"{details}. Take {direction} as positive. Assume an inertial frame, "
            "constant mass and negligible air resistance. Use signed SI quantities "
            "and answer the calculation parts."
        )

    @staticmethod
    def _force_given(force: Force) -> str:
        components = ", ".join(
            "?" if isinstance(component, UnknownValue) else f"{component.value:g}"
            for component in force.vector.components
        )
        source = force.source.identifier
        return f"{force.kind.value} force from {source} on {force.target_body_id}: ({components}) N"

    @staticmethod
    def _positive_direction(scenario: NewtonScenario) -> str:
        axis = scenario.coordinates.axes[0]
        if isinstance(axis, CartesianDirection):
            return {
                CartesianDirection.RIGHT: "right",
                CartesianDirection.LEFT: "left",
                CartesianDirection.UP: "upward",
                CartesianDirection.DOWN: "downward",
            }[axis]
        if isinstance(scenario.coordinates, SurfaceCoordinates):
            return {
                SurfaceDirection.ALONG_RIGHT: "up the incline",
                SurfaceDirection.ALONG_LEFT: "down the incline",
            }[axis]
        return "the authored positive direction"

    @staticmethod
    def _scenario_data(
        scenario: NewtonScenario, problem: NewtonGeneratedProblem
    ) -> dict[str, object]:
        return {
            "curriculum_topic": NEWTONS_LAWS_TOPIC_ID,
            "grade": 11,
            "family": problem.family.value,
            "difficulty": problem.difficulty.value,
            "positive_direction": NewtonCalculationQuestionGenerator._positive_direction(scenario),
            "assumptions": {
                "inertial_frame": True,
                "constant_mass": True,
                "air_resistance_neglected": True,
            },
            "source_generator_id": problem.provenance.generator_id,
            "source_generator_version": problem.provenance.generator_version,
            "source_seed": (
                problem.provenance.seed.value if problem.provenance.seed is not None else None
            ),
        }

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
        return slug or "problem"


NewtonQuestionGenerator = NewtonCalculationQuestionGenerator


__all__ = [
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "NewtonCalculationQuestionGenerator",
    "NewtonCalculationTemplate",
    "NewtonQuestionGenerator",
    "NewtonQuestionOptions",
]
