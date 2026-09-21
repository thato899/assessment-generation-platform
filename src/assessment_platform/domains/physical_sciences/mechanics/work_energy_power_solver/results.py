"""Immutable derived results and failure semantics for M5."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from ..work_energy_power import (
    Displacement,
    EnergyState,
    GravitationalFieldMagnitude,
    KineticEnergy,
    KineticState,
    Mass,
    RelativeHeight,
    SignedEnergy,
    SignedForce,
    Speed,
)
from ..work_energy_power.values import identifier


class FailureReason(StrEnum):
    UNDERDETERMINED = "underdetermined"
    INCONSISTENT = "physically-inconsistent"
    UNSUPPORTED = "unsupported"
    NUMERICAL_RANGE = "numerical-range"


class WorkEnergySolveError(ValueError):
    """A structurally valid authored relationship cannot produce a result."""

    def __init__(self, reason: FailureReason, message: str) -> None:
        super().__init__(message)
        self.reason = reason


def _id(value: str, name: str) -> str:
    return identifier(value, name)


def _finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


@dataclass(frozen=True, slots=True)
class Watts:
    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite(self.value, "power"))


class PowerKind(StrEnum):
    AVERAGE = "average"
    CONSTANT_SPEED = "constant-speed"
    PUMPING = "pumping"


@dataclass(frozen=True, slots=True)
class WorkResult:
    contribution_id: str
    work: SignedEnergy

    def __post_init__(self) -> None:
        object.__setattr__(self, "contribution_id", _id(self.contribution_id, "contribution ID"))
        if not isinstance(self.work, SignedEnergy):
            raise ValueError("work result must contain SignedEnergy")


@dataclass(frozen=True, slots=True)
class NetWorkResult:
    contributions: tuple[WorkResult, ...]
    net_work: SignedEnergy

    def __post_init__(self) -> None:
        contributions = tuple(self.contributions)
        if any(not isinstance(item, WorkResult) for item in contributions):
            raise ValueError("net-work result contributions must be WorkResult values")
        ids = tuple(item.contribution_id for item in contributions)
        if len(ids) != len(set(ids)):
            raise ValueError("net-work result contribution IDs must be unique")
        object.__setattr__(self, "contributions", contributions)
        if not isinstance(self.net_work, SignedEnergy):
            raise ValueError("net-work result must contain SignedEnergy")


@dataclass(frozen=True, slots=True)
class AlongPlaneWorkResult:
    resultant_force: SignedForce
    displacement: Displacement
    work: SignedEnergy

    def __post_init__(self) -> None:
        if not isinstance(self.resultant_force, SignedForce):
            raise ValueError("along-plane result force must be SignedForce")
        if not isinstance(self.displacement, Displacement):
            raise ValueError("along-plane result displacement must be Displacement")
        if not isinstance(self.work, SignedEnergy):
            raise ValueError("along-plane result must contain SignedEnergy")


@dataclass(frozen=True, slots=True)
class KineticEnergyResult:
    state_id: str
    mass: Mass
    speed: Speed
    kinetic_energy: KineticEnergy

    def __post_init__(self) -> None:
        object.__setattr__(self, "state_id", _id(self.state_id, "state ID"))
        if not isinstance(self.mass, Mass) or not isinstance(self.speed, Speed):
            raise ValueError("kinetic result must retain Mass and Speed")
        if not isinstance(self.kinetic_energy, KineticEnergy):
            raise ValueError("kinetic energy result must contain KineticEnergy")


@dataclass(frozen=True, slots=True)
class PotentialEnergyResult:
    state_id: str
    reference_level_id: str
    mass: Mass
    gravitational_field: GravitationalFieldMagnitude
    height: RelativeHeight
    potential_energy: SignedEnergy

    def __post_init__(self) -> None:
        object.__setattr__(self, "state_id", _id(self.state_id, "state ID"))
        object.__setattr__(
            self, "reference_level_id", _id(self.reference_level_id, "reference level ID")
        )
        if not isinstance(self.mass, Mass):
            raise ValueError("potential result mass must be Mass")
        if not isinstance(self.gravitational_field, GravitationalFieldMagnitude):
            raise ValueError("potential result field must be GravitationalFieldMagnitude")
        if not isinstance(self.height, RelativeHeight):
            raise ValueError("potential result height must be RelativeHeight")
        if not isinstance(self.potential_energy, SignedEnergy):
            raise ValueError("potential result must contain SignedEnergy")


@dataclass(frozen=True, slots=True)
class WorkEnergyResult:
    initial_state: KineticState
    final_state: KineticState
    net_work: SignedEnergy
    initial_kinetic_energy: KineticEnergy
    final_kinetic_energy: KineticEnergy

    def __post_init__(self) -> None:
        if not isinstance(self.initial_state, KineticState) or not isinstance(
            self.final_state, KineticState
        ):
            raise ValueError("work-energy result states must be KineticState")
        if self.initial_state.state is not EnergyState.INITIAL:
            raise ValueError("work-energy result initial state identity is invalid")
        if self.final_state.state is not EnergyState.FINAL:
            raise ValueError("work-energy result final state identity is invalid")
        if not isinstance(self.net_work, SignedEnergy):
            raise ValueError("work-energy result must contain SignedEnergy")
        for name in ("initial_kinetic_energy", "final_kinetic_energy"):
            if not isinstance(getattr(self, name), KineticEnergy):
                raise ValueError(f"{name} must be KineticEnergy")


@dataclass(frozen=True, slots=True)
class MechanicalEnergyResult:
    initial_state_id: str
    final_state_id: str
    reference_level_id: str
    initial_kinetic_energy: KineticEnergy
    final_kinetic_energy: KineticEnergy
    initial_potential_energy: SignedEnergy
    final_potential_energy: SignedEnergy
    non_conservative_work: SignedEnergy

    def __post_init__(self) -> None:
        object.__setattr__(self, "initial_state_id", _id(self.initial_state_id, "initial state ID"))
        object.__setattr__(self, "final_state_id", _id(self.final_state_id, "final state ID"))
        object.__setattr__(
            self, "reference_level_id", _id(self.reference_level_id, "reference level ID")
        )
        for name in ("initial_kinetic_energy", "final_kinetic_energy"):
            if not isinstance(getattr(self, name), KineticEnergy):
                raise ValueError(f"{name} must be KineticEnergy")
        for name in (
            "initial_potential_energy",
            "final_potential_energy",
            "non_conservative_work",
        ):
            if not isinstance(getattr(self, name), SignedEnergy):
                raise ValueError(f"{name} must be SignedEnergy")


@dataclass(frozen=True, slots=True)
class PowerResult:
    kind: PowerKind
    power: Watts

    def __post_init__(self) -> None:
        if not isinstance(self.kind, PowerKind):
            raise ValueError("power result kind must be PowerKind")
        if not isinstance(self.power, Watts):
            raise ValueError("power result must contain Watts")


@dataclass(frozen=True, slots=True)
class PumpingPowerResult:
    power: Watts

    def __post_init__(self) -> None:
        if not isinstance(self.power, Watts) or self.power.value < 0:
            raise ValueError("pumping power must be a non-negative Watts result")


__all__ = [
    "AlongPlaneWorkResult",
    "FailureReason",
    "KineticEnergyResult",
    "MechanicalEnergyResult",
    "NetWorkResult",
    "PumpingPowerResult",
    "PowerKind",
    "PowerResult",
    "PotentialEnergyResult",
    "Watts",
    "WorkEnergyResult",
    "WorkEnergySolveError",
    "WorkResult",
]
