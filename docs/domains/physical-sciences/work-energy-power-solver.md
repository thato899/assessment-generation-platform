# Work, Energy & Power solver

`mechanics.work_energy_power_solver` is the single numerical authority for
M5. It consumes the authored objects in `mechanics.work_energy_power` and
returns frozen, typed derived results. It never writes into an authored
scenario. Issue #76 generation and later question/API layers validate or
consume results through this boundary.

## Identity and numerical policy

The stable solver identity is `caps-work-energy-power-solver`, version `1`.
`VALIDATION_TOLERANCE = 1e-9` is an internal physical-consistency tolerance;
it is not a learner-facing marking tolerance. Every arithmetic operation is
checked for overflow and non-finite output and maps to
`FailureReason.NUMERICAL_RANGE`. No intermediate or display rounding occurs.
Net work uses `math.fsum` in authored contribution order.

Angles of exactly 0, 90, and 180 degrees use exact cosine values of 1, 0, and
-1. Other bounded angles use deterministic trigonometry. This removes the
floating-point residue that ordinary cosine evaluation produces for an exact
perpendicular relationship.

## Failure semantics

`WorkEnergySolveError.reason` is one of:

- `UNDERDETERMINED`: valid authored structure lacks enough independent known
  quantities;
- `INCONSISTENT`: known authored values contradict a relationship or physical
  bound;
- `UNSUPPORTED`: a valid relationship lies outside the bounded CAPS solver;
- `NUMERICAL_RANGE`: checked arithmetic produced a non-finite result.

Domain construction errors remain `ValueError`; solver applicability and
numerical failures use the typed solver error.

## Work operations

`work_by_force` evaluates signed work from force magnitude, displacement
magnitude, and authored angle. Unknown quantities produce
`UNDERDETERMINED`; a contact contribution that is not maintained over the
full modeled displacement is `UNSUPPORTED`. No vectors or Newton calls are
inferred. `net_work` solves every contribution, preserves authored order, and
accumulates signed results with `math.fsum`; one unresolved contribution means
no net result is returned. `along_plane_work` multiplies the authored signed
resultant force by authored displacement and never derives a resultant.

## Energy operations

`kinetic_energy` uses only authored mass and non-negative speed magnitude.
`potential_energy` uses authored mass, positive near-Earth field magnitude,
and signed height relative to its explicit reference level. There is no hidden
9.8/9.81 default and no universal-gravitation operation.

`work_energy` applies `W_net = K_final - K_initial`. Its supported matrix is:

| Known data | Operation |
| --- | --- |
| both masses equal, both speeds known | derive and validate net work |
| equal known mass, initial speed and net work known, final speed unknown | derive final speed |
| equal known mass, final speed and net work known, initial speed unknown | derive initial speed |
| any unknown mass, two unknown speeds, or multiple unknowns | `UNDERDETERMINED` |

An authored `work_input` and authored `net_work` are independently reconciled
when both are present. Negative derived speed-squared beyond tolerance is
`INCONSISTENT`; a near-zero value is normalized to zero before taking the
square root.

`mechanical_energy` uses the sign convention

`W_non-conservative = (K_final + U_final) - (K_initial + U_initial)`.

It derives or validates non-conservative work, and supports one unknown speed
or one unknown relative height when all required masses and fields are known
and non-conservative work is authored. Multiple unknowns, unknown fields,
contradictory masses, and contradictory fields are `UNDERDETERMINED` or
`INCONSISTENT` as applicable. Initial and final field magnitudes must agree
within the internal tolerance; the solver never averages them.

## Power operations

`average_power` evaluates signed work divided by positive authored time.
`constant_speed_power` evaluates the authored signed along-motion force times
authored speed for either horizontal or inclined context; it does not take an
absolute value or infer friction. `pumping_power` evaluates positive mass-flow
rate times authored field magnitude times authored lift. Its result is
non-negative, contains no motor-efficiency field, and performs no density or
fluid-dynamics conversion.

## Results and validation

The public result families are `WorkResult`, `NetWorkResult`,
`AlongPlaneWorkResult`, `KineticEnergyResult`, `PotentialEnergyResult`,
`WorkEnergyResult`, `MechanicalEnergyResult`, `PowerResult`, and
`PumpingPowerResult`. `Watts` and the domain's signed/non-negative energy
wrappers preserve semantic signs. The solver exposes independent validation
methods for every result family; tampered values, ownership IDs, bases, or
authored relationships return an invalid `ValidationResult` rather than being
accepted or silently recomputed downstream.

All results are frozen and slotted. Repeated calls with the same authored
objects return equal values and do not touch global state or randomness.

## Dependency and exclusions

The package imports only Python standard library, the core validation result,
and the M5 authored domain. It does not import FastAPI, Pydantic, application
services, API DTOs, renderers, generators, questions, Newton, Momentum, or
Projectile solvers. It contains no generation, SVG, marking, learner
projection, motor efficiency, springs, or API route. #76 owns deterministic
scenario generation; later issues own presentation, questions, and API work.
