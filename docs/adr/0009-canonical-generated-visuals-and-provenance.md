# ADR 0009: Renderer-neutral visuals and minimal generation provenance

- Status: Accepted
- Date: 2026-09-18

## Context

The first subject question generator needs to return canonical assessment data,
carry an existing deterministic SVG, and expose enough metadata to reproduce a
generated question. The core model must not depend on the SVG renderer or an
HTTP framework, and a general asset-management or provenance system would be
premature.

## Decision

Add two small framework-independent value objects to the core model:
`VisualReference` carries an identifier, media type, serialized content, and
dimensions; `GenerationProvenance` carries generator ID/version, an optional
existing `GenerationSeed`, and selected template IDs. `Question` may contain
tuples of both values. Subject generators convert renderer output into the
generic visual value and retain solver/template metadata there.

The vertical-projectile generator uses the existing SVG renderer with numeric
event labels disabled. It does not calculate physics or use random UUIDs,
timestamps, or module-global randomness.

## Consequences

Canonical questions can carry deterministic visual and reproducibility data
without importing rendering, FastAPI, or Pydantic into the domain. The values
are intentionally not a universal asset store or provenance framework; future
needs must justify any extension. Learner/API projection and authentication
remain separate application concerns.
