"""Solver-backed canonical calculation questions for Work, Energy & Power.

The generator owns wording and assessment packaging.  Every numeric answer is
read from :class:`WorkEnergySolver`; this module contains no physics equations.
"""
# ruff: noqa: E501

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

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
    CAPS,
    GRADE_12,
    PHYSICAL_SCIENCES,
    WORK_ENERGY_POWER_TOPIC_ID,
    CurriculumTopic,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power import (
    AlongPlaneWorkInput,
    HeightState,
    KineticState,
    MechanicalEnergyContext,
    NetWorkInput,
    UnknownValue,
    WorkContribution,
    WorkEnergyContext,
    WorkEnergyScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power_generation import (
    GeneratedWorkEnergyProblem,
    WorkEnergyGenerationFamily,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power_solver import (
    WorkEnergySolveError,
    WorkEnergySolver,
)
from assessment_platform.rendering.svg.work_energy_power import (
    WorkEnergyDiagramKind,
    WorkEnergyRenderOptions,
    WorkEnergySvgRenderer,
)

GENERATOR_ID: Final[str] = "caps-grade-12-work-energy-power-calculation-question-generator"
GENERATOR_VERSION: Final[str] = "1"
NUMERIC_TOLERANCE: Final[float] = 0.01


class WorkEnergyCalculationTemplate(StrEnum):
    WORK_BY_FORCE = "work-energy.work-by-force.calculate"
    NET_WORK = "work-energy.net-work.calculate"
    ALONG_PLANE_WORK = "work-energy.along-plane-work.calculate"
    KINETIC_ENERGY = "work-energy.kinetic-energy.calculate"
    GRAVITATIONAL_POTENTIAL_ENERGY = "work-energy.gravitational-potential-energy.calculate"
    WORK_ENERGY_NET_WORK = "work-energy.theorem-net-work.calculate"
    WORK_ENERGY_FINAL_SPEED = "work-energy.theorem-final-speed.calculate"
    WORK_ENERGY_INITIAL_SPEED = "work-energy.theorem-initial-speed.calculate"
    MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK = "work-energy.mechanical-non-conservative-work.calculate"
    MECHANICAL_ENERGY_FINAL_SPEED = "work-energy.mechanical-final-speed.calculate"
    AVERAGE_POWER = "work-energy.average-power.calculate"
    CONSTANT_SPEED_POWER = "work-energy.constant-speed-power.calculate"
    PUMPING_POWER = "work-energy.pumping-power.calculate"


@dataclass(frozen=True, slots=True)
class WorkEnergyQuestionOptions:
    """Immutable learner-safe calculation-question options."""

    include_visuals: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.include_visuals, bool):
            raise ValueError("include_visuals must be a boolean")


@dataclass(frozen=True, slots=True)
class _TemplateSpec:
    template: WorkEnergyCalculationTemplate
    marks: int
    unit: str
    diagram_kind: WorkEnergyDiagramKind | None


_SPECS: Final[dict[WorkEnergyGenerationFamily, _TemplateSpec]] = {
    WorkEnergyGenerationFamily.WORK_BY_FORCE: _TemplateSpec(
        WorkEnergyCalculationTemplate.WORK_BY_FORCE, 3, "J", WorkEnergyDiagramKind.WORK_CONTRIBUTIONS
    ),
    WorkEnergyGenerationFamily.NET_WORK: _TemplateSpec(
        WorkEnergyCalculationTemplate.NET_WORK, 4, "J", WorkEnergyDiagramKind.WORK_CONTRIBUTIONS
    ),
    WorkEnergyGenerationFamily.ALONG_PLANE_WORK: _TemplateSpec(
        WorkEnergyCalculationTemplate.ALONG_PLANE_WORK, 3, "J", WorkEnergyDiagramKind.ALONG_PLANE
    ),
    WorkEnergyGenerationFamily.KINETIC_ENERGY: _TemplateSpec(
        WorkEnergyCalculationTemplate.KINETIC_ENERGY, 3, "J", WorkEnergyDiagramKind.MOTION_STATES
    ),
    WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY: _TemplateSpec(
        WorkEnergyCalculationTemplate.GRAVITATIONAL_POTENTIAL_ENERGY, 4, "J", WorkEnergyDiagramKind.HEIGHT_STATES
    ),
    WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK: _TemplateSpec(
        WorkEnergyCalculationTemplate.WORK_ENERGY_NET_WORK, 3, "J", WorkEnergyDiagramKind.MOTION_STATES
    ),
    WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED: _TemplateSpec(
        WorkEnergyCalculationTemplate.WORK_ENERGY_FINAL_SPEED, 4, "m/s", WorkEnergyDiagramKind.MOTION_STATES
    ),
    WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED: _TemplateSpec(
        WorkEnergyCalculationTemplate.WORK_ENERGY_INITIAL_SPEED, 4, "m/s", WorkEnergyDiagramKind.MOTION_STATES
    ),
    WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK: _TemplateSpec(
        WorkEnergyCalculationTemplate.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK, 4, "J", WorkEnergyDiagramKind.HEIGHT_STATES
    ),
    WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED: _TemplateSpec(
        WorkEnergyCalculationTemplate.MECHANICAL_ENERGY_FINAL_SPEED, 5, "m/s", WorkEnergyDiagramKind.HEIGHT_STATES
    ),
    WorkEnergyGenerationFamily.AVERAGE_POWER: _TemplateSpec(
        WorkEnergyCalculationTemplate.AVERAGE_POWER, 3, "W", None
    ),
    WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER: _TemplateSpec(
        WorkEnergyCalculationTemplate.CONSTANT_SPEED_POWER, 3, "W", WorkEnergyDiagramKind.CONSTANT_SPEED_SURFACE
    ),
    WorkEnergyGenerationFamily.PUMPING_POWER: _TemplateSpec(
        WorkEnergyCalculationTemplate.PUMPING_POWER, 4, "W", WorkEnergyDiagramKind.PUMPING
    ),
}


class WorkEnergyCalculationQuestionGenerator:
    """Create one canonical calculation part from a generated M5 problem."""

    def __init__(
        self,
        topic: CurriculumTopic,
        options: WorkEnergyQuestionOptions | None = None,
    ) -> None:
        self._validate_topic(topic)
        self.topic = topic
        self.options = options or WorkEnergyQuestionOptions()
        self._renderer = WorkEnergySvgRenderer()

    def generate(self, problem: GeneratedWorkEnergyProblem) -> Question:
        if not isinstance(problem, GeneratedWorkEnergyProblem):
            raise ValueError("problem must be a GeneratedWorkEnergyProblem")
        try:
            spec = _SPECS[problem.family]
        except KeyError as error:
            raise ValueError("generated family has no supported calculation template") from error
        question_id = f"wep-question-v{GENERATOR_VERSION}-{self._slug(problem.identifier)}"
        value = self._answer(problem)
        part_id = f"{question_id}.{spec.template.value}"
        part = self._part(part_id, spec, value)
        visuals = self._visuals(question_id, problem, spec)
        return Question(
            identifier=question_id,
            prompt=self._prompt(problem),
            parts=(part,),
            scenario=Scenario(problem.identifier, self._scenario_data(problem)),
            visuals=visuals,
            provenance=GenerationProvenance(
                GENERATOR_ID,
                GENERATOR_VERSION,
                problem.provenance.seed,
                (spec.template.value,),
            ),
        )

    def _answer(self, problem: GeneratedWorkEnergyProblem) -> float:
        solver = WorkEnergySolver(problem.scenario)
        family = problem.family
        try:
            if family is WorkEnergyGenerationFamily.WORK_BY_FORCE:
                authored = self._net_input(problem.scenario)
                return solver.work_by_force(authored.contributions[0]).work.value
            if family is WorkEnergyGenerationFamily.NET_WORK:
                return solver.net_work(self._net_input(problem.scenario)).net_work.value
            if family is WorkEnergyGenerationFamily.ALONG_PLANE_WORK:
                return solver.along_plane_work(self._along_input(problem.scenario)).work.value
            if family is WorkEnergyGenerationFamily.KINETIC_ENERGY:
                return solver.kinetic_energy(problem.scenario.kinetic_states[0]).kinetic_energy.value
            if family is WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY:
                if problem.authored_mass is None:
                    raise ValueError("potential-energy problem has no authored mass")
                return solver.potential_energy(problem.authored_mass, problem.scenario.height_states[0]).potential_energy.value
            if family in (
                WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK,
                WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED,
                WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED,
            ):
                work_result = solver.work_energy(problem.scenario.work_energy_contexts[0])
                if family is WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK:
                    return work_result.net_work.value
                state = (
                    work_result.final_state
                    if family is WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED
                    else work_result.initial_state
                )
                if isinstance(state.speed, UnknownValue):
                    raise ValueError("solver returned no resolved target speed")
                return state.speed.value
            if family in (
                WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK,
                WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED,
            ):
                mechanical_result = solver.mechanical_energy(
                    problem.scenario.mechanical_energy_contexts[0]
                )
                if family is WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK:
                    return mechanical_result.non_conservative_work.value
                if mechanical_result.final_speed is None:
                    raise ValueError("solver result does not expose the resolved final speed")
                return mechanical_result.final_speed.value
            if family is WorkEnergyGenerationFamily.AVERAGE_POWER:
                return solver.average_power(problem.scenario.average_power_inputs[0]).power.value
            if family is WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER:
                return solver.constant_speed_power(problem.scenario.constant_speed_power_inputs[0]).power.value
            if family is WorkEnergyGenerationFamily.PUMPING_POWER:
                return solver.pumping_power(problem.scenario.pumping_power_inputs[0]).power.value
        except WorkEnergySolveError as error:
            raise ValueError(
                f"Work, Energy & Power calculation is not applicable: {error.reason.value}"
            ) from error
        raise ValueError("generated family has no supported calculation template")

    @staticmethod
    def _part(identifier: str, spec: _TemplateSpec, value: float) -> QuestionPart:
        criteria: tuple[MarkingCriterion, ...] = (
            MarkingCriterion(f"{identifier}.method", "Applies the appropriate Work, Energy & Power relationship.", spec.marks - 2),
            MarkingCriterion(f"{identifier}.substitution", "Substitutes the authored data consistently, including sign conventions.", 1),
            MarkingCriterion(f"{identifier}.answer", f"States the correct final answer with unit {spec.unit}.", 1),
        )
        # A two-mark template still needs positive criteria whose sum reconciles.
        if spec.marks == 2:
            criteria = (
                MarkingCriterion(f"{identifier}.method", "Applies the appropriate relationship and authored sign convention.", 1),
                MarkingCriterion(f"{identifier}.answer", f"States the correct final answer with unit {spec.unit}.", 1),
            )
        return QuestionPart(
            identifier,
            WorkEnergyCalculationQuestionGenerator._part_prompt(spec.template),
            spec.marks,
            ResponseSpecification(
                ResponseKind.CALCULATION,
                suggested_line_count=4,
                expects_working=True,
                expects_final_answer=True,
                expects_units=True,
                required_fields=("working", "final"),
            ),
            ExpectedAnswer(ExpectedAnswerKind.NUMERIC, value, spec.unit, NUMERIC_TOLERANCE),
            MarkingScheme(spec.marks, criteria),
        )

    @staticmethod
    def _part_prompt(template: WorkEnergyCalculationTemplate) -> str:
        return {
            WorkEnergyCalculationTemplate.WORK_BY_FORCE: "Calculate the work done by the stated force.",
            WorkEnergyCalculationTemplate.NET_WORK: "Calculate the signed net work from the listed force contributions.",
            WorkEnergyCalculationTemplate.ALONG_PLANE_WORK: "Calculate the signed work done by the resultant force along the plane.",
            WorkEnergyCalculationTemplate.KINETIC_ENERGY: "Calculate the kinetic energy of the stated object.",
            WorkEnergyCalculationTemplate.GRAVITATIONAL_POTENTIAL_ENERGY: "Calculate the gravitational potential energy relative to the stated reference level.",
            WorkEnergyCalculationTemplate.WORK_ENERGY_NET_WORK: "Calculate the signed net work using the work-energy theorem.",
            WorkEnergyCalculationTemplate.WORK_ENERGY_FINAL_SPEED: "Calculate the final speed.",
            WorkEnergyCalculationTemplate.WORK_ENERGY_INITIAL_SPEED: "Calculate the initial speed.",
            WorkEnergyCalculationTemplate.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK: "Calculate the signed non-conservative work.",
            WorkEnergyCalculationTemplate.MECHANICAL_ENERGY_FINAL_SPEED: "Calculate the final speed using the mechanical-energy relationship.",
            WorkEnergyCalculationTemplate.AVERAGE_POWER: "Calculate the signed average power.",
            WorkEnergyCalculationTemplate.CONSTANT_SPEED_POWER: "Calculate the power for the constant-speed motion.",
            WorkEnergyCalculationTemplate.PUMPING_POWER: "Calculate the minimum ideal pumping power.",
        }[template]

    def _visuals(
        self, question_id: str, problem: GeneratedWorkEnergyProblem, spec: _TemplateSpec
    ) -> tuple[VisualReference, ...]:
        if not self.options.include_visuals or spec.diagram_kind is None:
            return ()
        document = self._renderer.render(
            problem.scenario,
            WorkEnergyRenderOptions(diagram_kind=spec.diagram_kind),
        )
        return (
            VisualReference(
                f"{question_id}-diagram",
                "image/svg+xml",
                document.markup,
                document.width,
                document.height,
            ),
        )

    def _prompt(self, problem: GeneratedWorkEnergyProblem) -> str:
        scenario = problem.scenario
        family = problem.family
        details: list[str] = []
        if family is WorkEnergyGenerationFamily.WORK_BY_FORCE:
            details.append(self._contribution_text(self._net_input(scenario).contributions[0]))
        elif family is WorkEnergyGenerationFamily.NET_WORK:
            details.append("The authored contributions are " + "; ".join(self._contribution_text(item) for item in self._net_input(scenario).contributions))
        elif family is WorkEnergyGenerationFamily.ALONG_PLANE_WORK:
            authored = self._along_input(scenario)
            details.append(self._along_text(authored))
        elif family is WorkEnergyGenerationFamily.KINETIC_ENERGY:
            details.append(self._kinetic_text(scenario.kinetic_states[0]))
        elif family is WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY:
            details.append(self._height_text(scenario.height_states[0]))
            if problem.authored_mass is not None:
                details.append(f"The mass is {problem.authored_mass.value:g} kg")
        elif family in (WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK, WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED, WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED):
            details.append(self._work_energy_text(scenario.work_energy_contexts[0]))
        elif family in (WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK, WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED):
            details.append(self._mechanical_text(scenario.mechanical_energy_contexts[0]))
        elif family is WorkEnergyGenerationFamily.AVERAGE_POWER:
            average_input = scenario.average_power_inputs[0]
            details.append(
                self._value_text("work", average_input.work, "J")
                + " and "
                + self._value_text("time", average_input.time, "s")
            )
        elif family is WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER:
            constant_input = scenario.constant_speed_power_inputs[0]
            details.append(
                self._value_text("force along motion", constant_input.force_along_motion, "N")
                + ", "
                + self._value_text("speed", constant_input.speed, "m/s")
                + f", on a {constant_input.surface.value} surface"
            )
        elif family is WorkEnergyGenerationFamily.PUMPING_POWER:
            pumping_input = scenario.pumping_power_inputs[0]
            details.append(
                ", ".join(
                    (
                        self._value_text("mass flow rate", pumping_input.mass_flow_rate, "kg/s"),
                        self._value_text("lift", pumping_input.lift, "m"),
                        self._value_text(
                            "gravitational field", pumping_input.gravitational_field, "m/s²"
                        ),
                    )
                )
            )
        return "Use the authored SI data. " + ". ".join(details) + " State your answer with the correct SI unit."

    @staticmethod
    def _value_text(name: str, value: object, unit: str) -> str:
        if isinstance(value, UnknownValue):
            return f"{name} is not supplied"
        numeric = getattr(value, "value", None)
        if not isinstance(numeric, (int, float)):
            raise ValueError(f"{name} has no authored numeric value")
        return f"{name} = {numeric:g} {unit}"

    @classmethod
    def _contribution_text(cls, item: WorkContribution) -> str:
        return f"{item.identifier}: {cls._value_text('force', item.force_magnitude, 'N')}, {cls._value_text('displacement', item.displacement, 'm')}, {cls._value_text('angle', item.angle, 'degrees')}"

    @classmethod
    def _along_text(cls, item: AlongPlaneWorkInput) -> str:
        return f"resultant force along the plane: {cls._value_text('force', item.resultant_force, 'N')}, {cls._value_text('displacement', item.displacement, 'm')}"

    @classmethod
    def _kinetic_text(cls, item: KineticState) -> str:
        return f"{item.state.value} state: {cls._value_text('mass', item.mass, 'kg')}, {cls._value_text('speed', item.speed, 'm/s')}"

    @classmethod
    def _height_text(cls, item: HeightState) -> str:
        return f"{item.state.value} height relative to {item.reference_level.identifier}: {cls._value_text('height', item.height, 'm')}, {cls._value_text('gravitational field', item.gravitational_field, 'm/s²')}"

    @classmethod
    def _work_energy_text(cls, item: WorkEnergyContext) -> str:
        text = f"{cls._kinetic_text(item.initial_state)}; {cls._kinetic_text(item.final_state)}"
        if not isinstance(item.net_work, UnknownValue):
            text += f"; {cls._value_text('net work', item.net_work, 'J')}"
        elif isinstance(item.work_input, NetWorkInput):
            text += "; authored work contributions: " + "; ".join(
                cls._contribution_text(contribution) for contribution in item.work_input.contributions
            )
        elif isinstance(item.work_input, AlongPlaneWorkInput):
            text += "; " + cls._along_text(item.work_input)
        return text

    @classmethod
    def _mechanical_text(cls, item: MechanicalEnergyContext) -> str:
        text = f"{cls._kinetic_text(item.initial_state)}; {cls._kinetic_text(item.final_state)}; {cls._height_text(item.initial_height)}; {cls._height_text(item.final_height)}"
        if not isinstance(item.non_conservative_work, UnknownValue):
            text += f"; {cls._value_text('non-conservative work', item.non_conservative_work, 'J')}"
        return text

    @staticmethod
    def _net_input(scenario: WorkEnergyScenario) -> NetWorkInput:
        for item in scenario.work_inputs:
            if isinstance(item, NetWorkInput):
                return item
        raise ValueError("scenario has no authored NetWorkInput")

    @staticmethod
    def _along_input(scenario: WorkEnergyScenario) -> AlongPlaneWorkInput:
        for item in scenario.work_inputs:
            if isinstance(item, AlongPlaneWorkInput):
                return item
        raise ValueError("scenario has no authored AlongPlaneWorkInput")

    @staticmethod
    def _validate_topic(topic: CurriculumTopic) -> None:
        if not isinstance(topic, CurriculumTopic):
            raise ValueError("topic must be a CurriculumTopic")
        reference = topic.reference
        if topic.identifier != WORK_ENERGY_POWER_TOPIC_ID:
            raise ValueError("generator requires the CAPS Work, Energy & Power topic")
        if reference.curriculum != CAPS or reference.subject != PHYSICAL_SCIENCES or reference.grade != GRADE_12:
            raise ValueError("generator requires Grade 12 CAPS Physical Sciences metadata")
        if topic.domain.identifier != "mechanics":
            raise ValueError("generator requires the Mechanics domain")

    @staticmethod
    def _scenario_data(problem: GeneratedWorkEnergyProblem) -> dict[str, str]:
        return {
            "curriculum_topic": WORK_ENERGY_POWER_TOPIC_ID,
            "grade": "12",
            "domain": "mechanics",
            "family": problem.family.value,
            "difficulty": problem.difficulty.value,
        }

    @staticmethod
    def _slug(value: str) -> str:
        slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
        return slug or "problem"


WorkEnergyQuestionGenerator = WorkEnergyCalculationQuestionGenerator


__all__ = [
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "NUMERIC_TOLERANCE",
    "WorkEnergyCalculationQuestionGenerator",
    "WorkEnergyCalculationTemplate",
    "WorkEnergyQuestionGenerator",
    "WorkEnergyQuestionOptions",
]
