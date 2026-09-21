# Status

Last updated: 2026-09-21

## Current milestone

M4 - Newton's Laws - Issue #61 in progress

M3 - Momentum & Impulse — COMPLETE

## Current phase

Issues #28, #30, #32, #35, #36, #37, #38, #39, #40, #41, #42, and #43 are
closed. M3 implementation and final coverage verification are complete. M4
planning and Issue #54 scope validation are merged. Issue #55 is merged and
closed; Issue #56 is merged and closed at `5568b527bdba75bd46f11ab7bdc2014289c836a4`.
Issue #57 is merged and closed at `70b212c5d416a36d535c389a056f79a95c25761e`;
Issue #58 is merged and closed at `c3ee3b9e707ea04b1f73826b5cb8f6b008cf5e21`;
Issue #59 is merged and closed at `5025c3730e4af6e46e3851f468215c501d490f30`;
Issue #60 is merged and closed at `f0e5a46e8c6f985945aff4427f79fca1de1b009d`;
Issue #61 is active on `feature/issue-61-newton-api-integration`; #62 remains deferred.

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
- Issue #54 CAPS Newton's Laws scope and curriculum metadata merged via PR #64
  at `703de9acf8f334be6eafae0249cc8868f8215c66` and closed, with
  Grade 11 core placement, Grade 12 consolidation/examinability context, and
  a dedicated scope contract; no Newton production pipeline was added.

## In progress

- Issue #55 immutable Newton bodies, forces, coordinate conventions, system
  membership and contact/friction/string/third-law/gravity relationships are
  merged and closed. Structural validity remains separate from solvability.
- Issue #56 deterministic Newton solver and validation are merged and closed.
- Issue #57 deterministic seeded Newton scenario generation is merged and
  closed. Issue #58 deterministic Newton SVG rendering is merged and closed.
  Issue #59 solver-backed calculation questions and Issue #60 conceptual questions
  are merged and closed; Issue #61 application/API integration is active; #62 remains backlog.

## Blocked

- GitHub Project and branch protection were not configured because the available CLI token does not expose project administration.
## Next tasks

- Complete implementation and open the Issue #61 application/API integration PR.
  Do not merge it in this execution and do not begin #62.
- Keep marking, printable documents, learner submissions, and additional subject engines deferred.

## Known problems

- Newton generation is now available through the existing v1 application/API route
  for the exact Grade 11 `newtons-laws` route. Issue #62 remains deferred.

## Test/CI status

- Issue #54 pre-merge CI quality and dependency-audit checks passed; no review
  conversations were outstanding. Post-merge main baseline: 590 tests passed,
  91% coverage, clean working tree before #55 branched.
- Issue #55 local verification: 750 passed; 92% total coverage; the Newton
  package has 100% statement coverage. Newton domain: 159 tests. Momentum
  selection: 353 passed; projectile selection: 166 passed; curriculum,
  application and API checks: 52 passed. Ruff, mypy, build, pip check and
  `git diff --check` passed. CI is tracked on the linked issue PR.
- Issue #57 focused verification: generation tests cover all 12 families,
  replay, global RNG isolation, authored unknown preservation and solver-backed
  validation.
- Issue #58 focused verification: 22 renderer tests passed with 93% module
  coverage; all 12 generated families render as force diagrams and projectile,
  Momentum, solver, generation and API regressions remain green. Full suite:
  876 passed. Ruff, mypy, wheel build, pip check and `git diff --check` passed.
- Issue #59 merged verification: 17 calculation-question tests passed with 93%
  module coverage; PR #69 CI passed and merged at `5025c373`.
- Issue #60 merged verification: 26 conceptual-template, rubric-reconciliation,
  context, visual, immutability, and misconception tests passed with 94% module
  coverage; full suite 919 passed. PR #70 CI passed and merged at `f0e5a46`.
- Issue #61 focused application/API verification: 60 tests passed with 97% combined
  application/API coverage; full suite 933 passed with 93% total coverage. Ruff,
  mypy, wheel build, pip check and `git diff --check` passed locally.
- Issue #56 focused verification: 82 Newton solver tests and 832 full-suite
  tests passed locally; Ruff, mypy, and wheel build passed. PR #66 merged at
  `5568b527bdba75bd46f11ab7bdc2014289c836a4`.
- Hypothesis was not added: the bounded structural invariants are covered by
  deterministic parameterized tests. No shared-unit refactor or ADR was needed.
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
- Milestone `M3 - Momentum & Impulse` is complete, including Issues #38–#43.
- PR #47 merged at `159ee9f6b9ca03bffc354f3bdc46f87eba969d24`; Issue #37 is
  closed. Issue #38 and the later M3 implementation/verification issues are
  closed with their implementation merged.
- PR #63 merged at `f64aa1a85698272917ec66c028ccd45e60350a8c`; M4 planning is
  present on `main`.
- PR #64 merged at `703de9acf8f334be6eafae0249cc8868f8215c66`; Issue #54 is closed.
- PR #65 merged at `2f6adeb8d8df5e1b3faa9ef30c9fae4830f158f`; Issue #55 is
  closed. PR #66 merged Issue #56 at `5568b527bdba75bd46f11ab7bdc2014289c836a4`.
  PR #67 merged Issue #57 at `70b212c5d416a36d535c389a056f79a95c25761e`.
  PR #68 merged Issue #58 at `c3ee3b9e707ea04b1f73826b5cb8f6b008cf5e21`.
  PR #69 merged at `5025c3730e4af6e46e3851f468215c501d490f30`; Issue #59 is closed.
  PR #70 merged at `f0e5a46e8c6f985945aff4427f79fca1de1b009d`; Issue #60 is closed.
  Issue #61 is active on its feature branch; #62 remains backlog.
- Existing Momentum & Impulse and projectile API behavior is preserved; Newton routing
  is now supported only for the exact Grade 11 route.
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
