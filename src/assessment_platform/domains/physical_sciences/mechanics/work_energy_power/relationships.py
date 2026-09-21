"""Authored Work, Energy & Power relationships.

The classes in this module retain authored quantities and applicability facts;
they intentionally do not calculate work, energy, or power.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .values import (
    AngleDegrees,
    Displacement,
    ForceMagnitude,
    GravitationalFieldMagnitude,
    Mass,
    MassFlowRate,
    RelativeHeight,
    SignedEnergy,
    SignedForce,
    Speed,
    TimeInterval,
    UnknownValue,
    identifier,
)

type Maybe[T] = T | UnknownValue


class EnergyState(StrEnum):
    INITIAL = "initial"
    FINAL = "final"


class ForceEnergyClassification(StrEnum):
    CONSERVATIVE = "conservative"
    NON_CONSERVATIVE = "non-conservative"


class SurfaceContext(StrEnum):
    HORIZONTAL = "horizontal"
    INCLINED = "inclined"


@dataclass(frozen=True, slots=True)
class ContactCondition:
    maintained_over_displacement: bool

    def __post_init__(self) -> None:
        if not isinstance(self.maintained_over_displacement, bool):
            raise ValueError("maintained_over_displacement must be a boolean")


@dataclass(frozen=True, slots=True)
class WorkContribution:
    """One authored force/displacement/angle contribution to work."""

    identifier: str
    force_magnitude: Maybe[ForceMagnitude]
    displacement: Maybe[Displacement]
    angle: Maybe[AngleDegrees]
    classification: ForceEnergyClassification | None = None
    contact: ContactCondition | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", identifier(self.identifier, "contribution identifier")
        )
        for name, expected in (
            ("force_magnitude", ForceMagnitude),
            ("displacement", Displacement),
            ("angle", AngleDegrees),
        ):
            value = getattr(self, name)
            if not isinstance(value, (expected, UnknownValue)):
                raise ValueError(f"{name} must be {expected.__name__} or UnknownValue")
        if self.classification is not None and not isinstance(
            self.classification, ForceEnergyClassification
        ):
            raise ValueError("classification must be ForceEnergyClassification or None")
        if self.contact is not None and not isinstance(self.contact, ContactCondition):
            raise ValueError("contact must be ContactCondition or None")


@dataclass(frozen=True, slots=True)
class NetWorkInput:
    contributions: tuple[WorkContribution, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.contributions, (tuple, list)):
            raise ValueError("contributions must be an ordered sequence")
        contributions = tuple(self.contributions)
        if not contributions:
            raise ValueError("net-work input requires at least one contribution")
        if any(not isinstance(item, WorkContribution) for item in contributions):
            raise ValueError("contributions must contain WorkContribution values")
        identifiers = tuple(item.identifier for item in contributions)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("contribution identifiers must be unique")
        object.__setattr__(self, "contributions", contributions)


@dataclass(frozen=True, slots=True)
class AlongPlaneWorkInput:
    """Explicit scalar resultant force and displacement along an authored plane."""

    resultant_force: Maybe[SignedForce]
    displacement: Maybe[Displacement]

    def __post_init__(self) -> None:
        if not isinstance(self.resultant_force, (SignedForce, UnknownValue)):
            raise ValueError("resultant_force must be SignedForce or UnknownValue")
        if not isinstance(self.displacement, (Displacement, UnknownValue)):
            raise ValueError("displacement must be Displacement or UnknownValue")


@dataclass(frozen=True, slots=True)
class ReferenceLevel:
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", identifier(self.identifier, "reference level identifier")
        )


@dataclass(frozen=True, slots=True)
class KineticState:
    identifier: str
    state: EnergyState
    mass: Maybe[Mass]
    speed: Maybe[Speed]

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier, "state identifier"))
        if not isinstance(self.state, EnergyState):
            raise ValueError("state must be EnergyState")
        if not isinstance(self.mass, (Mass, UnknownValue)):
            raise ValueError("mass must be Mass or UnknownValue")
        if not isinstance(self.speed, (Speed, UnknownValue)):
            raise ValueError("speed must be Speed or UnknownValue")


MotionState = KineticState


@dataclass(frozen=True, slots=True)
class HeightState:
    identifier: str
    state: EnergyState
    reference_level: ReferenceLevel
    height: Maybe[RelativeHeight]
    gravitational_field: Maybe[GravitationalFieldMagnitude]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", identifier(self.identifier, "height state identifier")
        )
        if not isinstance(self.state, EnergyState):
            raise ValueError("state must be EnergyState")
        if not isinstance(self.reference_level, ReferenceLevel):
            raise ValueError("reference_level must be ReferenceLevel")
        if not isinstance(self.height, (RelativeHeight, UnknownValue)):
            raise ValueError("height must be RelativeHeight or UnknownValue")
        if not isinstance(self.gravitational_field, (GravitationalFieldMagnitude, UnknownValue)):
            raise ValueError(
                "gravitational_field must be GravitationalFieldMagnitude or UnknownValue"
            )


@dataclass(frozen=True, slots=True)
class WorkEnergyContext:
    initial_state: KineticState
    final_state: KineticState
    net_work: Maybe[SignedEnergy] = UnknownValue.UNKNOWN
    work_input: NetWorkInput | AlongPlaneWorkInput | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.initial_state, KineticState) or not isinstance(
            self.final_state, KineticState
        ):
            raise ValueError("work-energy states must be KineticState")
        if self.initial_state.state is not EnergyState.INITIAL:
            raise ValueError("initial_state must have INITIAL identity")
        if self.final_state.state is not EnergyState.FINAL:
            raise ValueError("final_state must have FINAL identity")
        if not isinstance(self.net_work, (SignedEnergy, UnknownValue)):
            raise ValueError("net_work must be signed energy or UnknownValue")
        if self.work_input is not None and not isinstance(
            self.work_input, (NetWorkInput, AlongPlaneWorkInput)
        ):
            raise ValueError("work_input must be a supported authored work input")


@dataclass(frozen=True, slots=True)
class MechanicalEnergyContext:
    initial_state: KineticState
    final_state: KineticState
    initial_height: HeightState
    final_height: HeightState
    non_conservative_work: Maybe[SignedEnergy] = UnknownValue.UNKNOWN

    def __post_init__(self) -> None:
        if not isinstance(self.initial_state, KineticState) or not isinstance(
            self.final_state, KineticState
        ):
            raise ValueError("mechanical-energy states must be KineticState")
        if self.initial_state.state is not EnergyState.INITIAL:
            raise ValueError("initial_state must have INITIAL identity")
        if self.final_state.state is not EnergyState.FINAL:
            raise ValueError("final_state must have FINAL identity")
        if not isinstance(self.initial_height, HeightState) or not isinstance(
            self.final_height, HeightState
        ):
            raise ValueError("height states must be HeightState")
        if self.initial_height.state is not EnergyState.INITIAL:
            raise ValueError("initial_height must have INITIAL identity")
        if self.final_height.state is not EnergyState.FINAL:
            raise ValueError("final_height must have FINAL identity")
        if self.initial_height.reference_level != self.final_height.reference_level:
            raise ValueError("initial and final heights must share a reference level")
        if not isinstance(self.non_conservative_work, (SignedEnergy, UnknownValue)):
            raise ValueError("non_conservative_work must be signed energy or UnknownValue")


@dataclass(frozen=True, slots=True)
class AveragePowerInput:
    work: Maybe[SignedEnergy]
    time: Maybe[TimeInterval]

    def __post_init__(self) -> None:
        if not isinstance(self.work, (SignedEnergy, UnknownValue)):
            raise ValueError("work must be signed energy or UnknownValue")
        if not isinstance(self.time, (TimeInterval, UnknownValue)):
            raise ValueError("time must be TimeInterval or UnknownValue")


@dataclass(frozen=True, slots=True)
class ConstantSpeedPowerInput:
    force_along_motion: Maybe[SignedForce]
    speed: Maybe[Speed]
    surface: SurfaceContext

    def __post_init__(self) -> None:
        if not isinstance(self.force_along_motion, (SignedForce, UnknownValue)):
            raise ValueError("force_along_motion must be SignedForce or UnknownValue")
        if not isinstance(self.speed, (Speed, UnknownValue)):
            raise ValueError("speed must be Speed or UnknownValue")
        if not isinstance(self.surface, SurfaceContext):
            raise ValueError("surface must be SurfaceContext")


@dataclass(frozen=True, slots=True)
class PumpingPowerInput:
    mass_flow_rate: Maybe[MassFlowRate]
    lift: Maybe[Displacement]
    gravitational_field: Maybe[GravitationalFieldMagnitude]

    def __post_init__(self) -> None:
        if not isinstance(self.mass_flow_rate, (MassFlowRate, UnknownValue)):
            raise ValueError("mass_flow_rate must be MassFlowRate or UnknownValue")
        if not isinstance(self.lift, (Displacement, UnknownValue)):
            raise ValueError("lift must be Displacement or UnknownValue")
        if not isinstance(self.gravitational_field, (GravitationalFieldMagnitude, UnknownValue)):
            raise ValueError(
                "gravitational_field must be GravitationalFieldMagnitude or UnknownValue"
            )


@dataclass(frozen=True, slots=True)
class WorkEnergyAssumptions:
    """Optional explicit applicability flags; omitted flags are not inferred."""

    inertial_frame: bool | None = None
    constant_mass: bool | None = None
    near_earth_field: bool | None = None
    constant_force: bool | None = None
    constant_speed: bool | None = None
    reference_level_declared: bool | None = None

    def __post_init__(self) -> None:
        for name in (
            "inertial_frame",
            "constant_mass",
            "near_earth_field",
            "constant_force",
            "constant_speed",
            "reference_level_declared",
        ):
            value = getattr(self, name)
            if value is not None and not isinstance(value, bool):
                raise ValueError(f"{name} must be a boolean or None")


__all__ = [
    "AlongPlaneWorkInput",
    "AveragePowerInput",
    "ConstantSpeedPowerInput",
    "ContactCondition",
    "EnergyState",
    "ForceEnergyClassification",
    "HeightState",
    "KineticState",
    "MechanicalEnergyContext",
    "MotionState",
    "NetWorkInput",
    "PumpingPowerInput",
    "ReferenceLevel",
    "SurfaceContext",
    "WorkContribution",
    "WorkEnergyAssumptions",
    "WorkEnergyContext",
]
