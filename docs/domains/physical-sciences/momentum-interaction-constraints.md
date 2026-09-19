# Momentum interaction constraints

Issue #35 adds framework-independent authored constraints for one-dimensional
Momentum & Impulse interactions. Issue #36 consumes those constraints through
the separate ConstrainedMomentumSolver and returns derived result models; the
authored models themselves still never calculate or mutate results.

## Why the constraint boundary exists

The existing `MomentumScenario` is a valid initial-state model. The current
`MomentumImpulseSolver` calculates body momentum, aggregate momentum, and
aggregate impulse effects, but it does not invent individual final body
velocities. With two unknown final velocities, one conservation equation is
underdetermined.

Issue #35 therefore keeps `MomentumScenario` unchanged and introduces a
separate immutable `MomentumInteraction` wrapper:

```text
MomentumInteraction
  +-- MomentumScenario      # authoritative initial state
  +-- InteractionConstraint # authored post-interaction information
```

This preserves valid underdetermined scenarios while giving the constrained
solver an explicit input boundary. The aggregate solver remains authoritative
for initial and final total momentum; the constrained solver adds only the
individual final states justified by this wrapper.

## Constraint families

### Known final velocity

`KnownFinalVelocityConstraint` references one stable `MomentumBody.identifier`
and stores an authored signed `MetresPerSecond` value. The domain does not
infer which other body is unknown and does not calculate that body's result.

### Common final velocity / sticking

`CommonFinalVelocityConstraint` references exactly two distinct body IDs. It
represents the explicit physical statement that those bodies stick together,
which is a perfectly inelastic condition. It stores no final velocity; Issue
#36 derives the common value from the aggregate final momentum. Generic
inelastic behavior is not treated as sticking.

### Complete final state

`CompleteFinalStateConstraint` contains one immutable `FinalBodyState` per
scenario body. Each state carries a stable body ID and an authored signed
`MetresPerSecond` value. The interaction validates that the set of IDs covers
the scenario exactly once, without relying on tuple position or display order.

## Structural validation

`MomentumInteraction` validates that:

- the initial scenario is a `MomentumScenario`;
- the constraint is one of the supported families;
- referenced body IDs exist in the scenario;
- duplicate body IDs are rejected;
- complete states cover every scenario body exactly once; and
- all velocities use the existing finite signed value object.

These checks are structural only. The domain does not determine whether a
given interaction is mathematically solvable under its system boundary or
external impulse. A scenario with no interaction constraint remains valid and
represents a physically valid but potentially underdetermined state.

## Sign, system, and compatibility boundaries

Final velocities retain their signed scalar values under
`PositiveAxis.RIGHT` or `PositiveAxis.LEFT`; physical direction is not stored
as a replacement for the mathematical sign. Existing `SystemBoundary` and
external-impulse ownership remain on `MomentumScenario`; the interaction does
not duplicate or reinterpret them. See
momentum-constrained-collisions.md for the solver and validation contract.

The existing scenario factory, aggregate solver, projectile pipeline, API, and
generation policy remain unchanged. The new model imports no FastAPI,
Pydantic, persistence, renderer, LMS, or solver implementation. No randomness,
generated IDs, kinetic-energy type, collision classification, or calculation
is introduced.
