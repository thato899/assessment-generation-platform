# Work, Energy & Power calculation-question generation

Issue #78 packages each generated M5 authored problem as one canonical Grade 12
CAPS calculation question. `WorkEnergyCalculationQuestionGenerator` owns
wording, stable question/part IDs, response specifications, expected-answer
packaging, marking criteria, provenance, optional Issue #77 visuals, and safe
applicability failures.

## Contract and family matrix

The generator requires the exact `work-energy-and-power` CAPS Grade 12 Physical
Sciences Mechanics topic. It receives an already generated
`GeneratedWorkEnergyProblem`; it does not select seeds, mutate scenarios, or
recalculate physics. Every numeric `ExpectedAnswer` comes directly from
`WorkEnergySolver`. Learner tolerance is `0.01`, separate from the solver's
internal consistency tolerance.

| Family | Generated input and solver operation | Unit | Diagram | Marks |
| --- | --- | --- | --- | ---: |
| `WORK_BY_FORCE` | `WorkContribution` → `work_by_force` | J | `WORK_CONTRIBUTIONS` | 3 |
| `NET_WORK` | `NetWorkInput` → `net_work` | J | `WORK_CONTRIBUTIONS` | 4 |
| `ALONG_PLANE_WORK` | `AlongPlaneWorkInput` → `along_plane_work` | J | `ALONG_PLANE` | 3 |
| `KINETIC_ENERGY` | `KineticState` → `kinetic_energy` | J | `MOTION_STATES` | 3 |
| `GRAVITATIONAL_POTENTIAL_ENERGY` | authored `Mass` + `HeightState` → `potential_energy` | J | `HEIGHT_STATES` | 4 |
| `WORK_ENERGY_NET_WORK` | `WorkEnergyContext` → `work_energy` net work | J | `MOTION_STATES` | 3 |
| `WORK_ENERGY_FINAL_SPEED` | `WorkEnergyContext` → `work_energy` final speed | m/s | `MOTION_STATES` | 4 |
| `WORK_ENERGY_INITIAL_SPEED` | `WorkEnergyContext` → `work_energy` initial speed | m/s | `MOTION_STATES` | 4 |
| `MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK` | `MechanicalEnergyContext` → `mechanical_energy` non-conservative work | J | `HEIGHT_STATES` | 4 |
| `MECHANICAL_ENERGY_FINAL_SPEED` | `MechanicalEnergyContext` → `mechanical_energy` final speed | m/s | `HEIGHT_STATES` | 5 |
| `AVERAGE_POWER` | `AveragePowerInput` → `average_power` | W | none | 3 |
| `CONSTANT_SPEED_POWER` | `ConstantSpeedPowerInput` → `constant_speed_power` | W | `CONSTANT_SPEED_SURFACE` | 3 |
| `PUMPING_POWER` | `PumpingPowerInput` → `pumping_power` | W | `PUMPING` | 4 |

The mapping is exhaustive. A question has one assessable `QuestionPart`; its
calculation response specification expects working, a final value, and units.
Criteria cover method, authored substitution/sign handling, and the final
answer, and always reconcile exactly to the part mark allocation.

## Boundaries and reproducibility

Signed work, net work, relative potential energy, non-conservative work, and
solver-defined power retain their signs. Kinetic energy, speed, and ideal
pumping power retain their solver-defined non-negative semantics. Unknown
values remain unknown in the authored problem and are requested in the part;
no unknown is printed as zero or copied from a derived solver result into the
prompt. Prompt and metadata values are authored givens only, with no answer
leakage.

IDs are deterministic: `wep-question-v1-<generated-problem-id>` and a
family-template suffix for the part. Provenance records the generator ID,
version, seed, and template. The answer-free `Scenario` metadata records only
topic, grade, domain, family, and difficulty. `include_visuals=True` adds one
safe authored-only SVG for supported families; average power intentionally has
no visual. `include_visuals=False` produces no visuals while leaving all other
fields unchanged. The memorandum is derived by the platform from the same
`QuestionPart` answer and marking scheme, so no parallel M5 memo model exists.

Solver applicability failures (`UNDERDETERMINED`, `INCONSISTENT`,
`UNSUPPORTED`, or numerical-range failures) are surfaced as a safe generator
refusal with no partial question. The module has no physics equations, API
route, conceptual rubric, automatic marker, worked-solution engine, PDF/LMS
output, or new generation policy. Conceptual questions remain Issue #82 and API
integration remains Issue #83.
