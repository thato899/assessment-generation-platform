import pytest

from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    Metres,
    MetresPerSecond,
    MetresPerSecondSquared,
    PositiveDirection,
    ScenarioType,
    VerticalProjectileScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    EventType,
    Seconds,
    VerticalProjectileSolver,
)


def make_scenario(**overrides: object) -> VerticalProjectileScenario:
    values: dict[str, object] = {
        "identifier": "solver-case",
        "launch_position": Metres(0),
        "initial_velocity": MetresPerSecond(20),
        "gravitational_acceleration": MetresPerSecondSquared(-10),
        "positive_direction": PositiveDirection.UP,
        "launch_direction": LaunchDirection.UPWARD,
        "scenario_type": ScenarioType.PROJECTED_UPWARD,
    }
    values.update(overrides)
    return VerticalProjectileScenario(**values)  # type: ignore[arg-type]


def test_position_velocity_and_displacement_use_consistent_equations() -> None:
    solver = VerticalProjectileSolver(make_scenario())
    assert solver.position_at(Seconds(1)) == pytest.approx(15)
    assert solver.velocity_at(Seconds(1)) == pytest.approx(10)
    assert solver.displacement_over(Seconds(1)) == pytest.approx(15)


def test_upward_ground_launch_has_maximum_return_and_impact_events() -> None:
    solution = VerticalProjectileSolver(make_scenario()).solve()
    assert solution.event(EventType.MAXIMUM_HEIGHT).time.value == pytest.approx(2)
    assert solution.event(EventType.MAXIMUM_HEIGHT).position == pytest.approx(20)
    assert solution.event(EventType.RETURN_TO_LAUNCH_POSITION).time.value == pytest.approx(4)
    assert solution.event(EventType.GROUND_IMPACT).time.value == pytest.approx(4)


def test_elevated_upward_launch_selects_later_ground_root() -> None:
    solution = VerticalProjectileSolver(make_scenario(launch_position=Metres(5))).solve()
    impact = solution.event(EventType.GROUND_IMPACT)
    assert impact.time.value == pytest.approx(4.2360679775)
    assert impact.position == pytest.approx(0)


def test_downward_launch_from_elevation_has_ground_impact_without_maximum() -> None:
    scenario = make_scenario(
        launch_position=Metres(20), initial_velocity=MetresPerSecond(-5),
        launch_direction=LaunchDirection.DOWNWARD, scenario_type=ScenarioType.PROJECTED_DOWNWARD,
    )
    solution = VerticalProjectileSolver(scenario).solve()
    assert solution.event(EventType.MAXIMUM_HEIGHT) is None
    assert solution.event(EventType.GROUND_IMPACT).time.value == pytest.approx(1.5615528128)


def test_drop_from_rest_uses_same_equation() -> None:
    scenario = make_scenario(
        launch_position=Metres(20), initial_velocity=MetresPerSecond(0),
        launch_direction=LaunchDirection.REST, scenario_type=ScenarioType.DROPPED_FROM_REST,
    )
    solution = VerticalProjectileSolver(scenario).solve()
    assert solution.event(EventType.GROUND_IMPACT).time.value == pytest.approx(2)


def test_downward_positive_coordinates_have_consistent_signs() -> None:
    scenario = make_scenario(
        launch_position=Metres(0), initial_velocity=MetresPerSecond(-20),
        gravitational_acceleration=MetresPerSecondSquared(10),
        positive_direction=PositiveDirection.DOWN,
        launch_direction=LaunchDirection.UPWARD, scenario_type=ScenarioType.PROJECTED_UPWARD,
    )
    solver = VerticalProjectileSolver(scenario)
    assert solver.position_at(Seconds(1)) == pytest.approx(-15)
    assert solver.velocity_at(Seconds(1)) == pytest.approx(-10)


def test_solution_validation_checks_events_against_scenario() -> None:
    solver = VerticalProjectileSolver(make_scenario())
    solution = solver.solve()
    assert solver.validate(solution).valid
    event = solution.event(EventType.MAXIMUM_HEIGHT)
    invalid = type(solution)(solution.scenario_identifier, (type(event)(
        event.event_type, event.time, event.position + 1, event.velocity),))
    result = solver.validate(invalid)
    assert not result.valid
    assert "position" in result.errors[0]


def test_repeated_solving_is_deterministic() -> None:
    solver = VerticalProjectileSolver(make_scenario())
    assert solver.solve() == solver.solve()


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
def test_time_rejects_invalid_values(value: float) -> None:
    with pytest.raises(ValueError):
        Seconds(value)
