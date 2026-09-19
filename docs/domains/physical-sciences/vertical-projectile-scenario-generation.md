# Deterministic vertical-projectile scenario generation

`VerticalProjectileScenarioFactory` creates validated initial conditions for
the Physical Sciences vertical-projectile domain. It returns the existing
`VerticalProjectileScenario`; it does not create a parallel scenario model,
solve a trajectory, generate a question, or call the API.

## Input and output

`ScenarioGenerationInput` is an immutable request containing:

- a required non-negative `GenerationSeed`;
- an optional `ScenarioFamily` restriction;
- a concrete `Difficulty` (`introductory`, `moderate`, or `advanced`); and
- an explicit `PositiveDirection` (`up` or `down`).

The factory returns a scenario with the seed and a
`GenerationProvenance` value. The provenance records the stable factory ID,
policy version, seed, selected family, difficulty, and coordinate direction.

## Supported families

The policy supports four pedagogical initial-condition families:

1. upward projection from the reference level;
2. upward projection from an elevated position;
3. downward projection from an elevated position; and
4. dropping from rest from an elevated position.

When no family is requested, the factory selects one deterministically from
the policy's allowed families. An explicit family is always honoured or
rejected if the policy does not allow it.

## Platform generation policy

The default policy is version `1` and uses discrete platform-generation pools:

| Difficulty | Initial-speed magnitudes (m/s) | Elevated heights (m) |
| --- | --- | --- |
| Introductory | 10, 15 | 5, 10 |
| Moderate | 15, 20, 25 | 10, 15, 20, 25 |
| Advanced | 20, 25, 30 | 15, 20, 25, 30 |

The platform policy uses a gravity magnitude of `10.0 m/s^2`. The discrete
integer pools keep generated inputs teachable, bounded, and reproducible;
they are not arbitrary per-request floats.

These values are platform generation policy, not a replacement for CAPS
constraints. CAPS curriculum metadata and later validation determine whether a
generated scenario is appropriate for a particular curriculum context. The
factory owns numeric generation policy only and does not encode
Physical-Sciences question or marking logic.

## Sign and direction policy

Gravity is always signed to point downward in the requested coordinate system:
`-10.0 m/s^2` when up is positive and `+10.0 m/s^2` when down is positive.
Initial velocity is signed consistently with the selected launch direction.

The current `Metres` value object requires a non-negative launch position. As
a result, down-positive generation currently supports only upward projection
from the reference level: an elevated position would need a negative
coordinate in that convention. The factory rejects incompatible explicit
requests and filters them out of automatic family selection rather than
silently changing the requested convention.

## Reproducibility and boundaries

The factory constructs a local `random.Random` from the supplied seed. It does
not use module-global random state, timestamps, UUIDs, or arbitrary floating
point sampling. The same input and policy version produce the same scenario;
the scenario identifier includes the policy version, family, difficulty,
direction, and seed. A policy change must increment its version when it can
change generated values or identifiers.

The factory does not import or depend on `VerticalProjectileSolver` or the
question generator. The solver remains authoritative for all trajectory
calculations and validation. The v1 FastAPI generation endpoint remains
unavailable with HTTP 503 until the later application orchestration work is
complete.
