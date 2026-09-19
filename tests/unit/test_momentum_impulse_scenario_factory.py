import inspect
import random

import pytest

from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    DEFAULT_MOMENTUM_GENERATION_POLICY,
    MomentumDifficultyProfile,
    MomentumGenerationPolicy,
    MomentumScenarioFactory,
    MomentumScenarioFamily,
    MomentumScenarioGenerationInput,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    PhysicalDirection,
    PositiveAxis,
)

FACTORY = MomentumScenarioFactory()


def request(
    seed: int = 42,
    *,
    family: MomentumScenarioFamily | None = None,
    difficulty: Difficulty = Difficulty.MODERATE,
    positive_axis: PositiveAxis | None = None,
) -> MomentumScenarioGenerationInput:
    return MomentumScenarioGenerationInput(
        seed=GenerationSeed(seed),
        family=family,
        difficulty=difficulty,
        positive_axis=positive_axis,
    )


@pytest.mark.parametrize("family", list(MomentumScenarioFamily))
@pytest.mark.parametrize("difficulty", list(Difficulty))
def test_each_family_and_difficulty_produces_valid_scenario(
    family: MomentumScenarioFamily, difficulty: Difficulty
) -> None:
    scenario = FACTORY.generate(request(family=family, difficulty=difficulty))

    assert scenario.bodies
    assert len({body.identifier for body in scenario.bodies}) == len(scenario.bodies)
    assert scenario.provenance is not None
    assert scenario.provenance.template_ids[0] == family
    if family is MomentumScenarioFamily.EXTERNAL_IMPULSE:
        assert not scenario.system.isolated
        assert scenario.system.external_impulse is not None
    else:
        assert scenario.system.isolated
        assert scenario.system.external_impulse is None


def test_explicit_family_and_axis_are_honoured() -> None:
    scenario = FACTORY.generate(
        request(
            family=MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED,
            positive_axis=PositiveAxis.LEFT,
        )
    )

    assert scenario.positive_axis is PositiveAxis.LEFT
    assert scenario.provenance is not None
    assert scenario.provenance.template_ids == (
        MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED,
        Difficulty.MODERATE.value,
        PositiveAxis.LEFT.value,
    )
    assert scenario.bodies[0].initial_velocity.physical_direction(PositiveAxis.LEFT) is (
        PhysicalDirection.RIGHT
    )
    assert scenario.bodies[1].initial_velocity.physical_direction(PositiveAxis.LEFT) is (
        PhysicalDirection.LEFT
    )


def test_repeated_identical_inputs_reproduce_scenario_and_provenance() -> None:
    first = FACTORY.generate(request(seed=18472))
    second = FACTORY.generate(request(seed=18472))

    assert first == second
    assert first.identifier == second.identifier
    assert first.provenance == second.provenance


def test_different_seeds_can_produce_different_initial_conditions() -> None:
    scenarios = {
        FACTORY.generate(
            request(
                seed=seed,
                family=MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED,
                positive_axis=PositiveAxis.RIGHT,
            )
        ).bodies
        for seed in range(6)
    }

    assert len(scenarios) > 1


def test_omitted_family_and_axis_selection_is_seeded() -> None:
    first = FACTORY.generate(request(seed=1))
    second = FACTORY.generate(request(seed=1))

    assert (first.provenance, first.positive_axis, first.bodies, first.system) == (
        second.provenance,
        second.positive_axis,
        second.bodies,
        second.system,
    )


def test_generation_does_not_mutate_module_global_random_state() -> None:
    random.seed(991)
    before = random.getstate()

    FACTORY.generate(request(seed=33))

    after = random.getstate()
    assert after == before


def test_generated_values_are_bounded_by_the_selected_policy() -> None:
    policy = MomentumGenerationPolicy(
        introductory=MomentumDifficultyProfile((1.5,), (2.5,), (0.0,)),
        moderate=MomentumDifficultyProfile((2.5,), (3.5,), (1.0,)),
        advanced=MomentumDifficultyProfile((4.5,), (5.5,), (2.0,)),
    )
    scenario = MomentumScenarioFactory(policy).generate(
        request(difficulty=Difficulty.ADVANCED, family=MomentumScenarioFamily.EXTERNAL_IMPULSE)
    )

    assert {body.mass.value for body in scenario.bodies} == {4.5}
    assert {abs(body.initial_velocity.value) for body in scenario.bodies} == {5.5}
    assert scenario.system.external_impulse is not None
    assert abs(scenario.system.external_impulse.value) == 2.0


def test_policy_rejects_duplicate_and_invalid_generation_values() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        MomentumDifficultyProfile((1.0, 1.0), (2.0,), (0.0,))
    with pytest.raises(ValueError, match="positive"):
        MomentumDifficultyProfile((0.0,), (2.0,), (0.0,))
    with pytest.raises(ValueError, match="non-negative"):
        MomentumDifficultyProfile((1.0,), (2.0,), (-1.0,))


def test_policy_rejects_duplicate_axes_and_families() -> None:
    with pytest.raises(ValueError, match="families"):
        MomentumGenerationPolicy(allowed_families=(MomentumScenarioFamily.SINGLE_BODY,) * 2)
    with pytest.raises(ValueError, match="axes"):
        MomentumGenerationPolicy(allowed_axes=(PositiveAxis.RIGHT, PositiveAxis.RIGHT))


def test_factory_rejects_disallowed_family_and_axis() -> None:
    policy = MomentumGenerationPolicy(
        allowed_families=(MomentumScenarioFamily.SINGLE_BODY,),
        allowed_axes=(PositiveAxis.RIGHT,),
    )
    factory = MomentumScenarioFactory(policy)

    with pytest.raises(ValueError, match="family"):
        factory.generate(request(family=MomentumScenarioFamily.EXTERNAL_IMPULSE))
    with pytest.raises(ValueError, match="axis"):
        factory.generate(request(positive_axis=PositiveAxis.LEFT))


def test_identifiers_include_policy_and_generation_inputs() -> None:
    scenario = FACTORY.generate(
        request(
            seed=9,
            family=MomentumScenarioFamily.SINGLE_BODY,
            difficulty=Difficulty.INTRODUCTORY,
            positive_axis=PositiveAxis.RIGHT,
        )
    )

    assert scenario.identifier == (
        "mi-scenario-v1-single-body-introductory-right-seed-9"
    )
    assert scenario.provenance is not None
    assert scenario.provenance.generator_id == "caps-grade-12-momentum-impulse-scenario-factory"
    assert scenario.provenance.generator_version == "1"
    assert not hasattr(scenario, "final_bodies")


def test_factory_has_no_solver_or_framework_dependency() -> None:
    source = inspect.getsource(MomentumScenarioFactory)

    assert "MomentumImpulseSolver" not in source
    assert "fastapi" not in source.lower()
    assert "pydantic" not in source.lower()
    assert "Random" in source


def test_default_policy_is_immutable_and_available() -> None:
    assert DEFAULT_MOMENTUM_GENERATION_POLICY.policy_version == "1"
    with pytest.raises(AttributeError):
        DEFAULT_MOMENTUM_GENERATION_POLICY.policy_version = "2"  # type: ignore[misc]
