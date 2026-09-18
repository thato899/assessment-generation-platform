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
- GitHub Project and branch protection were not configured in this bootstrap because the available CLI token does not expose project administration; no claim is made that they exist.

## Next tasks
- Implement core assessment models and CAPS references, then the deterministic vertical-projectile scenario.

## Known problems
- Generation endpoint intentionally returns 501 until M1/M2.

## Test/CI status
Local: 2 tests passed; Ruff passed; mypy passed; wheel build passed. GitHub Actions workflow is pushed and awaiting its first run.

## GitHub state
- Repository: https://github.com/thato899/assessment-generation-platform
- Default branch: `main`
- Milestones: M0, M1, M2, M6
- Open backlog issues: #1–#6, all labelled `status:backlog`
- Pull request: none; bootstrap was pushed to the initial `main` branch.
- Project board: blocked/not created; verify permissions before creating one.

## Important decisions
- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- Apache-2.0 planned.
