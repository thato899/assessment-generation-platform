import inspect

import pytest

from assessment_platform.core import GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    CommonFinalVelocityConstraint,
    CompleteFinalStateConstraint,
    FinalBodyState,
    Impulse,
    InteractionConstraintKind,
    Kilograms,
    KnownFinalVelocityConstraint,
    MetresPerSecond,
    MomentumBody,
    MomentumInteraction,
    MomentumScenario,
    PositiveAxis,
    SystemBoundary,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    momentum_interaction as interaction_module,
)


def body(identifier: str, velocity: float) -> MomentumBody:
    return MomentumBody(identifier, Kilograms(2), MetresPerSecond(velocity))


def scenario(
    *,
    positive_axis: PositiveAxis = PositiveAxis.RIGHT,
    bodies: tuple[MomentumBody, ...] = (body("a", 4), body("b", -1)),
    system: SystemBoundary | None = None,
) -> MomentumScenario:
    return MomentumScenario(
        identifier="scenario-1",
        bodies=bodies,
        positive_axis=positive_axis,
        system=system or SystemBoundary(isolated=True),
        seed=GenerationSeed(17),
    )


def test_known_final_velocity_preserves_authored_signed_value_and_kind() -> None:
    interaction = MomentumInteraction(
        "interaction-1",
        scenario(),
        KnownFinalVelocityConstraint("a", MetresPerSecond(-2)),
    )

    assert interaction.constraint.kind is InteractionConstraintKind.KNOWN_FINAL_VELOCITY
    assert interaction.constraint.body_identifier == "a"
    assert interaction.constraint.final_velocity == MetresPerSecond(-2)


@pytest.mark.parametrize("value", [-4.0, 0.0, 4.0])
def test_known_final_velocity_accepts_negative_zero_and_positive_values(value: float) -> None:
    constraint = KnownFinalVelocityConstraint("a", MetresPerSecond(value))

    assert constraint.final_velocity.value == value


def test_known_final_velocity_rejects_unknown_body() -> None:
    with pytest.raises(ValueError, match="not part"):
        MomentumInteraction(
            "interaction-1",
            scenario(),
            KnownFinalVelocityConstraint("unknown", MetresPerSecond(2)),
        )


def test_known_final_velocity_rejects_invalid_identifier_or_unit() -> None:
    with pytest.raises(ValueError, match="identifier"):
        KnownFinalVelocityConstraint(" ", MetresPerSecond(2))
    with pytest.raises(ValueError, match="MetresPerSecond"):
        KnownFinalVelocityConstraint("a", object())  # type: ignore[arg-type]


def test_common_final_velocity_represents_explicit_sticking_without_a_value() -> None:
    interaction = MomentumInteraction(
        "interaction-1",
        scenario(),
        CommonFinalVelocityConstraint(("a", "b")),
    )

    assert interaction.constraint.kind is InteractionConstraintKind.COMMON_FINAL_VELOCITY
    assert interaction.constraint.body_identifiers == ("a", "b")
    assert not hasattr(interaction.constraint, "final_velocity")


@pytest.mark.parametrize("identifiers", [("a",), ("a", "b", "c"), ("a", "a")])
def test_common_final_velocity_requires_two_distinct_bodies(
    identifiers: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        CommonFinalVelocityConstraint(identifiers)


def test_common_final_velocity_rejects_unknown_body_in_interaction() -> None:
    with pytest.raises(ValueError, match="not part"):
        MomentumInteraction(
            "interaction-1",
            scenario(),
            CommonFinalVelocityConstraint(("a", "unknown")),
        )


def test_complete_final_state_preserves_signed_authored_states() -> None:
    constraint = CompleteFinalStateConstraint(
        (
            FinalBodyState("a", MetresPerSecond(-2)),
            FinalBodyState("b", MetresPerSecond(3)),
        )
    )
    interaction = MomentumInteraction("interaction-1", scenario(), constraint)

    assert interaction.constraint.kind is InteractionConstraintKind.COMPLETE_FINAL_STATE
    assert interaction.constraint.final_states == (
        FinalBodyState("a", MetresPerSecond(-2)),
        FinalBodyState("b", MetresPerSecond(3)),
    )


def test_complete_final_state_rejects_duplicate_entries() -> None:
    with pytest.raises(ValueError, match="unique"):
        CompleteFinalStateConstraint(
            (
                FinalBodyState("a", MetresPerSecond(1)),
                FinalBodyState("a", MetresPerSecond(2)),
            )
        )


def test_complete_final_state_rejects_unknown_or_missing_body() -> None:
    with pytest.raises(ValueError, match="every scenario body"):
        MomentumInteraction(
            "interaction-1",
            scenario(),
            CompleteFinalStateConstraint((FinalBodyState("a", MetresPerSecond(1)),)),
        )
    with pytest.raises(ValueError, match="every scenario body"):
        MomentumInteraction(
            "interaction-1",
            scenario(),
            CompleteFinalStateConstraint(
                (
                    FinalBodyState("a", MetresPerSecond(1)),
                    FinalBodyState("b", MetresPerSecond(2)),
                    FinalBodyState("unknown", MetresPerSecond(3)),
                )
            ),
        )


def test_complete_final_state_uses_body_identity_not_tuple_position() -> None:
    interaction = MomentumInteraction(
        "interaction-1",
        scenario(),
        CompleteFinalStateConstraint(
            (
                FinalBodyState("b", MetresPerSecond(3)),
                FinalBodyState("a", MetresPerSecond(-2)),
            )
        ),
    )

    assert tuple(state.body_identifier for state in interaction.constraint.final_states) == (
        "b",
        "a",
    )


def test_complete_final_state_rejects_invalid_entries() -> None:
    with pytest.raises(ValueError, match="FinalBodyState"):
        CompleteFinalStateConstraint((object(),))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="final velocity"):
        FinalBodyState("a", object())  # type: ignore[arg-type]


def test_valid_scenario_can_remain_underdetermined_without_interaction() -> None:
    model = scenario()

    assert model.bodies
    assert not hasattr(model, "interaction")
    assert not hasattr(model, "final_bodies")


def test_non_isolated_external_impulse_remains_on_system_boundary() -> None:
    model = scenario(
        system=SystemBoundary(isolated=False, external_impulse=Impulse(-5)),
    )
    interaction = MomentumInteraction(
        "interaction-1",
        model,
        KnownFinalVelocityConstraint("a", MetresPerSecond(1)),
    )

    assert interaction.scenario.system.external_impulse == Impulse(-5)
    assert not hasattr(interaction, "external_impulse")


@pytest.mark.parametrize(
    ("axis", "value"),
    [(PositiveAxis.RIGHT, 4), (PositiveAxis.LEFT, -4)],
)
def test_final_velocity_preserves_the_selected_mathematical_axis(
    axis: PositiveAxis, value: float
) -> None:
    interaction = MomentumInteraction(
        "interaction-1",
        scenario(positive_axis=axis),
        KnownFinalVelocityConstraint("a", MetresPerSecond(value)),
    )

    assert interaction.scenario.positive_axis is axis
    assert interaction.constraint.final_velocity == MetresPerSecond(value)


def test_interaction_rejects_invalid_constraint_or_scenario_types() -> None:
    with pytest.raises(ValueError, match="MomentumScenario"):
        MomentumInteraction(
            "interaction-1",
            object(),  # type: ignore[arg-type]
            KnownFinalVelocityConstraint("a", MetresPerSecond(1)),
        )
    with pytest.raises(ValueError, match="constraint"):
        MomentumInteraction("interaction-1", scenario(), object())  # type: ignore[arg-type]


def test_interaction_models_are_immutable_and_deterministically_equal() -> None:
    first = MomentumInteraction(
        "interaction-1",
        scenario(),
        CompleteFinalStateConstraint(
            (FinalBodyState("a", MetresPerSecond(-2)), FinalBodyState("b", MetresPerSecond(3)))
        ),
    )
    second = MomentumInteraction(
        "interaction-1",
        scenario(),
        CompleteFinalStateConstraint(
            (FinalBodyState("a", MetresPerSecond(-2)), FinalBodyState("b", MetresPerSecond(3)))
        ),
    )

    assert first == second
    with pytest.raises(AttributeError):
        first.constraint = KnownFinalVelocityConstraint("a", MetresPerSecond(1))  # type: ignore[misc]
    with pytest.raises(TypeError):
        first.constraint.final_states[0] = FinalBodyState("a", MetresPerSecond(1))  # type: ignore[index]


def test_final_state_does_not_duplicate_body_mass_or_calculate_results() -> None:
    state = FinalBodyState("a", MetresPerSecond(2))

    assert not hasattr(state, "mass")
    assert not hasattr(state, "momentum")


def test_interaction_module_is_framework_independent_and_has_no_solver_logic() -> None:
    source = inspect.getsource(interaction_module)

    assert "fastapi" not in source.lower()
    assert "pydantic" not in source.lower()
    assert "MomentumImpulseSolver" not in source
    assert "KineticEnergy" not in source
    assert "Impulse(" not in source
