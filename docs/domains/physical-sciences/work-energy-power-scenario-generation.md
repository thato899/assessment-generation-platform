# Work, Energy & Power scenario generation

Generated authored scenarios may be rendered by the independent Issue #77 SVG presentation layer;
the renderer does not inspect generator metadata or solver answers.

Issue #76 adds the bounded scenario factory for the authored M5 domain. The
factory chooses authored facts and delegates every solvability decision and
numerical result to `mechanics.work_energy_power_solver`. It never copies
solver equations, stores a result, or changes an authored object after it has
been constructed.

## Identity and public API

The stable generator identity is
`caps-m5-work-energy-power-scenario-factory`, version `1`, with policy version
`1`. The public API is `WorkEnergyGenerationInput`,
`WorkEnergyGenerationFamily`, `WorkEnergyDifficultyProfile`,
`WorkEnergyGenerationPolicy`, `DEFAULT_WORK_ENERGY_GENERATION_POLICY`, and
`WorkEnergyProblemFactory`. `GeneratedWorkEnergyMetadata` and
`GeneratedWorkEnergyProblem` carry the generated authored scenario and target
identifier where a later question family needs one. They contain no answer or
solver-result field. Potential-energy cases carry their authored mass in the
wrapper because the #74 scenario model stores height states independently.

The input requires a `GenerationSeed`; raw integers are rejected. An omitted
family is selected from the policy's allowed families. An explicit family must
be allowed by the policy and is honoured without substitution.

## Family inventory and solver boundary

| Family | Authored data | Acceptance operation |
| --- | --- | --- |
| `WORK_BY_FORCE` | force magnitude, displacement, angle | `work_by_force` |
| `NET_WORK` | ordered unique contributions | `net_work` |
| `ALONG_PLANE_WORK` | signed resultant and displacement | `along_plane_work` |
| `KINETIC_ENERGY` | mass and speed | `kinetic_energy` |
| `GRAVITATIONAL_POTENTIAL_ENERGY` | mass, reference level, height, field | `potential_energy` |
| `WORK_ENERGY_NET_WORK` | complete states, work input, unknown net work | `work_energy` |
| `WORK_ENERGY_FINAL_SPEED` | known initial state and net work, unknown final speed | `work_energy` |
| `WORK_ENERGY_INITIAL_SPEED` | known final state and net work, unknown initial speed | `work_energy` |
| `MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK` | complete kinetic/height states, unknown non-conservative work | `mechanical_energy` |
| `MECHANICAL_ENERGY_FINAL_SPEED` | known initial state, heights, and non-conservative work, unknown final speed | `mechanical_energy` |
| `AVERAGE_POWER` | signed work and positive time | `average_power` |
| `CONSTANT_SPEED_POWER` | signed along-motion force, speed, horizontal/inclined context | `constant_speed_power` |
| `PUMPING_POWER` | positive mass flow, lift, explicit field | `pumping_power` |

The factory calls the relevant operation before returning. The transient
result is discarded. No unsupported mass-solving, hidden field, motor
efficiency, friction inference, Cartesian geometry, or cross-domain solver is
introduced.

## Determinism, profiles, and IDs

Each request creates a local `random.Random(seed.value)`. Module-level random
state is never seeded or consumed. Repeated requests reproduce the family,
authored values, ordering, identifiers, and provenance. The three immutable
profiles contain finite, non-duplicate pools for masses, force magnitudes,
displacements, angles, speeds, relative heights, gravitational fields, time,
mass-flow rates, along-motion force magnitudes, non-conservative work, and net
contribution counts. Profiles differ in available pedagogical values and
angle/context variety; advanced does not mean only larger numbers.

Identifiers use the answer-free form
`wep-problem-v1-<family>-<difficulty>-seed-<seed>`. Provenance contains the
generator ID/version, seed, family, difficulty, and policy template ID only.
No timestamp, UUID, derived work, energy, speed, power, or solver result is
encoded.

## Unknowns, retries, and immutability

Final-speed, initial-speed, and mechanical-energy target cases preserve
`UnknownValue.UNKNOWN` in the returned scenario. The solver may derive a
temporary value in its immutable result, but that value is never written back.
The non-conservative-work target follows the same rule.

Random combinations that can be physically inconsistent are attempted at most
64 times using the same local RNG. Only expected solver inconsistency or
numerical-range failures are retried. Underdetermined, unsupported, or other
programming failures are surfaced explicitly; a family is never silently
changed.

## Boundaries

Generation imports only the core seed/provenance/difficulty types, the #74 M5
authored domain, the #75 solver, and the Python standard library. It adds no
renderer, SVG, question, conceptual, marking, API, FastAPI, Pydantic, Newton,
Momentum, or Projectile code. Issue #77 owns technical visuals and #78 owns
calculation questions.
