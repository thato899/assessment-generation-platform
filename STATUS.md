# Status

Last updated: 2026-09-19

## Current milestone

M2 - Physical Sciences: Vertical Projectile Motion - application generation

## Current phase

Issue #23 - application/API orchestration is in review via PR #26.

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
- Issue #24 deterministic vertical-projectile scenario generation inputs and factory merged via PR #25 at `f709c77465044e5663c4bfac63c49e641be28783`.

## In progress

- Pull request #26 for Issue #23 is open for review; CI is passing.

## Blocked

- GitHub Project and branch protection were not configured because the available CLI token does not expose project administration.
## Next tasks

- Review and merge PR #26 after CI passes.
- Select the next planned M2 work only after Issue #23 is complete.
- Keep marking, printable documents, learner submissions, and additional subject engines deferred.

## Known problems

- The first generation path is intentionally narrow: one CAPS Grade 12 Physical Sciences vertical-projectile question. Unsupported combinations return stable errors.

## Test/CI status

- Issue #21 final suite: 82 tests passed; 95% coverage; Ruff, mypy, and build passed. PR #22 CI quality and dependency-audit checks passed.
- Issue #24 full local suite: 201 tests passed; 95% total coverage; Ruff, mypy, and build passed.
- Issue #23 full local suite: 228 tests passed; 94% total coverage; Ruff, mypy, and build passed. PR #26 CI quality and dependency-audit checks passed.
- Issues #1-#6, #16, #21, and #24 merged with CI quality and dependency-audit checks passing.

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
- PR #22 merged at `ed61df29cb1688c5f308ead5315081be4390ab11`.
- Issue #21 is closed; PR #22 is merged.
- PR #25 merged at `f709c77465044e5663c4bfac63c49e641be28783`.
- Issue #23 is open and marked `status:in-review`; PR #26 is open.
- Issue #24 is closed after its deterministic scenario-generation prerequisite was merged.
- Project board: blocked/not created; verify permissions before creating one.

## Important decisions

- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- API v1 uses explicit boundary DTOs, stable error codes, deterministic seed semantics, and learner-safe projections.
- Vertical-projectile generation consumes validated solver results, uses deterministic typed templates, and keeps visuals/provenance renderer-neutral in the core.
- API orchestration delegates scenario creation to the deterministic Issue #24 factory and does not fabricate scenarios.
- Scenario models use explicit SI value objects and an explicit coordinate sign convention.
- Canonical assessment relationships use stable QuestionPartId values, not display order.
- Apache-2.0 planned.
