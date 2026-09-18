# Vertical projectile scenario model

`VerticalProjectileScenario` represents only the initial state and modelling assumptions for a CAPS Grade 12 one-dimensional vertical projectile. It is framework-independent and is the future single source of truth for the solver, validator, renderer, question generator, worked solution, and marking rubric.

The model uses explicit SI value objects: `Metres`, `MetresPerSecond`, and `MetresPerSecondSquared`. A scenario must declare whether up or down is positive. Velocity and gravitational acceleration are stored with signs in that coordinate system; gravity must point downward. Launch direction must agree with the signed initial velocity, and a rest launch must have zero velocity.

Supported initial configurations are upward projection, downward projection, and dropping from rest. Each can start at the reference level (`0 m`) or an elevated non-negative position. An optional shared `GenerationSeed` records reproducibility metadata but does not generate randomness.

The CAPS assumptions currently represented are near-Earth motion, no air friction, and one-dimensional vertical motion. Calculations such as maximum height, time of flight, impact velocity, and graph coordinates are intentionally deferred to the solver and renderers.
