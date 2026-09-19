# Constrained one-dimensional collisions

Issue #36 extends the framework-independent Momentum & Impulse boundary with
ConstrainedMomentumSolver. It accepts a MomentumInteraction and produces an
immutable ConstrainedCollisionSolution. It is a calculation and validation
component only: it does not generate scenarios, author questions, render
diagrams, expose HTTP endpoints, or implement force-time impulse.

## Supported constraints

- KnownFinalVelocityConstraint supports exactly two bodies. The named body's
  authored signed final velocity is preserved, and the other body's velocity
  is derived from the aggregate final momentum.
- CommonFinalVelocityConstraint supports exactly the two scenario bodies.
  Their common velocity is derived from total mass and aggregate final
  momentum. This is the explicit sticking/perfectly-inelastic case.
- CompleteFinalStateConstraint carries all authored final velocities. The
  solver returns those values unchanged and validation checks their momenta,
  totals, and system boundary.

Stable body identifiers are used for lookup. Tuple ordering is used only for
the deterministic presentation order of result states.

## Conservation and external impulse

The constrained solver delegates initial total momentum, external impulse, and
final total momentum to MomentumImpulseSolver. The declared external impulse
is therefore applied exactly once:

final total momentum = initial total momentum + external impulse

Signed values and the scenario's explicit PositiveAxis are preserved. Axis
reversal changes mathematical signs but does not introduce hidden sign
transformations. An interaction with more than two bodies is rejected by the
constrained solver, while the existing aggregate solver remains valid for
general scenario body counts.

## Validation and classification

validate(solution) independently checks aggregate authority, body identity,
p = m v, signed final totals, authored constraints, kinetic-energy values,
seed/axis metadata, and isolated-system conservation. It uses the existing
absolute tolerance of 1e-9 and performs no intermediate rounding.

An interaction-less scenario is explicitly underdetermined and is rejected;
the solver never inserts arbitrary or zero final velocities. Complete authored
states are not repaired when they violate conservation, so invalid authored
states return an invalid ValidationResult while retaining their authored values
in the returned result.

For isolated interactions, the result includes the minimum kinetic-energy
representation needed for classification:

- equal initial and final kinetic energy within 1e-9: elastic;
- unequal kinetic energy with distinct final velocities: inelastic;
- explicit common final velocity/sticking: perfectly-inelastic.

Externally impulsed interactions receive no collision classification because
the isolated collision energy interpretation does not apply. Classification
is never inferred from an underdetermined state.

## Deferred boundaries

Issue #37 owns force/time impulse and remains separate. Scenario-factory
expansion (#38), SVG rendering (#39), question generation (#40/#41), and API
integration (#42) are not part of this solver.
