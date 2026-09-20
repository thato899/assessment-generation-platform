"""Structural Newton contracts, deliberately independent of numerical Newton laws."""

import ast
import dataclasses
from pathlib import Path

import pytest

from assessment_platform.domains.physical_sciences.mechanics import newtons_laws as n

AXES = n.CartesianCoordinates((n.CartesianDirection.RIGHT, n.CartesianDirection.UP))
EARTH = n.EnvironmentReference("earth")
FLOOR = n.EnvironmentReference("floor")
STRING = n.EnvironmentReference("cord")
UNKNOWN = n.UnknownValue.UNKNOWN


def body(identifier="a"):
    return n.NewtonBody(identifier, n.Kilograms(2))


def vector(x=1, y=0, coordinates=AXES):
    return n.ForceVector(coordinates, (n.Newtons(x), n.Newtons(y)))


def acceleration(x=0, y=0, coordinates=AXES):
    return n.AccelerationVector(
        coordinates, (n.MetresPerSecondSquared(x), n.MetresPerSecondSquared(y))
    )


def force(
    identifier="push",
    kind=n.ForceKind.APPLIED,
    target="a",
    source=FLOOR,
    relationship=None,
    components=None,
):
    return n.Force(identifier, kind, target, source, components or vector(), relationship)


def scenario(**overrides):
    values = dict(
        identifier="newton-example",
        bodies=(body(), body("b")),
        coordinates=AXES,
        system=n.SystemBoundary(("a",)),
        assumptions=n.NewtonAssumptions(True, True, True),
        environment=(EARTH, FLOOR, STRING),
    )
    values.update(overrides)
    return n.NewtonScenario(**values)


def contact_scenario(regime=n.FrictionRegime.STATIC, **overrides):
    values = dict(
        surfaces=(n.Surface("plane", FLOOR, 30),),
        contacts=(
            n.Contact(
                "touch",
                "a",
                "plane",
                n.Friction(
                    regime, None if regime is n.FrictionRegime.NONE else n.FrictionCoefficient(1.2)
                ),
            ),
        ),
    )
    values.update(overrides)
    return scenario(**values)


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("-inf"), float("nan"), True, "2"])
@pytest.mark.parametrize("unit", [n.Kilograms, n.Metres])
def test_positive_units_reject_invalid_values(unit, value):
    with pytest.raises(ValueError):
        unit(value)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan"), True, "2"])
@pytest.mark.parametrize("unit", [n.Newtons, n.MetresPerSecondSquared, n.FrictionCoefficient])
def test_finite_components_and_coefficients(unit, value):
    with pytest.raises(ValueError):
        unit(value)


@pytest.mark.parametrize("value", [-12, 0, 7.5])
def test_signed_force_and_acceleration_values(value):
    assert n.Newtons(value).value == value
    assert n.MetresPerSecondSquared(value).value == value


@pytest.mark.parametrize("value", [0, 0.4, 1.5])
def test_coefficient_has_no_artificial_upper_bound(value):
    assert n.FrictionCoefficient(value).value == value


def test_negative_coefficient_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        n.FrictionCoefficient(-0.1)


@pytest.mark.parametrize("identifier", ["", "  ", 7, None])
@pytest.mark.parametrize("factory", [body, n.BodyReference, n.EnvironmentReference])
def test_identifiers_are_explicit(factory, identifier):
    with pytest.raises(ValueError, match="identifier"):
        factory(identifier)


def test_body_has_positive_mass_stable_identity_and_no_results():
    assert body(" a ") == body()
    assert body().mass == n.Kilograms(2)
    assert [field.name for field in dataclasses.fields(body())] == ["identifier", "mass"]
    with pytest.raises(ValueError, match="mass"):
        n.NewtonBody("a", 2)


@pytest.mark.parametrize(
    "obj, field, value",
    [
        (body(), "mass", n.Kilograms(5)),
        (force(), "kind", n.ForceKind.WEIGHT),
        (scenario(), "forces", (force(),)),
        (vector(), "components", (n.Newtons(8),)),
    ],
)
def test_domain_is_frozen(obj, field, value):
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(obj, field, value)


@pytest.mark.parametrize(
    "axes",
    [
        (),
        (n.CartesianDirection.RIGHT, n.CartesianDirection.LEFT),
        (n.CartesianDirection.UP, n.CartesianDirection.DOWN),
        ("right",),
        (n.CartesianDirection.RIGHT,) * 3,
    ],
)
def test_malformed_cartesian_basis_rejected(axes):
    with pytest.raises(ValueError):
        n.CartesianCoordinates(axes)


@pytest.mark.parametrize("direction", list(n.CartesianDirection))
def test_one_dimensional_horizontal_and_vertical_bases(direction):
    coordinates = n.CartesianCoordinates((direction,))
    given = n.ForceVector(coordinates, (n.Newtons(-5),))
    model = scenario(coordinates=coordinates, forces=(force(components=given),))
    assert model.forces_on("a")[0].vector.coordinates.axes == (direction,)


def test_two_dimensional_basis_need_not_point_right_or_up():
    coordinates = n.CartesianCoordinates((n.CartesianDirection.LEFT, n.CartesianDirection.DOWN))
    model = scenario(
        coordinates=coordinates, forces=(force(components=vector(-3, 4, coordinates)),)
    )
    assert model.forces[0].vector.components == (n.Newtons(-3), n.Newtons(4))


@pytest.mark.parametrize(
    "axes",
    [
        (),
        (n.SurfaceDirection.NORMAL_OUT,),
        (n.SurfaceDirection.ALONG_RIGHT, n.SurfaceDirection.ALONG_LEFT),
        ("along-right",),
        (n.SurfaceDirection.ALONG_RIGHT,) * 3,
    ],
)
def test_malformed_surface_basis_rejected(axes):
    with pytest.raises(ValueError):
        n.SurfaceCoordinates("plane", axes)


@pytest.mark.parametrize("angle", [-45, 0, 30])
def test_horizontal_and_inclined_surface_facts_without_resolving_components(angle):
    coordinates = n.SurfaceCoordinates(
        "plane", (n.SurfaceDirection.ALONG_LEFT, n.SurfaceDirection.NORMAL_OUT)
    )
    given = n.ForceVector(coordinates, (UNKNOWN, UNKNOWN))
    model = contact_scenario(
        coordinates=coordinates,
        surfaces=(n.Surface("plane", FLOOR, angle),),
        forces=(force("weight", n.ForceKind.WEIGHT, source=EARTH, components=given),),
    )
    assert model.surfaces[0].inclination_degrees == angle
    assert model.forces[0].vector.components == (UNKNOWN, UNKNOWN)


@pytest.mark.parametrize("angle", [-90, 90, 180, float("nan"), float("inf"), True])
def test_invalid_surface_orientation(angle):
    with pytest.raises(ValueError):
        n.Surface("plane", FLOOR, angle)


@pytest.mark.parametrize(
    "constructor, components",
    [
        (n.ForceVector, (n.Newtons(2),)),
        (n.ForceVector, (2, 3)),
        (n.AccelerationVector, (n.MetresPerSecondSquared(1),)),
        (n.AccelerationVector, (n.Newtons(0), n.Newtons(0))),
    ],
)
def test_vector_dimensions_and_units_are_explicit(constructor, components):
    with pytest.raises(ValueError):
        constructor(AXES, components)


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"bodies": ()}, "one or two"),
        ({"bodies": (body(), body())}, "unique"),
        ({"bodies": (body(), body("b"), body("c"))}, "one or two"),
        ({"system": n.SystemBoundary(("missing",))}, "unknown body"),
        ({"forces": (force(), force())}, "unique"),
        ({"forces": (force(target="missing"),)}, "unknown body"),
        ({"forces": (force(source=n.BodyReference("missing")),)}, "unknown body"),
        ({"forces": (force(source=n.EnvironmentReference("missing")),)}, "unknown environment"),
        ({"environment": (EARTH, EARTH)}, "unique"),
        ({"assumptions": "inertial"}, "assumptions"),
        ({"coordinates": "right"}, "coordinates"),
    ],
)
def test_aggregate_references_and_uniqueness(overrides, message):
    with pytest.raises(ValueError, match=message):
        scenario(**overrides)


@pytest.mark.parametrize("members", [(), ("a", "a"), (" a ", "a")])
def test_system_membership_is_nonempty_and_unique(members):
    with pytest.raises(ValueError):
        n.SystemBoundary(members)


@pytest.mark.parametrize(
    "flags", [(False, True, True), (True, False, True), (True, True, False), (1, True, True)]
)
def test_unsupported_or_untyped_assumptions(flags):
    with pytest.raises(ValueError, match="assumptions"):
        n.NewtonAssumptions(*flags)


def test_selected_system_and_external_sources_are_distinct():
    given = force(source=n.BodyReference("b"))
    model = scenario(forces=(given,))
    assert model.system.body_ids == ("a",)
    assert given.source.identifier not in model.system.body_ids
    assert model.environment == (EARTH, FLOOR, STRING)
    assert not hasattr(given, "is_external")


@pytest.mark.parametrize(
    "overrides",
    [
        {"kind": "applied"},
        {"source": "earth"},
        {"source": n.BodyReference("a")},
        {"kind": n.ForceKind.NORMAL},
        {"relationship": "unrelated"},
    ],
)
def test_ambiguous_force_semantics_rejected(overrides):
    with pytest.raises(ValueError):
        force(**overrides)


@pytest.mark.parametrize("regime", list(n.FrictionRegime))
def test_contact_regimes_and_supported_force_kinds(regime):
    forces = [
        force("weight", n.ForceKind.WEIGHT, source=EARTH),
        force(),
        force("normal", n.ForceKind.NORMAL, relationship="touch"),
    ]
    if regime is not n.FrictionRegime.NONE:
        forces.append(force("friction", n.ForceKind.FRICTION, relationship="touch"))
    model = contact_scenario(regime, forces=forces)
    assert model.contacts[0].friction.regime is regime
    assert model.forces_on("a") == tuple(forces)


def test_unknown_friction_coefficient_is_an_explicit_valid_input():
    model = contact_scenario(
        contacts=(n.Contact("touch", "a", "plane", n.Friction(n.FrictionRegime.STATIC, UNKNOWN)),)
    )
    assert model.contacts[0].friction.coefficient is UNKNOWN


@pytest.mark.parametrize(
    "regime, coefficient",
    [
        (n.FrictionRegime.NONE, n.FrictionCoefficient(0)),
        (n.FrictionRegime.STATIC, None),
        (n.FrictionRegime.KINETIC, 0.2),
        ("static", None),
    ],
)
def test_contradictory_or_ambiguous_friction(regime, coefficient):
    with pytest.raises(ValueError):
        n.Friction(regime, coefficient)


def test_frictionless_contact_rejects_friction_and_duplicate_regimes():
    with pytest.raises(ValueError, match="frictionless"):
        contact_scenario(
            n.FrictionRegime.NONE,
            forces=(force("friction", n.ForceKind.FRICTION, relationship="touch"),),
        )
    model = contact_scenario()
    other = n.Contact(
        "other", "a", "plane", n.Friction(n.FrictionRegime.KINETIC, n.FrictionCoefficient(0.3))
    )
    with pytest.raises(ValueError, match="one friction regime"):
        dataclasses.replace(model, contacts=(*model.contacts, other))


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"surfaces": ()}, "unknown surface"),
        (
            {"contacts": (n.Contact("c", "missing", "plane", n.Friction(n.FrictionRegime.NONE)),)},
            "unknown body",
        ),
        ({"surfaces": (n.Surface("plane", n.BodyReference("a"), 0),)}, "own surface"),
        ({"forces": (force("n", n.ForceKind.NORMAL, relationship="absent"),)}, "unknown contact"),
        (
            {"forces": (force("n", n.ForceKind.NORMAL, source=EARTH, relationship="touch"),)},
            "ownership",
        ),
    ],
)
def test_contact_reference_failures(overrides, message):
    with pytest.raises(ValueError, match=message):
        contact_scenario(**overrides)


def string(**overrides):
    values = dict(
        identifier="link",
        body_ids=("a", "b"),
        source=STRING,
        negligible_mass=True,
        taut=True,
        inextensible=True,
    )
    values.update(overrides)
    return n.StringConnection(**values)


def test_bounded_light_string_and_tension():
    tension = force("tension", n.ForceKind.TENSION, source=STRING, relationship="link")
    model = scenario(strings=(string(),), forces=(tension,))
    assert model.strings[0].body_ids == ("a", "b")
    assert model.forces_on("a") == (tension,)
    assert model.accelerations == ()


@pytest.mark.parametrize(
    "overrides",
    [
        {"body_ids": ("a", "a")},
        {"body_ids": ("a",)},
        {"negligible_mass": False},
        {"negligible_mass": 1},
        {"taut": "yes"},
        {"inextensible": 1},
        {"source": n.BodyReference("b")},
    ],
)
def test_invalid_string_declarations(overrides):
    with pytest.raises(ValueError):
        string(**overrides)


def test_string_unknown_endpoint_and_networks_rejected():
    with pytest.raises(ValueError, match="unknown body"):
        scenario(strings=(string(body_ids=("a", "missing")),))
    with pytest.raises(ValueError, match="single bounded string"):
        scenario(strings=(string(), string(identifier="other")))


def test_universal_gravitation_inputs_and_explicit_force_ownership():
    interaction = n.GravitationalInteraction("gravity", ("a", "b"), n.Metres(10))
    given = force(
        "gravity-on-a",
        n.ForceKind.GRAVITATIONAL,
        source=n.BodyReference("b"),
        relationship="gravity",
    )
    model = scenario(gravitation=(interaction,), forces=(given,))
    assert model.gravitation[0].separation == n.Metres(10)
    assert model.forces_on("a") == (given,)


@pytest.mark.parametrize("members", [("a",), ("a", "a"), ("a", "b", "c")])
def test_gravitation_requires_two_distinct_bodies(members):
    with pytest.raises(ValueError):
        n.GravitationalInteraction("gravity", members, n.Metres(1))


def test_unknown_gravitational_body_rejected():
    with pytest.raises(ValueError, match="unknown body"):
        scenario(gravitation=(n.GravitationalInteraction("g", ("a", "missing"), n.Metres(1)),))


def test_authored_gravity_and_zero_acceleration_do_not_create_weight_or_normal():
    field = n.GravitationalField(EARTH, ("a",), acceleration(0, -9.8))
    stationary = n.AuthoredAcceleration("a", acceleration())
    model = scenario(gravitational_fields=(field,), accelerations=(stationary,))
    assert model.forces == ()
    assert model.accelerations[0].vector.components == (
        n.MetresPerSecondSquared(0),
        n.MetresPerSecondSquared(0),
    )


def test_valid_underdetermined_scenario_preserves_unknowns_and_absence():
    unknown_force = force(components=n.ForceVector(AXES, (UNKNOWN, n.Newtons(0))))
    model = scenario(forces=(unknown_force,))
    assert model.accelerations == ()
    assert model.gravitational_fields == ()
    assert model.forces == (unknown_force,)
    assert model.forces[0].vector.components[0] is UNKNOWN
    assert model.forces[0].vector.components[1] == n.Newtons(0)
    assert not hasattr(model, "resultant_force")
    assert not hasattr(model, "is_equilibrium")
    assert scenario().forces == ()


def test_third_law_and_fbd_ownership_do_not_check_numeric_agreement():
    first = force("b-on-a", source=n.BodyReference("b"), components=vector(2, 4))
    second = force("a-on-b", target="b", source=n.BodyReference("a"), components=vector(99, 3))
    pair = n.ThirdLawPair((first.identifier, second.identifier))
    model = scenario(forces=(first, second), third_law_pairs=(pair,))
    assert model.forces_on("a") == (first,)
    assert model.forces_on("b") == (second,)
    assert first.source == n.BodyReference(second.target_body_id)
    assert second.source == n.BodyReference(first.target_body_id)
    with pytest.raises(ValueError, match="unknown body"):
        model.forces_on("absent")


def test_contact_third_law_pair_can_reverse_surface_ownership():
    first = force("b-on-a", n.ForceKind.NORMAL, source=n.BodyReference("b"), relationship="touch")
    second = force(
        "a-on-b", n.ForceKind.NORMAL, target="b", source=n.BodyReference("a"), relationship="touch"
    )
    model = contact_scenario(
        surfaces=(n.Surface("plane", n.BodyReference("b"), 0),),
        forces=(first, second),
        third_law_pairs=(n.ThirdLawPair(("b-on-a", "a-on-b")),),
    )
    assert model.forces_on("b") == (second,)


@pytest.mark.parametrize(
    "second",
    [
        force("second", source=n.BodyReference("b")),
        force("second", target="b", source=EARTH),
        force("second", n.ForceKind.WEIGHT, target="b", source=n.BodyReference("a")),
    ],
)
def test_malformed_third_law_pair_rejected(second):
    first = force("first", source=n.BodyReference("b"))
    with pytest.raises(ValueError, match="reverse ownership"):
        scenario(forces=(first, second), third_law_pairs=(n.ThirdLawPair(("first", "second")),))


@pytest.mark.parametrize("members", [("push",), ("push", "push")])
def test_malformed_pair_membership(members):
    with pytest.raises(ValueError):
        n.ThirdLawPair(members)


def test_missing_third_law_force_rejected():
    with pytest.raises(ValueError, match="unknown force"):
        scenario(forces=(force(),), third_law_pairs=(n.ThirdLawPair(("push", "absent")),))


def test_ordered_inputs_are_copied_and_equal_without_random_metadata():
    bodies = [body("b"), body()]
    forces = [force("second"), force("first")]
    model = scenario(bodies=bodies, forces=forces)
    bodies.clear()
    forces.clear()
    assert model == scenario(bodies=(body("b"), body()), forces=(force("second"), force("first")))
    assert tuple(item.identifier for item in model.forces) == ("second", "first")
    assert hash(model) == hash(scenario(bodies=model.bodies, forces=model.forces))
    assert dataclasses.asdict(model) == dataclasses.asdict(
        scenario(bodies=model.bodies, forces=model.forces)
    )
    with pytest.raises(ValueError, match="ordered"):
        scenario(bodies={body(), body("b")})


def test_vectors_reject_silent_basis_changes():
    other = n.CartesianCoordinates((n.CartesianDirection.LEFT, n.CartesianDirection.UP))
    with pytest.raises(ValueError, match="basis"):
        scenario(forces=(force(components=vector(coordinates=other)),))
    with pytest.raises(ValueError, match="basis"):
        scenario(accelerations=(n.AuthoredAcceleration("a", acceleration(coordinates=other)),))


def test_newton_production_imports_only_stdlib_and_its_own_domain():
    for path in Path(n.__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in {"dataclasses", "enum", "math"} for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module in {"dataclasses", "enum", "math"}


def test_surface_basis_requires_a_declared_surface():
    with pytest.raises(ValueError, match="unknown surface"):
        scenario(coordinates=n.SurfaceCoordinates("absent", (n.SurfaceDirection.ALONG_RIGHT,)))


def test_duplicate_gravitational_relationships_are_ambiguous_even_with_reversed_endpoints():
    with pytest.raises(ValueError, match="body pair must be unique"):
        scenario(
            gravitation=(
                n.GravitationalInteraction("first", ("a", "b"), n.Metres(1)),
                n.GravitationalInteraction("second", ("b", "a"), n.Metres(2)),
            )
        )


def test_field_cannot_act_on_its_source_or_duplicate_a_source_target_declaration():
    with pytest.raises(ValueError, match="own gravitational field"):
        scenario(
            gravitational_fields=(
                n.GravitationalField(n.BodyReference("a"), ("a",), acceleration()),
            )
        )
    field = n.GravitationalField(EARTH, ("a",), acceleration(0, -9.8))
    with pytest.raises(ValueError, match="source/target membership must be unique"):
        scenario(gravitational_fields=(field, field))


def test_multiple_authored_accelerations_for_one_body_rejected():
    with pytest.raises(ValueError, match="acceleration must be unique"):
        scenario(
            accelerations=(
                n.AuthoredAcceleration("a", acceleration()),
                n.AuthoredAcceleration("a", acceleration(1, 2)),
            )
        )


def test_contact_force_membership_cannot_be_duplicated_under_a_new_id():
    with pytest.raises(ValueError, match="relationship/target membership must be unique"):
        contact_scenario(
            forces=(
                force("first", n.ForceKind.NORMAL, relationship="touch"),
                force("second", n.ForceKind.NORMAL, relationship="touch"),
            )
        )


@pytest.mark.parametrize(
    "kind, source, relation, message",
    [
        (n.ForceKind.TENSION, STRING, "absent", "unknown string"),
        (n.ForceKind.TENSION, EARTH, "link", "tension ownership"),
        (n.ForceKind.GRAVITATIONAL, n.BodyReference("b"), "absent", "unknown gravitational"),
        (n.ForceKind.GRAVITATIONAL, EARTH, "g", "gravitational force ownership"),
    ],
)
def test_force_relationship_must_exist_and_match_source(kind, source, relation, message):
    with pytest.raises(ValueError, match=message):
        scenario(
            strings=(string(),),
            gravitation=(n.GravitationalInteraction("g", ("a", "b"), n.Metres(1)),),
            forces=(force(kind=kind, source=source, relationship=relation),),
        )


def test_force_cannot_have_multiple_third_law_partners():
    first = force("first", source=n.BodyReference("b"))
    second = force("second", target="b", source=n.BodyReference("a"))
    pair = n.ThirdLawPair(("first", "second"))
    with pytest.raises(ValueError, match="only one third-law pair"):
        scenario(forces=(first, second), third_law_pairs=(pair, pair))


def test_unordered_vector_input_is_rejected():
    with pytest.raises(ValueError, match="ordered"):
        n.ForceVector(AXES, {n.Newtons(1), n.Newtons(2)})


def test_composed_incline_and_light_string_scenario_retains_only_authored_facts():
    coordinates = n.SurfaceCoordinates(
        "plane", (n.SurfaceDirection.ALONG_RIGHT, n.SurfaceDirection.NORMAL_OUT)
    )
    normal = force(
        "normal",
        n.ForceKind.NORMAL,
        relationship="touch",
        components=n.ForceVector(coordinates, (n.Newtons(0), UNKNOWN)),
    )
    tension = force(
        "tension",
        n.ForceKind.TENSION,
        source=STRING,
        relationship="link",
        components=n.ForceVector(coordinates, (UNKNOWN, n.Newtons(0))),
    )
    model = contact_scenario(coordinates=coordinates, strings=(string(),), forces=(normal, tension))
    assert model.forces_on("a") == (normal, tension)
    assert model.forces_on("b") == ()
    assert model.accelerations == ()
    assert model.contacts[0].friction.regime is n.FrictionRegime.STATIC
    assert model.strings[0].negligible_mass is True
