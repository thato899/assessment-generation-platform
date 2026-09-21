"""Deterministic Issue #76 Work, Energy & Power generation tests."""

import ast
import inspect
import random
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    DEFAULT_WORK_ENERGY_GENERATION_POLICY,
    GeneratedWorkEnergyProblem,
    WorkEnergyDifficultyProfile,
    WorkEnergyGenerationFamily,
    WorkEnergyGenerationInput,
    WorkEnergyGenerationPolicy,
    WorkEnergyProblemFactory,
    WorkEnergySolver,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power import (
    AlongPlaneWorkInput,
    AveragePowerInput,
    HeightState,
    NetWorkInput,
    PumpingPowerInput,
    UnknownValue,
)

FACTORY = WorkEnergyProblemFactory()


def request(
    seed: int = 42,
    *,
    family: WorkEnergyGenerationFamily | None = None,
    difficulty: Difficulty = Difficulty.MODERATE,
) -> WorkEnergyGenerationInput:
    return WorkEnergyGenerationInput(GenerationSeed(seed), family, difficulty)


def assert_solver_accepts(problem: GeneratedWorkEnergyProblem) -> None:
    solver = WorkEnergySolver()
    scenario = problem.scenario
    family = problem.family
    if family is WorkEnergyGenerationFamily.WORK_BY_FORCE:
        authored = scenario.work_inputs[0]
        assert isinstance(authored, NetWorkInput)
        solver.work_by_force(authored.contributions[0])
    elif family is WorkEnergyGenerationFamily.NET_WORK:
        authored = scenario.work_inputs[0]
        assert isinstance(authored, NetWorkInput)
        solver.net_work(authored)
    elif family is WorkEnergyGenerationFamily.ALONG_PLANE_WORK:
        authored = scenario.work_inputs[0]
        assert isinstance(authored, AlongPlaneWorkInput)
        solver.along_plane_work(authored)
    elif family is WorkEnergyGenerationFamily.KINETIC_ENERGY:
        solver.kinetic_energy(scenario.kinetic_states[0])
    elif family is WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY:
        assert problem.authored_mass is not None
        solver.potential_energy(problem.authored_mass, scenario.height_states[0])
    elif family in (
        WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK,
        WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED,
        WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED,
    ):
        solver.work_energy(scenario.work_energy_contexts[0])
    elif family in (
        WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK,
        WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED,
    ):
        solver.mechanical_energy(scenario.mechanical_energy_contexts[0])
    elif family is WorkEnergyGenerationFamily.AVERAGE_POWER:
        solver.average_power(scenario.average_power_inputs[0])
    elif family is WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER:
        solver.constant_speed_power(scenario.constant_speed_power_inputs[0])
    elif family is WorkEnergyGenerationFamily.PUMPING_POWER:
        solver.pumping_power(scenario.pumping_power_inputs[0])
    else:
        raise AssertionError(f"uncovered family: {family}")


@pytest.mark.parametrize("difficulty", list(Difficulty))
@pytest.mark.parametrize("family", list(WorkEnergyGenerationFamily))
def test_every_family_and_difficulty_is_typed_and_solver_accepted(
    family: WorkEnergyGenerationFamily, difficulty: Difficulty
) -> None:
    problem = FACTORY.generate(request(family=family, difficulty=difficulty))
    assert problem.family is family
    assert problem.difficulty is difficulty
    assert problem.scenario.identifier == problem.identifier
    assert problem.provenance.seed == GenerationSeed(42)
    assert problem.provenance.generator_id == "caps-m5-work-energy-power-scenario-factory"
    assert problem.provenance.generator_version == "1"
    assert problem.metadata.policy_version == "1"
    assert_solver_accepts(problem)
    assert not hasattr(problem, "answer")
    assert not hasattr(problem, "solver_result")


def test_same_request_replays_and_omitted_family_selection_is_seeded() -> None:
    first = FACTORY.generate(request(seed=18472))
    second = FACTORY.generate(request(seed=18472))
    assert first == second
    assert first.identifier == second.identifier
    assert first.provenance == second.provenance


def test_generation_does_not_mutate_global_random_state() -> None:
    random.seed(991)
    before = random.getstate()
    FACTORY.generate(request(seed=33))
    assert random.getstate() == before


def test_explicit_family_is_honoured_and_disallowed_family_is_rejected() -> None:
    problem = FACTORY.generate(
        request(family=WorkEnergyGenerationFamily.PUMPING_POWER, difficulty=Difficulty.ADVANCED)
    )
    assert problem.family is WorkEnergyGenerationFamily.PUMPING_POWER
    restricted = WorkEnergyGenerationPolicy(
        allowed_families=(WorkEnergyGenerationFamily.WORK_BY_FORCE,)
    )
    with pytest.raises(ValueError, match="not allowed"):
        WorkEnergyProblemFactory(restricted).generate(
            request(family=WorkEnergyGenerationFamily.PUMPING_POWER)
        )


def test_work_energy_unknown_targets_and_mechanical_unknown_work_remain_authored_unknown() -> None:
    final_speed = FACTORY.generate(
        request(family=WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED)
    )
    final_context = final_speed.scenario.work_energy_contexts[0]
    assert final_context.final_state.speed is UnknownValue.UNKNOWN
    WorkEnergySolver().work_energy(final_context)
    assert final_context.final_state.speed is UnknownValue.UNKNOWN

    initial_speed = FACTORY.generate(
        request(family=WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED)
    )
    initial_context = initial_speed.scenario.work_energy_contexts[0]
    assert initial_context.initial_state.speed is UnknownValue.UNKNOWN
    WorkEnergySolver().work_energy(initial_context)
    assert initial_context.initial_state.speed is UnknownValue.UNKNOWN

    non_conservative = FACTORY.generate(
        request(family=WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK)
    )
    mechanical = non_conservative.scenario.mechanical_energy_contexts[0]
    assert mechanical.non_conservative_work is UnknownValue.UNKNOWN
    WorkEnergySolver().mechanical_energy(mechanical)
    assert mechanical.non_conservative_work is UnknownValue.UNKNOWN


def test_generated_ids_and_provenance_are_stable_and_answer_free() -> None:
    problem = FACTORY.generate(
        request(
            seed=9,
            family=WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED,
            difficulty=Difficulty.INTRODUCTORY,
        )
    )
    assert problem.identifier == ("wep-problem-v1-work-energy-final-speed-introductory-seed-9")
    assert problem.provenance.template_ids == (
        WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED.value,
        Difficulty.INTRODUCTORY.value,
        "policy-1",
    )
    assert all(
        token not in problem.identifier.lower()
        for token in ("answer", "work-result", "power-result", "final-speed-value")
    )
    assert not any(
        "uuid" in path.read_text(encoding="utf-8").lower()
        for path in Path(__file__).parents[2].glob("**/work_energy_power_generation.py")
    )


def test_policy_profiles_are_distinct_and_reject_invalid_values() -> None:
    policy = DEFAULT_WORK_ENERGY_GENERATION_POLICY
    assert policy.introductory != policy.moderate
    assert policy.moderate != policy.advanced
    with pytest.raises(ValueError, match="duplicate"):
        replace(
            policy,
            allowed_families=(WorkEnergyGenerationFamily.WORK_BY_FORCE,) * 2,
        )
    with pytest.raises(ValueError, match="empty"):
        WorkEnergyDifficultyProfile(
            (), (1,), (1,), (0,), (1,), (0,), (9.8,), (1,), (1,), (1,), (0,), (1,)
        )
    with pytest.raises(ValueError, match="finite"):
        WorkEnergyDifficultyProfile(
            (1,), (1,), (1,), (0,), (1,), (0,), (float("nan"),), (1,), (1,), (1,), (0,), (1,)
        )
    with pytest.raises(ValueError, match="angle"):
        WorkEnergyDifficultyProfile(
            (1,), (1,), (1,), (181,), (1,), (0,), (9.8,), (1,), (1,), (1,), (0,), (1,)
        )


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: WorkEnergyGenerationInput(42),
        lambda: WorkEnergyGenerationInput(GenerationSeed(1), family="work-by-force"),
        lambda: WorkEnergyGenerationInput(GenerationSeed(1), difficulty="moderate"),
        lambda: WorkEnergyProblemFactory().generate(GenerationSeed(1)),
    ],
)
def test_public_generation_inputs_reject_ambiguous_types(constructor: object) -> None:
    with pytest.raises(ValueError):
        constructor()  # type: ignore[operator]


def test_generation_objects_are_frozen_and_factory_has_only_allowed_dependencies() -> None:
    with pytest.raises(FrozenInstanceError):
        DEFAULT_WORK_ENERGY_GENERATION_POLICY.policy_version = "2"  # type: ignore[misc]
    problem = FACTORY.generate(request(family=WorkEnergyGenerationFamily.WORK_BY_FORCE))
    with pytest.raises(FrozenInstanceError):
        problem.metadata = problem.metadata  # type: ignore[misc]

    source = Path(inspect.getfile(WorkEnergyProblemFactory)).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = (
        "fastapi",
        "pydantic",
        "application",
        "rendering",
        "question",
        "newton_solver",
        "momentum_impulse_solver",
        "vertical_projectile_solver",
        "random.seed",
        "uuid4",
        "datetime",
        "sympy",
        "cos(",
        "sqrt(",
    )
    lowered = source.lower()
    assert not any(item in lowered for item in forbidden)
    assert all(
        not (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module
            and any(node.module.lower().startswith(item) for item in forbidden[:7])
        )
        for node in ast.walk(tree)
    )


def test_family_inventory_is_exhaustive_and_domain_types_are_authored_only() -> None:
    assert set(WorkEnergyGenerationFamily) == {
        WorkEnergyGenerationFamily.WORK_BY_FORCE,
        WorkEnergyGenerationFamily.NET_WORK,
        WorkEnergyGenerationFamily.ALONG_PLANE_WORK,
        WorkEnergyGenerationFamily.KINETIC_ENERGY,
        WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY,
        WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK,
        WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED,
        WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED,
        WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK,
        WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED,
        WorkEnergyGenerationFamily.AVERAGE_POWER,
        WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER,
        WorkEnergyGenerationFamily.PUMPING_POWER,
    }
    for family in WorkEnergyGenerationFamily:
        problem = FACTORY.generate(request(seed=family.value.__len__(), family=family))
        assert problem.scenario.__class__.__name__ == "WorkEnergyScenario"
        assert all(not isinstance(item, (float, int)) for item in problem.provenance.template_ids)


def test_power_and_potential_wrappers_keep_expected_authored_shapes() -> None:
    potential = FACTORY.generate(
        request(family=WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY)
    )
    assert isinstance(potential.scenario.height_states[0], HeightState)
    assert potential.authored_mass is not None
    power = FACTORY.generate(request(family=WorkEnergyGenerationFamily.AVERAGE_POWER))
    assert isinstance(power.scenario.average_power_inputs[0], AveragePowerInput)
    pumping = FACTORY.generate(request(family=WorkEnergyGenerationFamily.PUMPING_POWER))
    assert isinstance(pumping.scenario.pumping_power_inputs[0], PumpingPowerInput)
    assert pumping.scenario.pumping_power_inputs[0].gravitational_field is not UnknownValue.UNKNOWN
