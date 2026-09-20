# Status

Last updated: 2026-09-19

## Current milestone

M3 - Momentum & Impulse

## Current phase

Issues #28, #30, #32, #35, #36, #37, #38, #39, and #40 are complete. Issue #41 is in
progress on its dedicated feature branch. PR #33 merged the deterministic
Momentum & Impulse scenario generation policy and factory at
`86079a764c9143a778444ed3bdb4e60584726637`. M3 dependency planning is now
recorded in `docs/planning/m3-momentum-impulse.md`; Issue #38 is the active
implementation issue and Issues #39-#43 are planned backlog items.

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
- Issue #23 vertical-projectile application/API orchestration merged via PR #26 at `d7f709c4cdaefe1c994e6e9d37f63576d117b60b`.
- Issue #28 Momentum & Impulse domain scenario models merged via PR #29 at `bdd2f5bc1a322d2fbd5924505fe5d1bc0b07e7d3`.
- Issue #30 deterministic Momentum & Impulse solver and validation merged via PR #31 at `6972075738cc0b876368f12dc9a6578e352d60e0`.
- Issue #35 authored Momentum interaction constraints merged via PR #45 at `027028c679e4fed2777fa10f459d364239f38819`.
- Issue #36 constrained collision solver merged via PR #46 at `237ef2500271f4f5e5cba5bf5100feabb3e9982a`.
- Issue #37 force-time and momentum-change relationships merged via PR #47 at `159ee9f6b9ca03bffc354f3bdc46f87eba969d24`.

## In progress

- Issue #41 is in progress on its dedicated feature branch. Issues #42-#43 are
  backlog. Question generation,
  rendering, application, and API remain deferred behind their documented
  dependencies.

## Blocked

- GitHub Project and branch protection were not configured because the available CLI token does not expose project administration.
## Next tasks

- Complete and review Issue #41 without starting downstream M3
  issues before their documented dependencies are complete.
- Keep marking, printable documents, learner submissions, and additional subject engines deferred.

## Known problems

- The first generation path is intentionally narrow: one CAPS Grade 12 Physical Sciences vertical-projectile question. Unsupported combinations return stable errors.

## Test/CI status

- Issue #21 final suite: 82 tests passed; 95% coverage; Ruff, mypy, and build passed. PR #22 CI quality and dependency-audit checks passed.
- Issue #24 full local suite: 201 tests passed; 95% total coverage; Ruff, mypy, and build passed.
- Issue #23 full local suite: 236 tests passed; 95% total coverage; Ruff, mypy, and build passed. PR #26 and post-merge main CI quality and dependency-audit checks passed.
- Issue #28 branch suite: 257 tests passed; 95% total coverage; Ruff, mypy, and build passed locally. PR #29 quality and dependency-audit checks passed.
- Issue #30 full suite: 269 tests passed; 94% total coverage; Ruff, mypy, and build passed. PR #31 CI passed.
- Issue #32 final suite: 308 tests passed; 94% total coverage; Ruff, mypy, and build passed locally. Momentum solver and projectile regression tests passed explicitly. PR #33 CI quality and dependency-audit checks passed.
- Issue #35 branch suite: 332 tests passed; 94% total coverage; Ruff, mypy, and build passed locally. Momentum domain/solver/factory tests and projectile regressions passed explicitly.
- Issue #36 full suite: 349 tests passed; 93% total coverage; Ruff, mypy, and build passed locally. Constrained solver, legacy Momentum, and projectile regression tests passed explicitly. PR #46 CI quality and dependency-audit checks passed.
- Issue #37 full suite: 386 tests passed; 92% total coverage; Ruff, mypy, and build passed locally. Momentum and projectile regressions passed explicitly. PR #47 CI quality and dependency-audit checks passed.
- Issue #38 local validation: 580 tests passed; 91% total coverage; Momentum
  regression 344 passed; projectile regression 204 passed; Ruff, mypy, and
  build passed. PR #48 quality and dependency-audit checks passed.
- Issues #1-#6, #16, #21, #23, #24, #28, #30, and #32 merged with CI quality and dependency-audit checks passing.

## GitHub state

- Repository: https://github.com/thato899/assessment-generation-platform
- Default branch: `main`
- Milestones: M0, M1, M2, M3, M6
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
- PR #26 merged at `d7f709c4cdaefe1c994e6e9d37f63576d117b60b`.
- Issue #23 is closed; PR #26 is merged.
- Issue #24 is closed after its deterministic scenario-generation prerequisite was merged.
- PR #29 merged at `bdd2f5bc1a322d2fbd5924505fe5d1bc0b07e7d3`.
- Issue #28 is closed; PR #29 is merged.
- PR #31 merged at `6972075738cc0b876368f12dc9a6578e352d60e0`.
- Issue #30 is closed; PR #31 is merged.
- PR #33 merged at `86079a764c9143a778444ed3bdb4e60584726637`.
- Issue #32 is closed; PR #33 is merged.
- PR #45 merged at `027028c679e4fed2777fa10f459d364239f38819`; Issue #35 is
  closed.
- PR #46 merged at `237ef2500271f4f5e5cba5bf5100feabb3e9982a`; Issue #36 is
  closed.
- Milestone `M3 - Momentum & Impulse` exists with Issue #38 in progress and
  Issues #39-#43 planned backlog.
- PR #47 merged at `159ee9f6b9ca03bffc354f3bdc46f87eba969d24`; Issue #37 is
  closed. PR #48 is open and unmerged; Issue #38 is in review and PR quality
  and dependency-audit checks passed.
- No Momentum & Impulse API support has been added.
- Project board: blocked/not created; verify permissions before creating one.

## Important decisions

- Python/FastAPI/Pydantic; deterministic domain engines remain framework-independent.
- API v1 uses explicit boundary DTOs, stable error codes, deterministic seed semantics, and learner-safe projections.
- Vertical-projectile generation consumes validated solver results, uses deterministic typed templates, and keeps visuals/provenance renderer-neutral in the core.
- API orchestration delegates scenario creation to the deterministic Issue #24 factory and does not fabricate scenarios.
- Scenario models use explicit SI value objects and an explicit coordinate sign convention.
- Canonical assessment relationships use stable QuestionPartId values, not display order.
- Apache-2.0 planned.
- M3 Issue #28 models one-dimensional initial states with explicit signed
  velocities, positive-axis conventions, body identity, and system boundaries;
  derived momentum and final states remain solver responsibilities.
- M3 Issue #30 derives only typed, directly computable body and aggregate
  momentum results; underdetermined individual final velocities are not
  fabricated.
- M3 Issue #32 generates only bounded deterministic initial conditions from a
  versioned platform policy and never calls or duplicates solver calculations.
- M3 Issue #36 keeps authored interaction constraints separate from derived
  collision results, delegates aggregate authority to Issue #30, and rejects
  underdetermined or unsupported constrained outcomes.
- M3 Issue #37 owns deterministic signed momentum-change, impulse,
  average-force, and contact-time relationships independently of collision
  solving; force/time results are not generated by the scenario factory.
- M3 Issue #38 adds a version-2 typed problem-generation companion that
  composes the version-1 scenario factory, uses bounded platform policy pools,
  and delegates all answers and complete-state validation to existing solvers.
