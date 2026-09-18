# Status

Last updated: 2026-09-18

## Current milestone
M2 — Physical Sciences: Vertical Projectile Motion complete

## Current phase
Issue #16 assessment response/marking model is implemented and its pull request is in review.

## Completed
- Repository scaffold, Python packaging, FastAPI app, versioned health endpoint, request validation, CI, security, and governance documentation.
- Issue #1 core value objects and framework-independent assessment models merged via PR #13.
- Issue #2 CAPS Grade 12 Physical Sciences curriculum metadata merged via PR #14.
- Issue #3 vertical projectile scenario model merged via PR #15.
- Issue #4 deterministic projectile solver and solution validation merged via PR #17.
- Issue #16 canonical assessment response, memorandum, and marking model implemented on a feature branch.

## In progress
- Pull request for Issue #16 is ready for CI review.

## Blocked
- GitHub Project and branch protection were not configured because the available CLI token does not expose project administration.

## Next tasks
- Complete Issue #16 before beginning question-generation or automatic-marking work.

## Known problems
- Generation endpoint intentionally returns 501 until later milestones.

## Test/CI status
Issues #1–#4 merged with CI quality and dependency-audit checks passing. Issue #16 local suite: pending final report.

## GitHub state
- Repository: https://github.com/thato899/assessment-generation-platform
- Default branch: `main`
- Milestones: M0, M1, M2, M6
- PR #13 merged at `405cb1927fa0d68fa11ca55d432e1382f6ba59a1`.
- PR #14 merged at `ad815850d9b9458978b4c92c153abbaace7d96d7`.
- PR #15 merged at `15236ce0abb902689c96e4b3fe01f7a85a09b0d5`.
- PR #17 merged at `ab895c6c6e9006ede0fe81100797c8398749416f`.
- Issue #16 pull request pending CI.
- Project board: blocked/not created; verify permissions before creating one.

## Important decisions
- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- Scenario models use explicit SI value objects and an explicit coordinate sign convention.
- Canonical assessment relationships use stable QuestionPartId values, not display order.
- Apache-2.0 planned.
