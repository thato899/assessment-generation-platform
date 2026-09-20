"""Deterministic, learner-safe SVG rendering for one-dimensional momentum."""
# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any

from assessment_platform.domains.physical_sciences.mechanics.momentum_constrained_solver import (
    ConstrainedCollisionSolution,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    MomentumScenario,
    PhysicalDirection,
    PositiveAxis,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_interaction import (
    CompleteFinalStateConstraint,
    KnownFinalVelocityConstraint,
    MomentumInteraction,
)
from assessment_platform.rendering.svg.projectile import SvgDocument


@dataclass(frozen=True, slots=True)
class MomentumDiagramOptions:
    width: int = 760
    height: int = 420
    show_mass: bool = True
    show_initial_velocity: bool = True
    show_final_velocity: bool = True
    show_positive_axis: bool = True
    show_before_panel: bool = True
    show_after_panel: bool = False
    reveal_derived_final_velocity: bool = False
    show_system_boundary: bool = False

    def __post_init__(self) -> None:
        if self.width < 420 or self.height < 260:
            raise ValueError("diagram dimensions are too small")


class MomentumSvgRenderer:
    """Render supplied state; never derive momentum or collision values."""

    VERSION = "1"

    def render(
        self,
        scenario: MomentumScenario,
        interaction: MomentumInteraction | None = None,
        solution: ConstrainedCollisionSolution | None = None,
        options: MomentumDiagramOptions | None = None,
    ) -> SvgDocument:
        if not isinstance(scenario, MomentumScenario):
            raise ValueError("scenario must be a MomentumScenario")
        if interaction is not None and interaction.scenario != scenario:
            raise ValueError("interaction scenario does not match scenario")
        if solution is not None and solution.positive_axis is not scenario.positive_axis:
            raise ValueError("solution positive axis does not match scenario")
        opts = options or MomentumDiagramOptions()
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{opts.width}" height="{opts.height}" '
            f'viewBox="0 0 {opts.width} {opts.height}" role="img" aria-labelledby="momentum-title momentum-desc">',
            f'<title id="momentum-title">Momentum diagram: {escape(scenario.identifier)}</title>',
            f'<desc id="momentum-desc">{escape(self._description(scenario, interaction, opts))}</desc>',
            '<defs><marker id="momentum-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
            '<path d="M0,0 L6,3 L0,6 Z" fill="#174a7e"/></marker></defs>',
            '<g id="momentum-diagram" font-family="sans-serif" font-size="14">',
        ]
        if opts.show_positive_axis:
            axis_x = 70 if scenario.positive_axis is PositiveAxis.RIGHT else opts.width - 70
            end_x = axis_x + 44 if scenario.positive_axis is PositiveAxis.RIGHT else axis_x - 44
            parts.append(self._arrow("positive-axis", axis_x, 32, end_x, 32, "positive axis"))
        if opts.show_before_panel:
            parts.extend(
                self._panel(
                    scenario, scenario.bodies, "before", 105, opts, False, interaction, solution
                )
            )
        if opts.show_after_panel:
            parts.extend(
                self._panel(
                    scenario, scenario.bodies, "after", 285, opts, True, interaction, solution
                )
            )
        if opts.show_system_boundary:
            parts.append(
                f'<rect id="system-boundary" x="18" y="65" width="{opts.width - 36}" height="{opts.height - 82}" fill="none" stroke="#777" stroke-dasharray="6 4"/>'
            )
            parts.append(self._text("system-label", 28, 82, "system"))
        parts.append("</g></svg>")
        return SvgDocument("".join(parts), opts.width, opts.height)

    def _panel(
        self,
        scenario: MomentumScenario,
        bodies: tuple[Any, ...],
        panel: str,
        y: float,
        opts: MomentumDiagramOptions,
        final: bool,
        interaction: MomentumInteraction | None,
        solution: ConstrainedCollisionSolution | None,
    ) -> list[str]:
        ordered = tuple(sorted(bodies, key=lambda body: body.identifier))
        parts = [self._text(f"{panel}-label", 40, y - 28, panel.upper())]
        spacing = (opts.width - 120) / max(len(ordered), 1)
        final_values = (
            {state.body_identifier: state.final_velocity for state in solution.final_states}
            if solution
            else {}
        )
        for index, body in enumerate(ordered):
            x = 80 + spacing * (index + 0.5)
            velocity = final_values.get(body.identifier) if final else body.initial_velocity
            visible, label = self._velocity_label(body, velocity, final, opts, interaction)
            parts.append(
                f'<rect id="body-{escape(body.identifier)}-{panel}" x="{x - 42:.3f}" y="{y:.3f}" width="84" height="44" rx="4" fill="#e7f0f8" stroke="#174a7e"/>'
            )
            parts.append(
                self._text(
                    f"body-label-{escape(body.identifier)}-{panel}", x - 28, y + 27, body.identifier
                )
            )
            if opts.show_mass:
                parts.append(
                    self._text(
                        f"mass-{escape(body.identifier)}-{panel}",
                        x - 25,
                        y + 65,
                        f"{body.mass.value:g} kg",
                    )
                )
            if visible:
                direction = (
                    velocity.physical_direction(scenario.positive_axis)
                    if velocity
                    else PhysicalDirection.REST
                )
                if direction is not PhysicalDirection.REST:
                    dx = 55 if direction is PhysicalDirection.RIGHT else -55
                    parts.append(
                        self._arrow(
                            f"velocity-{escape(body.identifier)}-{panel}",
                            x,
                            y + 22,
                            x + dx,
                            y + 22,
                            "velocity",
                        )
                    )
                parts.append(
                    self._text(
                        f"velocity-label-{escape(body.identifier)}-{panel}", x - 34, y + 92, label
                    )
                )
            elif final and opts.show_final_velocity:
                parts.append(
                    self._text(
                        f"velocity-label-{escape(body.identifier)}-{panel}", x - 8, y + 92, "?"
                    )
                )
        return parts

    @staticmethod
    def _velocity_label(
        body: Any,
        velocity: Any,
        final: bool,
        opts: MomentumDiagramOptions,
        interaction: MomentumInteraction | None,
    ) -> tuple[bool, str]:
        if velocity is None or not (
            opts.show_final_velocity if final else opts.show_initial_velocity
        ):
            return False, ""
        authored = (
            not final
            or (
                interaction is not None
                and isinstance(interaction.constraint, CompleteFinalStateConstraint)
            )
            or (
                interaction is not None
                and isinstance(interaction.constraint, KnownFinalVelocityConstraint)
                and interaction.constraint.body_identifier == body.identifier
            )
        )
        if final and not authored and not opts.reveal_derived_final_velocity:
            return False, ""
        return True, f"{velocity.value:g} m/s"

    @staticmethod
    def _arrow(identifier: str, x1: float, y1: float, x2: float, y2: float, label: str) -> str:
        return f'<line id="{identifier}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#174a7e" stroke-width="2" marker-end="url(#momentum-arrow)" aria-label="{escape(label)}"/>'

    @staticmethod
    def _text(identifier: str, x: float, y: float, value: str) -> str:
        return f'<text id="{identifier}" x="{x:.3f}" y="{y:.3f}">{escape(value)}</text>'

    @staticmethod
    def _description(
        scenario: MomentumScenario,
        interaction: MomentumInteraction | None,
        opts: MomentumDiagramOptions,
    ) -> str:
        directions = ", ".join(
            f"{b.identifier} {b.initial_velocity.physical_direction(scenario.positive_axis).value}"
            for b in sorted(scenario.bodies, key=lambda body: body.identifier)
        )
        return f"One-dimensional momentum diagram for {directions}; positive axis points {scenario.positive_axis.value}."
