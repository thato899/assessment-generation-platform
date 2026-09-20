"""Deterministic conceptual Newton questions and machine-readable rubrics."""

from __future__ import annotations

import re
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
    Scenario,
    VisualReference,
)
from assessment_platform.curriculum.caps.physical_sciences import (
    GRADE_11,
    PHYSICAL_SCIENCES,
    CurriculumTopic,
)
from assessment_platform.domains.physical_sciences.mechanics.newton_generation import (
    NewtonGeneratedProblem,
)
from assessment_platform.domains.physical_sciences.mechanics.newtons_laws import (
    NewtonScenario,
)
from assessment_platform.rendering.svg.newton import (
    NewtonDiagramKind,
    NewtonRenderOptions,
    NewtonSvgRenderer,
)

GENERATOR_ID = "caps-grade-11-newton-conceptual-question-generator"
GENERATOR_VERSION = "1"
NEWTONS_LAWS_TOPIC_ID = "newtons-laws"


class NewtonConceptualTemplate(StrEnum):
    NEWTON_FIRST_LAW = "newton.first-law.statement"
    NEWTON_SECOND_LAW = "newton.second-law.statement"
    NEWTON_THIRD_LAW = "newton.third-law.statement"
    ACTION_REACTION_PAIR = "newton.action-reaction.identify"
    ZERO_RESULTANT_MOTION = "newton.zero-resultant.motion"
    EQUILIBRIUM = "newton.equilibrium.distinguish"
    MASS_VS_WEIGHT = "newton.mass-weight.distinguish"
    WEIGHT_VS_APPARENT_WEIGHT = "newton.weight-apparent-weight.distinguish"
    NORMAL_FORCE = "newton.normal-force.concept"
    STATIC_VS_KINETIC_FRICTION = "newton.friction.static-kinetic.distinguish"
    STATIC_FRICTION_LIMIT = "newton.friction.static-limit.concept"
    SYSTEM_AND_ENVIRONMENT = "newton.system-environment.distinguish"
    INTERNAL_VS_EXTERNAL_FORCE = "newton.internal-external.distinguish"
    FREE_BODY_DIAGRAM = "newton.free-body-diagram.interpret"
    FORCE_DIAGRAM_VS_FBD = "newton.force-diagram-fbd.distinguish"
    FORCE_TYPE_IDENTIFICATION = "newton.force-types.identify"
    LIGHT_STRING_ASSUMPTIONS = "newton.string-assumptions.concept"
    UNIVERSAL_GRAVITATION = "newton.universal-gravitation.concept"
    APPARENT_WEIGHTLESSNESS = "newton.apparent-weightlessness.concept"
    MODEL_ASSUMPTIONS = "newton.model-assumptions.identify"


@dataclass(frozen=True, slots=True)
class NewtonConceptualQuestionOptions:
    """Immutable conceptual-generation options."""

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


_SPECS: dict[NewtonConceptualTemplate, _ConceptSpec] = {
    NewtonConceptualTemplate.NEWTON_FIRST_LAW: _spec(
        "State Newton's First Law precisely.",
        (
            "rest_or_constant_velocity",
            "zero_resultant_preserves_motion",
            "nonzero_resultant_changes_motion",
        ),
        (
            ("state", "Includes rest or constant velocity as the unchanged state.", 1),
            ("resultant", "Relates the unchanged state to a zero resultant/net force.", 1),
            ("change", "States that a non-zero resultant changes the motion.", 1),
        ),
    ),
    NewtonConceptualTemplate.NEWTON_SECOND_LAW: _spec(
        "State Newton's Second Law for constant mass using precise terms.",
        ("resultant_force", "acceleration_relationship", "same_direction", "constant_mass"),
        (
            ("resultant", "Uses resultant/net force rather than an isolated force.", 1),
            ("relationship", "Relates the resultant force to acceleration for constant mass.", 1),
            ("direction", "Recognises that acceleration has the resultant-force direction.", 1),
            ("mass", "Keeps the constant-mass condition explicit.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.NEWTON_THIRD_LAW: _spec(
        "State Newton's Third Law for one interaction.",
        ("same_interaction", "equal_magnitude", "opposite_direction", "different_bodies"),
        (
            ("interaction", "Identifies one interaction pair.", 1),
            ("magnitude", "States that the pair has equal magnitudes.", 1),
            ("direction", "States that the directions are opposite.", 1),
            ("ownership", "States that the two forces act on different bodies.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.ACTION_REACTION_PAIR: _spec(
        "Identify the partner force and state each force's source and target.",
        ("same_interaction", "source_target_ownership", "different_bodies", "simultaneous_pair"),
        (
            ("pair", "Links the two forces as one interaction pair.", 1),
            ("ownership", "Identifies which body exerts and receives each force.", 1),
            ("bodies", "Places the partner forces on different bodies.", 1),
            ("simultaneous", "Treats the pair as simultaneous parts of one interaction.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.ZERO_RESULTANT_MOTION: _spec(
        "Can an object move while its resultant force is zero? Explain.",
        ("yes", "constant_velocity", "zero_acceleration", "not_necessarily_rest"),
        (
            ("possibility", "Recognises that motion is possible.", 1),
            ("constant", "Identifies constant velocity.", 1),
            ("acceleration", "Relates zero resultant to zero acceleration.", 1),
            ("rest", "Does not restrict zero-resultant motion to rest.", 1),
        ),
    ),
    NewtonConceptualTemplate.EQUILIBRIUM: _spec(
        "Distinguish equilibrium from non-equilibrium motion.",
        (
            "equilibrium_zero_resultant",
            "non_equilibrium_nonzero_resultant",
            "constant_velocity_possible",
        ),
        (
            ("equilibrium", "Defines equilibrium using a zero resultant force.", 1),
            ("non_equilibrium", "Defines non-equilibrium using a non-zero resultant force.", 1),
            ("motion", "Allows rest or constant velocity in equilibrium.", 1),
        ),
    ),
    NewtonConceptualTemplate.MASS_VS_WEIGHT: _spec(
        "Distinguish mass from weight, including units and physical meaning.",
        (
            "mass_inertial_property",
            "mass_kg",
            "weight_gravitational_force",
            "weight_N",
            "field_dependence",
        ),
        (
            ("mass", "Describes mass as an inertial property measured in kilograms.", 1),
            ("weight", "Describes weight as a gravitational force measured in newtons.", 1),
            ("field", "Recognises that weight depends on the gravitational field.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.WEIGHT_VS_APPARENT_WEIGHT: _spec(
        "Distinguish gravitational weight from apparent weight.",
        ("weight_gravitational_force", "apparent_support_force", "not_necessarily_gravity_change"),
        (
            ("weight", "Identifies gravitational force as actual weight.", 1),
            ("support", "Identifies apparent weight with the relevant support/contact force.", 1),
            (
                "distinction",
                "Does not interpret apparent-weight change as automatic removal of gravity.",
                1,
            ),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.NORMAL_FORCE: _spec(
        "What is the normal force at a contact surface?",
        ("contact_force", "perpendicular_to_surface", "not_universal_weight_equality"),
        (
            ("contact", "Identifies the normal force as a contact force.", 1),
            ("direction", "States that it is perpendicular to the contact surface.", 1),
            ("boundary", "Does not define it as a universal equality with weight.", 1),
        ),
    ),
    NewtonConceptualTemplate.STATIC_VS_KINETIC_FRICTION: _spec(
        "Distinguish static friction from kinetic friction.",
        (
            "static_no_sliding",
            "static_adapts_to_tendency",
            "kinetic_sliding",
            "parallel_contact_surface",
        ),
        (
            ("static", "Describes static friction when contact surfaces do not slide.", 1),
            ("kinetic", "Describes kinetic friction during sliding.", 1),
            (
                "direction",
                "Relates friction to relative motion or its tendency along the surface.",
                1,
            ),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.STATIC_FRICTION_LIMIT: _spec(
        "Explain the limiting value of static friction.",
        ("maximum_static", "threshold_of_sliding", "not_always_required_value"),
        (
            ("maximum", "Identifies limiting static friction as the maximum static value.", 1),
            ("threshold", "Links it to impending/sliding threshold.", 1),
            ("adaptation", "Recognises that ordinary static friction need not be at its limit.", 1),
        ),
    ),
    NewtonConceptualTemplate.SYSTEM_AND_ENVIRONMENT: _spec(
        "Distinguish a selected system from its environment.",
        ("selected_objects_system", "outside_objects_environment", "boundary_context"),
        (
            ("system", "Identifies the selected object or objects as the system.", 1),
            (
                "environment",
                "Identifies relevant objects outside the system as the environment.",
                1,
            ),
            ("boundary", "Recognises that the classification depends on the chosen boundary.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.INTERNAL_VS_EXTERNAL_FORCE: _spec(
        "Distinguish internal and external forces for a selected system.",
        (
            "internal_inside_system",
            "external_from_environment",
            "boundary_dependent",
            "not_third_law_definition",
        ),
        (
            ("internal", "Identifies interactions between bodies inside the selected system.", 1),
            ("external", "Identifies a source outside the system acting on a system body.", 1),
            ("boundary", "Recognises that the classification changes with system choice.", 1),
            ("third_law", "Keeps system classification distinct from third-law pairing.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.FREE_BODY_DIAGRAM: _spec(
        "Explain what a correct free-body diagram represents.",
        ("one_selected_body", "forces_on_body", "force_arrows", "exclude_forces_exerted_by_body"),
        (
            ("isolate", "Isolates one selected body.", 1),
            ("acting", "Includes forces acting on that body.", 1),
            ("arrows", "Uses arrows to represent force directions.", 1),
            ("ownership", "Excludes forces exerted by the selected body on another body.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.FORCE_DIAGRAM_VS_FBD: _spec(
        "Distinguish a force/system diagram from a free-body diagram.",
        ("system_context", "fbd_one_body", "fbd_acting_forces"),
        (
            (
                "context",
                "Describes a force/system diagram as retaining relevant interaction context.",
                1,
            ),
            ("isolation", "Describes a free-body diagram as isolating one body.", 1),
            ("ownership", "Limits an FBD to forces acting on its selected body.", 1),
        ),
    ),
    NewtonConceptualTemplate.FORCE_TYPE_IDENTIFICATION: _spec(
        "Identify the approved force types that may appear in a Newton force diagram.",
        ("weight", "normal", "friction", "applied", "tension"),
        (
            ("types", "Identifies weight, normal, friction, applied and tension forces.", 2),
            ("semantics", "Distinguishes force type by its interaction/source meaning.", 1),
        ),
    ),
    NewtonConceptualTemplate.LIGHT_STRING_ASSUMPTIONS: _spec(
        "Explain the assumptions represented by a light, taut and inextensible string.",
        ("negligible_string_mass", "taut", "inextensible", "tension_along_string"),
        (
            ("mass", "Recognises negligible string mass.", 1),
            ("taut", "Recognises that the string is taut.", 1),
            ("length", "Recognises that an inextensible string keeps its length.", 1),
            ("tension", "Places tension along the string.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.UNIVERSAL_GRAVITATION: _spec(
        "Describe the approved conceptual model of universal gravitation.",
        (
            "every_pair_attracts",
            "line_of_centres",
            "mass_dependence",
            "separation_dependence",
            "equal_opposite_pair",
        ),
        (
            ("attraction", "States that each pair of masses attracts.", 1),
            ("direction", "Places the interaction along the line joining centres.", 1),
            ("dependence", "Recognises dependence on masses and separation.", 1),
            ("pair", "Recognises equal and opposite interaction forces on the two bodies.", 1),
        ),
        ResponseKind.LONG_TEXT,
    ),
    NewtonConceptualTemplate.APPARENT_WEIGHTLESSNESS: _spec(
        "Explain apparent weightlessness in the approved contact-force context.",
        ("support_force_zero", "gravity_may_exist", "not_gravity_absent"),
        (
            ("support", "Identifies an absent or zero support/contact force.", 1),
            ("gravity", "Allows the gravitational field to remain present.", 1),
            ("distinction", "Does not equate apparent weightlessness with zero gravity.", 1),
        ),
    ),
    NewtonConceptualTemplate.MODEL_ASSUMPTIONS: _spec(
        "Identify the modelling assumptions used for these Newton questions.",
        ("inertial_frame", "constant_mass", "air_resistance_neglected"),
        (
            ("frame", "Identifies an inertial reference frame.", 1),
            ("mass", "Identifies constant mass.", 1),
            ("air", "Identifies neglected air resistance.", 1),
        ),
    ),
}


class NewtonConceptualQuestionGenerator:
    """Create conceptual canonical Questions without numerical solving."""

    def __init__(
        self,
        topic: CurriculumTopic,
        options: NewtonConceptualQuestionOptions | None = None,
    ) -> None:
        if not isinstance(topic, CurriculumTopic):
            raise ValueError("topic must be a CurriculumTopic")
        if topic.identifier != NEWTONS_LAWS_TOPIC_ID:
            raise ValueError("generator requires the CAPS Newton's Laws topic")
        if topic.reference.grade != GRADE_11 or topic.reference.subject != PHYSICAL_SCIENCES:
            raise ValueError("generator requires Grade 11 CAPS Physical Sciences metadata")
        if options is not None and not isinstance(options, NewtonConceptualQuestionOptions):
            raise ValueError("options must be NewtonConceptualQuestionOptions")
        self.topic = topic
        self.options = options or NewtonConceptualQuestionOptions()
        self._renderer = NewtonSvgRenderer()

    def generate(
        self,
        template: NewtonConceptualTemplate,
        seed: GenerationSeed | None = None,
        context: NewtonGeneratedProblem | NewtonScenario | None = None,
    ) -> Question:
        if not isinstance(template, NewtonConceptualTemplate):
            raise ValueError("template must be a NewtonConceptualTemplate")
        if seed is not None and not isinstance(seed, GenerationSeed):
            raise ValueError("seed must be a GenerationSeed")
        scenario, source_id, source_seed = self._context(context)
        spec = _SPECS[template]
        prompt = self._context_prompt(template, spec.prompt, scenario)
        concepts, criteria = self._context_semantics(template, spec, scenario)
        question_id = f"newton-conceptual-v{GENERATOR_VERSION}-{template.value}"
        if source_id is not None:
            question_id += f"-{self._slug(source_id)}"
        part_id = f"{question_id}.response"
        marks = sum(item[2] for item in criteria)
        part = QuestionPart(
            identifier=part_id,
            prompt=prompt,
            marks=marks,
            response_specification=ResponseSpecification(
                spec.response_kind,
                suggested_line_count=2 if spec.response_kind is ResponseKind.SHORT_TEXT else 5,
                expects_final_answer=True,
                required_fields=("key_points",),
            ),
            expected_answer=ExpectedAnswer(ExpectedAnswerKind.TEXT, concepts),
            marking_scheme=MarkingScheme(
                marks,
                tuple(
                    MarkingCriterion(f"{template.value}.{key}", description, value)
                    for key, description, value in criteria
                ),
            ),
        )
        visuals: tuple[VisualReference, ...] = ()
        if self.options.include_visuals and scenario is not None:
            visuals = (self._visual(question_id, template, scenario),)
        scenario_data = None
        if scenario is not None:
            scenario_data = Scenario(
                scenario.identifier,
                {
                    "curriculum_topic": NEWTONS_LAWS_TOPIC_ID,
                    "grade": 11,
                    "template": template.value,
                    "source_scenario": scenario.identifier,
                    "system_body_ids": scenario.system.body_ids,
                },
            )
        return Question(
            identifier=question_id,
            prompt=prompt,
            parts=(part,),
            scenario=scenario_data,
            visuals=visuals,
            provenance=GenerationProvenance(
                GENERATOR_ID,
                GENERATOR_VERSION,
                seed if seed is not None else source_seed,
                (template.value,),
            ),
        )

    @staticmethod
    def _context(
        context: NewtonGeneratedProblem | NewtonScenario | None,
    ) -> tuple[NewtonScenario | None, str | None, GenerationSeed | None]:
        if context is None:
            return None, None, None
        if isinstance(context, NewtonGeneratedProblem):
            return context.scenario, context.scenario.identifier, context.provenance.seed
        if isinstance(context, NewtonScenario):
            return context, context.identifier, None
        raise ValueError("context must be a generated Newton problem or NewtonScenario")

    @staticmethod
    def _context_prompt(
        template: NewtonConceptualTemplate, prompt: str, scenario: NewtonScenario | None
    ) -> str:
        if scenario is None:
            return prompt
        systems = ", ".join(scenario.system.body_ids)
        if template is NewtonConceptualTemplate.ACTION_REACTION_PAIR:
            pair = scenario.third_law_pairs[0] if scenario.third_law_pairs else None
            if pair is not None:
                forces = {force.identifier: force for force in scenario.forces}
                first, second = (forces[item] for item in pair.force_ids)
                return (
                    f"In scenario {scenario.identifier}, {first.source.identifier} exerts a force "
                    f"on {first.target_body_id}. Identify its partner involving "
                    f"{second.source.identifier} and {second.target_body_id}. {prompt}"
                )
        return f"For the selected system ({systems}) in scenario {scenario.identifier}: {prompt}"

    @staticmethod
    def _context_semantics(
        template: NewtonConceptualTemplate,
        spec: _ConceptSpec,
        scenario: NewtonScenario | None,
    ) -> tuple[tuple[str, ...], tuple[tuple[str, str, int], ...]]:
        if scenario is None:
            return spec.concepts, spec.criteria
        if template is NewtonConceptualTemplate.ACTION_REACTION_PAIR:
            return (
                spec.concepts + ("authored_source_target",),
                spec.criteria
                + (("authored_ownership", "Matches the authored source and target ownership.", 1),),
            )
        if template is NewtonConceptualTemplate.INTERNAL_VS_EXTERNAL_FORCE:
            return (
                spec.concepts + ("authored_boundary",),
                spec.criteria + (("authored_boundary", "Uses the authored system boundary.", 1),),
            )
        if template is NewtonConceptualTemplate.FREE_BODY_DIAGRAM:
            return (
                spec.concepts + ("authored_forces_on_selected_body",),
                spec.criteria
                + (
                    (
                        "authored_forces",
                        "Uses the authored forces acting on the selected body.",
                        1,
                    ),
                ),
            )
        return spec.concepts, spec.criteria

    def _visual(
        self, question_id: str, template: NewtonConceptualTemplate, scenario: NewtonScenario
    ) -> VisualReference:
        if template in (
            NewtonConceptualTemplate.FREE_BODY_DIAGRAM,
            NewtonConceptualTemplate.ACTION_REACTION_PAIR,
        ):
            body_id = scenario.bodies[0].identifier
            options = NewtonRenderOptions(
                diagram_kind=NewtonDiagramKind.FREE_BODY_DIAGRAM,
                body_id=body_id,
            )
        else:
            options = NewtonRenderOptions(diagram_kind=NewtonDiagramKind.FORCE_DIAGRAM)
        document = self._renderer.render(scenario, options)
        return VisualReference(
            f"{question_id}-diagram",
            "image/svg+xml",
            document.markup,
            document.width,
            document.height,
        )

    @staticmethod
    def _slug(value: str) -> str:
        result = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
        return result or "context"


NewtonQuestionTemplate = NewtonConceptualTemplate
NewtonQuestionOptions = NewtonConceptualQuestionOptions


__all__ = [
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "NewtonConceptualQuestionGenerator",
    "NewtonConceptualQuestionOptions",
    "NewtonConceptualTemplate",
    "NewtonQuestionOptions",
    "NewtonQuestionTemplate",
]
