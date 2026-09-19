"""Immutable model for a CAPS Grade 12 one-dimensional projectile scenario.

This module describes initial conditions and modelling assumptions only. It does
not calculate a trajectory or any derived result; those responsibilities belong
to the future deterministic solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from assessment_platform.core import GenerationProvenance, GenerationSeed


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


@dataclass(frozen=True, slots=True)
class Metres:
    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "position")
        if value < 0:
            raise ValueError("position must be non-negative metres")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class MetresPerSecond:
    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite(self.value, "velocity"))


@dataclass(frozen=True, slots=True)
class MetresPerSecondSquared:
    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "gravitational acceleration")
        if value == 0:
            raise ValueError("gravitational acceleration must not be zero")
        object.__setattr__(self, "value", value)


class PositiveDirection(StrEnum):
    UP = "up"
    DOWN = "down"


class LaunchDirection(StrEnum):
    UPWARD = "upward"
    DOWNWARD = "downward"
    REST = "rest"


class ScenarioType(StrEnum):
    PROJECTED_UPWARD = "projected-upward"
    PROJECTED_DOWNWARD = "projected-downward"
    DROPPED_FROM_REST = "dropped-from-rest"


@dataclass(frozen=True, slots=True)
class VerticalProjectileScenario:
    """Initial conditions for one vertical projectile in a 1D coordinate system.

    Position is measured from a declared reference level in metres. Velocity and
    acceleration are signed according to ``positive_direction``. The model uses
    SI units and the CAPS assumptions of near-Earth motion without air friction.
    """

    identifier: str
    launch_position: Metres
    initial_velocity: MetresPerSecond
    gravitational_acceleration: MetresPerSecondSquared
    positive_direction: PositiveDirection
    launch_direction: LaunchDirection
    scenario_type: ScenarioType
    seed: GenerationSeed | None = None
    assumptions: tuple[str, ...] = (
        "near the surface of the Earth",
        "in the absence of air friction",
        "one-dimensional vertical motion",
    )
    provenance: GenerationProvenance | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier.strip():
            raise ValueError("scenario identifier must be a non-empty string")
        object.__setattr__(self, "identifier", self.identifier.strip())
        if not isinstance(self.positive_direction, PositiveDirection):
            raise ValueError("positive_direction must be explicit")
        if not isinstance(self.launch_direction, LaunchDirection):
            raise ValueError("launch_direction must be explicit")
        if not isinstance(self.scenario_type, ScenarioType):
            raise ValueError("scenario_type must be explicit")
        assumptions = tuple(assumption.strip() for assumption in self.assumptions)
        if not assumptions or any(not assumption for assumption in assumptions):
            raise ValueError("scenario assumptions must be non-empty strings")
        object.__setattr__(self, "assumptions", assumptions)
        if self.provenance is not None and not isinstance(
            self.provenance, GenerationProvenance
        ):
            raise ValueError("scenario provenance must be GenerationProvenance")
        self._validate_signs()

    def _validate_signs(self) -> None:
        velocity = self.initial_velocity.value
        gravity = self.gravitational_acceleration.value
        if self.positive_direction is PositiveDirection.UP and gravity >= 0:
            raise ValueError("gravity must be negative when up is positive")
        if self.positive_direction is PositiveDirection.DOWN and gravity <= 0:
            raise ValueError("gravity must be positive when down is positive")
        if self.launch_direction is LaunchDirection.UPWARD and not self._is_upward(velocity):
            raise ValueError("upward launch requires a velocity in the positive upward direction")
        if self.launch_direction is LaunchDirection.DOWNWARD and not self._is_downward(velocity):
            raise ValueError("downward launch requires a velocity in the downward direction")
        if self.launch_direction is LaunchDirection.REST and velocity != 0:
            raise ValueError("rest launch requires zero initial velocity")
        expected_type = {
            LaunchDirection.UPWARD: ScenarioType.PROJECTED_UPWARD,
            LaunchDirection.DOWNWARD: ScenarioType.PROJECTED_DOWNWARD,
            LaunchDirection.REST: ScenarioType.DROPPED_FROM_REST,
        }[self.launch_direction]
        if self.scenario_type is not expected_type:
            raise ValueError("scenario_type must match launch_direction")

    def _is_upward(self, velocity: float) -> bool:
        return velocity > 0 if self.positive_direction is PositiveDirection.UP else velocity < 0

    def _is_downward(self, velocity: float) -> bool:
        return velocity < 0 if self.positive_direction is PositiveDirection.UP else velocity > 0
