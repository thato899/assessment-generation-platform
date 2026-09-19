# Momentum & Impulse domain foundation

Issue #28 establishes the first M3 domain boundary for one-dimensional
Momentum & Impulse scenarios. It is intentionally an initial-state model;
the deterministic solver, scenario factory, question generator, renderer, and
API are later issues.

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

## Boundaries

The module imports only framework-independent core seed/provenance types. It
does not depend on FastAPI, Pydantic, HTTP, persistence, rendering, LLMs, or
LMS integrations. No Momentum API support is added by Issue #28, and the
existing vertical-projectile pipeline remains separate.
