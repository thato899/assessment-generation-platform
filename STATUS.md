# Status

Last updated: 2026-09-18

## Current milestone
M0 — Repository & Architecture Bootstrap

## Current phase
M1 Assessment Core — Issue #1 implementation in review.

## Completed
- Repository scaffold, Python packaging, FastAPI app, versioned health endpoint, request schema.
- Initial test, lint, type-check, CI, security, issue-template, and documentation structure.
- Architecture and deterministic-correctness decisions documented.
- Issue #1 core value objects and framework-independent assessment models merged via PR #13.

## In progress
- Issue #2: CAPS Grade 12 Physical Sciences curriculum constraints.

## Blocked
- GitHub Project and branch protection were not configured in this bootstrap because the available CLI token does not expose project administration; no claim is made that they exist.

## Next tasks
- Complete Issue #2, then begin Issue #3: deterministic vertical projectile scenario model.

## Known problems
- Generation endpoint intentionally returns 501 until M1/M2.

## Test/CI status
Issue #1 PR #13 merged with CI quality and dependency-audit checks passing. Local suite: 18 tests passed; 96% coverage; Ruff, mypy, and build passed.

## GitHub state
- Repository: https://github.com/thato899/assessment-generation-platform
- Default branch: `main`
- Milestones: M0, M1, M2, M6
- Open backlog issues: #1–#6, all labelled `status:backlog`
- Pull request #13 merged at `405cb1927fa0d68fa11ca55d432e1382f6ba59a1`.
- Project board: blocked/not created; verify permissions before creating one.

## Important decisions
- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- Apache-2.0 planned.
