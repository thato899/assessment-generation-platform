# ADR 0008: Versioned assessment generation API boundary

- Status: Accepted
- Date: 2026-09-18

## Context

The platform needs a stable public contract before a real assessment generator
exists. The contract must preserve framework-independent core models, support
deterministic seeds, and prevent learner responses from leaking teacher-side
answers or marking data.

## Decision

Expose explicit Pydantic DTOs at `/api/v1/assessments/generate`, mapped into
core value objects at the boundary. Reject unknown request fields, validate
the documented identifier and numeric ranges, and return stable error codes.
The initial application generation service supports only the documented CAPS
Grade 12 Physical Sciences vertical-projectile capability. Unsupported
capabilities return stable safe errors rather than fabricating questions;
future engines may use `503 generation_engine_unavailable` only when an engine
is genuinely unavailable.

The learner response projection contains prompts, response specifications,
marks, stable IDs, and visual references only. Teacher/memorandum entries are
separate DTOs and are not nested in the learner response.

## Consequences

The API can evolve independently from the domain model and has an explicit
compatibility boundary. The current application service defines effective-seed
behavior and deterministic output while preserving this contract. A new
breaking contract requires a new API version. Authentication and
authorization for teacher-side data remain future application concerns.
