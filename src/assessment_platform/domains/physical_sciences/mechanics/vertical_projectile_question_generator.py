"""Deterministic canonical question generation for vertical projectiles."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from math import isclose

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
    Scenario,
    VisualReference,
)
from assessment_platform.curriculum.caps.physical_sciences import (
    GRADE_12,
    PHYSICAL_SCIENCES,
    CurriculumTopic,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    PositiveDirection,
    VerticalProjectileScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    EventType,
    VerticalProjectileSolution,
    VerticalProjectileSolver,
)
from assessment_platform.rendering.svg.projectile import (
    ProjectileDiagramOptions,
    ProjectileSvgRenderer,
)

VERTICAL_PROJECTILE_TOPIC_ID = "vertical-projectile-motion-1d"
GENERATOR_ID = "caps-grade-12-vertical-projectile-question-generator"
GENERATOR_VERSION = "1"
NUMERIC_TOLERANCE = 0.01


class QuestionTemplateId(StrEnum):
    ACCELERATION_DIRECTION = "acceleration-direction"
    TIME_TO_MAXIMUM_HEIGHT = "time-to-maximum-height"
    MAXIMUM_HEIGHT = "maximum-height"
    RETURN_TO_LAUNCH_POSITION = "return-to-launch-position"
    GROUND_IMPACT_TIME = "ground-impact-time"
    GROUND_IMPACT_VELOCITY = "ground-impact-velocity"


@dataclass(frozen=True, slots=True)
class _TemplateSpec:
    identifier: QuestionTemplateId
    marks: int
    required_event: EventType | None = None


_ACCELERATION = _TemplateSpec(QuestionTemplateId.ACCELERATION_DIRECTION, 1)
_TIME_TO_MAXIMUM = _TemplateSpec(
    QuestionTemplateId.TIME_TO_MAXIMUM_HEIGHT, 3, EventType.MAXIMUM_HEIGHT
)
_MAXIMUM_HEIGHT = _TemplateSpec(QuestionTemplateId.MAXIMUM_HEIGHT, 4, EventType.MAXIMUM_HEIGHT)
_RETURN_TO_LAUNCH = _TemplateSpec(
    QuestionTemplateId.RETURN_TO_LAUNCH_POSITION,
    3,
    EventType.RETURN_TO_LAUNCH_POSITION,
)
_GROUND_IMPACT_TIME = _TemplateSpec(
    QuestionTemplateId.GROUND_IMPACT_TIME, 3, EventType.GROUND_IMPACT
)
_GROUND_IMPACT_VELOCITY = _TemplateSpec(
    QuestionTemplateId.GROUND_IMPACT_VELOCITY, 4, EventType.GROUND_IMPACT
)


class VerticalProjectileQuestionGenerator:
    """Build one canonical question from authoritative projectile results.

    Template selection is deliberately deterministic and coverage-oriented. The
    seed is retained as provenance for reproducibility and future seeded
    variation; this first generator has no random selection to avoid hidden
    randomness and to keep the pedagogical template set stable.
    """

    def __init__(self, renderer: ProjectileSvgRenderer | None = None) -> None:
        self._renderer = renderer or ProjectileSvgRenderer()

    def generate(
        self,
        scenario: VerticalProjectileScenario,
        solution: VerticalProjectileSolution,
        curriculum_topic: CurriculumTopic,
        seed: GenerationSeed | None = None,
        include_visuals: bool = True,
    ) -> Question:
        self._validate_topic(curriculum_topic)
        if not isinstance(include_visuals, bool):
            raise ValueError("include_visuals must be a boolean")
        if seed is not None and scenario.seed is not None and seed != scenario.seed:
            raise ValueError("generation seed must match the scenario seed when both are provided")
        effective_seed = seed if seed is not None else scenario.seed

        solver = VerticalProjectileSolver(scenario)
        validation = solver.validate(solution)
        if not validation.valid or solution.event(EventType.LAUNCH) is None:
            raise ValueError(f"solution does not validate against scenario: {validation.errors}")

        templates = self._applicable_templates(solution)
        if len(templates) < 2:
            raise ValueError("scenario does not support the minimum multi-part question")

        question_identifier = f"vp-{self._slug(scenario.identifier)}"
        parts = tuple(
            self._build_part(question_identifier, index, template, scenario, solution)
            for index, template in enumerate(templates, start=1)
        )
        visuals = self._visuals(question_identifier, scenario, solution) if include_visuals else ()
        scenario_data = {
            "scenario_type": scenario.scenario_type.value,
            "launch_position_m": scenario.launch_position.value,
            "initial_velocity_m_per_s": scenario.initial_velocity.value,
            "gravitational_acceleration_m_per_s2": scenario.gravitational_acceleration.value,
            "positive_direction": scenario.positive_direction.value,
            "launch_direction": scenario.launch_direction.value,
            "assumptions": scenario.assumptions,
            "curriculum_topic": curriculum_topic.identifier,
        }
        return Question(
            identifier=question_identifier,
            prompt=self._stem(scenario),
            parts=parts,
            scenario=Scenario(scenario.identifier, scenario_data),
            visuals=visuals,
            provenance=GenerationProvenance(
                GENERATOR_ID,
                GENERATOR_VERSION,
                effective_seed,
                tuple(template.identifier.value for template in templates),
            ),
        )

    @staticmethod
    def _validate_topic(topic: CurriculumTopic) -> None:
        if topic.identifier != VERTICAL_PROJECTILE_TOPIC_ID:
            raise ValueError("generator requires the CAPS vertical-projectile topic")
        if topic.reference.grade != GRADE_12 or topic.reference.subject != PHYSICAL_SCIENCES:
            raise ValueError("generator requires Grade 12 CAPS Physical Sciences metadata")

    @staticmethod
    def _applicable_templates(
        solution: VerticalProjectileSolution,
    ) -> tuple[_TemplateSpec, ...]:
        maximum = solution.event(EventType.MAXIMUM_HEIGHT)
        returning = solution.event(EventType.RETURN_TO_LAUNCH_POSITION)
        impact = solution.event(EventType.GROUND_IMPACT)
        templates: list[_TemplateSpec] = [_ACCELERATION]
        if maximum is not None:
            templates.extend((_TIME_TO_MAXIMUM, _MAXIMUM_HEIGHT))
        if returning is not None and (
            impact is None or not isclose(returning.time.value, impact.time.value, abs_tol=1e-9)
        ):
            templates.append(_RETURN_TO_LAUNCH)
        if impact is not None:
            templates.extend((_GROUND_IMPACT_TIME, _GROUND_IMPACT_VELOCITY))
        return tuple(templates)

    @staticmethod
    def _stem(scenario: VerticalProjectileScenario) -> str:
        position = scenario.launch_position.value
        if position == 0:
            location = "the ground/reference level"
        else:
            location = f"a height of {position:g} m above the ground"

        speed = abs(scenario.initial_velocity.value)
        if scenario.launch_direction is LaunchDirection.UPWARD:
            action = f"is projected vertically upward at {speed:g} m/s from {location}"
        elif scenario.launch_direction is LaunchDirection.DOWNWARD:
            action = f"is projected vertically downward at {speed:g} m/s from {location}"
        else:
            action = f"is released from rest from {location}"

        gravity = abs(scenario.gravitational_acceleration.value)
        return (
            f"A ball {action}. Take {scenario.positive_direction.value} as positive. "
            f"Ignore air resistance and use g = {gravity:g} m/s²."
        )

    def _build_part(
        self,
        question_identifier: str,
        index: int,
        template: _TemplateSpec,
        scenario: VerticalProjectileScenario,
        solution: VerticalProjectileSolution,
    ) -> QuestionPart:
        identifier = f"{question_identifier}.{index}"
        if template.identifier is QuestionTemplateId.ACCELERATION_DIRECTION:
            return QuestionPart(
                identifier,
                "State the direction of the acceleration while the ball is in motion.",
                template.marks,
                ResponseSpecification(ResponseKind.SHORT_TEXT, suggested_line_count=1),
                ExpectedAnswer(ExpectedAnswerKind.TEXT, "downward"),
                self._scheme(
                    identifier,
                    (("direction", "Correctly identifies the downward direction", 1),),
                ),
            )

        event = solution.event(template.required_event) if template.required_event else None
        if event is None:
            raise ValueError(f"template {template.identifier} requires an unavailable event")
        if template.identifier is QuestionTemplateId.TIME_TO_MAXIMUM_HEIGHT:
            return self._numeric_part(
                identifier,
                "Calculate the time taken for the ball to reach maximum height.",
                template,
                event.time.value,
                "s",
                "time",
                ("valid relationship", "Uses a valid kinematic relationship", 1),
                ("substitution", "Substitutes the given values consistently", 1),
                ("result", "Obtains the correct time with unit", 1),
            )
        if template.identifier is QuestionTemplateId.MAXIMUM_HEIGHT:
            return self._numeric_part(
                identifier,
                "Calculate the maximum height of the ball above the ground/reference level.",
                template,
                self._physical_height(scenario, event.position),
                "m",
                "height",
                ("valid relationship", "Uses a valid kinematic relationship", 1),
                ("substitution", "Substitutes the given values consistently", 1),
                ("result", "Obtains the correct height", 1),
                ("unit", "States the answer in metres", 1),
            )
        if template.identifier is QuestionTemplateId.RETURN_TO_LAUNCH_POSITION:
            return self._numeric_part(
                identifier,
                "Calculate the time taken for the ball to return to its launch position.",
                template,
                event.time.value,
                "s",
                "return time",
                ("valid relationship", "Uses a valid kinematic relationship", 1),
                ("substitution", "Substitutes the given values consistently", 1),
                ("result", "Obtains the correct time with unit", 1),
            )
        if template.identifier is QuestionTemplateId.GROUND_IMPACT_TIME:
            return self._numeric_part(
                identifier,
                "Calculate the time taken for the ball to reach the ground/reference level.",
                template,
                event.time.value,
                "s",
                "impact time",
                ("valid relationship", "Uses a valid kinematic relationship", 1),
                ("substitution", "Substitutes the given values consistently", 1),
                ("result", "Obtains the correct time with unit", 1),
            )
        if template.identifier is QuestionTemplateId.GROUND_IMPACT_VELOCITY:
            return QuestionPart(
                identifier,
                "Determine the velocity of the ball when it reaches the ground/reference level.",
                template.marks,
                ResponseSpecification(
                    ResponseKind.NUMERIC,
                    suggested_line_count=1,
                    expects_final_answer=True,
                    expects_units=True,
                ),
                ExpectedAnswer(
                    ExpectedAnswerKind.NUMERIC,
                    event.velocity,
                    "m/s",
                    NUMERIC_TOLERANCE,
                ),
                self._scheme(
                    identifier,
                    (
                        ("method", "Uses a valid relationship for velocity", 1),
                        ("substitution", "Substitutes the given values consistently", 1),
                        ("result", "Obtains the correct signed velocity", 2),
                    ),
                ),
            )
        raise ValueError(f"unsupported question template: {template.identifier}")

    def _numeric_part(
        self,
        identifier: str,
        prompt: str,
        template: _TemplateSpec,
        value: float,
        unit: str,
        quantity: str,
        *criteria: tuple[str, str, int],
    ) -> QuestionPart:
        return QuestionPart(
            identifier,
            prompt,
            template.marks,
            ResponseSpecification(
                ResponseKind.CALCULATION,
                suggested_line_count=4,
                expects_working=True,
                expects_final_answer=True,
                expects_units=True,
                required_fields=(quantity,),
            ),
            ExpectedAnswer(ExpectedAnswerKind.NUMERIC, value, unit, NUMERIC_TOLERANCE),
            self._scheme(identifier, criteria),
        )

    @staticmethod
    def _scheme(
        part_identifier: str,
        criteria: tuple[tuple[str, str, int], ...],
    ) -> MarkingScheme:
        return MarkingScheme(
            sum(marks for _, _, marks in criteria),
            tuple(
                MarkingCriterion(f"{part_identifier}-{criterion_id}", description, marks)
                for criterion_id, description, marks in criteria
            ),
        )

    @staticmethod
    def _physical_height(scenario: VerticalProjectileScenario, coordinate: float) -> float:
        return (
            coordinate
            if scenario.positive_direction is PositiveDirection.UP
            else -coordinate
        )

    def _visuals(
        self,
        question_identifier: str,
        scenario: VerticalProjectileScenario,
        solution: VerticalProjectileSolution,
    ) -> tuple[VisualReference, ...]:
        document = self._renderer.render(
            scenario,
            solution,
            ProjectileDiagramOptions(show_numeric_values=False),
        )
        return (
            VisualReference(
                f"{question_identifier}-diagram",
                "image/svg+xml",
                document.markup,
                document.width,
                document.height,
            ),
        )

    @staticmethod
    def _slug(identifier: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", identifier.lower()).strip("-")
        return slug or "scenario"
