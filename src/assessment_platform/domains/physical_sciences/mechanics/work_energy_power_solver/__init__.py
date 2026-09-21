"""Authoritative deterministic Work, Energy & Power numerical engine."""

from ._numerical import SOLVER_ID, SOLVER_VERSION, VALIDATION_TOLERANCE
from .results import (
    AlongPlaneWorkResult,
    FailureReason,
    KineticEnergyResult,
    MechanicalEnergyResult,
    NetWorkResult,
    PotentialEnergyResult,
    PowerKind,
    PowerResult,
    PumpingPowerResult,
    Watts,
    WorkEnergyResult,
    WorkEnergySolveError,
    WorkResult,
)
from .solver import WorkEnergySolver

__all__ = [
    "AlongPlaneWorkResult",
    "FailureReason",
    "KineticEnergyResult",
    "MechanicalEnergyResult",
    "NetWorkResult",
    "PowerKind",
    "PowerResult",
    "PotentialEnergyResult",
    "PumpingPowerResult",
    "SOLVER_ID",
    "SOLVER_VERSION",
    "VALIDATION_TOLERANCE",
    "Watts",
    "WorkEnergyResult",
    "WorkEnergySolveError",
    "WorkEnergySolver",
    "WorkResult",
]
