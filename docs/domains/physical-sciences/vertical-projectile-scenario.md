# Vertical projectile scenario model

`VerticalProjectileScenario` represents only the initial state and modelling assumptions for a CAPS Grade 12 one-dimensional vertical projectile. It is framework-independent and is the future single source of truth for the solver, validator, renderer, question generator, worked solution, and marking rubric.

The model uses explicit SI value objects: `Metres`, `MetresPerSecond`, and `MetresPerSecondSquared`. A scenario must declare whether up or down is positive. Velocity and gravitational acceleration are stored with signs in that coordinate system; gravity must point downward. Launch direction must agree with the signed initial velocity, and a rest launch must have zero velocity.

Supported initial configurations are upward projection, downward projection, and dropping from rest. Each can start at the reference level (`0 m`) or an elevated non-negative position. An optional shared `GenerationSeed` records reproducibility metadata but does not generate randomness.

The CAPS assumptions currently represented are near-Earth motion, no air friction, and one-dimensional vertical motion. Calculations such as maximum height, time of flight, impact velocity, and graph coordinates are intentionally deferred to the solver and renderers.

## Solver boundary

The solver consumes this scenario and uses `position(t) = position₀ + velocity₀t + ½acceleration·t²` and `velocity(t) = velocity₀ + acceleration·t` without rounding intermediate values. It reports structured launch, maximum-height, return-to-launch-position, and ground-impact events when physically meaningful. Positive roots are selected only when they are later than the launch-time tolerance; the launch root at `t = 0` is not treated as a later impact.
