"""Small Newton input values; no dependency on another mechanics engine."""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class UnknownValue(StrEnum):
    """Explicitly unauthored numerical input, distinct from any physical value."""

    UNKNOWN = "unknown"


def finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def identifier(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("identifier must be a non-empty string")
    return value.strip()


def require_type(value: object, expected: type | tuple[type, ...], name: str) -> None:
    if not isinstance(value, expected):
        raise ValueError(f"{name} has an invalid domain type")


def typed_tuple[T](values: tuple[T, ...], expected: type, name: str) -> tuple[T, ...]:
    # Reject unordered containers: authored order is part of deterministic state.
    if not isinstance(values, (tuple, list)):
        raise ValueError(f"{name} must be an ordered sequence")
    result = tuple(values)
    for value in result:
        require_type(value, expected, name)
    return result


def identifiers(values: tuple[str, ...]) -> tuple[str, ...]:
    result = tuple(identifier(item) for item in typed_tuple(values, str, "identifiers"))
    if not result or len(result) != len(set(result)):
        raise ValueError("identifiers must be non-empty and unique")
    return result


@dataclass(frozen=True, slots=True)
class Kilograms:
    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "mass")
        if value <= 0:
            raise ValueError("mass must be positive kilograms")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class Newtons:
    """An authored signed force component, including zero."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", finite(self.value, "force"))


@dataclass(frozen=True, slots=True)
class MetresPerSecondSquared:
    """An authored signed acceleration component, including zero."""

    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", finite(self.value, "acceleration"))


@dataclass(frozen=True, slots=True)
class Metres:
    """Strictly positive separation, not a position coordinate."""

    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "separation")
        if value <= 0:
            raise ValueError("separation must be positive metres")
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class FrictionCoefficient:
    """Dimensionless and non-negative; values greater than one are allowed."""

    value: float

    def __post_init__(self) -> None:
        value = finite(self.value, "friction coefficient")
        if value < 0:
            raise ValueError("friction coefficient must be non-negative")
        object.__setattr__(self, "value", value)
