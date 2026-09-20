"""One straight taut inextensible light string in one declared dimension."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import newtons_laws as n
from ..newtons_laws.values import require_type
from ._numerical import checked, consistent, total
from .contacts import validate_body_contacts
from .results import ConnectedBodiesResult, FailureReason, NewtonSolveError, StraightStringRequest

if TYPE_CHECKING:
    from .solver import NewtonSolver


def solve_connected(solver: NewtonSolver, request: StraightStringRequest) -> ConnectedBodiesResult:
    require_type(request, StraightStringRequest, "straight-string request")
    scenario = solver.scenario
    connection = next(
        (item for item in scenario.strings if item.identifier == request.connection_id), None
    )
    if connection is None:
        raise ValueError("unknown string connection")
    if (
        len(scenario.coordinates.axes) != 1
        or not connection.negligible_mass
        or not connection.taut
        or not connection.inextensible
    ):
        raise NewtonSolveError(
            FailureReason.UNSUPPORTED,
            "connected solving requires a straight 1D taut inextensible light string",
        )
    first_id, second_id = connection.body_ids
    first_values, second_values = solver._values(first_id), solver._values(second_id)
    tension_ids: list[str] = []
    external: list[float] = []
    for body_id, values in ((first_id, first_values), (second_id, second_values)):
        tension = [
            force
            for force in scenario.forces_on(body_id)
            if force.kind is n.ForceKind.TENSION and force.relationship_id == connection.identifier
        ]
        if len(tension) != 1:
            raise NewtonSolveError(
                FailureReason.UNDERDETERMINED, "one tension force must be declared at each endpoint"
            )
        tension_id = tension[0].identifier
        tension_ids.append(tension_id)
        external.append(
            total(
                tuple(
                    solver._known(parts[0], 0) for key, parts in values.items() if key != tension_id
                )
            )
        )
    mass_first, mass_second = solver._body(first_id).mass.value, solver._body(second_id).mass.value
    acceleration = checked(total(tuple(external)) / checked(mass_first + mass_second))
    signed_tension = checked(mass_first * acceleration - external[0])
    tension_magnitude = checked(signed_tension * request.pull_on_first.value)
    if tension_magnitude < 0:
        raise NewtonSolveError(
            FailureReason.INCONSISTENT,
            "the declared straight-string direction would require compression",
        )
    for values, force_id, expected in (
        (first_values, tension_ids[0], signed_tension),
        (second_values, tension_ids[1], -signed_tension),
    ):
        known = values[force_id][0]
        if isinstance(known, float):
            consistent(known, expected, "authored tension disagrees with connected-body balance")
        values[force_id][0] = expected
    for body_id, values in ((first_id, first_values), (second_id, second_values)):
        solver._balance_axis(body_id, values, 0)
        validate_body_contacts(solver, body_id, values)
    bodies = (
        solver._dynamics_result(first_id, first_values),
        solver._dynamics_result(second_id, second_values),
    )
    for body in bodies:
        consistent(
            body.acceleration.components[0].value,
            acceleration,
            "connected bodies must share acceleration in the straight-string case",
        )
    return ConnectedBodiesResult(
        scenario.identifier, connection.identifier, bodies, n.Newtons(tension_magnitude)
    )
