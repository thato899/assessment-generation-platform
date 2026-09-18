# Status

Last updated: 2026-09-18

## Current milestone
M0 — Repository & Architecture Bootstrap

## Current phase
Foundation implementation.

## Completed
- Repository scaffold, Python packaging, FastAPI app, versioned health endpoint, request schema.
- Initial test, lint, type-check, CI, security, issue-template, and documentation structure.
- Architecture and deterministic-correctness decisions documented.

## In progress
- GitHub repository governance and initial backlog.

## Blocked
- None known locally. GitHub project/branch protection depend on account permissions.

## Next tasks
- Implement core assessment models and CAPS references, then the deterministic vertical-projectile scenario.

## Known problems
- Generation endpoint intentionally returns 501 until M1/M2.

## Test/CI status
Local quality suite pending dependency installation. CI workflow configured.

## Important decisions
- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- Apache-2.0 planned.
