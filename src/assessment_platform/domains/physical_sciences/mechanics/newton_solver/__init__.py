"""Authoritative numerical Newton operations, separate from authored domain models."""

from ._numerical import (
    GRAVITATIONAL_CONSTANT,
    SOLVER_ID,
    SOLVER_VERSION,
    VALIDATION_TOLERANCE,
)
from .results import (
    BodyDynamicsResult,
    ComponentSign,
    ConnectedBodiesResult,
    ContactResult,
    FailureReason,
    ForceResult,
    FrictionResult,
    GravitationalResult,
    NewtonSolveError,
    ResultantResult,
    StraightStringRequest,
    WeightResult,
)
from .solver import NewtonSolver

__all__ = [
    "BodyDynamicsResult",
    "ComponentSign",
    "ConnectedBodiesResult",
    "ContactResult",
    "FailureReason",
    "ForceResult",
    "FrictionResult",
    "GRAVITATIONAL_CONSTANT",
    "GravitationalResult",
    "NewtonSolveError",
    "NewtonSolver",
    "ResultantResult",
    "SOLVER_ID",
    "SOLVER_VERSION",
    "StraightStringRequest",
    "VALIDATION_TOLERANCE",
    "WeightResult",
]
