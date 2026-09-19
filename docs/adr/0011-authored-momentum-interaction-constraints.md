# ADR 0011: Separate authored Momentum interaction constraints from derived results

- Status: Accepted
- Date: 2026-09-19

## Context

The M3 `MomentumScenario` is an immutable initial-state model. Momentum
conservation alone cannot determine two unknown final velocities, but later
CAPS-aligned questions need to represent explicit information such as one
known final velocity, an explicitly sticking pair, or a complete authored
final state.

Putting optional before/after data directly into `MomentumScenario` would
blur initial state and interaction state, make valid underdetermined scenarios
appear incomplete, and encourage the current aggregate solver to infer values
it cannot justify.

## Decision

Represent authored post-interaction information in a separate immutable
`MomentumInteraction` wrapper containing an existing `MomentumScenario` and
one explicit `InteractionConstraint` family:

- `KnownFinalVelocityConstraint` for one identified body;
- `CommonFinalVelocityConstraint` for exactly two explicitly sticking bodies;
- `CompleteFinalStateConstraint` for one authored final state per scenario body.

Constraints reference stable body identifiers and retain signed
`MetresPerSecond` values. Structural validation checks membership, uniqueness,
and completeness but performs no conservation, collision, impulse, force,
time, kinetic-energy, or classification calculations.

The existing scenario, factory, and aggregate solver remain backward
compatible. A future constrained solver consumes `MomentumInteraction` and
determines mathematical solvability. A valid scenario may continue to omit an
interaction constraint and remain underdetermined.

## Consequences

Authored constraints cannot be confused with solver-derived final states, and
future question generation has an explicit boundary for checking whether an
answer is justified. The model remains framework-independent and preserves the
existing sign, system-boundary, external-impulse, seed, and provenance
semantics. Collision solving, energy classification, generation expansion,
rendering, question generation, and API integration remain separate issues.
