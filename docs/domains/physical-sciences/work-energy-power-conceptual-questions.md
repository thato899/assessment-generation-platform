# Work, Energy & Power conceptual-question generation

Issue #82 adds a context-free conceptual assessment layer for the Grade 12
CAPS `work-energy-and-power` Mechanics topic. The generator creates canonical
`Question` and `QuestionPart` objects with machine-readable concept-token
answers and declarative marking schemes. It does not solve numerical physics,
evaluate learner responses, or route through the application API.

## Stable contract

- Generator ID: `caps-grade-12-work-energy-power-conceptual-question-generator`
- Version: `1`
- Topic: `work-energy-and-power`, CAPS Physical Sciences, Grade 12, Mechanics
- Default options: `include_visuals=False`
- Question ID: `wep-conceptual-v1-<template.value>`
- Part ID: `<question-id>.response`

Every template has one conceptual part. Short definitions use
`ResponseKind.SHORT_TEXT`; multi-point explanations use
`ResponseKind.LONG_TEXT`. Responses expect key points and a final response,
but not working or units. Each answer is `ExpectedAnswerKind.TEXT` containing a
stable tuple of concise semantic tokens. Tokens are internal answer meaning;
they are not shown in prompts and are not numerical answers.

## Template inventory

| Template | Conceptual focus | Main protection |
| --- | --- | --- |
| `WORK_DEFINITION` | Force-displacement meaning of work | A force alone does not guarantee work. |
| `WORK_IS_SCALAR` | Work as a signed scalar | Signed work is not a vector. |
| `POSITIVE_NEGATIVE_ZERO_WORK` | Positive, negative, and zero work | Sign follows the force-displacement relationship. |
| `PERPENDICULAR_ZERO_WORK` | Perpendicular force | A large perpendicular force can still do zero work. |
| `INDIVIDUAL_VS_NET_WORK` | One contribution versus scalar net work | The selected force is distinct from the relevant total. |
| `NET_WORK_AND_KINETIC_ENERGY` | Net-work sign and kinetic-energy change | Zero net work does not require rest. |
| `WORK_ENERGY_THEOREM` | Net work and kinetic-energy change | Both quantities remain scalar. |
| `KINETIC_ENERGY_CONCEPT` | Energy of motion | Kinetic energy follows speed magnitude, not velocity sign. |
| `POTENTIAL_ENERGY_REFERENCE_LEVEL` | Relative gravitational potential energy | The reference level is selected; values may be negative. |
| `CONSERVATIVE_FORCE` | Conservative-force meaning | No calculus or line-integral definition is introduced. |
| `CONSERVATIVE_VS_NON_CONSERVATIVE` | Force classification | The distinction is connected to mechanical-energy accounting. |
| `MECHANICAL_VS_TOTAL_ENERGY` | Mechanical versus total energy | Mechanical energy may change while total system energy remains conserved. |
| `FRICTION_NON_CONSERVATIVE_WORK` | Friction and mechanical-energy change | Friction is not assigned one sign in every configuration. |
| `POWER_AS_RATE` | Power as a rate | Power is distinct from work and energy. |
| `SAME_WORK_DIFFERENT_TIME` | Equal work over different times | Less time means a greater average rate. |
| `CONSTANT_SPEED_POWER_CONTEXT` | Rough horizontal/inclined constant-speed context | Constant speed does not mean no forces act. |
| `PUMPING_POWER_ASSUMPTIONS` | Minimum ideal pumping model | Flow, lift, field, and the motor-efficiency exclusion are explicit. |

## Concept tokens and rubrics

Each spec declares unique tokens and positive criterion marks. Criteria use
stable IDs and descriptive credit conditions. Their marks sum exactly to the
part marks and define what a complete answer should address. They are not a
scoring function: the module contains no keyword matching, token matching,
fuzzy matching, semantic similarity, learner-response evaluator, LLM grader,
or automatic marking engine.

The rubrics protect the approved distinctions. Work remains scalar; positive,
negative, zero, and perpendicular cases are related to force and displacement.
Net work is distinguished from an individual contribution, and its sign is
linked conceptually to kinetic-energy change. Kinetic energy is associated with
motion and uses speed magnitude. Gravitational potential energy is relative to
a chosen reference level.

Conservative and non-conservative forces are distinguished without calculus.
Mechanical energy is kept separate from total system energy. Friction may
change mechanical energy while internal or thermal transfer remains within the
total-energy account. Power is a rate rather than work or energy. The
constant-speed template states that forces can still act. Pumping covers mass
flow, vertical lift or depth, and an authored gravitational field under a
minimum ideal model; motor efficiency is outside the required CAPS model.

## Determinism and learner safety

Generation is context-free and does not require `WorkEnergyProblemFactory`.
An optional `GenerationSeed` is recorded as provenance only; it never changes
the selected template or prompt. Questions have no scenario metadata, no
visuals, and no answer-dependent values. `include_visuals=True` remains safe
and deterministic by producing the same visual-free question because no
contextual diagram is justified for this bounded layer.

Prompts contain learner wording only. Concept tokens, criterion IDs,
marking schemes, and hidden answers are not copied into prompts, provenance,
or scenario data. IDs contain only the generator version and template value;
they contain no answer, timestamp, UUID, or process-hash data.

## Boundaries

The conceptual module imports only core assessment contracts and CAPS topic
metadata. It does not import `WorkEnergySolver`, the calculation generator,
any Newton/Momentum/Projectile engine, FastAPI, application services, DTOs,
LLM SDKs, marking engines, or PDF/LMS libraries. It contains no numerical
equations or result types. Calculation questions remain Issue #78, API
integration remains Issue #83, and final M5 verification remains Issue #84.
