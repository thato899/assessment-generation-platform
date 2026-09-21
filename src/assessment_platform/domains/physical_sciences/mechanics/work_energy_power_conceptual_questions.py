"""Deterministic conceptual Work, Energy & Power questions and rubrics.

This module defines conceptual answer semantics only.  It deliberately has no
numerical solver dependency, generated scenario dependency, or learner-response
evaluation logic.
"""
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
from assessment_platform.curriculum.caps.physical_sciences import (
    CAPS,
    GRADE_12,
    PHYSICAL_SCIENCES,
    WORK_ENERGY_POWER_TOPIC_ID,
    CurriculumTopic,
)

GENERATOR_ID = "caps-grade-12-work-energy-power-conceptual-question-generator"
GENERATOR_VERSION = "1"


class WorkEnergyConceptualTemplate(StrEnum):
    """The bounded Grade 12 CAPS M5 conceptual question inventory."""

    WORK_DEFINITION = "work-energy.work.definition"
    WORK_IS_SCALAR = "work-energy.work.scalar"
    POSITIVE_NEGATIVE_ZERO_WORK = "work-energy.work.signs"
    PERPENDICULAR_ZERO_WORK = "work-energy.work.perpendicular"
    INDIVIDUAL_VS_NET_WORK = "work-energy.work.individual-vs-net"
    NET_WORK_AND_KINETIC_ENERGY = "work-energy.net-work.kinetic-energy"
    WORK_ENERGY_THEOREM = "work-energy.theorem.interpret"
    KINETIC_ENERGY_CONCEPT = "work-energy.kinetic-energy.concept"
    POTENTIAL_ENERGY_REFERENCE_LEVEL = "work-energy.potential-energy.reference-level"
    CONSERVATIVE_FORCE = "work-energy.force.conservative"
    CONSERVATIVE_VS_NON_CONSERVATIVE = "work-energy.force.conservative-vs-non-conservative"
    MECHANICAL_VS_TOTAL_ENERGY = "work-energy.energy.mechanical-vs-total"
    FRICTION_NON_CONSERVATIVE_WORK = "work-energy.friction.non-conservative-work"
    POWER_AS_RATE = "work-energy.power.rate"
    SAME_WORK_DIFFERENT_TIME = "work-energy.power.same-work-different-time"
    CONSTANT_SPEED_POWER_CONTEXT = "work-energy.power.constant-speed-context"
    PUMPING_POWER_ASSUMPTIONS = "work-energy.power.pumping-assumptions"


@dataclass(frozen=True, slots=True)
class WorkEnergyConceptualQuestionOptions:
    """Immutable options for the context-free conceptual generator."""

    include_visuals: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.include_visuals, bool):
            raise ValueError("include_visuals must be a boolean")


@dataclass(frozen=True, slots=True)
class _ConceptSpec:
    prompt: str
    concepts: tuple[str, ...]
    criteria: tuple[tuple[str, str, int], ...]
    response_kind: ResponseKind


def _spec(
    prompt: str,
    concepts: tuple[str, ...],
    criteria: tuple[tuple[str, str, int], ...],
    response_kind: ResponseKind = ResponseKind.SHORT_TEXT,
) -> _ConceptSpec:
    return _ConceptSpec(prompt, concepts, criteria, response_kind)


_SPECS: dict[WorkEnergyConceptualTemplate, _ConceptSpec] = {
    WorkEnergyConceptualTemplate.WORK_DEFINITION: _spec(
        "Explain what work means in the approved mechanics context.",
        ("force_displacement_relationship", "displacement_component", "force_alone_insufficient"),
        (
            ("relationship", "Relates work to a force acting through displacement.", 1),
            ("component", "Recognises that the force component along the displacement matters.", 1),
            ("force_alone", "States that the mere presence of a force does not guarantee work.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.WORK_IS_SCALAR: _spec(
        "Explain why work is a scalar quantity.",
        ("work_is_scalar", "signed_value_without_direction_vector", "individual_value"),
        (
            ("scalar", "Identifies work as scalar rather than a vector quantity.", 1),
            ("sign", "Explains that a signed work value does not give work a vector direction.", 1),
            ("meaning", "Keeps the scalar meaning distinct from force and displacement vectors.", 1),
        ),
    ),
    WorkEnergyConceptualTemplate.POSITIVE_NEGATIVE_ZERO_WORK: _spec(
        "Distinguish positive, negative and zero work using the force-displacement relationship.",
        ("positive_work", "negative_work", "zero_work", "relative_force_displacement_orientation"),
        (
            ("positive", "Relates positive work to a force component assisting displacement.", 1),
            ("negative", "Relates negative work to a force component opposing displacement.", 1),
            ("zero", "Allows zero work when the relevant force component contributes nothing.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.PERPENDICULAR_ZERO_WORK: _spec(
        "Explain why a force perpendicular to displacement does zero work.",
        ("perpendicular_force", "no_along_displacement_component", "large_force_not_sufficient"),
        (
            ("orientation", "Identifies the force as perpendicular to the displacement.", 1),
            ("component", "Explains that no component of the force acts along the displacement.", 1),
            ("magnitude", "States that a large force can still do zero work in this orientation.", 1),
        ),
    ),
    WorkEnergyConceptualTemplate.INDIVIDUAL_VS_NET_WORK: _spec(
        "Distinguish work done by one force from scalar net work.",
        ("individual_contribution", "scalar_combination", "relevant_forces", "net_work_total"),
        (
            ("individual", "Identifies the work contribution of a specified force.", 1),
            ("combination", "Describes net work as the scalar combination of relevant contributions.", 1),
            ("scope", "Keeps the selected force and the relevant set of forces distinct.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.NET_WORK_AND_KINETIC_ENERGY: _spec(
        "Explain what positive, negative and zero net work imply for kinetic energy.",
        ("positive_net_work_increases_kinetic_energy", "negative_net_work_decreases_kinetic_energy", "zero_net_work_no_change", "zero_net_work_not_necessarily_rest"),
        (
            ("positive", "Relates positive net work to an increase in kinetic energy.", 1),
            ("negative", "Relates negative net work to a decrease in kinetic energy.", 1),
            ("zero", "Relates zero net work to no change in kinetic energy.", 1),
            ("motion", "Does not conclude that zero net work requires the object to be at rest.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.WORK_ENERGY_THEOREM: _spec(
        "State and interpret the work-energy theorem.",
        ("net_work", "change_in_kinetic_energy", "scalar_relationship"),
        (
            ("net_work", "Identifies net work as the relevant work quantity.", 1),
            ("change", "Links net work to the change in kinetic energy.", 1),
            ("scalar", "Treats both quantities as scalar signed energy values.", 1),
        ),
    ),
    WorkEnergyConceptualTemplate.KINETIC_ENERGY_CONCEPT: _spec(
        "Explain kinetic energy as energy associated with motion.",
        ("energy_of_motion", "mass_dependence", "speed_magnitude", "velocity_sign_not_energy_sign"),
        (
            ("motion", "Identifies kinetic energy with energy associated with motion.", 1),
            ("mass", "Recognises that mass affects kinetic energy.", 1),
            ("speed", "Uses speed magnitude rather than a signed velocity direction.", 1),
            ("scalar", "Does not assign a negative kinetic energy to motion in the opposite direction.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.POTENTIAL_ENERGY_REFERENCE_LEVEL: _spec(
        "Explain how the selected reference level affects gravitational potential energy.",
        ("chosen_reference_level", "relative_value", "zero_convention", "negative_allowed"),
        (
            ("reference", "Identifies the reference level as a selected zero convention.", 1),
            ("relative", "Explains that potential energy is interpreted relative to that level.", 1),
            ("sign", "Recognises that the relative value may be positive, zero or negative.", 1),
            ("not_absolute", "Does not claim that gravitational potential energy has one universal zero.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.CONSERVATIVE_FORCE: _spec(
        "Describe the approved Grade 12 conceptual meaning of a conservative force.",
        ("path_independent_work", "mechanical_energy_context", "potential_energy_association"),
        (
            ("path", "States that the work of the force is independent of the path between positions.", 1),
            ("energy", "Connects the force with a mechanical-energy or potential-energy description.", 1),
            ("scope", "Keeps the explanation within the approved school-level mechanics context.", 1),
        ),
    ),
    WorkEnergyConceptualTemplate.CONSERVATIVE_VS_NON_CONSERVATIVE: _spec(
        "Distinguish conservative and non-conservative forces in the approved mechanics context.",
        ("conservative_path_independent", "non_conservative_path_dependent", "mechanical_energy_effect"),
        (
            ("conservative", "Describes conservative work as path independent in the approved model.", 1),
            ("non_conservative", "Describes non-conservative work as able to depend on the path or process.", 1),
            ("energy", "Relates the distinction to mechanical-energy accounting.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.MECHANICAL_VS_TOTAL_ENERGY: _spec(
        "Distinguish mechanical energy from total energy when non-conservative forces act.",
        ("mechanical_energy_kinetic_plus_potential", "mechanical_energy_may_change", "total_energy_conserved", "system_boundary"),
        (
            ("mechanical", "Identifies mechanical energy through kinetic and potential energy.", 1),
            ("change", "Recognises that non-conservative work can change mechanical energy.", 1),
            ("total", "States that total energy of the appropriately selected system remains conserved.", 1),
            ("distinction", "Keeps mechanical-energy change distinct from loss of total energy.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.FRICTION_NON_CONSERVATIVE_WORK: _spec(
        "Explain friction as an example of non-conservative work and its effect on mechanical energy.",
        ("friction_non_conservative", "mechanical_energy_change", "thermal_internal_transfer", "configuration_dependent_sign"),
        (
            ("classification", "Identifies friction as a non-conservative interaction in the approved model.", 1),
            ("mechanical", "Explains that friction can change mechanical energy.", 1),
            ("transfer", "Recognises transfer to internal or thermal energy within the total-energy account.", 1),
            ("care", "Does not claim that friction has one sign in every imaginable configuration.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.POWER_AS_RATE: _spec(
        "Explain what power means and distinguish it from work and energy.",
        ("power_rate", "work_per_time_meaning", "power_not_energy", "power_not_work"),
        (
            ("rate", "Defines power as a rate associated with doing work or transferring energy.", 1),
            ("work", "Keeps power distinct from the work quantity itself.", 1),
            ("energy", "Keeps power distinct from energy stored or transferred.", 1),
        ),
    ),
    WorkEnergyConceptualTemplate.SAME_WORK_DIFFERENT_TIME: _spec(
        "Explain why doing the same work in less time corresponds to greater average power.",
        ("same_work", "shorter_time", "greater_average_rate", "power_is_rate"),
        (
            ("same", "Keeps the amount of work the same in the comparison.", 1),
            ("time", "Identifies the shorter time interval.", 1),
            ("rate", "Explains that the shorter interval gives a greater average rate of doing work.", 1),
        ),
    ),
    WorkEnergyConceptualTemplate.CONSTANT_SPEED_POWER_CONTEXT: _spec(
        "Explain the approved constant-speed horizontal or inclined-plane power context.",
        ("constant_speed", "forces_can_still_act", "power_context", "rough_surface_possible"),
        (
            ("speed", "Identifies constant speed as unchanged speed, not absence of forces.", 1),
            ("forces", "Recognises that applied, contact or resistive forces can still act.", 1),
            ("context", "Keeps the explanation within the approved horizontal or inclined-plane power context.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    WorkEnergyConceptualTemplate.PUMPING_POWER_ASSUMPTIONS: _spec(
        "Explain the assumptions in the approved minimum ideal pumping-power model.",
        ("mass_flow_rate", "vertical_lift", "gravitational_field", "minimum_ideal_power", "efficiency_outside_model"),
        (
            ("flow", "Identifies mass flow rate as a required part of the pumping context.", 1),
            ("lift", "Identifies vertical lift or depth as a required part of the context.", 1),
            ("field", "Identifies the authored gravitational field as relevant.", 1),
            ("ideal", "Recognises that the requested power is minimum and ideal.", 1),
            ("efficiency", "Keeps motor efficiency outside the required CAPS model.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
}


class WorkEnergyConceptualQuestionGenerator:
    """Create one deterministic conceptual Question for a selected template."""

    def __init__(
        self,
        topic: CurriculumTopic,
        options: WorkEnergyConceptualQuestionOptions | None = None,
    ) -> None:
        self._validate_topic(topic)
        if options is not None and not isinstance(options, WorkEnergyConceptualQuestionOptions):
            raise ValueError("options must be WorkEnergyConceptualQuestionOptions")
        self.topic = topic
        self.options = options or WorkEnergyConceptualQuestionOptions()

    def generate(
        self,
        template: WorkEnergyConceptualTemplate,
        seed: GenerationSeed | None = None,
    ) -> Question:
        if not isinstance(template, WorkEnergyConceptualTemplate):
            raise ValueError("template must be a WorkEnergyConceptualTemplate")
        if seed is not None and not isinstance(seed, GenerationSeed):
            raise ValueError("seed must be a GenerationSeed")
        spec = _SPECS[template]
        question_id = f"wep-conceptual-v{GENERATOR_VERSION}-{template.value}"
        marks = sum(item[2] for item in spec.criteria)
        part_id = f"{question_id}.response"
        part = QuestionPart(
            identifier=part_id,
            prompt=spec.prompt,
            marks=marks,
            response_specification=ResponseSpecification(
                spec.response_kind,
                suggested_line_count=2 if spec.response_kind is ResponseKind.SHORT_TEXT else 5,
                expects_final_answer=True,
                required_fields=("key_points",),
            ),
            expected_answer=ExpectedAnswer(ExpectedAnswerKind.TEXT, spec.concepts),
            marking_scheme=MarkingScheme(
                marks,
                tuple(
                    MarkingCriterion(f"{template.value}.{key}", description, value)
                    for key, description, value in spec.criteria
                ),
            ),
        )
        return Question(
            identifier=question_id,
            prompt=spec.prompt,
            parts=(part,),
            provenance=GenerationProvenance(
                GENERATOR_ID,
                GENERATOR_VERSION,
                seed,
                (template.value,),
            ),
        )

    @staticmethod
    def _validate_topic(topic: CurriculumTopic) -> None:
        if not isinstance(topic, CurriculumTopic):
            raise ValueError("topic must be a CurriculumTopic")
        reference = topic.reference
        if topic.identifier != WORK_ENERGY_POWER_TOPIC_ID:
            raise ValueError("generator requires the CAPS Work, Energy & Power topic")
        if (
            reference.curriculum != CAPS
            or reference.subject != PHYSICAL_SCIENCES
            or reference.grade != GRADE_12
        ):
            raise ValueError("generator requires Grade 12 CAPS Physical Sciences metadata")
        if topic.domain.identifier != "mechanics":
            raise ValueError("generator requires the Mechanics domain")


WorkEnergyConceptualOptions = WorkEnergyConceptualQuestionOptions
WorkEnergyConceptualGenerator = WorkEnergyConceptualQuestionGenerator


__all__ = [
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "WorkEnergyConceptualGenerator",
    "WorkEnergyConceptualOptions",
    "WorkEnergyConceptualQuestionGenerator",
    "WorkEnergyConceptualQuestionOptions",
    "WorkEnergyConceptualTemplate",
]
