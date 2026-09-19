import pytest

from assessment_platform.core import GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    CollisionClassification,
    CommonFinalVelocityConstraint,
    CompleteFinalStateConstraint,
    ConstrainedMomentumSolver,
    FinalBodyState,
    Impulse,
    InteractionConstraintKind,
    Kilograms,
    KineticEnergy,
    KnownFinalVelocityConstraint,
    MetresPerSecond,
    Momentum,
    MomentumBody,
    MomentumInteraction,
    MomentumScenario,
    PositiveAxis,
    SystemBoundary,
)


def body(identifier: str, mass: float, velocity: float) -> MomentumBody:
    return MomentumBody(identifier, Kilograms(mass), MetresPerSecond(velocity))


def scenario(
    *,
    bodies: tuple[MomentumBody, ...] = (body("a", 2, 4), body("b", 3, -1)),
    positive_axis: PositiveAxis = PositiveAxis.RIGHT,
    system: SystemBoundary | None = None,
) -> MomentumScenario:
    return MomentumScenario(
        identifier="scenario-1",
        bodies=bodies,
        positive_axis=positive_axis,
        system=system or SystemBoundary(isolated=True),
        seed=GenerationSeed(17),
    )


def interaction(
    constraint: object,
    *,
    model: MomentumScenario | None = None,
) -> MomentumInteraction:
    return MomentumInteraction("interaction-1", model or scenario(), constraint)  # type: ignore[arg-type]


def state_map(solution: object) -> dict[str, float]:
    return {
        state.body_identifier: state.final_velocity.value
        for state in solution.final_states  # type: ignore[union-attr]
    }


def test_known_final_velocity_derives_the_other_body_by_stable_identifier() -> None:
    model = interaction(KnownFinalVelocityConstraint("a", MetresPerSecond(1)))

    result = ConstrainedMomentumSolver(model).solve()

    assert state_map(result) == {"a": 1.0, "b": 1.0}
    assert result.final_total_momentum == Momentum(5)
    assert [state.final_momentum for state in result.final_states] == [
        Momentum(2),
        Momentum(3),
    ]
    assert result.constraint_kind is InteractionConstraintKind.KNOWN_FINAL_VELOCITY
    assert ConstrainedMomentumSolver(model).validate(result).valid


def test_known_final_velocity_does_not_use_body_tuple_order_for_lookup() -> None:
    model = interaction(
        KnownFinalVelocityConstraint("b", MetresPerSecond(1)),
        model=scenario(bodies=(body("b", 3, -1), body("a", 2, 4))),
    )

    result = ConstrainedMomentumSolver(model).solve()

    assert state_map(result) == {"b": 1.0, "a": 1.0}
    assert tuple(state.body_identifier for state in result.final_states) == ("b", "a")


def test_known_final_velocity_applies_external_impulse_exactly_once() -> None:
    model = interaction(
        KnownFinalVelocityConstraint("a", MetresPerSecond(0)),
        model=scenario(
            system=SystemBoundary(isolated=False, external_impulse=Impulse(-2))
        ),
    )

    result = ConstrainedMomentumSolver(model).solve()

    assert result.initial_total_momentum == Momentum(5)
    assert result.external_impulse == Impulse(-2)
    assert result.final_total_momentum == Momentum(3)
    assert state_map(result) == {"a": 0.0, "b": 1.0}
    assert result.classification is None
    assert ConstrainedMomentumSolver(model).validate(result).valid


def test_common_final_velocity_solves_sticking_for_both_bodies() -> None:
    model = interaction(CommonFinalVelocityConstraint(("b", "a")))

    result = ConstrainedMomentumSolver(model).solve()

    assert state_map(result) == {"a": 1.0, "b": 1.0}
    assert result.classification is CollisionClassification.PERFECTLY_INELASTIC
    assert ConstrainedMomentumSolver(model).validate(result).valid


def test_common_final_velocity_requires_exactly_the_two_scenario_bodies() -> None:
    model = interaction(
        CommonFinalVelocityConstraint(("a", "b")),
        model=scenario(
            bodies=(body("a", 2, 4), body("b", 3, -1), body("c", 1, 0))
        ),
    )

    with pytest.raises(ValueError, match="exactly two"):
        ConstrainedMomentumSolver(model).solve()


def test_known_final_velocity_rejects_a_constrained_three_body_scenario() -> None:
    model = interaction(
        KnownFinalVelocityConstraint("a", MetresPerSecond(1)),
        model=scenario(
            bodies=(body("a", 2, 4), body("b", 3, -1), body("c", 1, 0))
        ),
    )

    with pytest.raises(ValueError, match="exactly two"):
        ConstrainedMomentumSolver(model).solve()


def test_complete_final_state_is_preserved_and_classified_as_elastic() -> None:
    model = interaction(
        CompleteFinalStateConstraint(
            (FinalBodyState("b", MetresPerSecond(3)), FinalBodyState("a", MetresPerSecond(-2)))
        )
    )

    result = ConstrainedMomentumSolver(model).solve()

    assert state_map(result) == {"a": -2.0, "b": 3.0}
    assert result.initial_kinetic_energy == KineticEnergy(17.5)
    assert result.final_kinetic_energy == KineticEnergy(17.5)
    assert result.classification is CollisionClassification.ELASTIC
    assert ConstrainedMomentumSolver(model).validate(result).valid


def test_complete_final_state_can_be_inelastic_without_being_sticking() -> None:
    model = interaction(
        CompleteFinalStateConstraint(
            (FinalBodyState("a", MetresPerSecond(2)), FinalBodyState("b", MetresPerSecond(1 / 3)))
        )
    )

    result = ConstrainedMomentumSolver(model).solve()

    assert result.classification is CollisionClassification.INELASTIC
    assert result.final_kinetic_energy.value < result.initial_kinetic_energy.value
    assert ConstrainedMomentumSolver(model).validate(result).valid


def test_invalid_complete_final_state_is_not_repaired_by_the_solver() -> None:
    model = interaction(
        CompleteFinalStateConstraint(
            (FinalBodyState("a", MetresPerSecond(0)), FinalBodyState("b", MetresPerSecond(0)))
        )
    )
    solver = ConstrainedMomentumSolver(model)

    result = solver.solve()

    assert state_map(result) == {"a": 0.0, "b": 0.0}
    assert not solver.validate(result).valid


def test_underdetermined_interaction_is_rejected_without_zero_placeholders() -> None:
    with pytest.raises(ValueError, match="underdetermined"):
        ConstrainedMomentumSolver(None).solve()


def test_axis_reversal_reverses_signed_final_velocities_and_preserves_classification() -> None:
    right = ConstrainedMomentumSolver(
        interaction(KnownFinalVelocityConstraint("a", MetresPerSecond(1)))
    ).solve()
    left = ConstrainedMomentumSolver(
        interaction(
            KnownFinalVelocityConstraint("a", MetresPerSecond(-1)),
            model=scenario(
                positive_axis=PositiveAxis.LEFT,
                bodies=(body("a", 2, -4), body("b", 3, 1)),
            ),
        )
    ).solve()

    assert state_map(left) == {"a": -right.final_states[0].final_velocity.value, "b": -1.0}
    assert left.classification is right.classification


def test_constrained_solver_is_deterministic_and_immutable() -> None:
    model = interaction(KnownFinalVelocityConstraint("a", MetresPerSecond(1)))
    solver = ConstrainedMomentumSolver(model)

    first = solver.solve()
    second = solver.solve()

    assert first == second
    with pytest.raises(AttributeError):
        first.final_total_momentum = Momentum(99)  # type: ignore[misc]


@pytest.mark.parametrize("value", [0.0, 1.0])
def test_kinetic_energy_accepts_finite_non_negative_values(value: float) -> None:
    assert KineticEnergy(value).value == value


@pytest.mark.parametrize("value", [-1.0, float("inf"), float("nan")])
def test_kinetic_energy_rejects_invalid_values(value: float) -> None:
    with pytest.raises(ValueError):
        KineticEnergy(value)
