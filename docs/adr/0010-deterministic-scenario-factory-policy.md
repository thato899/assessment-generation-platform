# ADR 0010: Versioned policy for deterministic scenario factories

- Status: Accepted
- Date: 2026-09-19

## Context

The application needs reproducible vertical-projectile inputs before it can
orchestrate the solver and question generator. The existing scenario model is
the domain source of truth, while CAPS metadata and the future application
service have different responsibilities. A factory also needs bounded,
pedagogically useful numeric choices without introducing global random state
or a second scenario representation.

## Decision

Define immutable `ScenarioGenerationInput`, `DifficultyProfile`, and
`VerticalProjectileGenerationPolicy` value types alongside a
`VerticalProjectileScenarioFactory` in the Physical Sciences mechanics domain.
The factory uses only a local `random.Random` initialized from
`GenerationSeed`, creates the existing `VerticalProjectileScenario`, and
records factory and policy version metadata through the existing
`GenerationProvenance` value.

The default policy owns discrete platform-generation pools and a gravity
magnitude. It is explicitly separate from CAPS curriculum constraints. The
factory performs no solving, question generation, API work, or curriculum
selection. Down-positive elevated cases are rejected because the current
non-negative `Metres` position value object cannot represent their required
negative coordinate relative to the reference level.

## Consequences

Scenario generation can be tested as a deterministic domain boundary and
replayed from a seed and policy version. Solver authority and framework
independence are preserved. Numeric policy changes require an explicit policy
version decision. Supporting down-positive elevated coordinates later requires
an intentional change to the position model and its dependent renderers and
solver semantics; the factory will not hide that change through conversion.
