# Newton's Laws deterministic solver

Issue #56 is the numerical boundary after the authored
[`NewtonScenario`](newtons-laws-domain.md) model from Issue #55:

```text
authored NewtonScenario -> NewtonSolver -> immutable derived results
```

The solver is framework-independent and deterministic. It does not generate
scenarios, write questions, render diagrams, mark responses, or expose an API.
It never mutates the authored scenario and never hides an unknown component by
returning zero.

## Public boundary

`NewtonSolver` consumes one authored scenario and exposes operations for:

- acting-force resultants and required resultants from authored acceleration;
- Newton II body dynamics, acceleration and equilibrium;
- solving one unknown force component per independent axis;
- validating authored accelerations and Newton III pairs;
- deriving weight from an authored gravitational field;
- normal force, apparent weight/weightlessness, and bounded static,
  limiting-static and kinetic friction;
- one straight, taut, inextensible, massless string joining two bodies; and
- scalar universal-gravity magnitude plus magnitude-only validation.

Derived values are frozen, slotted result objects. `ForceResult`,
`ResultantResult`, `BodyDynamicsResult`, `WeightResult`, `ContactResult`,
`FrictionResult`, `ConnectedBodiesResult` and `GravitationalResult` contain no
unknown components. `StraightStringRequest` records the explicit sign of the
pull on the first endpoint because the authored domain has no relative
position or pulley direction.

## Numerical policy

The package centralizes solver identity/version, the absolute validation
tolerance (`1e-9`), finite-value checks, `math.fsum` accumulation and the DBE
gravitational constant (`6.67e-11`). Intermediate values and returned values
are not rounded. Force components retain their authored coordinate basis;
surface-aligned components are not transformed a second time.

## Failure semantics

`NewtonSolveError.reason` is one of:

- `UNDERDETERMINED`: the authored facts do not identify a unique result;
- `INCONSISTENT`: authored values violate Newton or contact relationships;
- `UNSUPPORTED`: the request requires geometry or constraints outside this
  bounded solver; or
- `NUMERICAL_RANGE`: a calculation is non-finite or underflows/overflows.

No partial dynamics result is returned when any axis remains unresolved.
Contact direction is checked structurally, static friction is solved from the
required balance within its Coulomb bound, and kinetic/limiting-static
friction does not invent a direction when none is authored. Inclined Cartesian
contacts, slack or extensible strings, string networks, symbolic systems,
N-body systems, pulleys and 3D geometry remain outside this issue.

## Validation and regression coverage

The focused suite in `tests/unit/test_newton_solver.py` covers signed 1D/2D
resultants, Newton II, independent unknown resolution, underdetermination,
third-law/free-body semantics, authored fields and weight, contact/friction,
apparent weight, surface-aligned inclines, straight strings, gravitation,
no-rounding/replayability, immutable results and independent tamper
validation. The solver has no dependency on generation, rendering, API,
question or marking packages.
