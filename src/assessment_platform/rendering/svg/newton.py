"""Deterministic, learner-safe SVG diagrams for the authored Newton domain.

This module is deliberately a presentation boundary.  It maps authored
directions to screen directions and lays out technical primitives; it does
not derive any physical quantity or ask the Newton solver for one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from html import escape
from math import cos, radians, sin

from assessment_platform.domains.physical_sciences.mechanics.newtons_laws import (
    BodyReference,
    CartesianCoordinates,
    CartesianDirection,
    Force,
    ForceKind,
    ForceVector,
    NewtonScenario,
    SurfaceCoordinates,
    SurfaceDirection,
    UnknownValue,
)
from assessment_platform.rendering.svg.projectile import SvgDocument


class NewtonDiagramKind(StrEnum):
    """Technical views supported by the renderer."""

    FORCE_DIAGRAM = "force-diagram"
    FREE_BODY_DIAGRAM = "free-body-diagram"


@dataclass(frozen=True, slots=True)
class NewtonVisibilityOptions:
    """An allowlist of information that may be visible in a learner diagram."""

    show_body_labels: bool = True
    show_force_labels: bool = True
    show_numeric_values: bool = False
    show_coordinate_axes: bool = False
    show_surface_inclination: bool = False
    show_system_boundary: bool = False
    show_string: bool = True
    show_known_givens: bool = False
    show_derived_values: bool = False


@dataclass(frozen=True, slots=True)
class NewtonRenderOptions:
    """Immutable layout and visibility settings for a Newton SVG."""

    width: int = 760
    height: int = 480
    diagram_kind: NewtonDiagramKind = NewtonDiagramKind.FREE_BODY_DIAGRAM
    body_id: str | None = None
    visibility: NewtonVisibilityOptions = NewtonVisibilityOptions()

    def __post_init__(self) -> None:
        if self.width < 420 or self.height < 280:
            raise ValueError("diagram dimensions are too small")
        if not isinstance(self.diagram_kind, NewtonDiagramKind):
            raise ValueError("diagram_kind must be a NewtonDiagramKind")
        if not isinstance(self.visibility, NewtonVisibilityOptions):
            raise ValueError("visibility must be NewtonVisibilityOptions")
        if self.body_id is not None and (
            not isinstance(self.body_id, str) or not self.body_id.strip()
        ):
            raise ValueError("body_id must be a non-empty string when supplied")


_ARROW_LENGTH = 72.0
_BODY_WIDTH = 72.0
_BODY_HEIGHT = 42.0
_IDENTIFIER_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")


class NewtonSvgRenderer:
    """Render authored Newton facts without performing Newton calculations."""

    VERSION = "1"

    def render(
        self,
        scenario: NewtonScenario,
        options: NewtonRenderOptions | None = None,
        validated_result: object | None = None,
    ) -> SvgDocument:
        if not isinstance(scenario, NewtonScenario):
            raise ValueError("scenario must be a NewtonScenario")
        opts = options or NewtonRenderOptions()
        if validated_result is not None:
            result_scenario = getattr(validated_result, "scenario_identifier", None)
            if result_scenario != scenario.identifier:
                raise ValueError("validated result scenario identifier does not match scenario")

        selected_body = self._selected_body(scenario, opts)
        positions = self._body_positions(scenario, opts)
        title_id = self._id(scenario.identifier, "title")
        desc_id = self._id(scenario.identifier, "desc")
        title = self._title(scenario, opts, selected_body)
        description = self._description(scenario, opts, selected_body)
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{opts.width}" '
            f'height="{opts.height}" viewBox="0 0 {opts.width} {opts.height}" '
            f'role="img" aria-labelledby="{title_id} {desc_id}">',
            f'<title id="{title_id}">{escape(title)}</title>',
            f'<desc id="{desc_id}">{escape(description)}</desc>',
            '<defs><marker id="newton-arrow" markerWidth="8" markerHeight="8" '
            'refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" '
            'fill="#174a7e"/></marker></defs>',
            f'<g id="{self._id(scenario.identifier, "diagram")}" '
            'font-family="sans-serif" font-size="14">',
        ]

        if opts.visibility.show_coordinate_axes:
            parts.extend(self._coordinate_axes(scenario, opts))
        parts.extend(self._surface_parts(scenario, opts))
        parts.extend(self._body_parts(scenario, opts, positions, selected_body))
        if opts.diagram_kind is NewtonDiagramKind.FORCE_DIAGRAM:
            parts.extend(self._force_diagram_parts(scenario, opts, positions))
        else:
            parts.extend(self._free_body_parts(scenario, opts, positions, selected_body))
        if opts.visibility.show_string:
            parts.extend(self._string_parts(scenario, opts, positions))
        if opts.visibility.show_system_boundary:
            parts.extend(self._system_boundary_parts(scenario, opts, positions))
        parts.append("</g></svg>")
        return SvgDocument("".join(parts), opts.width, opts.height)

    @staticmethod
    def _selected_body(scenario: NewtonScenario, opts: NewtonRenderOptions) -> str | None:
        if opts.body_id is not None and opts.body_id not in {
            body.identifier for body in scenario.bodies
        }:
            raise ValueError("body_id does not identify a body in the scenario")
        if opts.diagram_kind is not NewtonDiagramKind.FREE_BODY_DIAGRAM:
            return opts.body_id
        if opts.body_id is not None:
            return opts.body_id
        if len(scenario.bodies) != 1:
            raise ValueError("a two-body free-body diagram requires body_id")
        return scenario.bodies[0].identifier

    @staticmethod
    def _body_positions(
        scenario: NewtonScenario, opts: NewtonRenderOptions
    ) -> dict[str, tuple[float, float]]:
        if len(scenario.bodies) == 1:
            return {scenario.bodies[0].identifier: (opts.width / 2, opts.height * 0.56)}
        return {
            scenario.bodies[0].identifier: (opts.width * 0.33, opts.height * 0.56),
            scenario.bodies[1].identifier: (opts.width * 0.67, opts.height * 0.56),
        }

    def _body_parts(
        self,
        scenario: NewtonScenario,
        opts: NewtonRenderOptions,
        positions: dict[str, tuple[float, float]],
        selected_body: str | None,
    ) -> list[str]:
        parts: list[str] = []
        for body in scenario.bodies:
            x, y = positions[body.identifier]
            selected = selected_body == body.identifier
            stroke = (
                "#174a7e"
                if selected or opts.diagram_kind is NewtonDiagramKind.FORCE_DIAGRAM
                else "#777"
            )
            parts.append(
                f'<rect id="{self._id("body", body.identifier)}" x="{x - _BODY_WIDTH / 2:.3f}" '
                f'y="{y - _BODY_HEIGHT / 2:.3f}" width="{_BODY_WIDTH:.3f}" '
                f'height="{_BODY_HEIGHT:.3f}" rx="4" fill="#e7f0f8" stroke="{stroke}"/>'
            )
            if opts.visibility.show_body_labels:
                parts.append(
                    self._text(
                        self._id("body-label", body.identifier), x - 20, y + 5, body.identifier
                    )
                )
        return parts

    def _free_body_parts(
        self,
        scenario: NewtonScenario,
        opts: NewtonRenderOptions,
        positions: dict[str, tuple[float, float]],
        selected_body: str | None,
    ) -> list[str]:
        if selected_body is None:
            return []
        return self._force_parts(
            scenario, opts, positions, scenario.forces_on(selected_body), selected_body
        )

    def _force_diagram_parts(
        self,
        scenario: NewtonScenario,
        opts: NewtonRenderOptions,
        positions: dict[str, tuple[float, float]],
    ) -> list[str]:
        return self._force_parts(scenario, opts, positions, scenario.forces, None)

    def _force_parts(
        self,
        scenario: NewtonScenario,
        opts: NewtonRenderOptions,
        positions: dict[str, tuple[float, float]],
        forces: tuple[Force, ...],
        selected_body: str | None,
    ) -> list[str]:
        parts: list[str] = []
        for force in forces:
            if selected_body is not None and force.target_body_id != selected_body:
                continue
            x, y = positions[force.target_body_id]
            direction = self._force_direction(scenario, force)
            if direction is not None:
                dx, dy = direction
                # Fixed arrow lengths prevent unauthored magnitudes leaking through geometry.
                end_x = x + dx * _ARROW_LENGTH
                end_y = y + dy * _ARROW_LENGTH
                parts.append(
                    f'<line id="{self._id("force", force.identifier)}" x1="{x:.3f}" y1="{y:.3f}" '
                    f'x2="{end_x:.3f}" y2="{end_y:.3f}" stroke="#174a7e" stroke-width="2" '
                    'marker-end="url(#newton-arrow)"/>'
                )
            elif self._has_unknown_component(force.vector):
                parts.append(
                    self._text(self._id("unknown-force", force.identifier), x + 12, y - 30, "?")
                )
            if opts.visibility.show_force_labels:
                label = self._force_label(scenario, force, opts.visibility)
                offset_x, offset_y = self._label_offset(direction)
                parts.append(
                    self._text(
                        self._id("force-label", force.identifier), x + offset_x, y + offset_y, label
                    )
                )
        return parts

    @staticmethod
    def _has_unknown_component(vector: ForceVector) -> bool:
        return any(component is UnknownValue.UNKNOWN for component in vector.components)

    def _force_direction(
        self, scenario: NewtonScenario, force: Force
    ) -> tuple[float, float] | None:
        components = force.vector.components
        if any(component is UnknownValue.UNKNOWN for component in components):
            if force.kind is not ForceKind.NORMAL:
                return None
            return self._normal_direction(scenario, force)
        values: list[float] = []
        for component in components:
            if isinstance(component, UnknownValue):
                return None
            values.append(component.value)
        if not any(value != 0 for value in values):
            return None
        directions = self._basis_directions(scenario, force.vector.coordinates)
        dx = sum(value * direction[0] for value, direction in zip(values, directions, strict=True))
        dy = sum(value * direction[1] for value, direction in zip(values, directions, strict=True))
        magnitude = (dx * dx + dy * dy) ** 0.5
        if magnitude == 0:
            return None
        return (dx / magnitude, dy / magnitude)

    def _normal_direction(
        self, scenario: NewtonScenario, force: Force
    ) -> tuple[float, float] | None:
        if force.relationship_id is None:
            return None
        contact = next(
            (item for item in scenario.contacts if item.identifier == force.relationship_id), None
        )
        if contact is None:
            return None
        surface = next(
            (item for item in scenario.surfaces if item.identifier == contact.surface_id), None
        )
        if surface is None:
            return None
        angle = radians(surface.inclination_degrees)
        out = (-sin(angle), -cos(angle))
        if force.target_body_id != contact.body_id or force.source == BodyReference(
            contact.body_id
        ):
            out = (-out[0], -out[1])
        return out

    @staticmethod
    def _basis_directions(
        scenario: NewtonScenario, coordinates: object
    ) -> tuple[tuple[float, float], ...]:
        if isinstance(coordinates, CartesianCoordinates):
            result: list[tuple[float, float]] = []
            for cart_axis in coordinates.axes:
                result.append(
                    {
                        CartesianDirection.RIGHT: (1.0, 0.0),
                        CartesianDirection.LEFT: (-1.0, 0.0),
                        CartesianDirection.UP: (0.0, -1.0),
                        CartesianDirection.DOWN: (0.0, 1.0),
                    }[cart_axis]
                )
            return tuple(result)
        if isinstance(coordinates, SurfaceCoordinates):
            surface = next(
                (item for item in scenario.surfaces if item.identifier == coordinates.surface_id),
                None,
            )
            if surface is None:
                return ()
            angle = radians(surface.inclination_degrees)
            tangent = (cos(angle), -sin(angle))
            normal = (-sin(angle), -cos(angle))
            surface_result: list[tuple[float, float]] = []
            for surface_axis in coordinates.axes:
                surface_result.append(
                    {
                        SurfaceDirection.ALONG_RIGHT: tangent,
                        SurfaceDirection.ALONG_LEFT: (-tangent[0], -tangent[1]),
                        SurfaceDirection.NORMAL_OUT: normal,
                        SurfaceDirection.NORMAL_IN: (-normal[0], -normal[1]),
                    }[surface_axis]
                )
            return tuple(surface_result)
        return ()

    @staticmethod
    def _label_offset(direction: tuple[float, float] | None) -> tuple[float, float]:
        if direction is None:
            return (12.0, -30.0)
        return (direction[0] * 82.0, direction[1] * 82.0)

    def _force_label(
        self, scenario: NewtonScenario, force: Force, visibility: NewtonVisibilityOptions
    ) -> str:
        names = {
            ForceKind.APPLIED: "F",
            ForceKind.NORMAL: "N",
            ForceKind.FRICTION: "f",
            ForceKind.TENSION: "T",
            ForceKind.WEIGHT: "W",
            ForceKind.GRAVITATIONAL: "F_g",
        }
        label = names[force.kind]
        if visibility.show_numeric_values:
            values = [
                f"{component.value:g} N" if component is not UnknownValue.UNKNOWN else "?"
                for component in force.vector.components
            ]
            label = f"{label} ({', '.join(values)})"
        if visibility.show_force_labels and isinstance(force.source, BodyReference):
            label = f"{label} {force.source.identifier}->{force.target_body_id}"
        return label

    def _surface_parts(self, scenario: NewtonScenario, opts: NewtonRenderOptions) -> list[str]:
        if not scenario.surfaces:
            return []
        surface = scenario.surfaces[0]
        centre_x, centre_y = opts.width / 2, opts.height * 0.72
        length = opts.width * 0.66
        angle = radians(surface.inclination_degrees)
        x1, y1 = centre_x - length / 2, centre_y + sin(angle) * length / 2
        x2, y2 = centre_x + length / 2, centre_y - sin(angle) * length / 2
        parts = [
            f'<line id="{self._id("surface", surface.identifier)}" x1="{x1:.3f}" y1="{y1:.3f}" '
            f'x2="{x2:.3f}" y2="{y2:.3f}" stroke="#555" stroke-width="3"/>'
        ]
        if opts.visibility.show_surface_inclination:
            parts.append(
                self._text(
                    self._id("surface-label", surface.identifier),
                    x1 + 8,
                    y1 + 22,
                    f"surface {surface.identifier}",
                )
            )
            parts.append(
                self._text(
                    self._id("inclination-label", surface.identifier),
                    x2 - 55,
                    y2 - 10,
                    f"{surface.inclination_degrees:g} deg",
                )
            )
        return parts

    def _string_parts(
        self,
        scenario: NewtonScenario,
        opts: NewtonRenderOptions,
        positions: dict[str, tuple[float, float]],
    ) -> list[str]:
        if not scenario.strings:
            return []
        string = scenario.strings[0]
        first, second = (positions[body_id] for body_id in string.body_ids)
        return [
            f'<line id="{self._id("string", string.identifier)}" '
            f'x1="{first[0]:.3f}" y1="{first[1]:.3f}" '
            f'x2="{second[0]:.3f}" y2="{second[1]:.3f}" stroke="#555" stroke-width="2"/>'
        ]

    def _system_boundary_parts(
        self,
        scenario: NewtonScenario,
        opts: NewtonRenderOptions,
        positions: dict[str, tuple[float, float]],
    ) -> list[str]:
        selected = [positions[body_id] for body_id in scenario.system.body_ids]
        if not selected:
            return []
        min_x = min(item[0] for item in selected) - 65
        max_x = max(item[0] for item in selected) + 65
        min_y = min(item[1] for item in selected) - 55
        max_y = max(item[1] for item in selected) + 55
        return [
            f'<rect id="{self._id(scenario.identifier, "system-boundary")}" '
            f'x="{min_x:.3f}" y="{min_y:.3f}" '
            f'width="{max_x - min_x:.3f}" height="{max_y - min_y:.3f}" fill="none" '
            'stroke="#777" stroke-width="2" stroke-dasharray="6 4"/>',
            self._text(
                self._id(scenario.identifier, "system-label"),
                min_x + 8,
                min_y + 18,
                "system boundary",
            ),
        ]

    @staticmethod
    def _coordinate_axes(scenario: NewtonScenario, opts: NewtonRenderOptions) -> list[str]:
        labels = ", ".join(axis.value for axis in scenario.coordinates.axes)
        return [
            f'<text id="{NewtonSvgRenderer._id(scenario.identifier, "axes-label")}" x="24" y="28">'
            f"{escape('positive: ' + labels)}</text>"
        ]

    def _title(
        self, scenario: NewtonScenario, opts: NewtonRenderOptions, body_id: str | None
    ) -> str:
        kind = (
            "free-body"
            if opts.diagram_kind is NewtonDiagramKind.FREE_BODY_DIAGRAM
            else "force/system"
        )
        suffix = f" for {body_id}" if body_id is not None else ""
        return f"Newton {kind} diagram{suffix}: {scenario.identifier}"

    def _description(
        self, scenario: NewtonScenario, opts: NewtonRenderOptions, body_id: str | None
    ) -> str:
        if body_id is not None:
            return (
                f"Free-body diagram for {body_id}; arrows show authored forces acting on that body."
            )
        return f"Technical Newton force diagram for {len(scenario.bodies)} authored bodies."

    @staticmethod
    def _text(identifier: str, x: float, y: float, value: str) -> str:
        return f'<text id="{identifier}" x="{x:.3f}" y="{y:.3f}">{escape(value)}</text>'

    @staticmethod
    def _id(*parts: str) -> str:
        value = "-".join(parts)
        safe = _IDENTIFIER_PATTERN.sub("_", value)
        if not safe or safe[0].isdigit():
            safe = f"n-{safe}"
        return safe


__all__ = [
    "NewtonDiagramKind",
    "NewtonDiagramOptions",
    "NewtonRenderOptions",
    "NewtonSvgRenderer",
    "NewtonVisibilityOptions",
]


# Name retained alongside the generic render-options spelling used by older
# technical renderers.
NewtonDiagramOptions = NewtonRenderOptions
