"""Explicit authoritative Newton operations; never writes authored scenario state."""

from dataclasses import dataclass
from math import hypot

from assessment_platform.core import ValidationResult

from .. import newtons_laws as n
from ..newtons_laws.values import require_type
from ._numerical import GRAVITATIONAL_CONSTANT, checked, close, consistent, total
from .results import (
    BodyDynamicsResult,
    ConnectedBodiesResult,
    ContactResult,
    FailureReason,
    ForceResult,
    GravitationalResult,
    NewtonSolveError,
    ResultantResult,
    StraightStringRequest,
    WeightResult,
)

type Components = dict[str, list[float | n.UnknownValue]]


@dataclass(frozen=True, slots=True)
class NewtonSolver:
    scenario: n.NewtonScenario

    def __post_init__(self) -> None:
        require_type(self.scenario, n.NewtonScenario, "scenario")

    def _body(self, body_id: str) -> n.NewtonBody:
        for body in self.scenario.bodies:
            if body.identifier == body_id:
                return body
        raise ValueError(f"unknown body: {body_id}")

    def _force(self, force_id: str) -> n.Force:
        for force in self.scenario.forces:
            if force.identifier == force_id:
                return force
        raise ValueError(f"unknown force: {force_id}")

    def _given(self, body_id: str) -> n.AccelerationVector | None:
        return next(
            (item.vector for item in self.scenario.accelerations if item.body_id == body_id), None
        )

    def _vector(self, values: tuple[float, ...]) -> n.ForceVector:
        return n.ForceVector(
            self.scenario.coordinates, tuple(n.Newtons(checked(v)) for v in values)
        )

    @staticmethod
    def _known(value: float | n.UnknownValue, axis: int) -> float:
        if isinstance(value, n.UnknownValue):
            raise NewtonSolveError(
                FailureReason.UNDERDETERMINED, f"unresolved force component on axis {axis}", (axis,)
            )
        return value

    def weight(self, body_id: str, source: n.ForceSource) -> WeightResult:
        body = self._body(body_id)
        require_type(source, (n.BodyReference, n.EnvironmentReference), "field source")
        field = next(
            (
                field
                for field in self.scenario.gravitational_fields
                if field.source == source and body_id in field.body_ids
            ),
            None,
        )
        if field is None:
            raise NewtonSolveError(FailureReason.UNDERDETERMINED, "no authored gravitational field")
        values = tuple(
            checked(body.mass.value * component.value)
            for component in field.acceleration.components
        )
        for force in self.scenario.forces_on(body_id):
            if force.kind is n.ForceKind.WEIGHT and force.source == source:
                for authored, expected in zip(force.vector.components, values, strict=True):
                    if isinstance(authored, n.Newtons):
                        consistent(authored.value, expected, "authored weight disagrees with field")
        return WeightResult(self.scenario.identifier, body_id, source, self._vector(values))

    def _values(self, body_id: str) -> Components:
        """Resolve only explicit field/contact direction constraints into temporary data."""
        from .contacts import orient_components

        self._body(body_id)
        forces = self.scenario.forces_on(body_id)
        if not forces:
            raise NewtonSolveError(FailureReason.UNDERDETERMINED, "no authored force inventory")
        values: Components = {}
        for force in forces:
            parts: list[float | n.UnknownValue] = [
                part.value if isinstance(part, n.Newtons) else part
                for part in force.vector.components
            ]
            if force.kind is n.ForceKind.WEIGHT and any(
                field.source == force.source and body_id in field.body_ids
                for field in self.scenario.gravitational_fields
            ):
                derived = self.weight(body_id, force.source)
                parts = [
                    part.value for part in derived.vector.components if isinstance(part, n.Newtons)
                ]
            values[force.identifier] = orient_components(self, force, parts)
        return values

    def _balance_axis(self, body_id: str, values: Components, axis: int) -> None:
        given = self._given(body_id)
        unknown = [key for key, parts in values.items() if isinstance(parts[axis], n.UnknownValue)]
        if unknown and (given is None or len(unknown) != 1):
            raise NewtonSolveError(
                FailureReason.UNDERDETERMINED,
                f"axis {axis} has insufficient independent constraints",
                (axis,),
            )
        known_total = total(
            tuple(
                value
                for parts in values.values()
                for value in (parts[axis],)
                if isinstance(value, float)
            )
        )
        if given is not None:
            mass = self._body(body_id).mass.value
            if unknown:
                required = checked(mass * given.components[axis].value)
                values[unknown[0]][axis] = checked(required - known_total)
            else:
                consistent(
                    checked(known_total / mass),
                    given.components[axis].value,
                    f"authored acceleration disagrees with forces on axis {axis}",
                )

    def _force_result(self, force_id: str, parts: list[float | n.UnknownValue]) -> ForceResult:
        force = self._force(force_id)
        return ForceResult(
            self.scenario.identifier,
            force.target_body_id,
            force_id,
            self._vector(tuple(self._known(v, i) for i, v in enumerate(parts))),
        )

    def resultant_force(self, body_id: str) -> ResultantResult:
        """Acting-force sum only; does not infer unknowns from acceleration."""
        values = self._values(body_id)
        result = tuple(
            total(tuple(self._known(parts[i], i) for parts in values.values()))
            for i in range(len(self.scenario.coordinates.axes))
        )
        return ResultantResult(
            self.scenario.identifier, (body_id,), tuple(values), self._vector(result)
        )

    def required_resultant(self, body_id: str) -> ResultantResult:
        """The force required by given acceleration, not a validation of acting forces."""
        body = self._body(body_id)
        given = self._given(body_id)
        if given is None:
            raise NewtonSolveError(FailureReason.UNDERDETERMINED, "acceleration was not authored")
        return ResultantResult(
            self.scenario.identifier,
            (body_id,),
            (),
            self._vector(
                tuple(checked(body.mass.value * component.value) for component in given.components)
            ),
        )

    def _dynamics_result(self, body_id: str, values: Components) -> BodyDynamicsResult:
        mass = self._body(body_id).mass.value
        resultant = tuple(
            total(tuple(self._known(parts[i], i) for parts in values.values()))
            for i in range(len(self.scenario.coordinates.axes))
        )
        acceleration = n.AccelerationVector(
            self.scenario.coordinates,
            tuple(n.MetresPerSecondSquared(checked(component / mass)) for component in resultant),
        )
        given = self._given(body_id)
        if given is not None:
            for actual, authored in zip(acceleration.components, given.components, strict=True):
                consistent(actual.value, authored.value, "authored acceleration is inconsistent")
        return BodyDynamicsResult(
            self.scenario.identifier,
            body_id,
            tuple(self._force_result(key, parts) for key, parts in values.items()),
            self._vector(resultant),
            acceleration,
            all(close(value, 0) for value in resultant),
        )

    def body_dynamics(self, body_id: str) -> BodyDynamicsResult:
        """Resolve at most one independent unknown per axis; return no partial body result."""
        values = self._values(body_id)
        unresolved: list[int] = []
        for axis in range(len(self.scenario.coordinates.axes)):
            try:
                self._balance_axis(body_id, values, axis)
            except NewtonSolveError as error:
                if error.reason is not FailureReason.UNDERDETERMINED:
                    raise
                unresolved.append(axis)
        if unresolved:
            raise NewtonSolveError(
                FailureReason.UNDERDETERMINED, "body has unresolved axes", tuple(unresolved)
            )
        from .contacts import validate_body_contacts

        validate_body_contacts(self, body_id, values)
        return self._dynamics_result(body_id, values)

    def solve_force(self, force_id: str) -> ForceResult:
        force = self._force(force_id)
        result = self.body_dynamics(force.target_body_id)
        return next(item for item in result.forces if item.force_id == force_id)

    def external_resultant(self) -> ResultantResult:
        """Classify from membership, never by blindly deleting third-law pairs."""
        selected = self.scenario.system.body_ids
        components: Components = {}
        for body_id in selected:
            values = self._values(body_id)
            for force in self.scenario.forces_on(body_id):
                if (
                    isinstance(force.source, n.BodyReference)
                    and force.source.identifier in selected
                ):
                    continue
                components[force.identifier] = values[force.identifier]
        vector = self._vector(
            tuple(
                total(tuple(self._known(parts[i], i) for parts in components.values()))
                for i in range(len(self.scenario.coordinates.axes))
            )
        )
        return ResultantResult(self.scenario.identifier, selected, tuple(components), vector)

    def validate_third_law(self, pair: n.ThirdLawPair) -> ValidationResult:
        if pair not in self.scenario.third_law_pairs:
            raise ValueError("third-law pair must belong to this scenario")
        first, second = (self._force(force_id) for force_id in pair.force_ids)
        errors: list[str] = []
        for axis, (left, right) in enumerate(
            zip(first.vector.components, second.vector.components, strict=True)
        ):
            if not isinstance(left, n.Newtons) or not isinstance(right, n.Newtons):
                raise NewtonSolveError(
                    FailureReason.UNDERDETERMINED, "third-law components are unknown", (axis,)
                )
            if not close(left.value, -right.value):
                errors.append(f"third-law partners are not equal/opposite on axis {axis}")
        return ValidationResult(not errors, tuple(errors))

    def gravitational_force(self, interaction_id: str) -> GravitationalResult:
        interaction = next(
            (item for item in self.scenario.gravitation if item.identifier == interaction_id), None
        )
        if interaction is None:
            raise ValueError("unknown gravitational interaction")
        # Fixed mass order preserves exact replay when endpoints are swapped.
        first, second = sorted(self._body(body_id).mass.value for body_id in interaction.body_ids)
        distance = interaction.separation.value
        magnitude = checked((first / distance) * (second / distance) * GRAVITATIONAL_CONSTANT)
        if magnitude == 0:
            raise NewtonSolveError(
                FailureReason.NUMERICAL_RANGE, "gravitational magnitude underflow"
            )
        return GravitationalResult(self.scenario.identifier, interaction_id, n.Newtons(magnitude))

    def validate_gravitational_force(self, force_id: str) -> ValidationResult:
        force = self._force(force_id)
        if force.kind is not n.ForceKind.GRAVITATIONAL or force.relationship_id is None:
            raise ValueError("force must describe universal gravitation")
        values = tuple(
            self._known(v.value if isinstance(v, n.Newtons) else v, i)
            for i, v in enumerate(force.vector.components)
        )
        expected = self.gravitational_force(force.relationship_id).magnitude.value
        valid = close(checked(hypot(*values)), expected)
        # Separation supplies no line-of-centres direction: magnitude validation only.
        return ValidationResult(
            valid, () if valid else ("gravitational magnitude is inconsistent",)
        )

    def contact_forces(self, contact_id: str) -> ContactResult:
        from .contacts import solve_contact

        return solve_contact(self, contact_id)

    def connected_bodies(self, request: StraightStringRequest) -> ConnectedBodiesResult:
        from .connected import solve_connected

        return solve_connected(self, request)

    def validate_dynamics(self, result: BodyDynamicsResult) -> ValidationResult:
        """Independently recompose Newton II and compare result ownership/authored inputs."""
        if not isinstance(result, BodyDynamicsResult):
            return ValidationResult(False, ("result must be BodyDynamicsResult",))
        try:
            body = self._body(result.body_id)
            authored = self._values(result.body_id)
            for axis in range(len(self.scenario.coordinates.axes)):
                unknowns = sum(
                    isinstance(parts[axis], n.UnknownValue) for parts in authored.values()
                )
                if unknowns and (unknowns != 1 or self._given(result.body_id) is None):
                    return ValidationResult(False, ("claimed result is underdetermined",))
            if (
                result.scenario_id != self.scenario.identifier
                or result.resultant.coordinates != self.scenario.coordinates
                or tuple(item.force_id for item in result.forces) != tuple(authored)
            ):
                return ValidationResult(
                    False, ("result identity, basis or force inventory mismatch",)
                )
            values: Components = {}
            for force in result.forces:
                parts = [
                    self._known(v.value if isinstance(v, n.Newtons) else v, i)
                    for i, v in enumerate(force.vector.components)
                ]
                for given, actual in zip(authored[force.force_id], parts, strict=True):
                    if isinstance(given, float):
                        consistent(given, actual, "result overwrites an authored force component")
                values[force.force_id] = list(parts)
            for axis in range(len(self.scenario.coordinates.axes)):
                self._balance_axis(result.body_id, values, axis)
                net = total(tuple(self._known(parts[axis], axis) for parts in values.values()))
                component = result.resultant.components[axis]
                assert isinstance(component, n.Newtons)
                consistent(net, component.value, "resultant is not the acting-force sum")
                consistent(
                    net,
                    checked(body.mass.value * result.acceleration.components[axis].value),
                    "result violates Newton II",
                )
            expected_equilibrium = all(
                close(v.value, 0) for v in result.resultant.components if isinstance(v, n.Newtons)
            )
            if result.equilibrium != expected_equilibrium:
                return ValidationResult(False, ("equilibrium classification is inconsistent",))
            from .contacts import validate_body_contacts

            validate_body_contacts(self, result.body_id, values)
        except ValueError as error:
            return ValidationResult(False, (str(error),))
        return ValidationResult(True)
