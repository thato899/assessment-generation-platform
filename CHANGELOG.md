# Changelog

## Unreleased
- Bootstrapped the Python/FastAPI repository, API v1 shell, validation, tests, governance documentation, and CI/security configuration.
- Added framework-independent core assessment value objects and models with validation tests.
- Added CAPS Grade 12 Physical Sciences Mechanics curriculum metadata and deterministic lookup tests.
- Added an immutable vertical projectile scenario model with explicit SI units, sign conventions, assumptions, and validation tests.
- Added deterministic vertical projectile position/velocity calculations, event detection, root selection, and solution validation.
- Added canonical question-part response specifications, expected answers, marking schemes, learner responses, marking results, and ID-derived memorandum entries.
- Added a safe deterministic SVG renderer for one-dimensional vertical projectile diagrams.
- Defined the versioned v1 assessment-generation API contract with explicit boundary DTOs, deterministic seed semantics, safe validation errors, and learner-safe response projections. Generation remains unavailable until its application service is implemented.
- Added deterministic CAPS vertical-projectile question generation with solver-derived canonical question parts, structured answers, marking schemes, optional SVG references, and provenance metadata.
- Added a deterministic, policy-driven vertical-projectile scenario factory with typed generation inputs, four supported scenario families, seed replay, and provenance metadata.
