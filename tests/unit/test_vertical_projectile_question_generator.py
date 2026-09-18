import random

import pytest

from assessment_platform.core import (
    Assessment,
    AssessmentType,
    CurriculumReference,
    ExpectedAnswerKind,
    GenerationSeed,
    ResponseKind,
)
from assessment_platform.curriculum.caps.physical_sciences import (
    get_caps_physical_sciences,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    vertical_projectile_question_generator as question_generator,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    Metres,
    MetresPerSecond,
    MetresPerSecondSquared,
    PositiveDirection,
    ScenarioType,
    VerticalProjectileScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    EventType,
    VerticalProjectileSolver,
)

TOPIC = get_caps_physical_sciences().topic("vertical-projectile-motion-1d")
GENERATOR = question_generator.VerticalProjectileQuestionGenerator()


def make_scenario(kind: str, seed: int = 18472) -> VerticalProjectileScenario:
    values: dict[str, object] = {
        "identifier": kind,
        "launch_position": Metres(0),
        "initial_velocity": MetresPerSecond(20),
        "gravitational_acceleration": MetresPerSecondSquared(-10),
        "positive_direction": PositiveDirection.UP,
        "launch_direction": LaunchDirection.UPWARD,
        "scenario_type": ScenarioType.PROJECTED_UPWARD,
        "seed": GenerationSeed(seed),
    }
    if kind == "upward-elevated":
        values["launch_position"] = Metres(5)
    elif kind == "downward-elevated":
        values.update(
            initial_velocity=MetresPerSecond(-5),
            launch_position=Metres(20),
            launch_direction=LaunchDirection.DOWNWARD,
            scenario_type=ScenarioType.PROJECTED_DOWNWARD,
        )
    elif kind == "dropped-from-rest":
        values.update(
            initial_velocity=MetresPerSecond(0),
            launch_position=Metres(20),
            launch_direction=LaunchDirection.REST,
            scenario_type=ScenarioType.DROPPED_FROM_REST,
        )
    return VerticalProjectileScenario(**values)  # type: ignore[arg-type]


def generate(kind: str, seed: int = 18472):
    scenario = make_scenario(kind, seed)
    solution = VerticalProjectileSolver(scenario).solve()
    return GENERATOR.generate(scenario, solution, TOPIC, GenerationSeed(seed))


def templates(question) -> tuple[str, ...]:
    assert question.provenance is not None
    return question.provenance.template_ids


@pytest.mark.parametrize(
    "kind,expected",
    [
        (
            "upward-ground",
            (
                "acceleration-direction",
                "time-to-maximum-height",
                "maximum-height",
                "ground-impact-time",
                "ground-impact-velocity",
            ),
        ),
        (
            "upward-elevated",
            (
                "acceleration-direction",
                "time-to-maximum-height",
                "maximum-height",
                "return-to-launch-position",
                "ground-impact-time",
                "ground-impact-velocity",
            ),
        ),
        (
            "downward-elevated",
            ("acceleration-direction", "ground-impact-time", "ground-impact-velocity"),
        ),
        (
            "dropped-from-rest",
            ("acceleration-direction", "ground-impact-time", "ground-impact-velocity"),
        ),
    ],
)
def test_supported_scenario_families_select_only_valid_templates(
    kind: str, expected: tuple[str, ...]
) -> None:
    question = generate(kind)
    assert templates(question) == expected
    assert len(question.parts) == len(expected)


def test_same_seed_is_reproducible_and_does_not_change_global_random_state() -> None:
    random.seed(9876)
    before = random.getstate()
    first = generate("upward-elevated", 42)
    after = random.getstate()
    second = generate("upward-elevated", 42)

    assert before == after
    assert first == second
    assert first.provenance is not None
    assert first.provenance.generator_id == question_generator.GENERATOR_ID
    assert first.provenance.seed == GenerationSeed(42)


def test_seed_is_recorded_without_fake_seed_dependent_physics() -> None:
    first = generate("upward-ground", 1)
    second = generate("upward-ground", 2)

    assert first.provenance is not None
    assert second.provenance is not None
    assert first.provenance.template_ids == second.provenance.template_ids
    assert first.parts == second.parts
    assert first.provenance.seed != second.provenance.seed


def test_question_parts_have_stable_ids_typed_answers_and_exact_marking() -> None:
    question = generate("upward-elevated")
    assert [part.identifier for part in question.parts] == [
        "vp-upward-elevated.1",
        "vp-upward-elevated.2",
        "vp-upward-elevated.3",
        "vp-upward-elevated.4",
        "vp-upward-elevated.5",
        "vp-upward-elevated.6",
    ]
    criterion_ids = []
    for part in question.parts:
        assert part.response_specification is not None
        assert part.expected_answer is not None
        assert part.marking_scheme is not None
        assert part.marking_scheme.maximum_marks == part.marks
        assert sum(item.marks for item in part.marking_scheme.criteria) == part.marks
        criterion_ids.extend(item.identifier for item in part.marking_scheme.criteria)
    assert len(criterion_ids) == len(set(criterion_ids))
    assert question.scenario is not None
    assert question.scenario.data["curriculum_topic"] == "vertical-projectile-motion-1d"
    with pytest.raises(AttributeError):
        question.parts.append(question.parts[0])  # type: ignore[attr-defined]


def test_response_kinds_expected_units_and_solver_values_are_semantic() -> None:
    scenario = make_scenario("upward-ground")
    solution = VerticalProjectileSolver(scenario).solve()
    question = GENERATOR.generate(scenario, solution, TOPIC, scenario.seed)
    by_template = dict(zip(templates(question), question.parts, strict=True))

    conceptual = by_template["acceleration-direction"]
    assert conceptual.response_specification.kind is ResponseKind.SHORT_TEXT
    assert conceptual.expected_answer.kind is ExpectedAnswerKind.TEXT

    time_part = by_template["time-to-maximum-height"]
    assert time_part.response_specification.kind is ResponseKind.CALCULATION
    assert time_part.expected_answer.value == pytest.approx(
        solution.event(EventType.MAXIMUM_HEIGHT).time.value  # type: ignore[union-attr]
    )
    assert time_part.expected_answer.unit == "s"

    height_part = by_template["maximum-height"]
    assert height_part.expected_answer.value == pytest.approx(20)
    assert height_part.expected_answer.unit == "m"

    velocity_part = by_template["ground-impact-velocity"]
    assert velocity_part.response_specification.kind is ResponseKind.NUMERIC
    assert velocity_part.expected_answer.value == pytest.approx(-20)
    assert velocity_part.expected_answer.unit == "m/s"
    assert velocity_part.expected_answer.tolerance == 0.01


def test_memorandum_is_derived_from_generated_question_parts() -> None:
    question = generate("upward-elevated")
    assessment = Assessment(
        "generated-assessment",
        AssessmentType.QUESTION,
        CurriculumReference("CAPS"),
        (question,),
    )
    assert [entry.question_part_id.value for entry in assessment.memorandum] == [
        part.identifier for part in question.parts
    ]


def test_visuals_are_renderer_output_and_can_be_disabled_without_answer_leakage() -> None:
    with_visual = generate("upward-ground")
    scenario = make_scenario("upward-ground")
    solution = VerticalProjectileSolver(scenario).solve()
    without_visual = GENERATOR.generate(
        scenario, solution, TOPIC, scenario.seed, include_visuals=False
    )

    assert len(with_visual.visuals) == 1
    visual = with_visual.visuals[0]
    assert visual.media_type == "image/svg+xml"
    assert visual.content.startswith("<svg ")
    assert "t = " not in visual.content
    assert "v = " not in visual.content
    assert "g = " not in visual.content
    assert without_visual.visuals == ()
    assert with_visual.prompt == without_visual.prompt
    assert "20 m/s" in with_visual.prompt
    assert "g = 10 m/s²" in with_visual.prompt
    assert "air resistance" in with_visual.prompt
    assert "ground" in with_visual.prompt
    assert "expected" not in with_visual.prompt.lower()
    assert "memorandum" not in with_visual.prompt.lower()


def test_topic_solution_and_seed_boundaries_are_validated() -> None:
    scenario = make_scenario("upward-ground")
    solution = VerticalProjectileSolver(scenario).solve()
    momentum = get_caps_physical_sciences().topic("momentum-and-impulse")
    with pytest.raises(ValueError, match="vertical-projectile"):
        GENERATOR.generate(scenario, solution, momentum, scenario.seed)
    with pytest.raises(ValueError, match="match the scenario seed"):
        GENERATOR.generate(scenario, solution, TOPIC, GenerationSeed(99))

    invalid_solution = type(solution)(solution.scenario_identifier, ())
    with pytest.raises(ValueError, match="does not validate"):
        GENERATOR.generate(scenario, invalid_solution, TOPIC, scenario.seed)


def test_no_events_means_no_invalid_multi_part_question() -> None:
    scenario = make_scenario(
        "ground-drop",
    )
    scenario = VerticalProjectileScenario(
        identifier=scenario.identifier,
        launch_position=Metres(0),
        initial_velocity=MetresPerSecond(0),
        gravitational_acceleration=MetresPerSecondSquared(-10),
        positive_direction=PositiveDirection.UP,
        launch_direction=LaunchDirection.REST,
        scenario_type=ScenarioType.DROPPED_FROM_REST,
        seed=scenario.seed,
    )
    solution = VerticalProjectileSolver(scenario).solve()
    with pytest.raises(ValueError, match="minimum multi-part"):
        GENERATOR.generate(scenario, solution, TOPIC, scenario.seed)
