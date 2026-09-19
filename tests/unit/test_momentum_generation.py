import inspect
import random

import pytest

from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    CommonFinalVelocityConstraint,
    ConstrainedMomentumSolver,
    GeneratedCollisionProblem,
    GeneratedContactTimeProblem,
    GeneratedForceFromMomentumChangeProblem,
    GeneratedImpulseForceTimeProblem,
    GeneratedInitialMomentumProblem,
    GeneratedMomentumChangeProblem,
    KnownFinalVelocityConstraint,
    MomentumGenerationFamily,
    MomentumImpulseRelationshipSolver,
    MomentumImpulseSolver,
    MomentumProblemFactory,
    MomentumProblemGenerationInput,
    MomentumScenarioFactory,
    MomentumScenarioFamily,
    MomentumScenarioGenerationInput,
    PositiveAxis,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    momentum_generation as generation_module,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_generation import (
    MomentumProblemDifficultyProfile,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    PhysicalDirection,
)

FACTORY = MomentumProblemFactory()


def request(
    seed: int = 42,
    *,
    family: MomentumGenerationFamily | None = None,
    difficulty: Difficulty = Difficulty.MODERATE,
    axis: PositiveAxis | None = None,
) -> MomentumProblemGenerationInput:
    return MomentumProblemGenerationInput(
        GenerationSeed(seed), family, difficulty, axis
    )


@pytest.mark.parametrize("family", list(MomentumGenerationFamily))
@pytest.mark.parametrize("difficulty", list(Difficulty))
@pytest.mark.parametrize("axis", list(PositiveAxis))
def test_each_policy_family_and_difficulty_produces_solver_supported_output(
    family: MomentumGenerationFamily,
    difficulty: Difficulty,
    axis: PositiveAxis,
) -> None:
    output = FACTORY.generate(request(family=family, difficulty=difficulty, axis=axis))

    assert output.metadata.family is family
    assert output.metadata.difficulty is difficulty
    assert output.metadata.provenance.seed == GenerationSeed(42)
    assert output.metadata.provenance.template_ids == (
        family.value,
        difficulty.value,
        axis.value,
    )
    if isinstance(output, GeneratedInitialMomentumProblem):
        assert output.scenario.provenance is not None
        assert output.scenario.positive_axis is axis
        solver = MomentumImpulseSolver(output.scenario)
        assert solver.validate(solver.solve()).valid
    elif isinstance(output, GeneratedMomentumChangeProblem):
        assert (
            MomentumImpulseRelationshipSolver()
            .calculate_momentum_change(output.input_data)
            .momentum_change
        )
    elif isinstance(output, GeneratedImpulseForceTimeProblem):
        assert MomentumImpulseRelationshipSolver().calculate_impulse_from_force_time(
            output.input_data
        )
    elif isinstance(output, GeneratedForceFromMomentumChangeProblem):
        solver = MomentumImpulseRelationshipSolver()
        change = solver.calculate_momentum_change(output.momentum_change_input)
        assert solver.calculate_force_from_momentum_change(change, output.contact_time)
    elif isinstance(output, GeneratedContactTimeProblem):
        assert MomentumImpulseRelationshipSolver().calculate_contact_time_from_impulse(
            output.impulse, output.force, output.positive_axis
        ).contact_time.value > 0
    else:
        assert isinstance(output, GeneratedCollisionProblem)
        solver = ConstrainedMomentumSolver(output.interaction)
        assert solver.validate(solver.solve()).valid


def test_initial_momentum_generation_composes_with_unchanged_issue_32_factory() -> None:
    legacy = MomentumScenarioFactory().generate(
        MomentumScenarioGenerationInput(
            GenerationSeed(42),
            MomentumScenarioFamily.SINGLE_BODY,
            Difficulty.MODERATE,
            PositiveAxis.RIGHT,
        )
    )
    generated = FACTORY.generate(
        request(
            family=MomentumGenerationFamily.INITIAL_MOMENTUM,
            axis=PositiveAxis.RIGHT,
        )
    )

    assert isinstance(generated, GeneratedInitialMomentumProblem)
    assert generated.scenario == legacy


def test_generated_outputs_are_deterministic_with_stable_ids_and_provenance() -> None:
    first = FACTORY.generate(
        request(
            seed=18472,
            family=MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION,
            difficulty=Difficulty.ADVANCED,
            axis=PositiveAxis.LEFT,
        )
    )
    second = FACTORY.generate(
        request(
            seed=18472,
            family=MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION,
            difficulty=Difficulty.ADVANCED,
            axis=PositiveAxis.LEFT,
        )
    )

    assert first == second
    assert first.metadata.identifier == second.metadata.identifier
    assert first.metadata.provenance == second.metadata.provenance
    assert isinstance(first, GeneratedCollisionProblem)
    assert first.interaction.identifier.endswith("-interaction")


def test_different_seeds_can_change_authored_problem_values() -> None:
    outputs = {
        FACTORY.generate(
            request(seed=seed, family=MomentumGenerationFamily.IMPULSE_FORCE_TIME)
        ).input_data
        for seed in range(6)
    }

    assert len(outputs) > 1


def test_generation_does_not_mutate_global_random_state() -> None:
    random.seed(991)
    before = random.getstate()

    FACTORY.generate(request(seed=33, family=MomentumGenerationFamily.MOMENTUM_CHANGE))

    assert random.getstate() == before


def test_difficulty_profiles_are_distinct_platform_policies() -> None:
    policy = FACTORY.policy

    assert policy.profile_for(Difficulty.INTRODUCTORY) != policy.profile_for(Difficulty.MODERATE)
    assert policy.profile_for(Difficulty.MODERATE) != policy.profile_for(Difficulty.ADVANCED)
    assert policy.policy_version == "2"


def test_generated_values_are_inside_selected_policy_pools() -> None:
    policy = FACTORY.policy
    output = FACTORY.generate(
        request(
            family=MomentumGenerationFamily.IMPULSE_FORCE_TIME,
            difficulty=Difficulty.ADVANCED,
        )
    )
    assert isinstance(output, GeneratedImpulseForceTimeProblem)
    profile = policy.profile_for(Difficulty.ADVANCED)
    assert abs(output.input_data.force.value) in profile.force_magnitudes_n
    assert output.input_data.contact_time.value in profile.contact_times_s


@pytest.mark.parametrize(
    "values",
    [
        ((), (1.0,), (1.0,), (1.0,), (1.0,)),
        ((1.0,), (0.0,), (1.0,), (1.0,), (1.0,)),
        ((1.0,), (1.0,), (float("nan"),), (1.0,), (1.0,)),
        ((1.0, 1.0), (1.0,), (1.0,), (1.0,), (1.0,)),
    ],
)
def test_difficulty_profile_rejects_invalid_or_duplicate_pools(
    values: tuple[tuple[float, ...], ...],
) -> None:
    with pytest.raises(ValueError):
        MomentumProblemDifficultyProfile(*values)


def test_contact_time_generation_rejects_zero_or_opposite_sign_inputs() -> None:
    output = FACTORY.generate(
        request(
            family=MomentumGenerationFamily.CONTACT_TIME_FROM_IMPULSE_FORCE,
            axis=PositiveAxis.LEFT,
        )
    )

    assert isinstance(output, GeneratedContactTimeProblem)
    assert output.impulse.value != 0
    assert output.force.value != 0
    assert output.impulse.value * output.force.value > 0


@pytest.mark.parametrize("seed", range(16))
@pytest.mark.parametrize("family", list(MomentumGenerationFamily))
def test_fixed_seed_corpus_remains_solver_supported(
    seed: int, family: MomentumGenerationFamily
) -> None:
    for difficulty in Difficulty:
        for axis in PositiveAxis:
            output = FACTORY.generate(
                request(seed, family=family, difficulty=difficulty, axis=axis)
            )
            if isinstance(output, GeneratedMomentumChangeProblem):
                MomentumImpulseRelationshipSolver().calculate_momentum_change(output.input_data)
            elif isinstance(output, GeneratedImpulseForceTimeProblem):
                MomentumImpulseRelationshipSolver().calculate_impulse_from_force_time(
                    output.input_data
                )
            elif isinstance(output, GeneratedForceFromMomentumChangeProblem):
                solver = MomentumImpulseRelationshipSolver()
                result = solver.calculate_momentum_change(output.momentum_change_input)
                solver.calculate_force_from_momentum_change(result, output.contact_time)
            elif isinstance(output, GeneratedContactTimeProblem):
                MomentumImpulseRelationshipSolver().calculate_contact_time_from_impulse(
                    output.impulse, output.force, output.positive_axis
                )
            elif isinstance(output, GeneratedCollisionProblem):
                solver = ConstrainedMomentumSolver(output.interaction)
                assert solver.validate(solver.solve()).valid


def test_known_collision_authors_one_stable_final_body_only() -> None:
    output = FACTORY.generate(
        request(family=MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION)
    )

    assert isinstance(output, GeneratedCollisionProblem)
    assert isinstance(output.interaction.constraint, KnownFinalVelocityConstraint)
    assert output.interaction.constraint.body_identifier in {
        body.identifier for body in output.scenario.bodies
    }
    assert hasattr(output.interaction.constraint, "final_velocity")
    assert not hasattr(output.interaction, "final_states")


def test_sticking_collision_authors_constraint_without_a_common_velocity() -> None:
    output = FACTORY.generate(
        request(family=MomentumGenerationFamily.STICKING_COLLISION)
    )

    assert isinstance(output, GeneratedCollisionProblem)
    assert isinstance(output.interaction.constraint, CommonFinalVelocityConstraint)
    assert set(output.interaction.constraint.body_identifiers) == {
        body.identifier for body in output.scenario.bodies
    }
    assert not hasattr(output.interaction.constraint, "final_velocity")


def test_complete_collision_is_solver_validated_without_storing_a_solution() -> None:
    output = FACTORY.generate(
        request(
            seed=19,
            family=MomentumGenerationFamily.COMPLETE_FINAL_STATE_COLLISION,
            difficulty=Difficulty.ADVANCED,
        )
    )

    assert isinstance(output, GeneratedCollisionProblem)
    solver = ConstrainedMomentumSolver(output.interaction)
    assert solver.validate(solver.solve()).valid
    assert not hasattr(output, "solution")


def test_advanced_momentum_change_corpus_contains_direction_reversal() -> None:
    outputs = [
        FACTORY.generate(
            request(
                seed=seed,
                family=MomentumGenerationFamily.MOMENTUM_CHANGE,
                difficulty=Difficulty.ADVANCED,
                axis=PositiveAxis.RIGHT,
            )
        )
        for seed in range(40)
    ]
    reversals = [
        output
        for output in outputs
        if isinstance(output, GeneratedMomentumChangeProblem)
        and output.input_data.initial_velocity.physical_direction(PositiveAxis.RIGHT)
        is PhysicalDirection.RIGHT
        and output.input_data.final_velocity.physical_direction(PositiveAxis.RIGHT)
        is PhysicalDirection.LEFT
    ]

    assert reversals


def test_policy_rejects_unsupported_family_and_axis() -> None:
    policy = FACTORY.policy.__class__(
        allowed_families=(MomentumGenerationFamily.MOMENTUM_CHANGE,),
        allowed_axes=(PositiveAxis.RIGHT,),
    )
    factory = MomentumProblemFactory(policy)

    with pytest.raises(ValueError, match="family"):
        factory.generate(request(family=MomentumGenerationFamily.STICKING_COLLISION))
    with pytest.raises(ValueError, match="axis"):
        factory.generate(request(axis=PositiveAxis.LEFT))


def test_policy_and_outputs_are_immutable() -> None:
    with pytest.raises(AttributeError):
        FACTORY.policy.policy_version = "3"  # type: ignore[misc]
    output = FACTORY.generate(
        request(family=MomentumGenerationFamily.MOMENTUM_CHANGE)
    )
    with pytest.raises(AttributeError):
        output.metadata = output.metadata  # type: ignore[misc]


def test_generation_module_has_no_authoritative_relationship_equations() -> None:
    source = inspect.getsource(generation_module)

    assert "MomentumImpulseSolver" not in source
    assert "MomentumImpulseRelationshipSolver" not in source
    assert "fastapi" not in source.lower()
    assert "pydantic" not in source.lower()
    assert "random.seed" not in source
