import pytest

from assessment_platform.core import GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    Kilograms,
    MetresPerSecond,
    Momentum,
    MomentumBody,
    MomentumScenario,
    PositiveAxis,
    SystemBoundary,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse_solver import (
    MomentumImpulseSolution,
    MomentumImpulseSolver,
)


def body(identifier: str, mass: float, velocity: float) -> MomentumBody:
    return MomentumBody(identifier, Kilograms(mass), MetresPerSecond(velocity))


def scenario(
    *,
    positive_axis: PositiveAxis = PositiveAxis.RIGHT,
    isolated: bool = True,
    external_impulse: Impulse | None = None,
    bodies: tuple[MomentumBody, ...] = (
        body("a", 2, 3),
        body("b", 1, -4),
    ),
) -> MomentumScenario:
    return MomentumScenario(
        identifier="scenario-1",
        bodies=bodies,
        positive_axis=positive_axis,
        system=SystemBoundary(isolated, external_impulse),
        seed=GenerationSeed(17),
    )


def test_body_momentum_preserves_positive_negative_and_zero_signs() -> None:
    solver = MomentumImpulseSolver(
        scenario(bodies=(body("positive", 2, 3), body("negative", 2, -3), body("rest", 2, 0)))
    )

    result = solver.solve()

    assert [item.momentum for item in result.body_momenta] == [
        Momentum(6),
        Momentum(-6),
        Momentum(0),
    ]
    assert result.initial_total_momentum == Momentum(0)


def test_total_momentum_is_signed_sum_for_opposite_moving_bodies() -> None:
    result = MomentumImpulseSolver(scenario()).solve()

    assert result.initial_total_momentum == Momentum(2)
    assert result.final_total_momentum == Momentum(2)
    assert result.external_impulse == Impulse(0)


def test_non_isolated_external_impulse_changes_only_aggregate_total() -> None:
    result = MomentumImpulseSolver(
        scenario(isolated=False, external_impulse=Impulse(-5))
    ).solve()

    assert result.initial_total_momentum == Momentum(2)
    assert result.external_impulse == Impulse(-5)
    assert result.final_total_momentum == Momentum(-3)
    assert len(result.body_momenta) == 2


def test_zero_external_impulse_is_valid_for_a_non_isolated_system() -> None:
    result = MomentumImpulseSolver(
        scenario(isolated=False, external_impulse=Impulse(0))
    ).solve()

    assert result.final_total_momentum == result.initial_total_momentum


def test_axis_reversal_reverses_signs_but_preserves_physical_result() -> None:
    right_positive = MomentumImpulseSolver(
        scenario(
            positive_axis=PositiveAxis.RIGHT,
            bodies=(body("a", 2, 3), body("b", 1, -4)),
        )
    ).solve()
    left_positive = MomentumImpulseSolver(
        scenario(
            positive_axis=PositiveAxis.LEFT,
            bodies=(body("a", 2, -3), body("b", 1, 4)),
        )
    ).solve()

    assert left_positive.body_momenta[0].momentum == Momentum(
        -right_positive.body_momenta[0].momentum.value
    )
    assert left_positive.body_momenta[1].momentum == Momentum(
        -right_positive.body_momenta[1].momentum.value
    )
    assert left_positive.initial_total_momentum == Momentum(
        -right_positive.initial_total_momentum.value
    )


def test_solver_is_deterministic_and_solution_is_immutable() -> None:
    solver = MomentumImpulseSolver(scenario())
    first = solver.solve()
    second = solver.solve()

    assert first == second
    with pytest.raises(AttributeError):
        first.final_total_momentum = Momentum(99)  # type: ignore[misc]


def test_isolated_system_validates_conservation_and_all_derived_values() -> None:
    solver = MomentumImpulseSolver(scenario())

    assert solver.validate(solver.solve()).valid


def test_non_isolated_system_validates_impulse_change_relationship() -> None:
    solver = MomentumImpulseSolver(
        scenario(isolated=False, external_impulse=Impulse(7.5))
    )

    assert solver.validate(solver.solve()).valid


def test_validation_rejects_tampered_body_momentum_and_total() -> None:
    solver = MomentumImpulseSolver(scenario())
    original = solver.solve()
    tampered = MomentumImpulseSolution(
        scenario_identifier=original.scenario_identifier,
        body_momenta=(
            original.body_momenta[0],
            type(original.body_momenta[1])("b", Momentum(999)),
        ),
        initial_total_momentum=Momentum(999),
        external_impulse=original.external_impulse,
        final_total_momentum=Momentum(999),
        positive_axis=original.positive_axis,
        seed=original.seed,
    )

    validation = solver.validate(tampered)

    assert not validation.valid
    assert "body momentum" in " ".join(validation.errors)
    assert "initial total" in " ".join(validation.errors)


def test_validation_rejects_mismatched_scenario_metadata() -> None:
    solver = MomentumImpulseSolver(scenario())
    original = solver.solve()
    tampered = MomentumImpulseSolution(
        scenario_identifier="other-scenario",
        body_momenta=original.body_momenta,
        initial_total_momentum=original.initial_total_momentum,
        external_impulse=original.external_impulse,
        final_total_momentum=original.final_total_momentum,
        positive_axis=PositiveAxis.LEFT,
        seed=GenerationSeed(18),
    )

    validation = solver.validate(tampered)

    assert not validation.valid
    assert len(validation.errors) == 3


def test_underdetermined_collision_does_not_fabricate_final_body_velocities() -> None:
    solver = MomentumImpulseSolver(
        scenario(
            bodies=(body("a", 2, 5), body("b", 3, -1)),
            isolated=True,
        )
    )

    solution = solver.solve()

    assert solution.initial_total_momentum == Momentum(7)
    assert solution.final_total_momentum == Momentum(7)
    assert not hasattr(solution, "final_body_velocities")


def test_solver_rejects_a_non_scenario_input() -> None:
    with pytest.raises(ValueError, match="MomentumScenario"):
        MomentumImpulseSolver(object())  # type: ignore[arg-type]
