"""Checked numerical policy for the Work, Energy & Power solver."""

from __future__ import annotations

from collections.abc import Callable
from math import fsum, isfinite
from typing import Final

from .results import FailureReason, WorkEnergySolveError

SOLVER_ID: Final[str] = "caps-work-energy-power-solver"
SOLVER_VERSION: Final[str] = "1"
VALIDATION_TOLERANCE: Final[float] = 1e-9


def checked(value: float, message: str = "non-finite Work, Energy & Power result") -> float:
    if not isfinite(value):
        raise WorkEnergySolveError(FailureReason.NUMERICAL_RANGE, message)
    return value


def operation(
    function: Callable[[], float], message: str = "Work, Energy & Power arithmetic overflow"
) -> float:
    try:
        return checked(float(function()), message)
    except OverflowError as error:
        raise WorkEnergySolveError(FailureReason.NUMERICAL_RANGE, message) from error
    except ZeroDivisionError as error:
        raise WorkEnergySolveError(FailureReason.NUMERICAL_RANGE, message) from error


def total(values: tuple[float, ...]) -> float:
    return operation(lambda: fsum(values), "Work, Energy & Power summation overflow")


def close(first: float, second: float) -> bool:
    return isfinite(first) and isfinite(second) and abs(first - second) <= VALIDATION_TOLERANCE


def consistent(first: float, second: float, message: str) -> None:
    if not close(first, second):
        raise WorkEnergySolveError(FailureReason.INCONSISTENT, message)


def cardinal_cosine(angle: float) -> float:
    """Return exact values for semantic cardinal angles; trig is solver-owned."""

    if angle == 0:
        return 1.0
    if angle == 90:
        return 0.0
    if angle == 180:
        return -1.0
    from math import cos, radians

    return operation(lambda: cos(radians(angle)), "force-displacement angle overflow")


__all__ = [
    "SOLVER_ID",
    "SOLVER_VERSION",
    "VALIDATION_TOLERANCE",
    "cardinal_cosine",
    "checked",
    "close",
    "consistent",
    "operation",
    "total",
]
