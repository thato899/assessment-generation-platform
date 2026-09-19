import random
from dataclasses import FrozenInstanceError

import pytest

from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    DEFAULT_GENERATION_POLICY,
    DifficultyProfile,
    ScenarioFamily,
    ScenarioGenerationInput,
    VerticalProjectileGenerationPolicy,
    VerticalProjectileScenarioFactory,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    PositiveDirection,
    ScenarioType,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    VerticalProjectileSolver,
)

FACTORY = VerticalProjectileScenarioFactory()


def request(
    seed: int = 42,
    *,
    family: ScenarioFamily | None = None,
    difficulty: Difficulty = Difficulty.MODERATE,
    positive_direction: PositiveDirection = PositiveDirection.UP,
) -> ScenarioGenerationInput:
    return ScenarioGenerationInput(
        seed=GenerationSeed(seed),
        family=family,
        difficulty=difficulty,
        positive_direction=positive_direction,
    )


@pytest.mark.parametrize(
    ("family", "launch_direction", "scenario_type", "position", "velocity_sign"),
    [
        (ScenarioFamily.UPWARD_GROUND, LaunchDirection.UPWARD, ScenarioType.PROJECTED_UPWARD, 0, 1),
        (
            ScenarioFamily.UPWARD_ELEVATED,
            LaunchDirection.UPWARD,
            ScenarioType.PROJECTED_UPWARD,
            1,
            1,
        ),
        (
            ScenarioFamily.DOWNWARD_ELEVATED,
            LaunchDirection.DOWNWARD,
            ScenarioType.PROJECTED_DOWNWARD,
            1,
            -1,
        ),
        (
            ScenarioFamily.DROPPED_FROM_REST,
            LaunchDirection.REST,
            ScenarioType.DROPPED_FROM_REST,
            1,
            0,
        ),
    ],
)
def test_each_supported_family_constructs_expected_initial_conditions(
    family: ScenarioFamily,
    launch_direction: LaunchDirection,
    scenario_type: ScenarioType,
    position: int,
    velocity_sign: int,
) -> None:
    scenario = FACTORY.generate(request(family=family))

    assert scenario.launch_direction is launch_direction
    assert scenario.scenario_type is scenario_type
    assert (scenario.launch_position.value > 0) is (position == 1)
    assert (
        scenario.initial_velocity.value == 0 or scenario.initial_velocity.value * velocity_sign > 0
    )
    assert scenario.gravitational_acceleration.value == -10.0
    assert scenario.seed == GenerationSeed(42)
    assert scenario.provenance is not None
    assert scenario.provenance.generator_id == "caps-grade-12-vertical-projectile-scenario-factory"
    assert scenario.provenance.generator_version == "1"
    assert scenario.provenance.template_ids == (
        family.value,
        Difficulty.MODERATE.value,
        PositiveDirection.UP.value,
    )


def test_same_input_is_reproducible_including_identifier_and_provenance() -> None:
    first = FACTORY.generate(request(seed=18472, family=ScenarioFamily.UPWARD_ELEVATED))
    second = FACTORY.generate(request(seed=18472, family=ScenarioFamily.UPWARD_ELEVATED))

    assert first == second
    assert first.identifier == ("vp-scenario-v1-upward-elevated-moderate-up-seed-18472")


def test_different_seeds_have_different_deterministic_identifiers() -> None:
    first = FACTORY.generate(request(seed=1, family=ScenarioFamily.UPWARD_GROUND))
    second = FACTORY.generate(request(seed=2, family=ScenarioFamily.UPWARD_GROUND))

    assert first.identifier != second.identifier


def test_generation_does_not_mutate_global_random_state() -> None:
    random.seed(20260919)
    expected = random.getstate()
    random.seed(20260919)

    FACTORY.generate(request(seed=123, family=ScenarioFamily.DOWNWARD_ELEVATED))

    assert random.getstate() == expected


@pytest.mark.parametrize("difficulty", list(Difficulty))
@pytest.mark.parametrize("seed", range(32))
def test_seed_corpus_stays_within_policy_and_domain_invariants(
    seed: int, difficulty: Difficulty
) -> None:
    scenario = FACTORY.generate(request(seed=seed, difficulty=difficulty))
    profile = DEFAULT_GENERATION_POLICY.profile_for(difficulty)

    assert scenario.gravitational_acceleration.value == -DEFAULT_GENERATION_POLICY.gravity_magnitude
    assert (
        scenario.initial_velocity.value == 0
        or abs(scenario.initial_velocity.value) in profile.initial_speeds
    )
    assert (
        scenario.launch_position.value == 0
        or scenario.launch_position.value in profile.elevated_heights
    )
    assert (
        VerticalProjectileSolver(scenario)
        .validate(VerticalProjectileSolver(scenario).solve())
        .valid
    )


def test_explicit_family_is_honoured() -> None:
    scenario = FACTORY.generate(request(family=ScenarioFamily.DROPPED_FROM_REST))

    assert scenario.launch_direction is LaunchDirection.REST
    assert scenario.initial_velocity.value == 0


def test_down_positive_generation_is_supported_for_ground_upward_projection() -> None:
    scenario = FACTORY.generate(
        request(
            family=ScenarioFamily.UPWARD_GROUND,
            positive_direction=PositiveDirection.DOWN,
        )
    )

    assert scenario.positive_direction is PositiveDirection.DOWN
    assert scenario.initial_velocity.value < 0
    assert scenario.gravitational_acceleration.value == 10.0
    assert scenario.launch_direction is LaunchDirection.UPWARD


def test_down_positive_elevated_families_are_rejected_by_current_position_model() -> None:
    with pytest.raises(ValueError, match="only upward-ground"):
        FACTORY.generate(
            request(
                family=ScenarioFamily.UPWARD_ELEVATED,
                positive_direction=PositiveDirection.DOWN,
            )
        )


def test_policy_rejects_family_not_in_allowed_set() -> None:
    policy = VerticalProjectileGenerationPolicy(allowed_families=(ScenarioFamily.UPWARD_GROUND,))

    with pytest.raises(ValueError, match="not allowed"):
        VerticalProjectileScenarioFactory(policy).generate(
            request(family=ScenarioFamily.DROPPED_FROM_REST)
        )


def test_policy_is_immutable_and_profiles_are_discrete() -> None:
    assert DEFAULT_GENERATION_POLICY.moderate.initial_speeds == (15, 20, 25)
    assert DEFAULT_GENERATION_POLICY.moderate.elevated_heights == (10, 15, 20, 25)
    with pytest.raises(FrozenInstanceError):
        DEFAULT_GENERATION_POLICY.gravity_magnitude = 9.81  # type: ignore[misc]


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: ScenarioGenerationInput(seed=42),
        lambda: ScenarioGenerationInput(seed=GenerationSeed(1), difficulty="moderate"),
        lambda: ScenarioGenerationInput(seed=GenerationSeed(1), family="upward-ground"),
        lambda: ScenarioGenerationInput(seed=GenerationSeed(1), positive_direction="up"),
    ],
)
def test_generation_input_rejects_ambiguous_types(constructor: object) -> None:
    with pytest.raises(ValueError):
        constructor()  # type: ignore[operator]


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: DifficultyProfile((), (1,)),
        lambda: DifficultyProfile((1,), ()),
        lambda: DifficultyProfile((0,), (1,)),
        lambda: DifficultyProfile((1,), (0,)),
        lambda: DifficultyProfile((1, 1), (1,)),
        lambda: DifficultyProfile((1,), (1, 1)),
    ],
)
def test_invalid_difficulty_profiles_are_rejected(constructor: object) -> None:
    with pytest.raises(ValueError):
        constructor()  # type: ignore[operator]


def test_invalid_policy_is_rejected() -> None:
    with pytest.raises(ValueError):
        VerticalProjectileGenerationPolicy(gravity_magnitude=0)
    with pytest.raises(ValueError):
        VerticalProjectileGenerationPolicy(allowed_families=())
