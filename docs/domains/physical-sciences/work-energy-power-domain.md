# Work, Energy & Power authored domain

This package defines the immutable authored facts accepted by the Grade 12
CAPS Work, Energy & Power slice. It is framework-independent and contains no
solver, generation, rendering, question, or API code. The merged #75 solver
derives numerical results from these facts, and the #76 factory creates
deterministic authored scenarios accepted by that solver.

## Boundary and invariants

All public objects are frozen, slotted dataclasses. Numeric wrappers reject
booleans, numeric strings, NaN, and infinities, normalize valid integers and
floats to `float`, and enforce their own physical ranges. Ordered authored
collections are copied to tuples and identifiers are non-empty and
deterministic. `UnknownValue.UNKNOWN` is distinct from zero and preserves
structurally valid underdetermined inputs for #75.

The domain performs structural validation only. It does not decide whether a
relationship is solvable or consistent, and it never calculates work, energy,
power, height differences, or gravitational results.

## Values and reuse decisions

The package uses local semantic value objects: `Mass`, `ForceMagnitude`,
`SignedForce`, `Displacement`, `Speed`, `TimeInterval`, `MassFlowRate`,
`GravitationalFieldMagnitude`, `AngleDegrees`, `RelativeHeight`, and signed
energy/work. `Kilograms` and `Seconds` are names for the corresponding local
types to match repository vocabulary.

Newton `Kilograms` was reviewed but is not reused because M5 owns its own
framework-independent semantic package and must not acquire a hidden Newton
dependency. Newton `Metres` is separation-specific and is not reused for
relative height. Newton `Newtons` represents signed force components rather
than force magnitudes, so it is not reused. Momentum's signed
`MetresPerSecond` is not reused as M5 speed, which is a non-negative
magnitude. Projectile `Metres` is non-negative position and is not reused for
signed reference-relative height. No shared-unit refactor was introduced.

## Work

`WorkContribution` stores an identifier, force magnitude, displacement,
authored angle from 0 to 180 degrees, and optional authored conservative or
non-conservative classification and contact condition. It does not store
derived work. `NetWorkInput` preserves an ordered tuple of unique
contributions without summing them. `AlongPlaneWorkInput` stores an explicit
signed resultant force and displacement along a declared plane; it does not
call Newton or infer a free-body diagram.

`ContactCondition` records whether contact is maintained over the
displacement. It does not determine a normal or friction force.

## Energy

`KineticState` carries explicit `INITIAL` or `FINAL` identity, mass, and
non-negative speed. It does not calculate or store kinetic energy.
`ReferenceLevel` is an authored semantic identity. `HeightState` associates a
state with that reference, a signed relative height, and an authored positive
near-Earth gravitational-field magnitude. Heights may be negative, zero, or
positive; no universal gravitational potential model is represented.

`WorkEnergyContext` retains initial/final kinetic states and authored or
unknown net work, optionally alongside a work input. It does not apply the
work-energy theorem. `MechanicalEnergyContext` retains initial/final kinetic
and height states plus authored or unknown non-conservative work. It checks
that both height states share the same reference level but does not calculate
mechanical energy, potential energy, or energy changes.

`ForceEnergyClassification` is authored metadata. The domain never infers a
classification from a force label.

## Power

`AveragePowerInput` stores signed work and positive time, each of which may be
unknown. `ConstantSpeedPowerInput` stores the authored signed force along
motion, non-negative speed, and horizontal/inclined surface context. It does
not infer force from Newton's Laws or friction. `PumpingPowerInput` stores
positive mass-flow rate, vertical lift, and an authored near-Earth field.
Motor efficiency is not a required field and is deferred as a future
non-ideal extension.

## Assumptions and scenario

`WorkEnergyAssumptions` provides optional typed flags for inertial frame,
constant mass, near-Earth field, constant force, constant speed, and declared
reference level. Omitted flags remain `None`; they are not inferred.
`WorkEnergyScenario` composes the authored structures, validates unique state
and reference identifiers, and checks that contexts reference declared
states and levels. It accepts incomplete and multiply unknown inputs when
their structure is coherent.

## Explicit exclusions

This package does not contain equations, trigonometry, numerical tolerances,
unknown solving, conservation calculations, friction or contact solving,
universal gravitation, motor efficiency, springs or spring potential energy,
random generation, SVG, questions, marking, learner projections, or API
routing. Those responsibilities remain outside #74; #75 owns deterministic
numerical solution and validation as documented in
[work-energy-power-solver.md](work-energy-power-solver.md), while #76 owns
scenario generation as documented in
[work-energy-power-scenario-generation.md](work-energy-power-scenario-generation.md).
