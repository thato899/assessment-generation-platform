import pytest

from assessment_platform.core import GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    Metres,
    MetresPerSecond,
    MetresPerSecondSquared,
    PositiveDirection,
    ScenarioType,
    VerticalProjectileScenario,
)


def scenario(**overrides: object) -> VerticalProjectileScenario:
    values: dict[str, object] = {
        "identifier": "scenario-1",
        "launch_position": Metres(0),
        "initial_velocity": MetresPerSecond(20),
        "gravitational_acceleration": MetresPerSecondSquared(-9.81),
        "positive_direction": PositiveDirection.UP,
        "launch_direction": LaunchDirection.UPWARD,
        "scenario_type": ScenarioType.PROJECTED_UPWARD,
    }
    values.update(overrides)
    return VerticalProjectileScenario(**values)  # type: ignore[arg-type]


def test_upward_ground_launch_is_explicit_and_seed_is_reusable() -> None:
    projectile = scenario(seed=GenerationSeed(18472))
    assert projectile.launch_position == Metres(0)
    assert projectile.initial_velocity == MetresPerSecond(20)
    assert projectile.seed == GenerationSeed(18472)
    assert "in the absence of air friction" in projectile.assumptions


def test_elevated_downward_launch_with_downward_positive_direction() -> None:
    projectile = scenario(
        launch_position=Metres(15),
        initial_velocity=MetresPerSecond(5),
        gravitational_acceleration=MetresPerSecondSquared(9.81),
        positive_direction=PositiveDirection.DOWN,
        launch_direction=LaunchDirection.DOWNWARD,
        scenario_type=ScenarioType.PROJECTED_DOWNWARD,
    )
    assert projectile.launch_position.value == 15


def test_elevated_drop_from_rest_is_supported() -> None:
    projectile = scenario(
        launch_position=Metres(25),
        initial_velocity=MetresPerSecond(0),
        launch_direction=LaunchDirection.REST,
        scenario_type=ScenarioType.DROPPED_FROM_REST,
    )
    assert projectile.initial_velocity.value == 0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_physical_values_reject_non_finite_numbers(value: float) -> None:
    with pytest.raises(ValueError):
        Metres(value)
    with pytest.raises(ValueError):
        MetresPerSecond(value)
    with pytest.raises(ValueError):
        MetresPerSecondSquared(value)


def test_sign_convention_rejects_gravity_in_wrong_direction() -> None:
    with pytest.raises(ValueError, match="negative"):
        scenario(gravitational_acceleration=MetresPerSecondSquared(9.81))


def test_sign_convention_rejects_inconsistent_launch_direction() -> None:
    with pytest.raises(ValueError, match="upward launch"):
        scenario(initial_velocity=MetresPerSecond(-20))


def test_scenario_type_must_match_launch_direction() -> None:
    with pytest.raises(ValueError, match="scenario_type"):
        scenario(scenario_type=ScenarioType.PROJECTED_DOWNWARD)


def test_values_are_immutable_and_construction_is_deterministic() -> None:
    first = scenario(seed=GenerationSeed(42))
    second = scenario(seed=GenerationSeed(42))
    assert first == second
    with pytest.raises(AttributeError):
        first.initial_velocity = MetresPerSecond(1)  # type: ignore[misc]
