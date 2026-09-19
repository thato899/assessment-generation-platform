"""Framework-independent domain models for one-dimensional momentum problems."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from assessment_platform.core import GenerationProvenance, GenerationSeed


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _identifier(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


class PositiveAxis(StrEnum):
    """Physical direction represented by a positive coordinate value."""

    RIGHT = "right"
    LEFT = "left"


class PhysicalDirection(StrEnum):
    """Physical direction of a body's velocity in one dimension."""

    RIGHT = "right"
    LEFT = "left"
    REST = "rest"


@dataclass(frozen=True, slots=True)
class Kilograms:
    """A finite, strictly positive mass measured in kilograms."""

    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "mass")
        if value <= 0:
            raise ValueError("mass must be positive kilograms")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class MetresPerSecond:
    """A signed velocity measured in metres per second."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite(self.value, "velocity"))

    def physical_direction(self, positive_axis: PositiveAxis) -> PhysicalDirection:
        if not isinstance(positive_axis, PositiveAxis):
            raise ValueError("positive_axis must be explicit")
        if self.value == 0:
            return PhysicalDirection.REST
        positive_value_direction = (
            PhysicalDirection.RIGHT
            if positive_axis is PositiveAxis.RIGHT
            else PhysicalDirection.LEFT
        )
        negative_value_direction = (
            PhysicalDirection.LEFT
            if positive_axis is PositiveAxis.RIGHT
            else PhysicalDirection.RIGHT
        )
        return positive_value_direction if self.value > 0 else negative_value_direction


@dataclass(frozen=True, slots=True)
class Momentum:
    """A signed momentum value measured in kilogram metres per second."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite(self.value, "momentum"))


@dataclass(frozen=True, slots=True)
class Impulse:
    """A signed impulse value measured in newton seconds."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite(self.value, "impulse"))


@dataclass(frozen=True, slots=True)
class KineticEnergy:
    """A finite, non-negative kinetic-energy value measured in joules."""

    value: float

    def __post_init__(self) -> None:
        value = _finite(self.value, "kinetic energy")
        if value < 0:
            raise ValueError("kinetic energy must be non-negative joules")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class MomentumBody:
    """One uniquely identified body's initial mass and velocity."""

    identifier: str
    mass: Kilograms
    initial_velocity: MetresPerSecond

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _identifier(self.identifier, "body identifier"))
        if not isinstance(self.mass, Kilograms):
            raise ValueError("body mass must be Kilograms")
        if not isinstance(self.initial_velocity, MetresPerSecond):
            raise ValueError("body initial velocity must be MetresPerSecond")


@dataclass(frozen=True, slots=True)
class SystemBoundary:
    """The external-impulse assumption for the modeled body system."""

    isolated: bool
    external_impulse: Impulse | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.isolated, bool):
            raise ValueError("isolated must be a boolean")
        if self.external_impulse is not None and not isinstance(self.external_impulse, Impulse):
            raise ValueError("external_impulse must be Impulse or None")
        if self.isolated and self.external_impulse is not None:
            raise ValueError("an isolated system cannot have an external impulse")
        if not self.isolated and self.external_impulse is None:
            raise ValueError("a non-isolated system must declare its external impulse")


@dataclass(frozen=True, slots=True)
class MomentumScenario:
    """Initial state and system boundary for one-dimensional momentum motion.

    This model intentionally contains no final state or derived momentum. A
    future authoritative solver must produce and validate those results.
    """

    identifier: str
    bodies: tuple[MomentumBody, ...]
    positive_axis: PositiveAxis
    system: SystemBoundary
    seed: GenerationSeed | None = None
    provenance: GenerationProvenance | None = None
    assumptions: tuple[str, ...] = ("one-dimensional motion",)

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _identifier(self.identifier, "scenario identifier"))
        bodies = tuple(self.bodies)
        if not bodies or any(not isinstance(body, MomentumBody) for body in bodies):
            raise ValueError("scenario must contain MomentumBody values")
        identifiers = tuple(body.identifier for body in bodies)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("scenario body identifiers must be unique")
        object.__setattr__(self, "bodies", bodies)
        if not isinstance(self.positive_axis, PositiveAxis):
            raise ValueError("positive_axis must be explicit")
        if not isinstance(self.system, SystemBoundary):
            raise ValueError("system must be a SystemBoundary")
        if self.seed is not None and not isinstance(self.seed, GenerationSeed):
            raise ValueError("scenario seed must be a GenerationSeed")
        if self.provenance is not None and not isinstance(
            self.provenance, GenerationProvenance
        ):
            raise ValueError("scenario provenance must be GenerationProvenance")
        assumptions = tuple(_identifier(item, "scenario assumption") for item in self.assumptions)
        if not assumptions:
            raise ValueError("scenario assumptions must not be empty")
        object.__setattr__(self, "assumptions", assumptions)

    def direction_of(self, body: MomentumBody) -> PhysicalDirection:
        """Return a body's physical direction under this scenario's axis convention."""

        if body not in self.bodies:
            raise ValueError("body is not part of this scenario")
        return body.initial_velocity.physical_direction(self.positive_axis)
