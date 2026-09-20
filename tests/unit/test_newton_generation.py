"""Deterministic Issue #57 Newton scenario-generation regressions."""

import random
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import newton_generation as g
from assessment_platform.domains.physical_sciences.mechanics import newtons_laws as n

SEED = GenerationSeed(1234)


def generate(family: g.NewtonGenerationFamily, difficulty=Difficulty.MODERATE):
    return g.NewtonProblemFactory().generate(g.NewtonGenerationInput(SEED, family, difficulty))


@pytest.mark.parametrize("family", tuple(g.NewtonGenerationFamily))
def test_every_supported_family_is_typed_and_solver_valid(family):
    result = generate(family)
    assert result.scenario.identifier == result.identifier
    assert result.provenance.seed == SEED
    assert result.provenance.generator_id == g.GENERATOR_ID
    assert result.metadata.policy_version == g.POLICY_VERSION


def test_generation_replays_and_varies_by_seed_without_global_random_state_changes():
    factory = g.NewtonProblemFactory()
    request = g.NewtonGenerationInput(SEED, g.NewtonGenerationFamily.NEWTON_II)
    first = factory.generate(request)
    second = factory.generate(request)
    assert first == second
    random.seed(991)
    expected = (random.random(), random.random())
    random.seed(991)
    factory.generate(request)
    assert (random.random(), random.random()) == expected
    other = factory.generate(
        g.NewtonGenerationInput(GenerationSeed(SEED.value + 1), request.family)
    )
    assert other.identifier != first.identifier


def test_policy_and_inputs_are_immutable_and_validate_types():
    policy = g.DEFAULT_NEWTON_GENERATION_POLICY
    with pytest.raises(FrozenInstanceError):
        policy.policy_version = "2"
    with pytest.raises(ValueError):
        g.NewtonGenerationInput(GenerationSeed(1), family="newton-ii")
    with pytest.raises(ValueError):
        g.NewtonProblemFactory(replace(policy, allowed_families=()))


def test_unknown_force_preserves_authored_unknown_and_does_not_store_answer():
    result = generate(g.NewtonGenerationFamily.UNKNOWN_FORCE)
    assert isinstance(result, g.GeneratedUnknownForceProblem)
    force = next(item for item in result.scenario.forces if item.identifier == result.force_id)
    assert force.vector.components == (n.UnknownValue.UNKNOWN,)
    assert not hasattr(result, "answer")


def test_contact_and_string_unknowns_remain_authored_unknowns():
    contact = generate(g.NewtonGenerationFamily.STATIC_FRICTION)
    assert isinstance(contact, g.GeneratedContactProblem)
    assert any(
        n.UnknownValue.UNKNOWN in force.vector.components
        for force in contact.scenario.forces
    )
    connected = generate(g.NewtonGenerationFamily.CONNECTED_BODIES)
    assert isinstance(connected, g.GeneratedConnectedBodiesProblem)
    assert (
        sum(
            n.UnknownValue.UNKNOWN in force.vector.components
            for force in connected.scenario.forces
            if force.kind is n.ForceKind.TENSION
        )
        == 2
    )


@pytest.mark.parametrize("difficulty", tuple(Difficulty))
def test_difficulty_selects_bounded_profile_values(difficulty):
    policy = g.DEFAULT_NEWTON_GENERATION_POLICY
    result = g.NewtonProblemFactory(policy).generate(
        g.NewtonGenerationInput(GenerationSeed(4), g.NewtonGenerationFamily.WEIGHT, difficulty)
    )
    field = result.scenario.gravitational_fields[0].acceleration.components[1].value
    assert abs(field) in policy.profile_for(difficulty).gravitational_fields_m_s2


def test_requested_disallowed_family_is_rejected():
    policy = replace(
        g.DEFAULT_NEWTON_GENERATION_POLICY,
        allowed_families=(g.NewtonGenerationFamily.NEWTON_II,),
    )
    with pytest.raises(ValueError, match="not allowed"):
        g.NewtonProblemFactory(policy).generate(
            g.NewtonGenerationInput(SEED, g.NewtonGenerationFamily.WEIGHT)
        )


def test_generated_ids_and_provenance_are_stable_and_semantic():
    result = generate(g.NewtonGenerationFamily.UNIVERSAL_GRAVITATION, Difficulty.ADVANCED)
    assert result.identifier.startswith("newton-problem-v1-universal-gravitation-advanced-seed-")
    assert result.provenance.template_ids == (
        g.NewtonGenerationFamily.UNIVERSAL_GRAVITATION.value,
        Difficulty.ADVANCED.value,
        "policy-1",
    )
    assert not any(
        "uuid" in path.read_text(encoding="utf-8").lower()
        for path in Path(g.__file__).parent.glob("newton_generation.py")
    )


def test_generated_scenarios_use_required_assumptions_and_no_generation_dependencies():
    for family in g.NewtonGenerationFamily:
        scenario = generate(family).scenario
        assert scenario.assumptions == n.NewtonAssumptions(True, True, True)
    forbidden = {"random.seed", "uuid4", "datetime", "sympy", "fastapi", "pydantic"}
    source = Path(g.__file__).read_text(encoding="utf-8").lower()
    assert not any(item in source for item in forbidden)
