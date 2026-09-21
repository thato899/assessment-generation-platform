"""Authored scalar values for the Work, Energy & Power domain.

These values describe inputs only.  They deliberately do not expose any
calculation methods; numerical relationships belong to the later solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class UnknownValue(StrEnum):
    """An authored quantity whose numerical value is intentionally unknown."""

    UNKNOWN = "unknown"


def finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def identifier(value: object, name: str = "identifier") -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def ordered_tuple[T](value: object, expected: type, name: str) -> tuple[T, ...]:
    if not isinstance(value, (tuple, list)):
        raise ValueError(f"{name} must be an ordered sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise ValueError(f"{name} contains an invalid value")
    return result


@dataclass(frozen=True, slots=True)
class Mass:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "mass")
        if value <= 0:
            raise ValueError("mass must be positive kilograms")
        object.__setattr__(self, "value", value)


Kilograms = Mass


@dataclass(frozen=True, slots=True)
class ForceMagnitude:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "force magnitude")
        if value < 0:
            raise ValueError("force magnitude must be non-negative")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class SignedForce:
    """An explicitly signed force component along an authored direction."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", finite(self.value, "signed force"))


ForceAlongMotion = SignedForce


@dataclass(frozen=True, slots=True)
class Displacement:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "displacement")
        if value < 0:
            raise ValueError("displacement magnitude must be non-negative")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class Speed:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "speed")
        if value < 0:
            raise ValueError("speed must be non-negative")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class TimeInterval:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "time interval")
        if value <= 0:
            raise ValueError("time interval must be positive seconds")
        object.__setattr__(self, "value", value)


Seconds = TimeInterval


@dataclass(frozen=True, slots=True)
class MassFlowRate:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "mass flow rate")
        if value <= 0:
            raise ValueError("mass flow rate must be positive kilograms per second")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class GravitationalFieldMagnitude:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "gravitational field magnitude")
        if value <= 0:
            raise ValueError("gravitational field magnitude must be positive")
        object.__setattr__(self, "value", value)


GravitationalField = GravitationalFieldMagnitude


@dataclass(frozen=True, slots=True)
class AngleDegrees:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "force-displacement angle")
        if not 0 <= value <= 180:
            raise ValueError("force-displacement angle must be between 0 and 180 degrees")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class RelativeHeight:
    """Signed height relative to an explicitly authored reference level."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", finite(self.value, "relative height"))


@dataclass(frozen=True, slots=True)
class SignedEnergy:
    """A signed authored energy/work quantity measured in joules."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", finite(self.value, "energy"))


SignedWork = SignedEnergy
Joules = SignedEnergy


@dataclass(frozen=True, slots=True)
class KineticEnergy:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "kinetic energy")
        if value < 0:
            raise ValueError("kinetic energy must be non-negative")
        object.__setattr__(self, "value", value)


__all__ = [
    "AngleDegrees",
    "Displacement",
    "ForceAlongMotion",
    "ForceMagnitude",
    "GravitationalField",
    "GravitationalFieldMagnitude",
    "Joules",
    "Kilograms",
    "KineticEnergy",
    "Mass",
    "MassFlowRate",
    "RelativeHeight",
    "Seconds",
    "SignedEnergy",
    "SignedForce",
    "SignedWork",
    "Speed",
    "TimeInterval",
    "UnknownValue",
]
