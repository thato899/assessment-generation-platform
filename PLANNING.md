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

Status: domain, solver, and deterministic scenario-generation foundations are
complete. Issues #28, #30, and #32 are merged; PR #33 merged at
`86079a764c9143a778444ed3bdb4e60584726637`.

The first planning slice will:

- inspect the CAPS Grade 12 momentum and impulse requirements and define the
  framework-independent domain boundary;
- identify the required scenario/value objects and authoritative deterministic
  solver inputs, including SI units, sign conventions, and seed semantics;
- separate domain, curriculum, application, API, and learner-safe projection
  responsibilities before selecting an implementation issue; and
- record explicit non-goals for marking, printable output, LMS integration,
  and unrelated subject logic.

M3 question generation, rendering, application, and API remain deferred until
the next boundary is selected explicitly.

### M3 next-stage decision gate

No next M3 implementation issue is selected yet. Before creating one, the
roadmap must decide whether the next boundary is:

- canonical question generation for quantities already exposed by
  `MomentumImpulseSolver`;
- technical scenario rendering;
- explicit domain constraints for solvable final-state or collision questions;
  or
- application/API orchestration after canonical question generation exists.

If question generation is selected, its supported question families must be
limited to authoritative solver results. Individual final velocities,
post-collision kinetic energy, elasticity, and other quantities not represented
by the current domain and solver must not be invented in the question layer.
If those outcomes are required, explicit solvable final-state constraints must
be designed first. Visual requirements and the ordering of rendering versus
question generation must also be decided rather than inferred from the
projectile sequence.

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
