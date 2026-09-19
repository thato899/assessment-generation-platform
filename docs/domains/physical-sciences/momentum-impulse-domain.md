# Momentum & Impulse domain foundation

Issue #28 establishes the first M3 domain boundary for one-dimensional
Momentum & Impulse scenarios. Issue #35 adds a separate authored interaction
constraint boundary; it does not turn the initial-state model into a mutable
before/after object. The deterministic solver, scenario factory, question
generator, renderer, and API remain separate boundaries.

## Domain objects

- `Kilograms` represents a finite, strictly positive mass.
- `MetresPerSecond` represents a finite signed velocity. Its sign is preserved;
  it is not a speed with a hidden sign transformation.
- `PositiveAxis` explicitly selects either left or right as the positive
  coordinate direction.
- `Momentum` and `Impulse` are distinct finite signed value objects. Their
  compatible dimensions do not make them interchangeable: momentum is measured
  in kg·m/s and impulse in N·s.
- `MomentumBody` identifies one body's mass and initial velocity.
- `MomentumChange` is a distinct finite signed value object for final momentum
  minus initial momentum.
- `Newtons` is a finite signed resultant-force value object.
- `Seconds` represents a strictly positive elapsed interaction interval.
- `SystemBoundary` states whether the modeled system is isolated. A
  non-isolated system must declare its external impulse; an isolated system
  cannot declare one.
- `MomentumScenario` contains unique body identities, the explicit axis
  convention, the system boundary, assumptions, and optional deterministic
  provenance.

The scenario does not contain a final state or derived momentum. A future
authoritative solver must calculate and validate those results. The model
does not assume that right is always positive and does not encode collision
type, conservation-law outcomes, or kinetic-energy behavior.

`MomentumInteraction` wraps a `MomentumScenario` with one explicit authored
constraint: a known final velocity for one body, a two-body common-final-
velocity/sticking condition, or a complete authored final state. It validates
body identity and structural completeness without claiming mathematical
solvability. A valid scenario may omit an interaction constraint and remain
underdetermined. See `momentum-interaction-constraints.md`.

## Boundaries

The module imports only framework-independent domain/core types. It does not
depend on FastAPI, Pydantic, HTTP, persistence, rendering, LLMs, solver
implementations, or LMS integrations. Issue #35 performs no calculations;
constrained solving belongs to Issue #36. Issue #37 provides the separate
deterministic relationship solver for momentum change, impulse,
average/resultant force, and contact time. No Momentum API support is added,
and the existing vertical-projectile pipeline remains separate.
