import inspect

import pytest

import assessment_platform.domains.physical_sciences.mechanics.momentum_impulse as momentum_module
from assessment_platform.core import GenerationProvenance, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    Kilograms,
    MetresPerSecond,
    Momentum,
    MomentumBody,
    MomentumScenario,
    PhysicalDirection,
    PositiveAxis,
    SystemBoundary,
)


def body(identifier: str = "ball-a", velocity: float = 4) -> MomentumBody:
    return MomentumBody(identifier, Kilograms(2), MetresPerSecond(velocity))


def scenario(**overrides: object) -> MomentumScenario:
    values: dict[str, object] = {
        "identifier": "momentum-scenario-1",
        "bodies": (body(), body("ball-b", -3)),
        "positive_axis": PositiveAxis.RIGHT,
        "system": SystemBoundary(isolated=True),
    }
    values.update(overrides)
    return MomentumScenario(**values)  # type: ignore[arg-type]


def test_valid_initial_state_preserves_identity_axis_and_signed_velocity() -> None:
    model = scenario(seed=GenerationSeed(42))

    assert model.bodies[1].initial_velocity == MetresPerSecond(-3)
    assert model.direction_of(model.bodies[0]) is PhysicalDirection.RIGHT
    assert model.direction_of(model.bodies[1]) is PhysicalDirection.LEFT
    assert model.seed == GenerationSeed(42)


def test_left_positive_axis_does_not_assume_right_is_positive() -> None:
    model = scenario(positive_axis=PositiveAxis.LEFT)

    assert model.direction_of(model.bodies[0]) is PhysicalDirection.LEFT
    assert model.direction_of(model.bodies[1]) is PhysicalDirection.RIGHT


def test_zero_velocity_is_rest() -> None:
    still = body(velocity=0)

    assert still.initial_velocity.physical_direction(PositiveAxis.RIGHT) is PhysicalDirection.REST


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), float("-inf")])
def test_mass_requires_a_finite_positive_value(value: float) -> None:
    with pytest.raises(ValueError):
        Kilograms(value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_signed_physical_values_reject_non_finite_numbers(value: float) -> None:
    with pytest.raises(ValueError):
        MetresPerSecond(value)
    with pytest.raises(ValueError):
        Momentum(value)
    with pytest.raises(ValueError):
        Impulse(value)


def test_signed_velocity_accepts_both_directions_and_zero() -> None:
    assert MetresPerSecond(-4).value == -4
    assert MetresPerSecond(4).value == 4
    assert MetresPerSecond(0).value == 0


def test_momentum_and_impulse_are_distinct_semantic_types() -> None:
    momentum = Momentum(8)
    impulse = Impulse(8)

    assert momentum.value == impulse.value
    assert type(momentum) is not type(impulse)


def test_non_isolated_system_requires_an_explicit_external_impulse() -> None:
    with pytest.raises(ValueError, match="external impulse"):
        SystemBoundary(isolated=False)

    boundary = SystemBoundary(isolated=False, external_impulse=Impulse(-2.5))
    assert boundary.external_impulse == Impulse(-2.5)


def test_isolated_system_cannot_declare_an_external_impulse() -> None:
    with pytest.raises(ValueError, match="isolated"):
        SystemBoundary(isolated=True, external_impulse=Impulse(0))


def test_scenario_rejects_empty_or_duplicate_body_identity() -> None:
    with pytest.raises(ValueError, match="MomentumBody"):
        scenario(bodies=())
    with pytest.raises(ValueError, match="unique"):
        scenario(bodies=(body(), body()))


def test_scenario_rejects_invalid_body_and_axis_types() -> None:
    with pytest.raises(ValueError, match="MomentumBody"):
        scenario(bodies=(object(),))
    with pytest.raises(ValueError, match="positive_axis"):
        scenario(positive_axis="right")


def test_scenario_keeps_initial_state_only_and_is_immutable() -> None:
    first = scenario(
        provenance=GenerationProvenance("m3-domain", "1", GenerationSeed(7)),
    )
    second = scenario(
        provenance=GenerationProvenance("m3-domain", "1", GenerationSeed(7)),
    )

    assert first == second
    assert not hasattr(first, "final_bodies")
    with pytest.raises(AttributeError):
        first.positive_axis = PositiveAxis.LEFT  # type: ignore[misc]


def test_direction_of_rejects_a_body_from_another_scenario() -> None:
    model = scenario()

    with pytest.raises(ValueError, match="not part"):
        model.direction_of(body("other"))


def test_assumptions_are_normalized_and_must_not_be_empty() -> None:
    model = scenario(assumptions=(" one-dimensional motion ",))
    assert model.assumptions == ("one-dimensional motion",)

    with pytest.raises(ValueError, match="assumptions"):
        scenario(assumptions=())


def test_momentum_domain_module_has_no_framework_dependency() -> None:
    source = inspect.getsource(momentum_module)

    assert "fastapi" not in source.lower()
    assert "pydantic" not in source.lower()
    assert "http" not in source.lower()
