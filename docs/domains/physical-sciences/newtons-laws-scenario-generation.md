# Newton's Laws scenario generation

Issue #57 adds a bounded generation boundary after the authored #55 domain and
the authoritative #56 solver:

```text
GenerationSeed + NewtonGenerationPolicy
        -> NewtonProblemFactory
        -> authored NewtonScenario
        -> NewtonSolver result
```

The factory authors a physical situation. It does not calculate a resultant,
acceleration, friction limit, tension, weight or gravitational force, and it
never replaces an authored `UnknownValue` with a solver answer.

## Versioned inputs, outputs and provenance

`NewtonGenerationInput` is frozen and contains a `GenerationSeed`, an optional
`NewtonGenerationFamily`, and the shared platform `Difficulty`. The immutable
`NewtonGenerationPolicy` owns platform pools, the allowed family set, and
`policy_version`. `NewtonProblemFactory` has generator ID
`caps-m4-newton-scenario-factory` and generator version `1`.

Generated variants carry a stable metadata record, the authored
`NewtonScenario`, and only family-specific semantic request data:

- `GeneratedNewtonIIProblem`, `GeneratedEquilibriumProblem`, and
  `GeneratedWeightProblem`;
- `GeneratedUnknownForceProblem` with its target force ID;
- `GeneratedContactProblem` with its contact ID;
- `GeneratedConnectedBodiesProblem` with a `StraightStringRequest`;
- `GeneratedGravitationProblem` with its interaction ID; and
- `GeneratedThirdLawProblem` with its `ThirdLawPair`.

The scenario ID and provenance template IDs are derived from policy version,
family, difficulty and seed. Generation uses a local `random.Random`; it never
seeds or reads Python's global random state. The same policy, input and seed
replay byte-for-byte equivalent frozen objects.

## Supported families and policy

The policy covers bounded single-body Newton II, unknown force, equilibrium,
authored gravitational field/weight, horizontal normal contact, static,
limiting-static and kinetic friction, surface-aligned incline, two-body
straight light string, universal gravitation, and Newton III pair scenarios.
Difficulty changes the discrete mass, force, acceleration, field, coefficient,
inclination, normal-force and separation pools. These are platform choices;
CAPS metadata remains separate from numeric policy.

Every family is solver-validated before it is returned:

| Family | Authoritative check |
| --- | --- |
| Newton II / equilibrium | `NewtonSolver.body_dynamics` and `validate_dynamics` |
| Unknown force | `NewtonSolver.solve_force` |
| Weight | `NewtonSolver.weight` |
| Contact and friction | `NewtonSolver.contact_forces` |
| Connected bodies | `NewtonSolver.connected_bodies` |
| Universal gravitation | `NewtonSolver.gravitational_force` |
| Third law | `NewtonSolver.validate_third_law` |

The generated corpus contains no pulleys, string networks, slack or extensible
strings, Cartesian inclined contacts, symbolic systems, N-body systems, 3D
geometry, rendering fields, questions, marking data or API routing. Surface
inclines use authored surface-aligned field components already supported by the
solver; the factory does not perform `sin`/`cos` resolution.

## Authored-data boundary

Unknown-force, contact, friction and string families retain their unknown
components in the generated scenario. Their semantic target or solve request
is carried separately for later question generation. Derived answers exist
only in the `NewtonSolver` result, so generation cannot become a second solver.

The policy uses constructive bounded inputs for supported cases. If future
families require candidate rejection, they must use a deterministic finite
retry count and fail explicitly after exhaustion; no unbounded retry loop or
silent value mutation is permitted. Issue #58 owns force/free-body rendering,
#59/#60 own questions and rubrics, and #61 owns API integration.
