# Roadmap

## Vision and MVP
Provide a versioned API that produces validated CAPS assessments from deterministic subject engines. MVP: validated core models, Grade 12 Physical Sciences vertical projectile generation, solver, rubric, SVG, and API contract.

## Milestones
- **M0** Repository & Architecture Bootstrap — governance, API shell, CI.
- **M1** Assessment Core — stable models, validation, seeds, contract tests.
- **M2** Physical Sciences: Vertical Projectile Motion — scenario, solver, renderer, questions, rubric.
- **M3** Momentum & Impulse; **M4** Newton's Laws; **M5** Work, Energy & Power.
- **M6** Mathematics Foundation; **M7** Mathematics: Functions.

## M3 preparation: Momentum & Impulse

Status: implementation underway. Issues #28 and #30 established the domain and
solver foundations; Issue #32 is implementing the deterministic scenario
generation boundary.

The first planning slice will:

- inspect the CAPS Grade 12 momentum and impulse requirements and define the
  framework-independent domain boundary;
- identify the required scenario/value objects and authoritative deterministic
  solver inputs, including SI units, sign conventions, and seed semantics;
- separate domain, curriculum, application, API, and learner-safe projection
  responsibilities before selecting an implementation issue; and
- record explicit non-goals for marking, printable output, LMS integration,
  and unrelated subject logic.

M3 API, question generation, rendering, and scenario-generation policy remain
deferred until their prerequisites are complete.

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
