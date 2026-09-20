"""Structurally valid authored Newton problems, including underdetermined ones."""

from dataclasses import dataclass
from enum import StrEnum

from .coordinates import (
    CartesianCoordinates,
    Coordinates,
    ForceVector,
    SurfaceCoordinates,
)
from .interactions import (
    AuthoredAcceleration,
    BodyReference,
    Contact,
    EnvironmentReference,
    ForceSource,
    FrictionRegime,
    GravitationalField,
    GravitationalInteraction,
    NewtonAssumptions,
    NewtonBody,
    StringConnection,
    Surface,
    SystemBoundary,
    ThirdLawPair,
)
from .values import identifier, require_type, typed_tuple


class ForceKind(StrEnum):
    WEIGHT = "weight"
    NORMAL = "normal"
    FRICTION = "friction"
    APPLIED = "applied"
    TENSION = "tension"
    GRAVITATIONAL = "gravitational"


@dataclass(frozen=True, slots=True)
class Force:
    """A force exerted by source on target, in an explicit basis.

    relationship_id names a contact for normal/friction, a string for tension,
    or a gravitational interaction for universal gravitation. Kind determines
    the reference namespace. Applied and weight forces use their source directly.
    """

    identifier: str
    kind: ForceKind
    target_body_id: str
    source: ForceSource
    vector: ForceVector
    relationship_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))
        object.__setattr__(self, "target_body_id", identifier(self.target_body_id))
        require_type(self.kind, ForceKind, "force kind")
        require_type(self.source, (BodyReference, EnvironmentReference), "force source")
        require_type(self.vector, ForceVector, "force vector")
        if self.source == BodyReference(self.target_body_id):
            raise ValueError("a body cannot exert a force on itself")
        if self.kind in (ForceKind.APPLIED, ForceKind.WEIGHT):
            if self.relationship_id is not None:
                raise ValueError("applied/weight force uses its source without a relationship")
        else:
            if self.relationship_id is None:
                raise ValueError("this force kind requires a relationship identifier")
            object.__setattr__(self, "relationship_id", identifier(self.relationship_id))


@dataclass(frozen=True, slots=True)
class NewtonScenario:
    """One or two bodies with explicit facts, never inferred forces or acceleration.

    Ordered inputs are copied to tuples. Author order is preserved for display
    and deterministic serialization; sets and dictionaries are not accepted.
    """

    identifier: str
    bodies: tuple[NewtonBody, ...]
    coordinates: Coordinates
    system: SystemBoundary
    assumptions: NewtonAssumptions
    environment: tuple[EnvironmentReference, ...] = ()
    forces: tuple[Force, ...] = ()
    surfaces: tuple[Surface, ...] = ()
    contacts: tuple[Contact, ...] = ()
    strings: tuple[StringConnection, ...] = ()
    gravitation: tuple[GravitationalInteraction, ...] = ()
    gravitational_fields: tuple[GravitationalField, ...] = ()
    accelerations: tuple[AuthoredAcceleration, ...] = ()
    third_law_pairs: tuple[ThirdLawPair, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier))
        require_type(self.coordinates, (CartesianCoordinates, SurfaceCoordinates), "coordinates")
        require_type(self.system, SystemBoundary, "system")
        require_type(self.assumptions, NewtonAssumptions, "assumptions")
        for name, domain_type in (
            ("bodies", NewtonBody),
            ("environment", EnvironmentReference),
            ("forces", Force),
            ("surfaces", Surface),
            ("contacts", Contact),
            ("strings", StringConnection),
            ("gravitation", GravitationalInteraction),
            ("gravitational_fields", GravitationalField),
            ("accelerations", AuthoredAcceleration),
            ("third_law_pairs", ThirdLawPair),
        ):
            values = typed_tuple(getattr(self, name), domain_type, name)
            object.__setattr__(self, name, values)
            if name in (
                "bodies",
                "environment",
                "forces",
                "surfaces",
                "contacts",
                "strings",
                "gravitation",
            ):
                ids = tuple(item.identifier for item in values)
                if len(ids) != len(set(ids)):
                    raise ValueError(f"{name} identifiers must be unique")
        if len(self.bodies) not in (1, 2):
            raise ValueError("M4 scenarios contain one or two bodies")
        if len(self.strings) > 1:
            raise ValueError("M4 supports a single bounded string, not string networks")
        self._validate_references()
        self._validate_forces()
        self._validate_pairs()

    def _body(self, body_id: str) -> None:
        if body_id not in tuple(body.identifier for body in self.bodies):
            raise ValueError(f"unknown body reference: {body_id}")

    def _source(self, source: ForceSource) -> None:
        if isinstance(source, BodyReference):
            self._body(source.identifier)
        elif source not in self.environment:
            raise ValueError(f"unknown environment reference: {source.identifier}")

    def _basis(self, coordinates: Coordinates) -> None:
        if coordinates != self.coordinates:
            raise ValueError("authored vectors must use the scenario coordinate basis")

    def _validate_references(self) -> None:
        for body_id in self.system.body_ids:
            self._body(body_id)
        surfaces = {surface.identifier: surface for surface in self.surfaces}
        if (
            isinstance(self.coordinates, SurfaceCoordinates)
            and self.coordinates.surface_id not in surfaces
        ):
            raise ValueError("coordinate basis references an unknown surface")
        for surface in self.surfaces:
            self._source(surface.owner)
        contact_membership: set[tuple[str, str]] = set()
        for contact in self.contacts:
            self._body(contact.body_id)
            if contact.surface_id not in surfaces:
                raise ValueError("contact references an unknown surface")
            if surfaces[contact.surface_id].owner == BodyReference(contact.body_id):
                raise ValueError("a body cannot contact its own surface")
            key = (contact.body_id, contact.surface_id)
            if key in contact_membership:
                raise ValueError("body/surface contact must be unique, with one friction regime")
            contact_membership.add(key)
        for string in self.strings:
            self._source(string.source)
            for body_id in string.body_ids:
                self._body(body_id)
        gravity_membership: set[frozenset[str]] = set()
        for interaction in self.gravitation:
            for body_id in interaction.body_ids:
                self._body(body_id)
            pair = frozenset(interaction.body_ids)
            if pair in gravity_membership:
                raise ValueError("a gravitational body pair must be unique")
            gravity_membership.add(pair)
        field_membership: set[tuple[ForceSource, str]] = set()
        for field in self.gravitational_fields:
            self._source(field.source)
            self._basis(field.acceleration.coordinates)
            for body_id in field.body_ids:
                self._body(body_id)
                if field.source == BodyReference(body_id):
                    raise ValueError("a body cannot supply its own gravitational field")
                field_key = (field.source, body_id)
                if field_key in field_membership:
                    raise ValueError("field source/target membership must be unique")
                field_membership.add(field_key)
        accelerated: set[str] = set()
        for acceleration in self.accelerations:
            self._body(acceleration.body_id)
            self._basis(acceleration.vector.coordinates)
            if acceleration.body_id in accelerated:
                raise ValueError("authored acceleration must be unique per body")
            accelerated.add(acceleration.body_id)

    def _validate_forces(self) -> None:
        contacts = {contact.identifier: contact for contact in self.contacts}
        surfaces = {surface.identifier: surface for surface in self.surfaces}
        strings = {string.identifier: string for string in self.strings}
        gravity = {interaction.identifier: interaction for interaction in self.gravitation}
        memberships: set[tuple[ForceKind, str, str]] = set()
        for force in self.forces:
            self._body(force.target_body_id)
            self._source(force.source)
            self._basis(force.vector.coordinates)
            relation = force.relationship_id
            if relation is None:
                continue
            key = (force.kind, relation, force.target_body_id)
            if key in memberships:
                raise ValueError("force kind/relationship/target membership must be unique")
            memberships.add(key)
            if force.kind in (ForceKind.NORMAL, ForceKind.FRICTION):
                if relation not in contacts:
                    raise ValueError("force references an unknown contact")
                contact = contacts[relation]
                owner = surfaces[contact.surface_id].owner
                forward = force.target_body_id == contact.body_id and force.source == owner
                reverse = owner == BodyReference(
                    force.target_body_id
                ) and force.source == BodyReference(contact.body_id)
                if not (forward or reverse):
                    raise ValueError("contact force ownership must match the contact participants")
                if (
                    force.kind is ForceKind.FRICTION
                    and contact.friction.regime is FrictionRegime.NONE
                ):
                    raise ValueError("friction force contradicts frictionless contact")
            elif force.kind is ForceKind.TENSION:
                if relation not in strings:
                    raise ValueError("force references an unknown string")
                string = strings[relation]
                if force.target_body_id not in string.body_ids or force.source != string.source:
                    raise ValueError("tension ownership must match its string and endpoint")
            elif force.kind is ForceKind.GRAVITATIONAL:
                if relation not in gravity:
                    raise ValueError("force references an unknown gravitational interaction")
                interaction = gravity[relation]
                if (
                    not isinstance(force.source, BodyReference)
                    or force.source.identifier not in interaction.body_ids
                    or force.target_body_id not in interaction.body_ids
                ):
                    raise ValueError("gravitational force ownership must match its body pair")

    def _validate_pairs(self) -> None:
        forces = {force.identifier: force for force in self.forces}
        paired: set[str] = set()
        for pair in self.third_law_pairs:
            if any(force_id not in forces for force_id in pair.force_ids):
                raise ValueError("third-law pair references an unknown force")
            if paired.intersection(pair.force_ids):
                raise ValueError("a force can belong to only one third-law pair")
            first, second = (forces[force_id] for force_id in pair.force_ids)
            if (
                first.target_body_id == second.target_body_id
                or first.source != BodyReference(second.target_body_id)
                or second.source != BodyReference(first.target_body_id)
                or first.kind is not second.kind
                or first.relationship_id != second.relationship_id
            ):
                raise ValueError(
                    "third-law partners must reverse ownership of the same interaction"
                )
            paired.update(pair.force_ids)

    def forces_on(self, body_id: str) -> tuple[Force, ...]:
        """Semantic free-body selection; never includes a force on another body."""
        self._body(body_id)
        return tuple(force for force in self.forces if force.target_body_id == body_id)
