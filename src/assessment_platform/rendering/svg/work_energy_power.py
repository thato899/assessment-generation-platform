"""Safe, deterministic SVG diagrams for authored Work, Energy & Power facts.

This module is presentation only.  It maps authored semantic values to fixed
schematic geometry and deliberately has no dependency on a solver or a
generator.  Numeric magnitudes never determine lengths, areas, or positions.
"""
# ruff: noqa: E501

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from html import escape
from math import cos, radians, sin

from assessment_platform.domains.physical_sciences.mechanics.work_energy_power import (
    AlongPlaneWorkInput,
    EnergyState,
    HeightState,
    KineticState,
    NetWorkInput,
    PumpingPowerInput,
    SurfaceContext,
    UnknownValue,
    WorkContribution,
    WorkEnergyScenario,
)
from assessment_platform.rendering.svg.document import SvgDocument


class WorkEnergyDiagramKind(StrEnum):
    """Explicit technical views; there is intentionally no automatic mode."""

    WORK_CONTRIBUTIONS = "work-contributions"
    WORK_CONTRIBUTION = "work-contributions"  # compatibility alias
    ALONG_PLANE = "along-plane"
    MOTION_STATES = "motion-states"
    MOTION_STATE = "motion-states"  # compatibility alias
    HEIGHT_STATES = "height-states"
    HEIGHT_REFERENCE = "height-states"  # compatibility alias
    HEIGHT_REFERENCE_LEVEL = "height-states"  # compatibility alias
    CONSTANT_SPEED_SURFACE = "constant-speed-surface"
    CONSTANT_SPEED = "constant-speed-surface"  # compatibility alias
    PUMPING = "pumping"
    PUMPING_POWER = "pumping"  # compatibility alias


@dataclass(frozen=True, slots=True)
class WorkEnergyVisibilityOptions:
    """Allowlist for authored labels and known numeric givens."""

    show_state_labels: bool = True
    show_force_labels: bool = True
    show_displacement_labels: bool = True
    show_angle_labels: bool = False
    show_reference_labels: bool = True
    show_surface_context: bool = True
    show_numeric_values: bool = False
    show_known_givens: bool = False

    def __post_init__(self) -> None:
        for name in (
            "show_state_labels",
            "show_force_labels",
            "show_displacement_labels",
            "show_angle_labels",
            "show_reference_labels",
            "show_surface_context",
            "show_numeric_values",
            "show_known_givens",
        ):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be a boolean")


@dataclass(frozen=True, slots=True)
class WorkEnergyRenderOptions:
    """Immutable layout, selection, and visibility settings."""

    width: int = 760
    height: int = 480
    diagram_kind: WorkEnergyDiagramKind = WorkEnergyDiagramKind.WORK_CONTRIBUTIONS
    visibility: WorkEnergyVisibilityOptions = WorkEnergyVisibilityOptions()
    contribution_id: str | None = None
    context_index: int | None = None
    state_id: str | None = None
    input_index: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.width, bool) or not isinstance(self.width, int):
            raise ValueError("width must be an integer")
        if isinstance(self.height, bool) or not isinstance(self.height, int):
            raise ValueError("height must be an integer")
        if self.width < 420 or self.height < 280:
            raise ValueError("diagram dimensions are too small")
        if not isinstance(self.diagram_kind, WorkEnergyDiagramKind):
            raise ValueError("diagram_kind must be a WorkEnergyDiagramKind")
        if not isinstance(self.visibility, WorkEnergyVisibilityOptions):
            raise ValueError("visibility must be WorkEnergyVisibilityOptions")
        for name in ("contribution_id", "state_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string when supplied")
        for name in ("context_index", "input_index"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise ValueError(f"{name} must be a non-negative integer when supplied")


_IDENTIFIER_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")
_ARROW_LENGTH = 64.0


class WorkEnergySvgRenderer:
    """Render authored M5 facts without deriving any physical quantity."""

    VERSION = "1"

    def render(
        self,
        scenario: WorkEnergyScenario,
        options: WorkEnergyRenderOptions | None = None,
    ) -> SvgDocument:
        if not isinstance(scenario, WorkEnergyScenario):
            raise ValueError("scenario must be a WorkEnergyScenario")
        opts = options or WorkEnergyRenderOptions()
        title_id = self._id("wep-title")
        desc_id = self._id("wep-desc")
        # Scenario identifiers are provenance, not visual facts; excluding them
        # keeps titles stable when an authored hidden magnitude changes.
        title = "Work, Energy and Power technical diagram"
        description = self._description(opts.diagram_kind)
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{opts.width}" '
            f'height="{opts.height}" viewBox="0 0 {opts.width} {opts.height}" role="img" '
            f'aria-labelledby="{title_id} {desc_id}">',
            f'<title id="{title_id}">{escape(title, quote=True)}</title>',
            f'<desc id="{desc_id}">{escape(description, quote=True)}</desc>',
            '<defs><marker id="wep-arrow" markerWidth="8" markerHeight="8" refX="6" '
            'refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#174a7e"/>'
            '</marker></defs>',
            f'<g id="{self._id("diagram")}" font-family="sans-serif" font-size="14">',
        ]
        if opts.diagram_kind is WorkEnergyDiagramKind.WORK_CONTRIBUTIONS:
            parts.extend(self._work_parts(scenario, opts))
        elif opts.diagram_kind is WorkEnergyDiagramKind.ALONG_PLANE:
            parts.extend(self._along_plane_parts(scenario, opts))
        elif opts.diagram_kind is WorkEnergyDiagramKind.MOTION_STATES:
            parts.extend(self._motion_parts(scenario, opts))
        elif opts.diagram_kind is WorkEnergyDiagramKind.HEIGHT_STATES:
            parts.extend(self._height_parts(scenario, opts))
        elif opts.diagram_kind is WorkEnergyDiagramKind.CONSTANT_SPEED_SURFACE:
            parts.extend(self._constant_speed_parts(scenario, opts))
        elif opts.diagram_kind is WorkEnergyDiagramKind.PUMPING:
            parts.extend(self._pumping_parts(scenario, opts))
        else:  # pragma: no cover - enum validation makes this unreachable
            raise ValueError("unsupported diagram kind")
        parts.append("</g></svg>")
        return SvgDocument("".join(parts), opts.width, opts.height)

    @staticmethod
    def _description(kind: WorkEnergyDiagramKind) -> str:
        return {
            WorkEnergyDiagramKind.WORK_CONTRIBUTIONS: "Authored force and displacement contribution schematic.",
            WorkEnergyDiagramKind.ALONG_PLANE: "Authored signed resultant force and displacement along a plane.",
            WorkEnergyDiagramKind.MOTION_STATES: "Authored initial and final motion states; speed geometry is schematic.",
            WorkEnergyDiagramKind.HEIGHT_STATES: "Authored height states relative to a reference level.",
            WorkEnergyDiagramKind.CONSTANT_SPEED_SURFACE: "Authored constant-speed surface and force direction.",
            WorkEnergyDiagramKind.PUMPING: "Authored pumping and vertical lift schematic.",
        }[kind]

    @staticmethod
    def _id(*parts: object) -> str:
        text = "-".join(str(part) for part in parts)
        safe = _IDENTIFIER_PATTERN.sub("-", text).strip("-") or "item"
        if safe[0].isdigit():
            safe = f"item-{safe}"
        return f"wep-{safe}"

    @staticmethod
    def _text(identifier: str, x: float, y: float, value: str) -> str:
        return f'<text id="{WorkEnergySvgRenderer._id(identifier)}" x="{x:.3f}" y="{y:.3f}">{escape(value, quote=True)}</text>'

    @staticmethod
    def _arrow(identifier: str, x1: float, y1: float, x2: float, y2: float, label: str = "") -> str:
        aria = f' aria-label="{escape(label, quote=True)}"' if label else ""
        return (
            f'<line id="{WorkEnergySvgRenderer._id(identifier)}" x1="{x1:.3f}" y1="{y1:.3f}" '
            f'x2="{x2:.3f}" y2="{y2:.3f}" stroke="#174a7e" stroke-width="2" '
            f'marker-end="url(#wep-arrow)"{aria}/>'
        )

    @staticmethod
    def _numbers(opts: WorkEnergyRenderOptions) -> bool:
        # show_numeric_values is the explicit opt-in; show_known_givens remains
        # available for callers that want to document that policy decision.
        return opts.visibility.show_numeric_values

    def _work_parts(self, scenario: WorkEnergyScenario, opts: WorkEnergyRenderOptions) -> list[str]:
        inputs: tuple[NetWorkInput, ...] = tuple(
            item for item in scenario.work_inputs if isinstance(item, NetWorkInput)
        )
        if not inputs:
            raise ValueError("WORK_CONTRIBUTIONS requires an authored NetWorkInput")
        selected: tuple[NetWorkInput, ...]
        if opts.input_index is not None:
            if opts.input_index >= len(inputs):
                raise ValueError("input_index does not identify a NetWorkInput")
            selected = (inputs[opts.input_index],)
        else:
            selected = inputs
        contributions = tuple(c for item in selected for c in item.contributions)
        if opts.contribution_id is not None:
            contributions = tuple(c for c in contributions if c.identifier == opts.contribution_id)
            if not contributions:
                raise ValueError("contribution_id does not identify an authored contribution")
        parts: list[str] = [self._text("work-heading", 36, 34, "FORCE / DISPLACEMENT CONTRIBUTIONS")]
        for index, contribution in enumerate(contributions):
            y = 105.0 + index * 125.0
            parts.extend(self._contribution_parts(contribution, opts, y, index))
        return parts

    def _contribution_parts(
        self, contribution: WorkContribution, opts: WorkEnergyRenderOptions, y: float, index: int
    ) -> list[str]:
        v = opts.visibility
        parts = [
            self._text(
                f"contribution-{index}-{contribution.identifier}",
                36,
                y - 28,
                contribution.identifier,
            )
        ]
        parts.append(self._arrow(f"displacement-{index}", 130, y, 230, y, "displacement"))
        if v.show_displacement_labels:
            label = "displacement"
            if self._numbers(opts) and contribution.displacement is not UnknownValue.UNKNOWN:
                label = f"d = {contribution.displacement.value:g} m"
            parts.append(self._text(f"displacement-label-{index}", 135, y + 22, label))
        if contribution.angle is UnknownValue.UNKNOWN:
            parts.append(self._text(f"force-unknown-{index}", 276, y - 16, "force direction ?"))
        else:
            angle = contribution.angle.value
            dx = cos(radians(angle)) * _ARROW_LENGTH
            dy = -sin(radians(angle)) * _ARROW_LENGTH
            parts.append(self._arrow(f"force-{index}", 275, y, 275 + dx, y + dy, "force"))
            if v.show_angle_labels:
                label = f"angle = {angle:g}°" if self._numbers(opts) else "force direction"
                parts.append(self._text(f"angle-label-{index}", 350, y - 22, label))
        if v.show_force_labels:
            label = "force"
            if self._numbers(opts) and contribution.force_magnitude is not UnknownValue.UNKNOWN:
                label = f"F = {contribution.force_magnitude.value:g} N"
            parts.append(self._text(f"force-label-{index}", 265, y + 84, label))
        return parts

    def _along_plane_parts(self, scenario: WorkEnergyScenario, opts: WorkEnergyRenderOptions) -> list[str]:
        inputs = tuple(item for item in scenario.work_inputs if isinstance(item, AlongPlaneWorkInput))
        if not inputs:
            raise ValueError("ALONG_PLANE requires an authored AlongPlaneWorkInput")
        if opts.input_index is not None:
            if opts.input_index >= len(inputs):
                raise ValueError("input_index does not identify an AlongPlaneWorkInput")
            authored = inputs[opts.input_index]
        elif len(inputs) == 1:
            authored = inputs[0]
        else:
            raise ValueError("multiple AlongPlaneWorkInput values require input_index")
        parts = [self._text("along-plane-heading", 36, 34, "ALONG-PLANE WORK")]
        parts.append('<path id="wep-plane" d="M100 245 L650 245" fill="none" stroke="#555" stroke-width="3"/>')
        parts.append(self._arrow("displacement", 190, 210, 290, 210, "displacement"))
        if opts.visibility.show_displacement_labels:
            label = "displacement"
            if self._numbers(opts) and authored.displacement is not UnknownValue.UNKNOWN:
                label = f"d = {authored.displacement.value:g} m"
            parts.append(self._text("displacement-label", 195, 195, label))
        force = authored.resultant_force
        if force is UnknownValue.UNKNOWN:
            parts.append(self._text("resultant-unknown", 430, 205, "resultant force ?"))
        elif force.value > 0:
            parts.append(self._arrow("resultant-force", 430, 245, 494, 245, "resultant force"))
        elif force.value < 0:
            parts.append(self._arrow("resultant-force", 494, 245, 430, 245, "resultant force"))
        else:
            parts.append(self._text("resultant-zero", 445, 238, "resultant force = 0"))
        if opts.visibility.show_force_labels:
            label = "signed resultant force"
            if self._numbers(opts) and force is not UnknownValue.UNKNOWN:
                label = f"Fᵣ = {force.value:g} N"
            parts.append(self._text("resultant-label", 390, 285, label))
        return parts

    def _motion_parts(self, scenario: WorkEnergyScenario, opts: WorkEnergyRenderOptions) -> list[str]:
        initial: KineticState
        final: KineticState | None
        contexts = scenario.work_energy_contexts
        if contexts:
            if opts.context_index is not None:
                if opts.context_index >= len(contexts):
                    raise ValueError("context_index does not identify a work-energy context")
                context = contexts[opts.context_index]
            elif len(contexts) == 1:
                context = contexts[0]
            else:
                raise ValueError("multiple work-energy contexts require context_index")
            initial, final = context.initial_state, context.final_state
        else:
            states = scenario.kinetic_states
            if opts.state_id is not None:
                states = tuple(state for state in states if state.identifier == opts.state_id)
                if not states:
                    raise ValueError("state_id does not identify an authored kinetic state")
            if len(states) > 2:
                raise ValueError("ambiguous kinetic state selection")
            if not states:
                raise ValueError("MOTION_STATES requires authored kinetic states")
            initial = next((s for s in states if s.state is EnergyState.INITIAL), states[0])
            final = next((s for s in states if s.state is EnergyState.FINAL), None)
        parts = [self._text("motion-heading", 36, 34, "MOTION STATES")]
        parts.extend(self._motion_state_parts(initial, 185, 220, opts, "initial"))
        if final is not None:
            parts.append(self._arrow("transition", 280, 220, 470, 220, "transition"))
            parts.extend(self._motion_state_parts(final, 565, 220, opts, "final"))
        return parts

    def _motion_state_parts(
        self, state: KineticState, x: float, y: float, opts: WorkEnergyRenderOptions, label: str
    ) -> list[str]:
        v = opts.visibility
        parts = [f'<rect id="{self._id("state", state.identifier)}" x="{x - 42:.3f}" y="{y - 25:.3f}" width="84" height="50" rx="5" fill="#e7f0f8" stroke="#174a7e"/>']
        if v.show_state_labels:
            parts.append(self._text(f"state-label-{label}", x - 30, y + 5, label.upper()))
        if state.speed is UnknownValue.UNKNOWN:
            parts.append(self._text(f"speed-{label}", x - 8, y + 65, "?"))
        else:
            parts.append(self._arrow(f"speed-arrow-{label}", x - 30, y - 48, x + 30, y - 48, "speed (schematic)"))
            speed_label = "speed"
            if self._numbers(opts):
                speed_label = f"v = {state.speed.value:g} m/s"
            parts.append(self._text(f"speed-label-{label}", x - 35, y + 65, speed_label))
        return parts

    def _height_parts(self, scenario: WorkEnergyScenario, opts: WorkEnergyRenderOptions) -> list[str]:
        contexts = scenario.mechanical_energy_contexts
        heights: tuple[HeightState, ...]
        if contexts:
            if opts.context_index is not None:
                if opts.context_index >= len(contexts):
                    raise ValueError("context_index does not identify a mechanical-energy context")
                context = contexts[opts.context_index]
            elif len(contexts) == 1:
                context = contexts[0]
            else:
                raise ValueError("multiple mechanical-energy contexts require context_index")
            heights = (context.initial_height, context.final_height)
        else:
            heights = scenario.height_states
            if opts.state_id is not None:
                heights = tuple(state for state in heights if state.identifier == opts.state_id)
            if not heights:
                raise ValueError("HEIGHT_STATES requires authored height states")
        level_id = heights[0].reference_level.identifier
        if any(state.reference_level.identifier != level_id for state in heights):
            raise ValueError("height states must share one reference level")
        parts = [self._text("height-heading", 36, 34, "HEIGHT / REFERENCE LEVEL")]
        parts.append('<line id="wep-reference-level" x1="100" y1="260" x2="660" y2="260" stroke="#555" stroke-width="2"/>')
        if opts.visibility.show_reference_labels:
            parts.append(self._text("reference-label", 500, 253, f"reference: {level_id}"))
        for index, state in enumerate(heights):
            x = 230.0 + index * 300.0
            if state.height is UnknownValue.UNKNOWN:
                # Unknown is an explicit unresolved state, not the reference level.
                y = 145.0
                parts.append(self._text(f"height-unknown-{index}", x - 34, y, "height ?"))
            else:
                value = state.height.value
                y = 195.0 if value > 0 else 325.0 if value < 0 else 260.0
                parts.append(
                    f'<circle id="{self._id("height", index, state.identifier)}" '
                    f'cx="{x:.3f}" cy="{y:.3f}" r="9" fill="#e7f0f8" '
                    'stroke="#174a7e"/>'
                )
                if self._numbers(opts):
                    parts.append(self._text(f"height-value-{index}", x - 22, y - 18, f"h = {value:g} m"))
            if opts.visibility.show_state_labels:
                parts.append(self._text(f"height-state-label-{index}", x - 34, 370 if y >= 260 else y - 18, state.state.value.upper()))
        return parts

    def _constant_speed_parts(self, scenario: WorkEnergyScenario, opts: WorkEnergyRenderOptions) -> list[str]:
        inputs = scenario.constant_speed_power_inputs
        if not inputs:
            raise ValueError("CONSTANT_SPEED_SURFACE requires an authored constant-speed input")
        index = opts.input_index or 0
        if index >= len(inputs):
            raise ValueError("input_index does not identify a constant-speed input")
        authored = inputs[index]
        parts = [self._text("surface-heading", 36, 34, "CONSTANT-SPEED SURFACE")]
        if opts.visibility.show_surface_context:
            surface = "HORIZONTAL" if authored.surface is SurfaceContext.HORIZONTAL else "INCLINED (schematic)"
            path = '<path id="wep-surface" d="M100 270 L660 270"' if authored.surface is SurfaceContext.HORIZONTAL else '<path id="wep-surface" d="M100 300 L660 220"'
            parts.append(f'{path} fill="none" stroke="#555" stroke-width="3"/>')
            parts.append(self._text("surface-label", 110, 195 if authored.surface is SurfaceContext.INCLINED else 295, surface))
        y = 260.0
        parts.append(f'<rect id="{self._id("body")}" x="350" y="235" width="72" height="50" rx="5" fill="#e7f0f8" stroke="#174a7e"/>')
        parts.append(self._arrow("motion", 430, y, 490, y, "motion (schematic)"))
        if authored.force_along_motion is UnknownValue.UNKNOWN:
            parts.append(self._text("force-unknown", 300, 210, "force ?"))
        elif authored.force_along_motion.value > 0:
            parts.append(self._arrow("force", 385, 225, 449, 225, "force along motion"))
        elif authored.force_along_motion.value < 0:
            parts.append(self._arrow("force", 449, 225, 385, 225, "force opposite motion"))
        else:
            parts.append(self._text("force-zero", 390, 215, "force = 0"))
        if opts.visibility.show_force_labels:
            label = "force along motion"
            if self._numbers(opts) and authored.force_along_motion is not UnknownValue.UNKNOWN:
                label = f"F = {authored.force_along_motion.value:g} N"
            parts.append(self._text("force-label", 300, 335, label))
        if self._numbers(opts) and authored.speed is not UnknownValue.UNKNOWN:
            parts.append(self._text("speed-label", 450, 290, f"v = {authored.speed.value:g} m/s"))
        return parts

    def _pumping_parts(self, scenario: WorkEnergyScenario, opts: WorkEnergyRenderOptions) -> list[str]:
        inputs = scenario.pumping_power_inputs
        if not inputs:
            raise ValueError("PUMPING requires an authored pumping input")
        index = opts.input_index or 0
        if index >= len(inputs):
            raise ValueError("input_index does not identify a pumping input")
        authored: PumpingPowerInput = inputs[index]
        parts = [self._text("pumping-heading", 36, 34, "PUMPING / VERTICAL LIFT")]
        parts.extend([
            '<line id="wep-ground" x1="80" y1="235" x2="680" y2="235" stroke="#555" stroke-width="3"/>',
            '<rect id="wep-borehole" x="330" y="235" width="90" height="180" fill="#eef3f7" stroke="#174a7e"/>',
            '<path id="wep-water" d="M332 350 L418 350" stroke="#4a90b8" stroke-width="5" fill="none"/>',
            self._arrow("lift", 470, 390, 470, 250, "vertical lift"),
            self._text("pump-label", 345, 220, "pump / lift"),
            self._text("flow-label", 345, 385, "water source"),
        ])
        if self._numbers(opts):
            if authored.lift is not UnknownValue.UNKNOWN:
                parts.append(self._text("lift-value", 480, 320, f"lift = {authored.lift.value:g} m"))
            if authored.mass_flow_rate is not UnknownValue.UNKNOWN:
                parts.append(self._text("flow-value", 90, 300, f"ṁ = {authored.mass_flow_rate.value:g} kg/s"))
            if authored.gravitational_field is not UnknownValue.UNKNOWN:
                parts.append(self._text("field-value", 90, 325, f"g = {authored.gravitational_field.value:g} m/s²"))
        return parts


__all__ = [
    "WorkEnergyDiagramKind",
    "WorkEnergyRenderOptions",
    "WorkEnergySvgRenderer",
    "WorkEnergyVisibilityOptions",
]
