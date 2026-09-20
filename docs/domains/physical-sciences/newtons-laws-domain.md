# Authored Newton domain

Issue #55 defines facts for the bounded M4 cases in the
[approved scope](newtons-laws-scope.md), implemented in
`assessment_platform.domains.physical_sciences.mechanics.newtons_laws`.
Curriculum ownership remains Grade 11, with Grade 12 consolidation and selected
examinability. The model describes inputs, not the results of Newton's laws.

## Architecture boundary

```text
authored NewtonScenario -> Issue #56 authoritative solver -> derived results
```

The package imports only the Python standard library and its own modules.
Constructors validate representation, references, ownership and supported
assumptions. They do not determine solvability or numerical physical consistency.
Valid domain state does not imply a unique solution. One or two modeled bodies
and at most one connecting string bound this slice; arbitrary body/string
networks, pulley mechanics and three-dimensional frames are absent.

## Model inventory

| Responsibility | Public types |
| --- | --- |
| SI inputs | `Kilograms`, `Newtons`, `MetresPerSecondSquared`, `Metres` |
| Dimensionless/unknown inputs | `FrictionCoefficient`, `UnknownValue` |
| Coordinates | `CartesianCoordinates`, `CartesianDirection`, `SurfaceCoordinates`, `SurfaceDirection`, `Coordinates` (union) |
| Vectors | `ForceVector`, `AccelerationVector` |
| Bodies and sources | `NewtonBody`, `BodyReference`, `EnvironmentReference`, `ForceSource` (union) |
| Forces | `Force`, `ForceKind` |
| System | `NewtonScenario`, `SystemBoundary`, `NewtonAssumptions` |
| Contact | `Surface`, `Contact`, `Friction`, `FrictionRegime` |
| Relationships | `StringConnection`, `GravitationalInteraction`, `ThirdLawPair` |
| Given acceleration/field | `AuthoredAcceleration`, `GravitationalField` |

## Bodies, stable identity and units

A body has a caller-authored, non-empty semantic identifier and positive finite
mass in kilograms. Identifiers follow the repository convention of trimmed
strings. Body and environment sources are distinguished by reference type.
Identifiers are unique within each scenario collection; force kind determines
the relationship namespace. There are no generated IDs, seeds, timestamps or
automatic labels. Later labels can use these stable semantic identities.

Newton owns small frozen SI values locally. Momentum's `Newtons` describes a
resultant force, projectile's acceleration value disallows zero, and projectile's
`Metres` describes a non-negative position. Newton needs individual signed force
components, acceleration including zero, and positive separation. No shared
generic unit layer already exists. A cross-engine extraction is unnecessary for
this issue; existing types and import paths are unchanged. No ADR is introduced.

All numbers must be finite; booleans and numeric strings are rejected. Mass and
separation must be positive. Friction coefficients are dimensionless and
non-negative, with no upper bound of one. Force and acceleration components can
be positive, negative or zero. Bodies contain no calculated quantities.

## Force ownership and relationships

Every `Force` has an identifier, enum kind, target body, typed source and
`ForceVector`. Kinds are `WEIGHT`, `NORMAL`, `FRICTION`, `APPLIED` (push/pull),
`TENSION` and `GRAVITATIONAL`. Resultant force is not an extra acting force; it
remains a derived result. All targets and sources must exist, and a body cannot
exert a force on itself.

| Kind | Meaning of `relationship_id` |
| --- | --- |
| Normal/friction | Required contact; ownership matches its body and surface owner, in either direction |
| Tension | Required string; target is an endpoint, source is the string's environment agent |
| Gravitational | Required interaction; source and target are the two distinct participant bodies |
| Applied/weight | None; the typed source directly identifies the agent |

Each contact/string/gravitational relationship allows only one force of a given
kind on a given target. Duplicate declarations under new force IDs are rejected
without summing any forces.

## Coordinates, acceleration and unknown inputs

Vectors carry their basis explicitly and must match the scenario basis.
Component order is x, then y for a two-dimensional representation. Cartesian
positive axes use `RIGHT`, `LEFT`, `UP` or `DOWN`. One axis gives a 1D basis;
two axes must be perpendicular. Mathematical positive x need not be physical
right, and positive y need not be physical up.

`SurfaceCoordinates` names a declared plane. Its tangent x is positive
`ALONG_RIGHT` or `ALONG_LEFT`; optional normal y is positive `NORMAL_OUT` or
`NORMAL_IN`. Inclination is in signed degrees from physical right: positive
rises to the right, negative rises to the left, zero is horizontal. The upper
face of a plane strictly between -90 and 90 degrees is supported; vertical
walls and overhangs are outside this contact slice.

No components, magnitudes, angles or basis transforms are calculated. A 1D
vector records its declared axis only, without silently authoring orthogonal
values. Use 2D for a full horizontal/incline force diagram with tangential and
normal forces. #56 checks whether supplied dimensional information suffices.

Force components are `Newtons` or `UnknownValue.UNKNOWN`; unknown never means
zero. `AccelerationVector` contains given signed `MetresPerSecondSquared` values.
`AuthoredAcceleration` associates one vector with a body at scenario level.
Absence means no acceleration is supplied. A given zero vector can express an
authored zero-acceleration condition without a derived equilibrium flag.

## System and environment

`SystemBoundary.body_ids` selects a non-empty, duplicate-free subset of the
declared bodies. Other modeled bodies and registered environment agents lie
outside that system. Source/target membership determines internal and external
ownership, so no duplicated `is_external` flag or resultant is stored.

`NewtonAssumptions` explicitly requires an inertial frame, constant mass and
neglected air resistance, consistent with M4 exclusions. False or untyped
declarations are rejected. Contact, string and gravity facts are composed in
their own relationships. No assumption asserts a calculated equilibrium state.

## Contacts, friction and strings

`Surface` records its body/environment owner and inclination. `Contact` links
a body to a surface and one `Friction` state. A body cannot contact its own
surface. Duplicate body/surface contacts, including conflicting regimes, fail.

Friction regimes are `NONE`, `STATIC`, `LIMITING_STATIC` and `KINETIC`.
Frictionless contact has no coefficient and rejects friction-force objects.
Other regimes explicitly supply `FrictionCoefficient` or `UnknownValue.UNKNOWN`.
Static/limiting-static coefficients describe static friction; kinetic
coefficients describe kinetic friction. Unknown coefficient data can remain
unknown without masquerading as a frictionless surface. Static force is not
equated to its limiting value and direction is not inferred from motion.

`StringConnection` names exactly two distinct bodies and an environment agent
representing the string. Negligible mass must explicitly be true. Tautness and
inextensibility are separate boolean facts, not consequences of lightness. No
lengths, pulleys, acceleration equality or tensions are calculated. Numerical
tension and constraint applicability, including slack/elastic declarations,
belong to #56. One string is supported, not a network.

## Third law and free-body semantics

`ThirdLawPair` names two distinct existing forces. They reverse body source/target
ownership, act on different bodies and describe the same kind and relationship.
A force cannot have multiple partners. Equal magnitude and opposite direction
are not tested; structurally valid but numerically inconsistent authored values
remain representable for #56 to validate.

`scenario.forces_on(body_id)` returns only forces acting on that body in authored
order. It excludes the partner acting on the other body. Normal/friction pairs
can explicitly reverse contact ownership. The light string is an environment
agent, not a positive-mass body; the tensions on its endpoints are not falsely
treated as third-law partners with each other.

These facts support a force diagram showing relevant objects or a free-body
diagram isolating a selected object. No SVG, pixels, arrow scales, layout or
typography exist in the domain. Presentation belongs to #58.

## Gravity, weight and apparent weight

`GravitationalField` links a typed source and a given acceleration vector to
explicit target bodies. A body cannot supply its own field, and duplicate
source/target declarations fail. A field does not create a weight force.
Weight may be independently authored, including unknown components, without
field data when the problem is underdetermined.

`GravitationalInteraction` records two distinct bodies and positive
centre-to-centre separation. Masses come from the bodies; duplicate interactions
for the same unordered pair fail. No gravitational constant or force is computed.
Mass is distinct from force. Weight, support/contact forces, field data and
acceleration can describe lift/apparent-weight and weightless cases without
populating an apparent-weight or weightlessness result.

## Immutability, determinism and underdetermination

All dataclasses are frozen and slotted. Ordered list inputs are copied to tuples;
unordered containers are rejected. Caller mutation cannot change a model.
Authored order is preserved for equality, free-body selection and dataclass
serialization. Equal ordered inputs produce equal state; reordered inputs
intentionally preserve the newly authored order. Process hashes never form IDs.

This example is structurally valid without enough information for acceleration:

```python
from assessment_platform.domains.physical_sciences.mechanics import newtons_laws as n

axes = n.CartesianCoordinates((n.CartesianDirection.RIGHT,))
hand = n.EnvironmentReference("hand")
scenario = n.NewtonScenario(
    identifier="unknown-push",
    bodies=(n.NewtonBody("block", n.Kilograms(2)),),
    coordinates=axes,
    system=n.SystemBoundary(("block",)),
    assumptions=n.NewtonAssumptions(True, True, True),
    environment=(hand,),
    forces=(n.Force(
        "push", n.ForceKind.APPLIED, "block", hand,
        n.ForceVector(axes, (n.UnknownValue.UNKNOWN,)),
    ),),
)
assert scenario.accelerations == ()
assert scenario.forces[0].vector.components == (n.UnknownValue.UNKNOWN,)
```

## Deferred work and verification

#56 alone owns resultants, acceleration, unknown-force solving, weight,
normal/friction/tension calculations, component resolution, gravitation,
equilibrium and third-law numerical validation. #57 owns seeded generation;
#58 rendering; #59/#60 canonical questions and conceptual rubrics; #61 API
routing. Automatic marking is absent. API regressions confirm Newton requests
remain unsupported for both Grade 11 and Grade 12.

Focused tests cover the finite structural invariants, composed scenarios,
third-law/free-body ownership, unknown inputs and underdetermination. Hypothesis
was reconsidered and not added: deterministic parameterized cases express these
bounded invariants clearly without a new dependency. Existing curriculum,
Momentum, projectile and API regressions remain required.
