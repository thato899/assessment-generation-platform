"""Central Newton numerical policy, independent of display rounding."""

from math import fsum, isfinite
from typing import Final

from .results import FailureReason, NewtonSolveError

SOLVER_ID: Final = "caps-newtons-laws-solver"
SOLVER_VERSION: Final = "1"
VALIDATION_TOLERANCE: Final = 1e-9
# DBE 2021 Physical Sciences Examination Guidelines, p. 27, Table 1 (SI N m² kg⁻²).
GRAVITATIONAL_CONSTANT: Final = 6.67e-11


def checked(value: float) -> float:
    if not isfinite(value):
        raise NewtonSolveError(FailureReason.NUMERICAL_RANGE, "non-finite Newton calculation")
    return value


def total(values: tuple[float, ...]) -> float:
    try:
        return checked(fsum(values))
    except OverflowError as error:
        raise NewtonSolveError(FailureReason.NUMERICAL_RANGE, "Newton sum overflow") from error


def close(first: float, second: float) -> bool:
    return isfinite(first) and isfinite(second) and abs(first - second) <= VALIDATION_TOLERANCE


def consistent(first: float, second: float, message: str) -> None:
    if not close(first, second):
        raise NewtonSolveError(FailureReason.INCONSISTENT, message)
