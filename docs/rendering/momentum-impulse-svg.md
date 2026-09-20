# Momentum & Impulse SVG renderer

`MomentumSvgRenderer` is a framework-independent, deterministic presentation
adapter. It consumes a `MomentumScenario`, optional authored
`MomentumInteraction`, optional constrained solution, and explicit rendering
options. It performs no physics calculations and never calls a solver.

The renderer supports single-body and two-body before/after technical
diagrams, known-final-velocity and sticking constraints, complete authored
final states, positive-axis indicators, system boundaries, mass labels, and
force/impulse values only when a future caller supplies a safe authored label.
Bodies are sorted by stable identifier for layout. Physical direction is
obtained from the domain's signed velocity and `PositiveAxis`; screen
coordinates are independent of the mathematical axis. Arrow length is a
fixed illustrative size, not a quantitative scale. Zero velocity is shown
as a stationary body with a value label.

Final values derived by a solver are hidden unless
`reveal_derived_final_velocity` is explicitly enabled. Unknown values are
represented by `?`; hidden values are not copied into titles, descriptions,
IDs, metadata, or attributes. Text is escaped, IDs are stable, and output
contains no scripts, handlers, remote resources, or arbitrary SVG fragments.
The output is the existing `SvgDocument` type and renderer layout version is
`1`. Calculation questions (#40), conceptual templates (#41), and API
integration (#42) remain deferred.
