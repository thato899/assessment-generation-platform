# Vertical projectile solver

`VerticalProjectileSolver` is the authoritative deterministic calculator for a validated `VerticalProjectileScenario`. It returns structured numeric values and trajectory events, not prose or formatted learner answers.

The solver uses the scenario's signed coordinate system directly. It does not assume upward is positive or invent a gravitational constant. It supports position, velocity, displacement, maximum-height, return-to-launch-position, and ground-impact results for upward-positive and downward-positive scenarios, including dropped objects.

Internal calculations retain floating-point precision. No intermediate rounding is performed. Event times use a `1e-9` second positive-root tolerance, and solution validation uses a `1e-9` value tolerance. Presentation rounding remains downstream.

For quadratic position roots, the solver ignores non-positive roots for later events and selects the smallest positive root. This explicitly excludes the launch root at `t = 0` while preserving the physically relevant later ground impact. Solution validation checks event times, positions, velocities, maximum-height velocity, and event-specific positions against the input scenario.
