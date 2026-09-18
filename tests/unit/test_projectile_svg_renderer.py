from xml.etree import ElementTree

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
    VerticalProjectileSolver,
)
from assessment_platform.rendering.svg.projectile import (
    ProjectileDiagramOptions,
    ProjectileSvgRenderer,
)


def make_diagram_scenario(**overrides: object) -> VerticalProjectileScenario:
    values: dict[str, object] = {
        "identifier": "diagram-case",
        "launch_position": Metres(0),
        "initial_velocity": MetresPerSecond(20),
        "gravitational_acceleration": MetresPerSecondSquared(-10),
        "positive_direction": PositiveDirection.UP,
        "launch_direction": LaunchDirection.UPWARD,
        "scenario_type": ScenarioType.PROJECTED_UPWARD,
    }
    values.update(overrides)
    return VerticalProjectileScenario(**values)  # type: ignore[arg-type]


def render(scenario: VerticalProjectileScenario) -> str:
    solution = VerticalProjectileSolver(scenario).solve()
    return ProjectileSvgRenderer().render(scenario, solution).markup


def test_upward_ground_diagram_is_valid_svg_and_deterministic() -> None:
    scenario = make_diagram_scenario()
    first = render(scenario)
    second = render(scenario)
    root = ElementTree.fromstring(first)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert first == second
    assert 'id="event-maximum-height"' in first
    assert 'id="event-ground-impact"' in first


def test_elevated_upward_launch_keeps_ground_below_launch_in_screen_space() -> None:
    svg = render(make_diagram_scenario(launch_position=Metres(5)))
    root = ElementTree.fromstring(svg)
    launch_y = float(root.find(".//*[@id='launch-point']").attrib["cy"])
    ground_y = float(root.find(".//*[@id='ground']").attrib["y1"])
    assert ground_y > launch_y


def test_downward_launch_and_drop_have_no_maximum_height_or_initial_velocity_arrow() -> None:
    downward = make_diagram_scenario(
        identifier="downward",
        launch_position=Metres(20),
        initial_velocity=MetresPerSecond(-5),
        launch_direction=LaunchDirection.DOWNWARD,
        scenario_type=ScenarioType.PROJECTED_DOWNWARD,
    )
    downward_svg = render(downward)
    assert "event-maximum-height" not in downward_svg
    assert "velocity-launch" in downward_svg

    dropped = make_diagram_scenario(
        identifier="dropped",
        launch_position=Metres(20),
        initial_velocity=MetresPerSecond(0),
        launch_direction=LaunchDirection.REST,
        scenario_type=ScenarioType.DROPPED_FROM_REST,
    )
    dropped_svg = render(dropped)
    assert "release (from rest)" in dropped_svg
    assert "velocity-launch" not in dropped_svg


def test_downward_positive_coordinates_still_draw_downward_gravity() -> None:
    scenario = make_diagram_scenario(
        identifier="down-positive",
        initial_velocity=MetresPerSecond(-20),
        gravitational_acceleration=MetresPerSecondSquared(10),
        positive_direction=PositiveDirection.DOWN,
        launch_direction=LaunchDirection.UPWARD,
        scenario_type=ScenarioType.PROJECTED_UPWARD,
    )
    svg = render(scenario)
    root = ElementTree.fromstring(svg)
    gravity = root.find(".//*[@id='gravity-arrow']")
    assert float(gravity.attrib["y2"]) > float(gravity.attrib["y1"])
    assert "positive direction: down" in svg
    assert "g = 10 m/s² (downward)" in svg


def test_maximum_height_omits_nonzero_velocity_arrow_and_shows_zero_event() -> None:
    svg = render(make_diagram_scenario())
    assert 'id="velocity-maximum-height"' not in svg
    assert "maximum height (t = 2 s)" in svg


def test_same_position_launch_and_return_are_not_separated_spatially() -> None:
    root = ElementTree.fromstring(render(make_diagram_scenario()))
    launch_y = root.find(".//*[@id='launch-point']").attrib["cy"]
    return_y = root.find(".//*[@id='event-return-to-launch-position']").attrib["cy"]
    assert return_y == launch_y


def test_renderer_rejects_solution_for_another_scenario() -> None:
    scenario = make_diagram_scenario()
    other = make_diagram_scenario(identifier="other")
    solution = VerticalProjectileSolver(other).solve()
    with pytest.raises(ValueError, match="identifier"):
        ProjectileSvgRenderer().render(scenario, solution)


def test_special_characters_are_escaped_and_svg_has_no_executable_content() -> None:
    svg = render(make_diagram_scenario(identifier='a<unsafe>&"'))
    ElementTree.fromstring(svg)
    assert "&lt;unsafe&gt;&amp;&quot;" in svg
    assert "<script" not in svg
    assert "onload=" not in svg
    assert "http://" not in svg.replace("http://www.w3.org/2000/svg", "")


def test_renderer_options_are_semantic_and_dimensions_are_deterministic() -> None:
    scenario = make_diagram_scenario()
    document = ProjectileSvgRenderer().render(
        scenario, VerticalProjectileSolver(scenario).solve(),
        ProjectileDiagramOptions(width=800, height=500, show_labels=False, show_velocities=False),
    )
    assert document.width == 800
    assert document.height == 500
    assert 'width="800"' in document.markup
    assert 'id="velocity-' not in document.markup
    with pytest.raises(ValueError):
        ProjectileDiagramOptions(width=100, height=100)
