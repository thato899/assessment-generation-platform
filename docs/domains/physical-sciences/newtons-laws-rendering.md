# Newton's Laws technical SVG rendering

Issue #58 provides `NewtonSvgRenderer` in
`assessment_platform.rendering.svg.newton`. The renderer consumes an authored
`NewtonScenario`, an immutable `NewtonRenderOptions` value, and optionally an
explicitly supplied validated result. It returns the repository's immutable
`SvgDocument`. It has no FastAPI, Pydantic, database, browser or image-service
dependency.

## Responsibility and diagram kinds

`NewtonDiagramKind.FREE_BODY_DIAGRAM` isolates one selected body and uses
`scenario.forces_on(body_id)`. A two-body free-body view therefore requires an
explicit `body_id`; a force acting on the other body is never copied into the
selected body's diagram. `FORCE_DIAGRAM` may show all authored bodies, their
acting forces, a straight `StringConnection`, surfaces and the authored
`SystemBoundary`. Newton III partner forces remain attached to their own
targets.

The renderer supports one- and two-dimensional Cartesian scenes, surface-
aligned scenes, horizontal and inclined contacts, bounded two-body strings,
Newton III interactions, and safe two-body gravitation visuals where the
scenario contains sufficient authored structure. A scalar separation never
creates a gravitational arrow.

## Direction and layout

Cartesian components follow their authored `CartesianDirection`: RIGHT and
LEFT map to screen x, while UP and DOWN map to screen y with SVG's downward
screen convention. A negative component reverses the authored basis direction.
Surface components follow `SurfaceDirection`; the authored inclination rotates
the tangent and normal display bases. These are display transforms only. The
renderer does not resolve components, calculate a resultant, or derive a
normal, friction, weight, tension, acceleration, or gravitational value.

Bodies, surfaces, arrows and straight strings use bounded deterministic
technical geometry. Arrow length is fixed by default, so hidden values cannot
be recovered from pixels. The implementation does not claim physical scale.

## Values, visibility and safety

`NewtonVisibilityOptions` is an allowlist. Learner-safe defaults show semantic
body and force labels but hide numeric values, coordinate axes, surface
inclination, system boundaries and derived results. Known authored numbers are
shown only when `show_numeric_values` is explicitly enabled; the separate
`show_known_givens` flag remains available to record that policy choice.
Unknown values remain symbolic or are omitted when their direction is not
structurally authored. A normal direction can be shown symbolically when the
contact surface establishes it; unknown friction direction is never guessed.
The renderer does not instantiate `NewtonSolver`, and a caller must provide a
validated result explicitly before any future derived-value presentation can
be added.

All authored visible strings are XML-escaped. IDs are deterministic sanitized
semantic IDs made from scenario, body, force, surface and relationship
identifiers; hidden numeric values are not inserted into IDs, attributes,
comments or metadata. The SVG contains only local primitives and a local arrow
marker: no scripts, event handlers, `javascript:` URLs, remote resources,
`foreignObject`, executable content or answer-bearing accessibility text.
The root has deterministic `title`, `desc`, `role="img"` and labelled-by
metadata describing only visible semantics.

## Supported generation families and boundaries

The renderer can consume scenarios from all twelve Issue #57 families:
Newton II, unknown force, equilibrium, weight, contact normal, static,
limiting-static and kinetic friction, inclined plane, connected bodies,
universal gravitation and Newton III. It only displays authored force data;
for example, a gravitational field alone does not manufacture a weight arrow.

Question wording, expected answers, marking, generation policy, API routing and
CAPS interpretation and numeric question packaging remain outside this module;
calculation questions are owned by active #59 and conceptual templates/API
work remain deferred to #60-#62. No new cross-cutting ADR is required for this
renderer.
