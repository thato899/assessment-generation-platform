# Deterministic Momentum & Impulse scenario generation

Issue #32 adds a versioned `MomentumScenarioFactory` for deterministic initial
conditions. It creates valid `MomentumScenario` input data for future
downstream consumers; it does not calculate momentum, solve collisions, or
generate final body states.

## Supported families

The platform policy currently supports three initial-condition families:

1. `single-body`: one body with a generated mass and a right, left, or rest
   initial velocity in an isolated system;
2. `opposite-moving-isolated`: two bodies moving in opposite physical
   directions in an isolated system; and
3. `external-impulse`: two opposite-moving bodies in a non-isolated system
   with one explicitly generated net external impulse.

The third family remains an initial-state scenario. It does not imply a
collision result or provide final body velocities.

## Platform policy versus CAPS

The factory's bounded mass, speed, and external-impulse pools are platform
generation policy. They are not claims about CAPS-prescribed numeric ranges.
Curriculum applicability remains a separate concern. The current policy is
version `1`:

| Difficulty | Masses (kg) | Speed magnitudes (m/s) | External impulse magnitudes (N·s) |
| --- | --- | --- | --- |
| Introductory | 1, 2 | 2, 4 | 0, 2 |
| Moderate | 2, 3, 4 | 3, 5, 7 | 0, 3, 6 |
| Advanced | 3, 4, 5 | 4, 6, 8 | 0, 4, 8 |

## Determinism and sign handling

`MomentumScenarioGenerationInput` requires a non-negative `GenerationSeed`.
The factory uses a local `random.Random` instance. An omitted family or axis
is selected deterministically from the policy; explicit values are honored or
rejected if the policy disallows them. Stable identifiers and
`GenerationProvenance` record the policy version, selected family, difficulty,
axis, and seed.

Velocity signs are derived from physical direction and the explicit
`PositiveAxis.RIGHT` or `PositiveAxis.LEFT` convention. The factory never
assumes that right is positive and never converts solver outputs or fabricates
final states.

## Boundaries

The factory imports no solver, renderer, API framework, or question generator.
It does not call `MomentumImpulseSolver` and does not reproduce its equations.
Generated scenarios may remain collision-underdetermined. Solver-authoritative
calculations, questions, visualizations, and API integration remain later M3
work.
