"""Safe deterministic SVG renderer for one-dimensional projectiles."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from html import escape

from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    PositiveDirection,
    VerticalProjectileScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    EventType,
    TrajectoryEvent,
    VerticalProjectileSolution,
)
from assessment_platform.rendering.svg.document import SvgDocument


@dataclass(frozen=True, slots=True)
class ProjectileDiagramOptions:
    width: int = 640
    height: int = 480
    show_labels: bool = True
    show_velocities: bool = True
    show_acceleration: bool = True
    show_sign_convention: bool = True
    show_numeric_values: bool = True

    def __post_init__(self) -> None:
        if self.width < 320 or self.height < 240:
            raise ValueError("diagram dimensions are too small")


class ProjectileSvgRenderer:
    """Render validated values; never derive physical events or quantities."""

    def render(
        self,
        scenario: VerticalProjectileScenario,
        solution: VerticalProjectileSolution,
        options: ProjectileDiagramOptions | None = None,
    ) -> SvgDocument:
        options = options or ProjectileDiagramOptions()
        if solution.scenario_identifier != scenario.identifier:
            raise ValueError("solution scenario identifier does not match scenario")
        events = solution.events
        heights = [0.0, self._physical_height(scenario, scenario.launch_position.value)]
        heights.extend(self._physical_height(scenario, event.position) for event in events)
        top = max(heights)
        bottom = min(heights)
        if top - bottom < 1e-9:
            top += 0.5
            bottom -= 0.5
        y_for_height = self._coordinate_mapper(top, bottom, options)
        axis_x = 150.0
        ground_y = y_for_height(0.0)
        launch = next(event for event in events if event.event_type is EventType.LAUNCH)
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{options.width}" '
            f'height="{options.height}" viewBox="0 0 {options.width} {options.height}">',
            f"<title>Vertical projectile motion diagram: {escape(scenario.identifier)}</title>",
            "<desc>Deterministic one-dimensional vertical motion schematic</desc>",
            '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
            'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#174a7e"/></marker></defs>',
            '<g id="diagram" font-family="sans-serif" font-size="14">',
            f'<line id="ground" x1="60" y1="{ground_y:.3f}" x2="570" y2="{ground_y:.3f}" '
            'stroke="#333" stroke-width="2"/>',
            f'<text id="ground-label" x="580" y="{ground_y + 5:.3f}">ground / reference</text>',
            f'<line id="axis" x1="{axis_x:.3f}" y1="50" x2="{axis_x:.3f}" '
            f'y2="{options.height - 45}" stroke="#777" stroke-width="2"/>',
            f'<line id="motion-line" x1="{axis_x:.3f}" y1="{y_for_height(top):.3f}" '
            f'x2="{axis_x:.3f}" y2="{y_for_height(bottom):.3f}" '
            'stroke="#8aa" stroke-dasharray="4 4"/>',
        ]
        launch_y = y_for_height(self._physical_height(scenario, launch.position))
        parts.append(
            f'<circle id="launch-point" cx="{axis_x:.3f}" cy="{launch_y:.3f}" '
            'r="7" fill="#174a7e"/>'
        )
        if options.show_labels:
            parts.append(
                self._text("launch-label", axis_x + 18, launch_y - 10, self._launch_label(scenario))
            )

        event_y_counts: dict[float, int] = {}
        for event in events:
            event_y = y_for_height(self._physical_height(scenario, event.position))
            event_y_counts[event_y] = event_y_counts.get(event_y, 0) + 1
            parts.append(self._event_marker(event, axis_x, event_y))
            if options.show_labels and event.event_type is not EventType.LAUNCH:
                offset = (event_y_counts[event_y] - 1) * 18
                label = self._event_label(event, options.show_numeric_values)
                parts.append(
                    self._text(f"{event.event_type}-label", axis_x + 18, event_y + offset, label)
                )

        if options.show_velocities:
            for event in events:
                if abs(event.velocity) < 1e-9:
                    continue
                event_y = y_for_height(self._physical_height(scenario, event.position))
                direction = self._visual_direction(scenario, event.velocity)
                delta = -32 if direction == "up" else 32
                parts.append(
                    f'<line id="velocity-{event.event_type}" x1="{axis_x + 45:.3f}" '
                    f'y1="{event_y:.3f}" x2="{axis_x + 45:.3f}" y2="{event_y + delta:.3f}" '
                    'stroke="#174a7e" stroke-width="2" marker-end="url(#arrow)"/>'
                )
                if options.show_labels:
                    value = (
                        f"v = {event.velocity:g} m/s"
                        if options.show_numeric_values else "velocity"
                    )
                    parts.append(
                        self._text(
                            f"velocity-{event.event_type}-label", axis_x + 58,
                            event_y + delta / 2, value,
                        )
                    )

        if options.show_acceleration:
            acceleration_y = options.height / 2
            parts.append(
                f'<line id="gravity-arrow" x1="{axis_x + 120:.3f}" y1="{acceleration_y - 28:.3f}" '
                f'x2="{axis_x + 120:.3f}" y2="{acceleration_y + 28:.3f}" stroke="#a33" '
                'stroke-width="2" marker-end="url(#arrow)"/>'
            )
            if options.show_labels:
                label = "g (downward)"
                if options.show_numeric_values:
                    label = f"g = {scenario.gravitational_acceleration.value:g} m/s² (downward)"
                parts.append(self._text("gravity-label", axis_x + 132, acceleration_y + 5, label))

        if options.show_sign_convention:
            parts.append(
                self._text("sign-convention", 60, options.height - 18,
                           f"positive direction: {scenario.positive_direction.value}")
            )
        parts.append("</g></svg>")
        return SvgDocument("".join(parts), options.width, options.height)

    @staticmethod
    def _coordinate_mapper(
        top: float, bottom: float, options: ProjectileDiagramOptions
    ) -> Callable[[float], float]:
        margin_top = 50.0
        margin_bottom = 45.0
        usable_height = options.height - margin_top - margin_bottom
        span = top - bottom

        def map_height(height: float) -> float:
            return margin_top + ((top - height) / span) * usable_height

        return map_height

    @staticmethod
    def _physical_height(scenario: VerticalProjectileScenario, coordinate: float) -> float:
        return coordinate if scenario.positive_direction is PositiveDirection.UP else -coordinate

    @staticmethod
    def _visual_direction(scenario: VerticalProjectileScenario, velocity: float) -> str:
        upward = (
            velocity > 0
            if scenario.positive_direction is PositiveDirection.UP
            else velocity < 0
        )
        return "up" if upward else "down"

    @staticmethod
    def _launch_label(scenario: VerticalProjectileScenario) -> str:
        if scenario.launch_direction is LaunchDirection.REST:
            return "release (from rest)"
        return "launch"

    @staticmethod
    def _event_label(event: TrajectoryEvent, show_value: bool) -> str:
        names = {
            EventType.MAXIMUM_HEIGHT: "maximum height",
            EventType.RETURN_TO_LAUNCH_POSITION: "return to launch position",
            EventType.GROUND_IMPACT: "ground impact",
        }
        label = names[event.event_type]
        return f"{label} (t = {event.time.value:g} s)" if show_value else label

    @staticmethod
    def _event_marker(event: TrajectoryEvent, axis_x: float, y: float) -> str:
        colour = "#174a7e" if event.event_type is EventType.MAXIMUM_HEIGHT else "#555"
        return (
            f'<circle id="event-{event.event_type}" cx="{axis_x:.3f}" cy="{y:.3f}" '
            f'r="5" fill="{colour}"/>'
        )

    @staticmethod
    def _text(identifier: str, x: float, y: float, value: str) -> str:
        return f'<text id="{identifier}" x="{x:.3f}" y="{y:.3f}">{escape(value)}</text>'
