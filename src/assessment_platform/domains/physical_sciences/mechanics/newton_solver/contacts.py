"""Bounded contact orientation, force balance and Coulomb friction relationships."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import newtons_laws as n
from ._numerical import VALIDATION_TOLERANCE, checked, close, consistent
from .results import ContactResult, FailureReason, FrictionResult, NewtonSolveError

if TYPE_CHECKING:
    from .solver import Components, NewtonSolver


def _geometry(
    solver: NewtonSolver, contact_id: str
) -> tuple[n.Contact, int | None, int, int | None]:
    scenario = solver.scenario
    contact = next((item for item in scenario.contacts if item.identifier == contact_id), None)
    if contact is None:
        raise ValueError("unknown contact")
    surface = next(item for item in scenario.surfaces if item.identifier == contact.surface_id)
    basis = scenario.coordinates
    if isinstance(basis, n.SurfaceCoordinates):
        if basis.surface_id != surface.identifier:
            raise NewtonSolveError(
                FailureReason.UNSUPPORTED, "contact uses a different surface basis"
            )
        normal_axis = 1 if len(basis.axes) == 2 else None
        sign = (
            -1 if normal_axis is not None and basis.axes[1] is n.SurfaceDirection.NORMAL_IN else 1
        )
        return contact, normal_axis, sign, 0
    if surface.inclination_degrees != 0:
        raise NewtonSolveError(
            FailureReason.UNSUPPORTED, "inclined contact requires its own surface-aligned basis"
        )
    vertical = (n.CartesianDirection.UP, n.CartesianDirection.DOWN)
    normal_axis = next((i for i, direction in enumerate(basis.axes) if direction in vertical), None)
    tangent_axis = next(
        (i for i, direction in enumerate(basis.axes) if direction not in vertical), None
    )
    sign = (
        -1
        if normal_axis is not None and basis.axes[normal_axis] is n.CartesianDirection.DOWN
        else 1
    )
    return contact, normal_axis, sign, tangent_axis


def orient_components(
    solver: NewtonSolver, force: n.Force, parts: list[float | n.UnknownValue]
) -> list[float | n.UnknownValue]:
    if force.kind not in (n.ForceKind.NORMAL, n.ForceKind.FRICTION):
        return parts
    assert force.relationship_id is not None
    contact, normal_axis, normal_sign, tangent_axis = _geometry(solver, force.relationship_id)
    active_axis = normal_axis if force.kind is n.ForceKind.NORMAL else tangent_axis
    if active_axis is None:
        raise NewtonSolveError(FailureReason.UNSUPPORTED, "contact force axis is absent from basis")
    result = list(parts)
    for axis, value in enumerate(parts):
        if axis != active_axis:
            if isinstance(value, float):
                consistent(value, 0, "contact force has a forbidden perpendicular component")
            else:
                result[axis] = 0.0  # Derived from normal/tangent semantics, not an unknown default.
    value = result[active_axis]
    if force.kind is n.ForceKind.NORMAL and isinstance(value, float):
        if force.target_body_id != contact.body_id:
            normal_sign = -normal_sign
        if value * normal_sign < -VALIDATION_TOLERANCE:
            raise NewtonSolveError(
                FailureReason.INCONSISTENT, "normal force cannot pull into surface"
            )
    return result


def _friction(
    solver: NewtonSolver,
    contact: n.Contact,
    normal_magnitude: float,
    values: Components,
    tangent_axis: int | None,
) -> FrictionResult | None:
    regime = contact.friction.regime
    if regime is n.FrictionRegime.NONE:
        return None
    coefficient = contact.friction.coefficient
    if not isinstance(coefficient, n.FrictionCoefficient):
        raise NewtonSolveError(FailureReason.UNDERDETERMINED, "friction coefficient is unknown")
    bound = checked(coefficient.value * normal_magnitude)
    force = next(
        (
            force
            for force in solver.scenario.forces_on(contact.body_id)
            if force.kind is n.ForceKind.FRICTION and force.relationship_id == contact.identifier
        ),
        None,
    )
    if force is None:
        if regime is n.FrictionRegime.STATIC:
            raise NewtonSolveError(
                FailureReason.UNDERDETERMINED, "static friction was not declared"
            )
        return FrictionResult(regime, n.Newtons(bound), n.Newtons(bound), None)
    if tangent_axis is None:
        raise NewtonSolveError(FailureReason.UNSUPPORTED, "friction requires a tangential axis")
    component = values[force.identifier][tangent_axis]
    if isinstance(component, n.UnknownValue):
        if solver._given(contact.body_id) is not None:
            try:
                solver._balance_axis(contact.body_id, values, tangent_axis)
            except NewtonSolveError as error:
                if error.reason is not FailureReason.UNDERDETERMINED:
                    raise
            component = values[force.identifier][tangent_axis]
        if isinstance(component, n.UnknownValue):
            if bound == 0:
                component = 0.0
                values[force.identifier][tangent_axis] = component
            elif regime is n.FrictionRegime.STATIC:
                raise NewtonSolveError(
                    FailureReason.UNDERDETERMINED,
                    "static friction requires a determined tangential balance",
                )
            else:
                return FrictionResult(regime, n.Newtons(bound), n.Newtons(bound), None)
    magnitude = abs(component)
    if regime is n.FrictionRegime.STATIC:
        if magnitude > bound + VALIDATION_TOLERANCE:
            raise NewtonSolveError(FailureReason.INCONSISTENT, "static friction exceeds its limit")
    else:
        consistent(
            magnitude, bound, "friction magnitude disagrees with coefficient and normal force"
        )
    # If acceleration and every tangential force are known, check their balance too.
    if solver._given(contact.body_id) is not None and all(
        isinstance(parts[tangent_axis], float) for parts in values.values()
    ):
        solver._balance_axis(contact.body_id, values, tangent_axis)
    result = solver._force_result(force.identifier, values[force.identifier])
    return FrictionResult(regime, n.Newtons(magnitude), n.Newtons(bound), result)


def _contact_result(solver: NewtonSolver, contact_id: str, values: Components) -> ContactResult:
    contact, normal_axis, normal_sign, tangent_axis = _geometry(solver, contact_id)
    normal = next(
        (
            force
            for force in solver.scenario.forces_on(contact.body_id)
            if force.kind is n.ForceKind.NORMAL and force.relationship_id == contact_id
        ),
        None,
    )
    if normal is None:
        raise NewtonSolveError(FailureReason.UNDERDETERMINED, "normal force was not declared")
    if normal_axis is None:
        raise NewtonSolveError(FailureReason.UNSUPPORTED, "normal axis is absent")
    solver._balance_axis(contact.body_id, values, normal_axis)
    values[normal.identifier] = orient_components(solver, normal, values[normal.identifier])
    signed_normal = solver._known(values[normal.identifier][normal_axis], normal_axis)
    magnitude = abs(signed_normal * normal_sign)
    friction = _friction(solver, contact, magnitude, values, tangent_axis)
    return ContactResult(
        solver.scenario.identifier,
        contact_id,
        contact.body_id,
        solver._force_result(normal.identifier, values[normal.identifier]),
        friction,
        n.Newtons(magnitude),
        close(magnitude, 0),
    )


def solve_contact(solver: NewtonSolver, contact_id: str) -> ContactResult:
    contact, _, _, _ = _geometry(solver, contact_id)
    return _contact_result(solver, contact_id, solver._values(contact.body_id))


def validate_body_contacts(solver: NewtonSolver, body_id: str, values: Components) -> None:
    for force_id, parts in values.items():
        orient_components(solver, solver._force(force_id), parts)
    for contact in solver.scenario.contacts:
        if contact.body_id == body_id:
            _contact_result(solver, contact.identifier, values)
