# Momentum & Impulse problem-generation policy

Issue #38 adds a framework-independent companion factory,
`MomentumProblemFactory`, for authored Momentum & Impulse inputs. It composes
the Issue #32 `MomentumScenarioFactory`; it does not replace or change that
factory's public behaviour.

## Policy boundary

CAPS supplies the Grade 12 concepts, one-dimensional applicability, signed
vector reasoning, conservation principles, and impulse relationships. The
numeric pools below are platform generation policy, not CAPS-prescribed
ranges. The policy is versioned as `2`; the composed Issue #32 scenario policy
remains version `1`.

The factory produces inputs. Existing solvers remain authoritative for
momentum, momentum change, impulse, force, contact time, constrained final
states, and collision classification. No answer or solver result is stored in
the generated problem envelope.

## Families and typed outputs

`MomentumGenerationFamily` selects one of these families:

| Family | Authored output | Authoritative solver |
| --- | --- | --- |
| `INITIAL_MOMENTUM` | Issue #32 single-body `MomentumScenario` | `MomentumImpulseSolver` |
| `MOMENTUM_CHANGE` | `MomentumChangeInput` | `MomentumImpulseRelationshipSolver` |
| `IMPULSE_FORCE_TIME` | `ForceTimeInput` | `MomentumImpulseRelationshipSolver` |
| `FORCE_FROM_MOMENTUM_CHANGE` | `MomentumChangeInput` plus positive `Seconds` | `MomentumImpulseRelationshipSolver` |
| `CONTACT_TIME_FROM_IMPULSE_FORCE` | signed non-zero `Impulse` and same-sign `Newtons` | `MomentumImpulseRelationshipSolver` |
| `KNOWN_FINAL_VELOCITY_COLLISION` | two-body scenario plus one `KnownFinalVelocityConstraint` | `ConstrainedMomentumSolver` |
| `STICKING_COLLISION` | two-body scenario plus `CommonFinalVelocityConstraint` | `ConstrainedMomentumSolver` |
| `COMPLETE_FINAL_STATE_COLLISION` | two-body scenario plus complete authored final states | `ConstrainedMomentumSolver` |

Typed generated variants prevent unrelated force, time, and collision fields
from being combined accidentally. Collision variants contain an authored
`MomentumInteraction`, not a derived solution.

## Bounded difficulty policy

Every profile uses finite, duplicate-free, positive pools:

| Difficulty | Masses (kg) | Speed magnitudes (m/s) | Force magnitudes (N) | Contact times (s) | Impulse magnitudes (N.s) |
| --- | --- | --- | --- | --- | --- |
| Introductory | 1, 2 | 2, 4 | 2, 4 | 1, 2 | 2, 4 |
| Moderate | 2, 3, 4 | 3, 5, 7 | 3, 5, 7 | 0.5, 1, 2 | 3, 5, 7 |
| Advanced | 3, 4, 5 | 4, 6, 8 | 4, 6, 8 | 0.2, 0.5, 1 | 4, 6, 8 |

Introductory momentum-change cases use speeding up. Moderate cases choose
speeding up, slowing down, stopping, or starting from rest. Advanced cases
add direction reversal. Force/contact-time inputs always use positive contact
times. Contact-time-from-impulse-and-force chooses impulse and force in the
same physical direction so their quotient is positive; it never repairs an
invalid pair with `abs()`.

Both `PositiveAxis.RIGHT` and `PositiveAxis.LEFT` are supported. Physical
directions are selected first and converted to signed values using the chosen
axis. A requested axis is respected; an omitted axis is selected by the local
seeded RNG.

## Collisions

Known-final-velocity generation selects a stable body identifier and authors
exactly one signed final velocity. The other final velocity is absent and is
derived only by `ConstrainedMomentumSolver`. Sticking generation authors the
two-body common-final-velocity constraint and no common velocity. Complete
final-state generation creates bounded authored candidates and accepts one
only after `ConstrainedMomentumSolver` validates the resulting interaction;
the factory does not reproduce conservation or energy equations.

## Determinism and provenance

`MomentumProblemGenerationInput` requires a `GenerationSeed` and optionally
selects family, difficulty, and positive axis. Each generation call uses a
local `random.Random(seed.value)`, so global random state is unchanged. Stable
identifiers include the problem factory, policy version, selected family,
difficulty, axis, and seed. `GenerationProvenance` records the factory ID
`caps-grade-12-momentum-impulse-problem-factory`, policy version, seed, and
the selected family/difficulty/axis template identifiers.

## Deferred boundaries

Issue #38 does not add question text, marking, SVG, application orchestration,
or API support. Those remain planned for #39 (SVG), #40 (calculation
questions), #41 (conceptual templates and rubrics), and #42 (application/API
integration). No CAPS-specific numeric claims or LMS integration belong in
this policy.
