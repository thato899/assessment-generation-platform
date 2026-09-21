# Roadmap

## Vision and MVP
Provide a versioned API that produces validated CAPS assessments from deterministic subject engines. MVP: validated core models, Grade 12 Physical Sciences vertical projectile generation, solver, rubric, SVG, and API contract.

## Milestones
- **M0** Repository & Architecture Bootstrap — governance, API shell, CI.
- **M1** Assessment Core — stable models, validation, seeds, contract tests.
- **M2** Physical Sciences: Vertical Projectile Motion — scenario, solver, renderer, questions, rubric.
- **M3** Momentum & Impulse (complete); **M4** Newton's Laws (#62 verification in progress);
  **M5** Work, Energy & Power.
- **M6** Mathematics Foundation; **M7** Mathematics: Functions.

## M3 preparation: Momentum & Impulse

Status: M3 foundation and dependency planning are complete. Issues #28, #30,
#32, #35, and #36 are merged. PR #46 merged the constrained collision solver at
`237ef2500271f4f5e5cba5bf5100feabb3e9982a`; PR #33 merged the scenario factory
at `86079a764c9143a778444ed3bdb4e60584726637`. The detailed sequence is recorded
in [docs/planning/m3-momentum-impulse.md](docs/planning/m3-momentum-impulse.md).

The first planning slice will:

- inspect the CAPS Grade 12 momentum and impulse requirements and define the
  framework-independent domain boundary;
- identify the required scenario/value objects and authoritative deterministic
  solver inputs, including SI units, sign conventions, and seed semantics;
- separate domain, curriculum, application, API, and learner-safe projection
  responsibilities before selecting an implementation issue; and
- record explicit non-goals for marking, printable output, LMS integration,
  and unrelated subject logic.

M3 question generation, rendering, application, API integration, and final
coverage verification are complete through Issue #43. M3 is formally complete.
M4 Newton's Laws is the current milestone; its planning document is
[docs/planning/m4-newtons-laws.md](docs/planning/m4-newtons-laws.md). Issue #54
is merged and closed. Issue #55 is merged and closed at `2f6adeb`; Issue #56 is
merged and closed at `5568b52`; Issue #57 is merged and closed at `70b212c`;
Issue #58 is merged and closed at `c3ee3b9`; Issue #59 is merged and closed at `5025c37`;
Issue #60 is merged and closed at `f0e5a46`; Issue #61 is merged and closed at
`7a3d8b8`; Issue #62 is active on its feature branch for final verification.

## Completed M3 scope

M3 delivered deterministic Momentum & Impulse domain models, authoritative
solvers, constrained collisions, generation policy, safe SVG rendering,
calculation and conceptual question generation, v1 API integration, and
evidence-based CAPS verification. See the M3 plan and coverage matrix.

## M4 Issue #54 scope validation

Issue #54 records the official Grade 11 placement of Newton's Laws, the Grade
12 consolidation/integrated-problem-solving relationship, and selected Grade
11 examinability in the Grade 12 final examination. The stable topic metadata
and the approved supported/deferred boundary are documented in
[docs/domains/physical-sciences/newtons-laws-scope.md](docs/domains/physical-sciences/newtons-laws-scope.md).
PR #64 merged at `703de9acf8f334be6eafae0249cc8868f8215c66` and closed #54.

## M4 Issue #55 domain representations

Issue #55 adds immutable authored bodies, forces, explicit coordinates, system
boundaries and contact/string/gravity relationships. Structural validity does
not imply solvability. The [domain contract](docs/domains/physical-sciences/newtons-laws-domain.md)
records ownership, unknown values, assumptions and the boundary with derived
results. [PR #65](https://github.com/thato899/assessment-generation-platform/pull/65)
merged at `2f6adeb8d8df5e1b3faa9ef30c9fae4830f158f`; #55 is closed. No
generator, renderer, question or API implementation is included.
#57-#60 are complete; #61 is merged and closed; #62 owns final verification.

## M4 Issue #56 authoritative solver

Issue #56 adds the deterministic, framework-independent Newton solver and
immutable derived results. It owns signed resultants, Newton II acceleration,
equilibrium, one-unknown force resolution, authored acceleration validation,
weight from authored fields, contact/normal/friction, straight light-string,
third-law numerical validation, and scalar universal-gravity magnitude. It
rejects underdetermined, inconsistent, unsupported, and numerical-range cases
explicitly. The focused solver suite has 82 tests and the full suite passes
locally. #56-#61 are complete; #62 is the active verification issue.

## M4 Issue #57 scenario generation

Issue #57 adds `NewtonProblemFactory`, immutable generation inputs/policies and
family-specific generated outputs. Local seeded randomness, stable IDs and
shared `GenerationProvenance` preserve replayability. Each advertised family
is accepted by the Issue #56 solver before return, while authored unknowns stay
in the scenario. #57 is complete at merge `70b212c`; #58 is complete at merge
`c3ee3b9`; #59 owns numeric calculation questions and #60 owns conceptual questions;
#61 owns application/API integration and #62 owns final verification.

## M4 Issue #58 Newton SVG rendering

Issue #58 adds a deterministic, framework-independent technical SVG renderer
for authored Newton force and free-body diagrams. It maps explicit Cartesian
and surface-coordinate directions to screen vectors, isolates authored
free-body ownership, and supports safe labels, strings, surfaces and selected
system boundaries. Hidden values use fixed arrow geometry and are absent from
all SVG text and metadata. The renderer does not calculate forces, acceleration,
weight, friction, tension or gravitation and does not call the solver. #58 is complete at merge `c3ee3b9`; #59 owns solver-backed numeric calculation
questions, #60 owns conceptual questions, and #61 owns application/API integration;
#62 owns final verification.

## M4 Issue #59 Newton calculation questions

Issue #59 adds canonical numeric `Question` generation over the typed #57
problem outputs. The generator delegates every expected value to #56
`NewtonSolver`, rejects unsupported or unresolved cases before returning, and
creates deterministic question/part IDs, provenance, response specifications,
numeric tolerances and reconciled marking schemes. It may attach learner-safe
#58 SVG visuals, but it does not calculate physics, mark responses, add
conceptual templates or route Newton requests through the API.

## M4 Issue #60 Newton conceptual questions

Issue #60 adds the deterministic conceptual generator and its machine-readable
concept-token answers and declarative rubrics. It covers Newton I/II/III,
action-reaction ownership, resultants and equilibrium, mass/weight, contact and
friction, systems and force diagrams, strings, gravitation, weightlessness, and
model assumptions. It may attach an existing #58 visual for authored context,
but performs no numeric physics, automatic marking, API routing, or PDF output.
The conceptual generator is merged at `f0e5a46`; #61 application/API integration
is merged and #62 owns final verification.

## M4 Issue #61 Newton application/API integration

Issue #61 adds a focused route in the existing application service and v1
assessment endpoint. The exact Grade 11 `newtons-laws` route delegates to the
merged factory and calculation/conceptual generators, selects the path from the
effective seed, preserves difficulty and visual preferences, and returns the
existing canonical `Assessment`. The learner projection remains unchanged and
answer/rubric/memo/scenario/provenance data stay internal. #62 owns final CAPS
coverage and M4 readiness verification. Its evidence matrix is recorded in
[docs/verification/m4-newtons-laws-caps-coverage.md](docs/verification/m4-newtons-laws-caps-coverage.md).

## M4 Issue #62 final verification

Issue #62 audits the approved CAPS matrix across #54 through #61, including
solver behavior, generated families, diagrams, calculation and conceptual
questions, API routing, determinism, sign/vector semantics, solvability,
answer-leakage, security, regressions, and quality gates. The verification
records explicit partial/deferred capabilities and the local dependency-audit
baseline. The bounded M4 scope is ready for completion pending review and merge
of the #62 verification PR; M5 remains deferred.

## Deferred / future enhancements

M3's documented partial areas remain future enhancements: a standalone
final-total-momentum question and a dedicated impulse-vector conceptual
template. General two-unknown elastic solving, multidimensional mechanics,
automatic free-text marking, printable output, and LMS adapters remain out of
scope.
See the dedicated
[M3 plan](docs/planning/m3-momentum-impulse.md) for the dependency graph,
CAPS coverage target, question-family matrix, and exit criteria.

## Canonical assessment architecture prerequisite

Before question-generation, answer-sheet, or automatic-marking work, Issue #16 must define the framework-independent question-part response, memorandum, and marking domain model. It will connect stable `QuestionPartId` values to response specifications, machine-readable expected answers, memo entries, marking schemes, learner responses, and marks. Learner and memorandum views must derive from one canonical assessment representation; display order and LMS-specific integrations are not valid relationship keys.

## Cross-cutting roadmaps
- Curriculum: CAPS representation, then Grade 12 Physical Sciences mappings.
- Validation: units, sign conventions, reproducibility, property-based tests.
- Visuals: deterministic SVG derived from the scenario source of truth.
- API: versioned schemas, errors, OpenAPI compatibility policy.
- Security: dependency scanning, CodeQL review, authentication/rate-limit design before production.
- Integration: future LMS adapters only; no EduQuest or Sky-Fundi business logic.

## Explicit non-goals
No LLM-authoritative calculations, generative scientific diagrams, LMS integration, speculative subject engines, or fake deployment pipeline in bootstrap.
