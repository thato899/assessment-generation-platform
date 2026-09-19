# Status

Last updated: 2026-09-19

## Current milestone

M2 - Physical Sciences: Vertical Projectile Motion - deterministic question generation

## Current phase

Issue #24 - deterministic vertical-projectile scenario generation inputs and factory is in progress on a feature branch.

## Completed

- Repository scaffold, Python packaging, FastAPI app, versioned health endpoint, request validation, CI, security, and governance documentation.
- Issue #1 core value objects and framework-independent assessment models merged via PR #13.
- Issue #2 CAPS Grade 12 Physical Sciences curriculum metadata merged via PR #14.
- Issue #3 vertical projectile scenario model merged via PR #15.
- Issue #4 deterministic projectile solver and solution validation merged via PR #17.
- Issue #16 canonical assessment response, memorandum, and marking model merged via PR #18.
- Issue #5 deterministic vertical projectile SVG renderer merged via PR #19.
- Issue #6 versioned assessment generation API contract merged via PR #20.
- Issue #21 deterministic Grade 12 CAPS vertical-projectile question generator merged via PR #22 at `ed61df29cb1688c5f308ead5315081be4390ab11`.

## In progress

- Issue #24 implementation is complete locally; its feature branch and pull request are pending final verification.

## Blocked

- GitHub Project and branch protection were not configured because the available CLI token does not expose project administration.
- Issue #23 remains blocked pending the deterministic scenario factory from Issue #24; its generation endpoint remains HTTP 503.

## Next tasks

- Review and merge the Issue #24 pull request after CI passes.
- Resume Issue #23 application orchestration and API wiring only after Issue #24 is complete.

## Known problems

- The generation endpoint intentionally returns HTTP 503 until a later milestone provides an application generation service.

## Test/CI status

- Issue #21 local suite: 82 tests passed; 95% coverage; Ruff, mypy, and build passed. PR #22 CI quality and dependency-audit checks passed.
- Issue #24 full local suite: 201 tests passed; 95% total coverage; Ruff, mypy, and build passed.
- Issues #1-#6 and #16 merged with CI quality and dependency-audit checks passing.

## GitHub state

- Repository: https://github.com/thato899/assessment-generation-platform
- Default branch: `main`
- Milestones: M0, M1, M2, M6
- PR #13 merged at `405cb1927fa0d68fa11ca55d432e1382f6ba59a1`.
- PR #14 merged at `ad815850d9b9458978b4c92c153abbaace7d96d7`.
- PR #15 merged at `15236ce0abb902689c96e4b3fe01f7a85a09b0d5`.
- PR #17 merged at `ab895c6c6e9006ede0fe81100797c8398749416f`.
- PR #18 merged at `6df9aae2e442b52df8d08319fef180628ac829f2`.
- PR #19 merged at `309ed99b25a14573c02263fa9411195aa6e3b99f`.
- PR #20 merged at `52150816851cbc006e5513eea3ce5c493170083f`.
- Issue #21 is closed; PR #22 is merged.
- Issue #23 is open and marked `status:in-progress` for deferred application/API orchestration, blocked by Issue #24.
- Issue #24 is open and marked `status:in-progress` for deterministic scenario generation.
- Project board: blocked/not created; verify permissions before creating one.

## Important decisions

- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- API v1 uses explicit boundary DTOs, stable error codes, deterministic seed semantics, and learner-safe projections.
- Vertical-projectile generation consumes validated solver results, uses deterministic typed templates, and keeps visuals/provenance renderer-neutral in the core.
- Scenario models use explicit SI value objects and an explicit coordinate sign convention.
- Canonical assessment relationships use stable QuestionPartId values, not display order.
- Apache-2.0 planned.
