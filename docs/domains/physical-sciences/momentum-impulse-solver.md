# Momentum & Impulse solver

The `MomentumImpulseSolver` is the authoritative deterministic calculator for
the directly derivable quantities in the Issue #28 initial-state model. It
does not solve collision outcomes, generate scenarios, write question text,
render diagrams, or expose an API.

## Inputs and outputs

The solver accepts one `MomentumScenario` containing identified bodies,
positive-axis convention, signed initial velocities, and a `SystemBoundary`.
It returns an immutable `MomentumImpulseSolution` containing:

- one `BodyMomentumResult` per body;
- signed initial total momentum;
- the effective net external impulse over the modeled interaction interval;
- signed final total system momentum; and
- the selected axis and optional seed metadata.

The solution deliberately contains no final body velocities. A collision with
two unknown final velocities is underdetermined by momentum conservation alone;
the solver exposes only the aggregate quantities that are justified by the
available information.

## Calculations and system boundary

For each body, the solver calculates signed momentum as `p = m v`. Total
momentum is the signed sum of body momenta; magnitudes are never added.

For an isolated system, the effective external impulse is `0 N·s`, so final
total momentum equals initial total momentum. For a non-isolated system, the
`SystemBoundary.external_impulse` value is interpreted as the net external
impulse over the modeled interaction interval and is applied once:

`final total momentum = initial total momentum + external impulse`

This does not infer individual final body states. Momentum and impulse remain
separate semantic types despite compatible dimensions.

## Sign and numerical policy

Velocity and momentum retain their mathematical signs under the scenario's
explicit `PositiveAxis.RIGHT` or `PositiveAxis.LEFT` convention. Reversing the
axis reverses signs for the same physical situation; solver logic never
assumes that right is positive.

All values must be finite. The solver performs no intermediate rounding.
Solution validation compares derived floating-point values with an absolute
tolerance of `1e-9`. Presentation rounding is deferred downstream.

## Validation and deferred functionality

`validate(solution)` checks scenario identity, axis and seed metadata, body
momentum (`p = m v`), signed totals, finite values, impulse change, and the
isolated-system conservation rule. It rejects tampered or inconsistent
solutions.

Force/time impulse calculations, collision constraints, elastic or inelastic
classification, kinetic energy, final body velocities, scenario generation,
question generation, rendering, and API integration are intentionally deferred
to later M3 issues.
