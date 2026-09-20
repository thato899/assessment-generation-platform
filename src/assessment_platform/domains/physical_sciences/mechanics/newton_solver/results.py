"""Immutable derived Newton results and bounded solve requests."""

from dataclasses import dataclass
from enum import IntEnum, StrEnum

from .. import newtons_laws as n
from ..newtons_laws.values import identifier, identifiers, require_type, typed_tuple


class FailureReason(StrEnum):
    UNDERDETERMINED = "underdetermined"
    INCONSISTENT = "physically-inconsistent"
    UNSUPPORTED = "unsupported"
    NUMERICAL_RANGE = "numerical-range"


class NewtonSolveError(ValueError):
    """A valid domain does not guarantee a supported, consistent, unique answer."""

    def __init__(self, reason: FailureReason, message: str, axes: tuple[int, ...] = ()) -> None:
        super().__init__(message)
        self.reason = reason
        self.axes = axes


def _ids(value: object, *names: str) -> None:
    for name in names:
        object.__setattr__(value, name, identifier(getattr(value, name)))


def _known(vector: n.ForceVector) -> None:
    require_type(vector, n.ForceVector, "derived force vector")
    if any(not isinstance(item, n.Newtons) for item in vector.components):
        raise ValueError("derived force vectors cannot contain unknowns")


def _magnitude(value: n.Newtons) -> None:
    require_type(value, n.Newtons, "magnitude")
    if value.value < 0:
        raise ValueError("magnitude must be non-negative")


@dataclass(frozen=True, slots=True)
class ForceResult:
    scenario_id: str
    body_id: str
    force_id: str
    vector: n.ForceVector

    def __post_init__(self) -> None:
        _ids(self, "scenario_id", "body_id", "force_id")
        _known(self.vector)


@dataclass(frozen=True, slots=True)
class ResultantResult:
    scenario_id: str
    body_ids: tuple[str, ...]
    force_ids: tuple[str, ...]
    vector: n.ForceVector

    def __post_init__(self) -> None:
        _ids(self, "scenario_id")
        object.__setattr__(self, "body_ids", identifiers(self.body_ids))
        force_ids = typed_tuple(self.force_ids, str, "force identifiers")
        object.__setattr__(self, "force_ids", identifiers(force_ids) if force_ids else ())
        _known(self.vector)


@dataclass(frozen=True, slots=True)
class BodyDynamicsResult:
    scenario_id: str
    body_id: str
    forces: tuple[ForceResult, ...]
    resultant: n.ForceVector
    acceleration: n.AccelerationVector
    equilibrium: bool

    def __post_init__(self) -> None:
        _ids(self, "scenario_id", "body_id")
        forces = typed_tuple(self.forces, ForceResult, "derived forces")
        identifiers(tuple(force.force_id for force in forces))
        object.__setattr__(self, "forces", forces)
        _known(self.resultant)
        require_type(self.acceleration, n.AccelerationVector, "acceleration")
        require_type(self.equilibrium, bool, "equilibrium")
        if self.resultant.coordinates != self.acceleration.coordinates or any(
            force.body_id != self.body_id
            or force.vector.coordinates != self.resultant.coordinates
            for force in forces
        ):
            raise ValueError("derived body result ownership and bases must agree")


@dataclass(frozen=True, slots=True)
class WeightResult:
    scenario_id: str
    body_id: str
    source: n.ForceSource
    vector: n.ForceVector

    def __post_init__(self) -> None:
        _ids(self, "scenario_id", "body_id")
        require_type(self.source, (n.BodyReference, n.EnvironmentReference), "field source")
        _known(self.vector)


@dataclass(frozen=True, slots=True)
class GravitationalResult:
    scenario_id: str
    interaction_id: str
    magnitude: n.Newtons

    def __post_init__(self) -> None:
        _ids(self, "scenario_id", "interaction_id")
        _magnitude(self.magnitude)


@dataclass(frozen=True, slots=True)
class FrictionResult:
    regime: n.FrictionRegime
    magnitude: n.Newtons
    coefficient_normal_product: n.Newtons
    force: ForceResult | None

    def __post_init__(self) -> None:
        require_type(self.regime, n.FrictionRegime, "friction regime")
        _magnitude(self.magnitude)
        _magnitude(self.coefficient_normal_product)
        if self.force is not None:
            require_type(self.force, ForceResult, "friction force")


@dataclass(frozen=True, slots=True)
class ContactResult:
    scenario_id: str
    contact_id: str
    body_id: str
    normal: ForceResult
    friction: FrictionResult | None
    apparent_weight: n.Newtons
    apparent_weightless: bool

    def __post_init__(self) -> None:
        _ids(self, "scenario_id", "contact_id", "body_id")
        require_type(self.normal, ForceResult, "normal")
        _magnitude(self.apparent_weight)
        require_type(self.apparent_weightless, bool, "apparent weightlessness")
        if self.friction is not None:
            require_type(self.friction, FrictionResult, "friction")
        forces: tuple[ForceResult, ...] = (self.normal,)
        if self.friction is not None and self.friction.force is not None:
            forces += (self.friction.force,)
        if any(
            force.body_id != self.body_id
            or force.scenario_id != self.scenario_id
            or force.vector.coordinates != self.normal.vector.coordinates
            for force in forces
        ):
            raise ValueError("contact result ownership and bases must agree")


class ComponentSign(IntEnum):
    POSITIVE = 1
    NEGATIVE = -1


@dataclass(frozen=True, slots=True)
class StraightStringRequest:
    """Declare a straight string along the sole axis and its pull on the first endpoint.

    The endpoint order is StringConnection.body_ids. This is geometric input,
    required because the domain records no relative body positions or pulleys.
    """

    connection_id: str
    pull_on_first: ComponentSign

    def __post_init__(self) -> None:
        _ids(self, "connection_id")
        require_type(self.pull_on_first, ComponentSign, "string pull direction")


@dataclass(frozen=True, slots=True)
class ConnectedBodiesResult:
    scenario_id: str
    connection_id: str
    bodies: tuple[BodyDynamicsResult, ...]
    tension: n.Newtons

    def __post_init__(self) -> None:
        _ids(self, "scenario_id", "connection_id")
        bodies = typed_tuple(self.bodies, BodyDynamicsResult, "connected body results")
        if len(bodies) != 2 or bodies[0].body_id == bodies[1].body_id:
            raise ValueError("connected result must contain two distinct bodies")
        if any(body.scenario_id != self.scenario_id for body in bodies):
            raise ValueError("connected result scenario must match")
        if bodies[0].acceleration.coordinates != bodies[1].acceleration.coordinates:
            raise ValueError("connected result bases must match")
        object.__setattr__(self, "bodies", bodies)
        _magnitude(self.tension)
