"""Authored ownership, contacts and bounded relationships for Newton scenarios."""

from dataclasses import dataclass
from enum import StrEnum

from .coordinates import AccelerationVector
from .values import (
    FrictionCoefficient,
    Kilograms,
    Metres,
    UnknownValue,
    finite,
    identifier,
    identifiers,
    require_type,
)


@dataclass(frozen=True, slots=True)
class BodyReference:
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))


@dataclass(frozen=True, slots=True)
class EnvironmentReference:
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))


type ForceSource = BodyReference | EnvironmentReference


@dataclass(frozen=True, slots=True)
class NewtonBody:
    identifier: str
    mass: Kilograms

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))
        require_type(self.mass, Kilograms, "mass")


@dataclass(frozen=True, slots=True)
class SystemBoundary:
    """Selected bodies; other declared bodies and environment agents lie outside it."""

    body_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "body_ids", identifiers(self.body_ids))


@dataclass(frozen=True, slots=True)
class NewtonAssumptions:
    inertial_frame: bool
    constant_mass: bool
    air_resistance_neglected: bool

    def __post_init__(self) -> None:
        if any(
            value is not True
            for value in (self.inertial_frame, self.constant_mass, self.air_resistance_neglected)
        ):
            raise ValueError(
                "M4 requires inertial, constant-mass, air-resistance-neglected assumptions"
            )


@dataclass(frozen=True, slots=True)
class Surface:
    """Upper face of a plane, tilted from physical right in signed degrees.

    Positive inclination rises to the right; negative rises to the left.
    Zero is horizontal. Vertical walls and overhangs are outside bounded M4 contact.
    """

    identifier: str
    owner: ForceSource
    inclination_degrees: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))
        require_type(self.owner, (BodyReference, EnvironmentReference), "surface owner")
        angle = finite(self.inclination_degrees, "inclination")
        if not -90 < angle < 90:
            raise ValueError("surface inclination must be between -90 and 90 degrees exclusively")
        object.__setattr__(self, "inclination_degrees", angle)


class FrictionRegime(StrEnum):
    NONE = "none"
    STATIC = "static"
    LIMITING_STATIC = "limiting-static"
    KINETIC = "kinetic"


@dataclass(frozen=True, slots=True)
class Friction:
    """The coefficient belongs to the selected regime, never an inferred force."""

    regime: FrictionRegime
    coefficient: FrictionCoefficient | UnknownValue | None = None

    def __post_init__(self) -> None:
        require_type(self.regime, FrictionRegime, "friction regime")
        if self.regime is FrictionRegime.NONE:
            if self.coefficient is not None:
                raise ValueError("frictionless contact cannot declare a coefficient")
        else:
            require_type(
                self.coefficient, (FrictionCoefficient, UnknownValue), "friction coefficient"
            )


@dataclass(frozen=True, slots=True)
class Contact:
    identifier: str
    body_id: str
    surface_id: str
    friction: Friction

    def __post_init__(self) -> None:
        for name in ("identifier", "body_id", "surface_id"):
            object.__setattr__(self, name, identifier(getattr(self, name)))
        require_type(self.friction, Friction, "friction")


@dataclass(frozen=True, slots=True)
class StringConnection:
    """One light string joining two bodies; no pulley or string-network topology."""

    identifier: str
    body_ids: tuple[str, ...]
    source: EnvironmentReference
    negligible_mass: bool
    taut: bool
    inextensible: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))
        endpoints = identifiers(self.body_ids)
        if len(endpoints) != 2:
            raise ValueError("a string must have exactly two distinct body endpoints")
        object.__setattr__(self, "body_ids", endpoints)
        require_type(self.source, EnvironmentReference, "string source")
        if self.negligible_mass is not True:
            raise ValueError("M4 strings must explicitly have negligible mass")
        require_type(self.taut, bool, "taut")
        require_type(self.inextensible, bool, "inextensible")


@dataclass(frozen=True, slots=True)
class GravitationalInteraction:
    """Two masses and centre-to-centre separation; no gravitational constant/result."""

    identifier: str
    body_ids: tuple[str, ...]
    separation: Metres

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))
        endpoints = identifiers(self.body_ids)
        if len(endpoints) != 2:
            raise ValueError("gravitation must reference exactly two distinct bodies")
        object.__setattr__(self, "body_ids", endpoints)
        require_type(self.separation, Metres, "separation")


@dataclass(frozen=True, slots=True)
class GravitationalField:
    """Authored field acting on selected bodies; does not create weight forces."""

    source: ForceSource
    body_ids: tuple[str, ...]
    acceleration: AccelerationVector

    def __post_init__(self) -> None:
        require_type(self.source, (BodyReference, EnvironmentReference), "field source")
        object.__setattr__(self, "body_ids", identifiers(self.body_ids))
        require_type(self.acceleration, AccelerationVector, "field acceleration")


@dataclass(frozen=True, slots=True)
class AuthoredAcceleration:
    body_id: str
    vector: AccelerationVector

    def __post_init__(self) -> None:
        object.__setattr__(self, "body_id", identifier(self.body_id))
        require_type(self.vector, AccelerationVector, "acceleration vector")


@dataclass(frozen=True, slots=True)
class ThirdLawPair:
    """Structural partner membership only; numerical agreement is a solver concern."""

    force_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        members = identifiers(self.force_ids)
        if len(members) != 2:
            raise ValueError("a third-law pair must reference exactly two distinct forces")
        object.__setattr__(self, "force_ids", members)
