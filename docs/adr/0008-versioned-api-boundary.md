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
Until an application generation service is implemented, return
`503 generation_engine_unavailable` rather than fabricate questions.

The learner response projection contains prompts, response specifications,
marks, stable IDs, and visual references only. Teacher/memorandum entries are
separate DTOs and are not nested in the learner response.

## Consequences

The API can evolve independently from the domain model and has an explicit
compatibility boundary. A later generator must define effective-seed behavior
and deterministic output while preserving this contract. A new breaking
contract requires a new API version. Authentication and authorization for
teacher-side data remain future application concerns.
