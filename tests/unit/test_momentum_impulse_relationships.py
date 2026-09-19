import pytest

from assessment_platform.domains.physical_sciences.mechanics import (
    ForceTimeInput,
    ForceTimeResult,
    Impulse,
    ImpulseResult,
    Kilograms,
    MetresPerSecond,
    Momentum,
    MomentumChange,
    MomentumChangeInput,
    MomentumChangeResult,
    MomentumImpulseRelationshipSolver,
    Newtons,
    PositiveAxis,
    Seconds,
)

SOLVER = MomentumImpulseRelationshipSolver()


def change(
    mass: float,
    initial_velocity: float,
    final_velocity: float,
    axis: PositiveAxis = PositiveAxis.RIGHT,
) -> MomentumChangeResult:
    return SOLVER.calculate_momentum_change(
        MomentumChangeInput(
            Kilograms(mass),
            MetresPerSecond(initial_velocity),
            MetresPerSecond(final_velocity),
            axis,
        )
    )


@pytest.mark.parametrize(
    ("initial", "final", "expected"),
    [
        (3, 7, 8),
        (6, 2, -8),
        (3, 0, -6),
        (0, 3, 6),
        (5, -3, -16),
        (-3, 4, 14),
        (-2, -5, -6),
        (4, 4, 0),
    ],
)
def test_momentum_change_is_signed_final_minus_initial(
    initial: float, final: float, expected: float
) -> None:
    result = change(2, initial, final)

    assert result.initial_momentum == Momentum(2 * initial)
    assert result.final_momentum == Momentum(2 * final)
    assert result.momentum_change == MomentumChange(expected)


def test_impulse_equals_signed_momentum_change_and_remains_distinct() -> None:
    result = SOLVER.calculate_impulse_from_momentum_change(change(2, 5, -3))

    assert result == ImpulseResult(Impulse(-16), MomentumChange(-16), PositiveAxis.RIGHT)
    assert type(result.impulse) is Impulse
    assert type(result.momentum_change) is MomentumChange
    assert not isinstance(result.impulse, Momentum)


@pytest.mark.parametrize(
    ("force", "time", "expected"),
    [(4, 2, 8), (-4, 2, -8), (0, 2, 0), (2.5, 0.4, 1)],
)
def test_impulse_from_force_and_positive_contact_time_preserves_force_sign(
    force: float, time: float, expected: float
) -> None:
    result = SOLVER.calculate_impulse_from_force_time(
        ForceTimeInput(Newtons(force), Seconds(time), PositiveAxis.RIGHT)
    )

    assert result.impulse == Impulse(expected)
    assert result.momentum_change == MomentumChange(expected)


def test_force_from_impulse_and_contact_time_uses_full_precision() -> None:
    result = SOLVER.calculate_force_from_impulse(
        Impulse(1), Seconds(3), PositiveAxis.RIGHT
    )

    assert result.force == Newtons(1 / 3)
    assert result.impulse == Impulse(1)
    assert result.momentum_change == MomentumChange(1)


def test_force_from_momentum_change_is_newtons_second_law_in_momentum_form() -> None:
    result = SOLVER.calculate_force_from_momentum_change(change(2, 3, 7), Seconds(2))

    assert result.force == Newtons(4)
    assert result.contact_time == Seconds(2)


@pytest.mark.parametrize(
    ("impulse", "force", "expected_time"),
    [(12, 4, 3), (-12, -4, 3), (1, 3, 1 / 3)],
)
def test_contact_time_requires_compatible_signed_impulse_and_force(
    impulse: float, force: float, expected_time: float
) -> None:
    result = SOLVER.calculate_contact_time_from_impulse(
        Impulse(impulse), Newtons(force), PositiveAxis.RIGHT
    )

    assert result.contact_time == Seconds(expected_time)
    assert result.impulse == Impulse(impulse)
    assert result.force == Newtons(force)


def test_contact_time_can_be_derived_from_momentum_change() -> None:
    result = SOLVER.calculate_contact_time_from_momentum_change(
        change(1.5, 8, -4), Newtons(-36)
    )

    assert result.contact_time == Seconds(0.5)
    assert result.momentum_change == MomentumChange(-18)


def test_opposite_impulse_and_force_signs_are_rejected_without_abs_conversion() -> None:
    with pytest.raises(ValueError, match="compatible signs"):
        SOLVER.calculate_contact_time_from_impulse(
            Impulse(-12), Newtons(4), PositiveAxis.RIGHT
        )


def test_zero_impulse_and_zero_force_contact_time_is_underdetermined() -> None:
    with pytest.raises(ValueError, match="underdetermined"):
        SOLVER.calculate_contact_time_from_impulse(
            Impulse(0), Newtons(0), PositiveAxis.RIGHT
        )


def test_non_zero_impulse_and_zero_force_contact_time_is_rejected() -> None:
    with pytest.raises(ValueError, match="zero force"):
        SOLVER.calculate_contact_time_from_impulse(
            Impulse(1), Newtons(0), PositiveAxis.RIGHT
        )


def test_zero_force_with_positive_time_produces_zero_impulse() -> None:
    result = SOLVER.calculate_impulse_from_force_time(
        ForceTimeInput(Newtons(0), Seconds(2), PositiveAxis.RIGHT)
    )

    assert result.impulse == Impulse(0)


def test_axis_reversal_negates_vector_quantities_but_not_contact_time() -> None:
    right_change = change(2, 5, -3, PositiveAxis.RIGHT)
    left_change = change(2, -5, 3, PositiveAxis.LEFT)
    right_force = SOLVER.calculate_force_from_momentum_change(right_change, Seconds(2))
    left_force = SOLVER.calculate_force_from_momentum_change(left_change, Seconds(2))

    assert left_change.momentum_change == MomentumChange(-right_change.momentum_change.value)
    assert (
        SOLVER.calculate_impulse_from_momentum_change(left_change).impulse
        == Impulse(-SOLVER.calculate_impulse_from_momentum_change(right_change).impulse.value)
    )
    assert left_force.force == Newtons(-right_force.force.value)
    assert left_force.contact_time == right_force.contact_time
    assert left_change.positive_axis is PositiveAxis.LEFT


def test_results_are_immutable_and_repeated_calls_are_deterministic() -> None:
    input_data = MomentumChangeInput(
        Kilograms(2), MetresPerSecond(3), MetresPerSecond(7), PositiveAxis.RIGHT
    )

    first = SOLVER.calculate_momentum_change(input_data)
    second = SOLVER.calculate_momentum_change(input_data)

    assert first == second
    with pytest.raises(AttributeError):
        first.momentum_change = MomentumChange(99)  # type: ignore[misc]


@pytest.mark.parametrize("value", [0, 1.5, -4.0])
def test_newtons_accepts_finite_signed_force_values(value: float) -> None:
    assert Newtons(value).value == value


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_seconds_rejects_non_positive_or_non_finite_contact_time(value: float) -> None:
    with pytest.raises(ValueError):
        Seconds(value)


@pytest.mark.parametrize("value", [float("inf"), float("nan")])
def test_relationship_value_objects_reject_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError):
        Newtons(value)
    with pytest.raises(ValueError):
        MomentumChange(value)


def test_inputs_require_explicit_axis_and_semantic_types() -> None:
    with pytest.raises(ValueError, match="positive_axis"):
        MomentumChangeInput(
            Kilograms(1), MetresPerSecond(1), MetresPerSecond(2), "right"  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="Seconds"):
        ForceTimeInput(Newtons(1), object(), PositiveAxis.RIGHT)  # type: ignore[arg-type]


def test_public_relationship_methods_reject_wrong_input_types() -> None:
    with pytest.raises(ValueError, match="MomentumChangeInput"):
        SOLVER.calculate_momentum_change(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="MomentumChangeResult"):
        SOLVER.calculate_impulse_from_momentum_change(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Impulse"):
        SOLVER.calculate_force_from_impulse(object(), Seconds(1), PositiveAxis.RIGHT)  # type: ignore[arg-type]


def test_result_models_reject_contradictory_relationship_values() -> None:
    with pytest.raises(ValueError, match="final minus initial"):
        MomentumChangeResult(
            Momentum(2), Momentum(8), MomentumChange(7), PositiveAxis.RIGHT
        )
    with pytest.raises(ValueError, match="momentum change"):
        ImpulseResult(Impulse(4), MomentumChange(3), PositiveAxis.RIGHT)
    with pytest.raises(ValueError, match="force multiplied"):
        ForceTimeResult(
            Newtons(4), Seconds(2), Impulse(7), MomentumChange(7), PositiveAxis.RIGHT
        )
