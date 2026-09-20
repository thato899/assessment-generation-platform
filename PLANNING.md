# Roadmap

## Vision and MVP
Provide a versioned API that produces validated CAPS assessments from deterministic subject engines. MVP: validated core models, Grade 12 Physical Sciences vertical projectile generation, solver, rubric, SVG, and API contract.

## Milestones
- **M0** Repository & Architecture Bootstrap — governance, API shell, CI.
- **M1** Assessment Core — stable models, validation, seeds, contract tests.
- **M2** Physical Sciences: Vertical Projectile Motion — scenario, solver, renderer, questions, rubric.
- **M3** Momentum & Impulse (complete); **M4** Newton's Laws (domain in review);
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
is merged and closed. Issue #55 domain implementation is in review; Issues
#56–#62 remain backlog in the existing dependency order.

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
results. Its PR remains open for review. No solver, generator, renderer,
question or API implementation is included. #56 is next only after #55 merges;
#56–#62 remain backlog and have not started.

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
