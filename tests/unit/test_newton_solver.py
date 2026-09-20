"""Independent analytical examples and physical-consistency regressions for #56."""

import ast
from dataclasses import FrozenInstanceError, asdict, replace
from itertools import permutations
from pathlib import Path

import pytest

from assessment_platform.domains.physical_sciences.mechanics import newton_solver as s
from assessment_platform.domains.physical_sciences.mechanics import newtons_laws as n

X = n.CartesianCoordinates((n.CartesianDirection.RIGHT,))
XY = n.CartesianCoordinates((n.CartesianDirection.RIGHT, n.CartesianDirection.UP))
ENV = n.EnvironmentReference("environment")
EARTH = n.EnvironmentReference("earth")
CORD = n.EnvironmentReference("cord")
U = n.UnknownValue.UNKNOWN


def vector(values, basis=X):
    return n.ForceVector(basis, tuple(n.Newtons(v) if v is not U else U for v in values))


def acceleration(values, basis=X):
    return n.AccelerationVector(basis, tuple(n.MetresPerSecondSquared(v) for v in values))


def force(key, parts, kind=n.ForceKind.APPLIED, body="a", source=ENV, relation=None, basis=X):
    return n.Force(key, kind, body, source, vector(parts, basis), relation)


def scenario(parts=((12,), (-4,)), mass=4, given=None, basis=X, **overrides):
    values = dict(
        identifier="example",
        bodies=(n.NewtonBody("a", n.Kilograms(mass)),),
        coordinates=basis,
        system=n.SystemBoundary(("a",)),
        assumptions=n.NewtonAssumptions(True, True, True),
        environment=(ENV, EARTH, CORD),
        forces=overrides["forces"]
        if "forces" in overrides
        else tuple(force(f"f{i}", row, basis=basis) for i, row in enumerate(parts)),
        accelerations=()
        if given is None
        else (n.AuthoredAcceleration("a", acceleration(given, basis)),),
    )
    values.update(overrides)
    return n.NewtonScenario(**values)


def components(vector):
    return tuple(v.value for v in vector.components)


def failure(reason):
    return pytest.raises(s.NewtonSolveError, match=".")


@pytest.mark.parametrize(
    "parts, expected",
    [
        (((7,),), (7,)),
        (((2,), (5,)), (7,)),
        (((12,), (-4,)), (8,)),
        (((4,), (-4,)), (0,)),
        (((-4,), (-3,)), (-7,)),
    ],
)
def test_analytical_signed_resultants(parts, expected):
    result = s.NewtonSolver(scenario(parts)).resultant_force("a")
    assert components(result.vector) == expected
    assert result.body_ids == ("a",)


@pytest.mark.parametrize(
    "parts, expected", [(((12,), (-4,)), 2), (((-12,), (4,)), -2), (((4,), (-4,)), 0)]
)
def test_newton_ii_known_forces_and_equilibrium(parts, expected):
    solver = s.NewtonSolver(scenario(parts))
    result = solver.body_dynamics("a")
    assert components(result.acceleration) == (expected,)
    assert result.equilibrium is (expected == 0)
    assert solver.validate_dynamics(result).valid


@pytest.mark.parametrize(
    "basis", [XY, n.CartesianCoordinates((n.CartesianDirection.LEFT, n.CartesianDirection.DOWN))]
)
def test_two_dimensional_components_are_not_world_directions(basis):
    result = s.NewtonSolver(scenario(((12, -6), (-4, 2)), basis=basis)).body_dynamics("a")
    assert components(result.resultant) == (8, -4)
    assert components(result.acceleration) == (2, -1)
    assert result.acceleration.coordinates == basis


@pytest.mark.parametrize("given", [(2,), (2 + 5e-10,)])
def test_authored_acceleration_is_validated_with_absolute_tolerance(given):
    result = s.NewtonSolver(scenario(given=given)).body_dynamics("a")
    assert components(result.acceleration) == (2,)


def test_inconsistent_acceleration_is_rejected_without_changing_input():
    model = scenario(given=(3,))
    before = asdict(model)
    with failure(s.FailureReason.INCONSISTENT) as caught:
        s.NewtonSolver(model).body_dynamics("a")
    assert caught.value.reason is s.FailureReason.INCONSISTENT
    assert asdict(model) == before


@pytest.mark.parametrize("known, expected", [(10, -4), (2, 4), (6, 0)])
def test_unique_unknown_force_and_independent_recomposition(known, expected):
    model = scenario(((known,), (U,)), mass=2, given=(3,))
    solver = s.NewtonSolver(model)
    result = solver.solve_force("f1")
    assert components(result.vector) == (expected,)
    assert known + result.vector.components[0].value == pytest.approx(2 * 3, abs=1e-9)
    assert components(solver.required_resultant("a").vector) == (6,)
    assert model.forces[1].vector.components == (U,)


def test_two_axes_solve_different_unknowns_independently():
    model = scenario(((U, 2), (3, U)), mass=2, given=(4, -1), basis=XY)
    result = s.NewtonSolver(model).body_dynamics("a")
    assert components(result.forces[0].vector) == (5, 2)
    assert components(result.forces[1].vector) == (3, -4)
    assert components(result.acceleration) == (4, -1)


@pytest.mark.parametrize(
    "given, parts, axes",
    [
        (None, ((U, 0), (1, 0)), (0,)),
        ((0, 0), ((U, 0), (U, 0)), (0,)),
        ((0, 0), ((U, U), (1, U)), (1,)),
    ],
)
def test_underdetermined_axes_are_explicit_and_no_partial_body_is_returned(given, parts, axes):
    model = scenario(parts, given=given, basis=XY)
    with failure(s.FailureReason.UNDERDETERMINED) as caught:
        s.NewtonSolver(model).body_dynamics("a")
    assert caught.value.reason is s.FailureReason.UNDERDETERMINED
    assert caught.value.axes == axes


def test_unknown_resultant_and_absent_acceleration_are_not_zero():
    solver = s.NewtonSolver(scenario(((U,),)))
    for operation in (solver.resultant_force, solver.required_resultant, solver.body_dynamics):
        with failure(s.FailureReason.UNDERDETERMINED) as caught:
            operation("a")
        assert caught.value.reason is s.FailureReason.UNDERDETERMINED
    with pytest.raises(s.NewtonSolveError, match="inventory"):
        s.NewtonSolver(scenario(parts=())).body_dynamics("a")


def pair_scenario(second=-5, first=5, selected=("a",)):
    return scenario(
        bodies=(n.NewtonBody("a", n.Kilograms(2)), n.NewtonBody("b", n.Kilograms(3))),
        system=n.SystemBoundary(selected),
        forces=(
            force("b-on-a", (first,), source=n.BodyReference("b")),
            force("a-on-b", (second,), body="b", source=n.BodyReference("a")),
            force("environment", (2,), body="b"),
        ),
        third_law_pairs=(n.ThirdLawPair(("b-on-a", "a-on-b")),),
    )


@pytest.mark.parametrize(
    "second, valid", [(-5, True), (-4, False), (5, False), (-5 + 5e-10, True), (-5 + 2e-9, False)]
)
def test_third_law_numeric_validation_and_fbd_separation(second, valid):
    model = pair_scenario(second)
    solver = s.NewtonSolver(model)
    assert solver.validate_third_law(model.third_law_pairs[0]).valid is valid
    assert components(solver.resultant_force("a").vector) == (5,)
    assert components(solver.resultant_force("b").vector) == (second + 2,)
    assert solver.resultant_force("a").force_ids == ("b-on-a",)


def test_third_law_unknown_is_not_numerically_validated():
    model = pair_scenario(U)
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(model).validate_third_law(model.third_law_pairs[0])
    assert caught.value.reason is s.FailureReason.UNDERDETERMINED


@pytest.mark.parametrize(
    "selected, expected, ids",
    [
        (("a",), 5, ("b-on-a",)),
        (("b",), -3, ("a-on-b", "environment")),
        (("a", "b"), 2, ("environment",)),
    ],
)
def test_system_external_sum_classifies_sources_by_membership(selected, expected, ids):
    model = pair_scenario(selected=selected)
    result = s.NewtonSolver(model).external_resultant()
    assert components(result.vector) == (expected,)
    assert result.force_ids == ids


def test_pure_internal_system_has_zero_external_resultant_without_pair_deletion():
    model = replace(pair_scenario(selected=("a", "b")), forces=pair_scenario().forces[:2])
    result = s.NewtonSolver(model).external_resultant()
    assert components(result.vector) == (0,)
    assert result.force_ids == ()


@pytest.mark.parametrize("field, expected", [((-9.8,), (-19.6,)), ((0,), (0,)), ((3, -4), (6, -8))])
def test_weight_uses_only_authored_field_components(field, expected):
    basis = X if len(field) == 1 else XY
    model = scenario(
        mass=2,
        basis=basis,
        parts=(),
        gravitational_fields=(n.GravitationalField(EARTH, ("a",), acceleration(field, basis)),),
    )
    result = s.NewtonSolver(model).weight("a", EARTH)
    assert components(result.vector) == expected
    assert result.vector.coordinates == basis
    assert model.forces == ()


def test_weight_has_no_hidden_g_and_rejects_inconsistent_authored_weight():
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(scenario()).weight("a", EARTH)
    assert caught.value.reason is s.FailureReason.UNDERDETERMINED
    model = scenario(
        mass=2,
        forces=(force("w", (-20,), n.ForceKind.WEIGHT, source=EARTH),),
        gravitational_fields=(n.GravitationalField(EARTH, ("a",), acceleration((-9.8,))),),
    )
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(model).weight("a", EARTH)
    assert caught.value.reason is s.FailureReason.INCONSISTENT


def contact_case(
    push=4,
    friction=U,
    normal=U,
    coefficient=0.3,
    regime=n.FrictionRegime.STATIC,
    given=(0, 0),
    mass=2,
    field=(0, -10),
    applied_normal=0,
    basis=XY,
    angle=0,
):
    mu = U if coefficient is U else n.FrictionCoefficient(coefficient)
    forces = [
        force("weight", (U, U), n.ForceKind.WEIGHT, source=EARTH, basis=basis),
        force("normal", (0, normal), n.ForceKind.NORMAL, relation="contact", basis=basis),
        force("push", (push, applied_normal), basis=basis),
    ]
    if regime is not n.FrictionRegime.NONE:
        forces.append(
            force("friction", (friction, 0), n.ForceKind.FRICTION, relation="contact", basis=basis)
        )
    return scenario(
        mass=mass,
        given=given,
        basis=basis,
        forces=forces,
        surfaces=(n.Surface("plane", ENV, angle),),
        contacts=(
            n.Contact(
                "contact",
                "a",
                "plane",
                n.Friction(regime, None if regime is n.FrictionRegime.NONE else mu),
            ),
        ),
        gravitational_fields=(n.GravitationalField(EARTH, ("a",), acceleration(field, basis)),),
    )


@pytest.mark.parametrize("push, expected", [(4, -4), (0, 0), (6, -6), (-4, 4)])
def test_static_friction_is_required_balance_not_always_its_limit(push, expected):
    model = contact_case(push=push)
    result = s.NewtonSolver(model).contact_forces("contact")
    assert components(result.normal.vector) == (0, 20)
    assert components(result.friction.force.vector) == (expected, 0)
    assert result.friction.coefficient_normal_product.value == 6
    assert result.friction.magnitude.value == abs(expected)
    dynamics = s.NewtonSolver(model).body_dynamics("a")
    assert dynamics.equilibrium
    assert s.NewtonSolver(model).validate_dynamics(dynamics).valid


def test_excess_static_friction_rejected_without_switching_regime():
    model = contact_case(push=8)
    for operation in (
        lambda: s.NewtonSolver(model).contact_forces("contact"),
        lambda: s.NewtonSolver(model).body_dynamics("a"),
    ):
        with pytest.raises(s.NewtonSolveError, match="static friction exceeds") as caught:
            operation()
        assert caught.value.reason is s.FailureReason.INCONSISTENT
    assert model.contacts[0].friction.regime is n.FrictionRegime.STATIC


@pytest.mark.parametrize("regime", [n.FrictionRegime.KINETIC, n.FrictionRegime.LIMITING_STATIC])
@pytest.mark.parametrize("friction", [-30, 30, U])
def test_kinetic_and_limiting_friction_magnitude_without_inventing_sign(regime, friction):
    result = s.NewtonSolver(
        contact_case(regime=regime, friction=friction, normal=20, coefficient=1.5, given=None)
    ).contact_forces("contact")
    assert result.friction.magnitude.value == 30
    if friction is U:
        assert result.friction.force is None
    else:
        assert components(result.friction.force.vector) == (friction, 0)


@pytest.mark.parametrize(
    "regime", [n.FrictionRegime.STATIC, n.FrictionRegime.LIMITING_STATIC, n.FrictionRegime.KINETIC]
)
def test_unknown_coefficient_is_not_zero(regime):
    with pytest.raises(s.NewtonSolveError, match="coefficient is unknown") as caught:
        s.NewtonSolver(contact_case(coefficient=U, regime=regime)).contact_forces("contact")
    assert caught.value.reason is s.FailureReason.UNDERDETERMINED


@pytest.mark.parametrize("regime", [n.FrictionRegime.KINETIC, n.FrictionRegime.LIMITING_STATIC])
def test_wrong_friction_magnitude_rejected(regime):
    with pytest.raises(s.NewtonSolveError, match="friction magnitude"):
        s.NewtonSolver(
            contact_case(regime=regime, friction=-4, normal=20, given=None)
        ).contact_forces("contact")


@pytest.mark.parametrize(
    "ay, applied, expected, weightless",
    [
        (0, 0, 490, False),
        (2, 0, 590, False),
        (-2, 0, 390, False),
        (-9.8, 0, 0, True),
        (0, -10, 500, False),
        (0, 10, 480, False),
    ],
)
def test_apparent_weight_from_actual_normal_axis_balance(ay, applied, expected, weightless):
    model = contact_case(
        mass=50,
        field=(0, -9.8),
        given=(0, ay),
        push=0,
        applied_normal=applied,
        regime=n.FrictionRegime.NONE,
    )
    solver = s.NewtonSolver(model)
    result = solver.contact_forces("contact")
    assert result.apparent_weight.value == pytest.approx(expected, abs=1e-9)
    assert result.apparent_weightless is weightless
    assert components(solver.weight("a", EARTH).vector) == pytest.approx((0, -490), abs=1e-9)
    assert result.friction is None
    assert model.forces[1].vector.components[1] is U


def test_normal_force_cannot_be_derived_from_missing_acceleration():
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(contact_case(given=None)).contact_forces("contact")
    assert caught.value.reason is s.FailureReason.UNDERDETERMINED


def test_required_negative_support_rejected():
    with pytest.raises(s.NewtonSolveError, match="normal force cannot pull"):
        s.NewtonSolver(
            contact_case(given=(0, -11), push=0, regime=n.FrictionRegime.NONE)
        ).contact_forces("contact")


@pytest.mark.parametrize(
    "normal_direction, field, expected",
    [
        (n.SurfaceDirection.NORMAL_OUT, (-5, -8), 16),
        (n.SurfaceDirection.NORMAL_IN, (-5, 8), -16),
    ],
)
def test_incline_uses_already_resolved_field_without_transforming_again(
    normal_direction, field, expected
):
    basis = n.SurfaceCoordinates("plane", (n.SurfaceDirection.ALONG_LEFT, normal_direction))
    model = contact_case(basis=basis, angle=37, field=field, push=10)
    solver = s.NewtonSolver(model)
    result = solver.contact_forces("contact")
    assert components(result.normal.vector) == (0, expected)
    assert components(result.friction.force.vector) == (0, 0)
    assert result.normal.vector.coordinates == basis
    assert components(solver.weight("a", EARTH).vector) == tuple(2 * v for v in field)


def test_inclined_cartesian_contact_is_explicitly_unsupported():
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(contact_case(angle=30)).contact_forces("contact")
    assert caught.value.reason is s.FailureReason.UNSUPPORTED


@pytest.mark.parametrize(
    "kind, parts",
    [
        (n.ForceKind.NORMAL, (2, 20)),
        (n.ForceKind.FRICTION, (-4, 1)),
        (n.ForceKind.NORMAL, (0, -20)),
    ],
)
def test_invalid_contact_force_orientation(kind, parts):
    model = contact_case()
    forces = tuple(
        replace(f, vector=vector(parts, XY)) if f.kind is kind else f for f in model.forces
    )
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(replace(model, forces=forces)).contact_forces("contact")
    assert caught.value.reason is s.FailureReason.INCONSISTENT


def connected_case(first_external=10, second_external=0, **connection_overrides):
    connection = dict(
        identifier="string",
        body_ids=("a", "b"),
        source=CORD,
        negligible_mass=True,
        taut=True,
        inextensible=True,
    )
    connection.update(connection_overrides)
    return scenario(
        bodies=(n.NewtonBody("a", n.Kilograms(2)), n.NewtonBody("b", n.Kilograms(3))),
        strings=(n.StringConnection(**connection),),
        forces=(
            force("pull-a", (first_external,)),
            force("pull-b", (second_external,), body="b"),
            force("ta", (U,), n.ForceKind.TENSION, source=CORD, relation="string"),
            force("tb", (U,), n.ForceKind.TENSION, body="b", source=CORD, relation="string"),
        ),
    )


@pytest.mark.parametrize(
    "external, direction, expected_a, expected_t",
    [
        (10, s.ComponentSign.NEGATIVE, 2, 6),
        (-10, s.ComponentSign.POSITIVE, -2, 6),
        (0, s.ComponentSign.POSITIVE, 0, 0),
    ],
)
def test_analytical_connected_body_acceleration_and_tension(
    external, direction, expected_a, expected_t
):
    model = connected_case(external)
    before = asdict(model)
    request = s.StraightStringRequest("string", direction)
    result = s.NewtonSolver(model).connected_bodies(request)
    assert result.tension.value == expected_t
    assert [components(body.acceleration) for body in result.bodies] == [
        (expected_a,),
        (expected_a,),
    ]
    for body in result.bodies:
        mass = next(item.mass.value for item in model.bodies if item.identifier == body.body_id)
        assert sum(f.vector.components[0].value for f in body.forces) == pytest.approx(
            mass * expected_a
        )
    assert asdict(model) == before
    assert result == s.NewtonSolver(model).connected_bodies(request)


@pytest.mark.parametrize("overrides", [{"taut": False}, {"inextensible": False}])
def test_slack_and_extensible_string_constraints_unsupported(overrides):
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(connected_case(**overrides)).connected_bodies(
            s.StraightStringRequest("string", s.ComponentSign.NEGATIVE)
        )
    assert caught.value.reason is s.FailureReason.UNSUPPORTED


def test_connected_unknown_external_force_remains_underdetermined():
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(connected_case(U)).connected_bodies(
            s.StraightStringRequest("string", s.ComponentSign.NEGATIVE)
        )
    assert caught.value.reason is s.FailureReason.UNDERDETERMINED


def test_wrong_string_direction_does_not_become_compressive_tension():
    with pytest.raises(s.NewtonSolveError, match="compression") as caught:
        s.NewtonSolver(connected_case()).connected_bodies(
            s.StraightStringRequest("string", s.ComponentSign.POSITIVE)
        )
    assert caught.value.reason is s.FailureReason.INCONSISTENT


def test_authored_tension_and_acceleration_must_match_connected_solution():
    base = connected_case()
    altered = replace(
        base,
        forces=tuple(
            replace(f, vector=vector((-4,))) if f.identifier == "ta" else f for f in base.forces
        ),
    )
    accelerated = replace(base, accelerations=(n.AuthoredAcceleration("a", acceleration((3,))),))
    for model in (altered, accelerated):
        with pytest.raises(s.NewtonSolveError) as caught:
            s.NewtonSolver(model).connected_bodies(
                s.StraightStringRequest("string", s.ComponentSign.NEGATIVE)
            )
        assert caught.value.reason is s.FailureReason.INCONSISTENT


def gravity_case(masses=(2, 3), distance=4, order=("a", "b")):
    return scenario(
        bodies=(
            n.NewtonBody("a", n.Kilograms(masses[0])),
            n.NewtonBody("b", n.Kilograms(masses[1])),
        ),
        gravitation=(n.GravitationalInteraction("gravity", order, n.Metres(distance)),),
    )


def test_universal_gravitation_has_central_dbe_constant_and_no_invented_direction():
    model = gravity_case()
    result = s.NewtonSolver(model).gravitational_force("gravity")
    assert s.GRAVITATIONAL_CONSTANT == 6.67e-11
    assert result.magnitude.value == pytest.approx(2.50125e-11, rel=1e-14, abs=0)
    assert result.magnitude.value > 0
    assert not hasattr(result, "vector")
    assert result == s.NewtonSolver(gravity_case(order=("b", "a"))).gravitational_force("gravity")


@pytest.mark.parametrize("masses, distance", [((1e308, 1e308), 1e-100), ((1e-200, 1e-200), 1e100)])
def test_gravitational_overflow_and_underflow_are_not_solved_zero_or_infinity(masses, distance):
    with pytest.raises(s.NewtonSolveError) as caught:
        s.NewtonSolver(gravity_case(masses, distance)).gravitational_force("gravity")
    assert caught.value.reason is s.FailureReason.NUMERICAL_RANGE


def test_gravitational_authored_magnitude_validation_does_not_claim_direction():
    base = gravity_case(masses=(1e6, 2e6), distance=1)
    for component, valid in ((133.4, True), (-133.4, True), (130, False)):
        model = replace(
            base,
            forces=(
                force(
                    "g",
                    (component,),
                    n.ForceKind.GRAVITATIONAL,
                    source=n.BodyReference("b"),
                    relation="gravity",
                ),
            ),
        )
        assert s.NewtonSolver(model).validate_gravitational_force("g").valid is valid


def test_no_intermediate_rounding_and_force_order_invariance():
    model = scenario(((1,),), mass=3)
    assert s.NewtonSolver(model).body_dynamics("a").acceleration.components[0].value == 1 / 3
    for ordering in permutations(((1e16,), (1,), (-1e16,))):
        assert components(s.NewtonSolver(scenario(ordering)).resultant_force("a").vector) == (1,)


def test_independent_validator_rejects_tampered_outputs_and_invented_unknown_solutions():
    solver = s.NewtonSolver(scenario())
    result = solver.body_dynamics("a")
    for invalid in (
        replace(result, resultant=vector((9,))),
        replace(result, acceleration=acceleration((3,))),
        replace(result, equilibrium=True),
        replace(result, scenario_id="different"),
    ):
        assert not solver.validate_dynamics(invalid).valid
    uncertain = s.NewtonSolver(scenario(((U,), (U,)), given=(2,)))
    assert not uncertain.validate_dynamics(result).valid


def test_results_and_scenario_are_immutable_and_replayable():
    model = contact_case()
    before = asdict(model)
    solver = s.NewtonSolver(model)
    result = solver.body_dynamics("a")
    assert result == solver.body_dynamics("a")
    assert asdict(model) == before
    with pytest.raises(FrozenInstanceError):
        result.equilibrium = False
    with pytest.raises(FrozenInstanceError):
        solver.scenario = scenario()
    with pytest.raises(ValueError, match="unknowns"):
        s.ForceResult("s", "a", "f", vector((U,)))


def test_invalid_requests_fail_before_solving():
    solver = s.NewtonSolver(scenario())
    with pytest.raises(ValueError, match="unknown body"):
        solver.body_dynamics("missing")
    with pytest.raises(ValueError, match="unknown force"):
        solver.solve_force("missing")
    with pytest.raises(ValueError):
        s.StraightStringRequest("string", 1)
    with pytest.raises(ValueError):
        s.NewtonSolver(object())


def test_newton_solver_has_no_generation_rendering_api_or_question_dependencies():
    forbidden = {"random", "uuid", "datetime", "fastapi", "pydantic", "sympy"}
    for path in Path(s.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(alias.name.split(".")[0] in forbidden for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert not any(
                    part in forbidden | {"rendering", "api", "generation"}
                    for part in (node.module or "").split(".")
                )
