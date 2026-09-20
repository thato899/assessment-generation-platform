# Architecture

The platform is a layered modular monolith initially: framework-independent domain and curriculum modules are exposed through an application boundary and a thin FastAPI adapter. Subject modules own scenarios, solvers, question generation, and validation. Rendering consumes validated domain objects. Integrations remain ports/adapters.

```text
api/v1 -> application -> domain engines + curriculum
                         |             |
                         +-> validation +-> rendering
```

Stable concepts include AssessmentRequest, Assessment, Question, Scenario, Diagram, Solution, MarkingRubric, CurriculumReference, Difficulty, and GenerationSeed. The versioned endpoint `POST /api/v1/assessments/generate` is defined by explicit boundary DTOs and currently supports only the CAPS Grade 12 Physical Sciences vertical-projectile application path. DTOs map to framework-independent core value objects; FastAPI and Pydantic do not cross into the domain layer.

The learner response projection excludes expected answers, marking schemes, memorandum entries, and worked solutions. Teacher-side memorandum data has a separate boundary DTO and must not be nested into learner responses. The contract uses stable identifiers, explicit seed semantics, safe error codes, and a new API version for breaking changes. See API documentation and ADR 0008.

The Physical Sciences vertical-projectile scenario is a framework-independent domain model. It owns explicit SI value objects and coordinate sign conventions; it contains no trajectory calculations. The deterministic scenario factory creates the same scenario from typed, immutable input and a versioned platform policy. Future solvers, validators, renderers, and generators must consume that scenario instance; the factory does not import or call them.

The application generation service selects supported curriculum metadata, maps the request to the scenario factory, invokes the authoritative solver and solution validation, invokes the question generator, and composes one canonical Assessment. It does not calculate subject results or expose teacher-side data through the learner projection. The vertical-projectile question generator consumes a validated scenario, its authoritative solver solution, CAPS topic metadata, and an optional seed. It selects only physically available typed templates, constructs canonical `QuestionPart` objects, and delegates visual production to the existing SVG renderer. Generated questions use the core's renderer-neutral `VisualReference` and minimal `GenerationProvenance` values so the domain remains independent of FastAPI, Pydantic, and renderer implementations. The scenario factory is an earlier boundary: it creates deterministic initial conditions only and has no solver or question-generator dependency.

M3 begins with a separate one-dimensional Momentum & Impulse domain boundary. Its immutable initial-state models represent explicitly identified bodies, positive-axis conventions, signed velocities, and isolated or externally impulsed system assumptions. Momentum and impulse remain semantically distinct value objects. Issue #28 deliberately does not calculate derived momentum, model final states, classify collisions, or expose an API; a future deterministic solver must remain authoritative for those results.

The M3 solver consumes that initial state and returns only typed, directly derivable body and aggregate momentum results. It interprets an external impulse over the modeled interaction interval, validates signed totals and system-boundary behavior, and does not fabricate individual final velocities for underdetermined collisions. Issue #35 adds a separate MomentumInteraction boundary for authored known-final-velocity, explicit sticking/common-final-velocity, and complete-final-state constraints. Issue #36 adds a separate constrained solver/result boundary that delegates aggregate authority, derives only supported two-body outcomes, and independently validates authored complete states. Scenario generation, question generation, rendering, and API wiring remain separate downstream decisions.

Issue #37 adds a separate MomentumImpulseRelationshipSolver for generic
one-dimensional signed momentum change, impulse, average/resultant force, and
positive contact-time relationships. It reuses the existing semantic value
objects while keeping MomentumChange, Impulse, Newtons, and Seconds distinct.
It is independent of the collision solver and is authoritative for these
relationships; downstream generation and API layers do not duplicate them.

Issue #38 adds a focused typed `MomentumProblemFactory` companion to the
existing scenario factory. It composes versioned initial-condition policy with
bounded momentum-change, force/time, and constrained-collision input policy.
Typed generated variants keep authored relationship inputs and interaction
constraints separate from solver-derived answers. Complete-state candidates
are accepted only through the constrained solver, so generation does not
duplicate conservation or classification equations. The original scenario
factory remains backward compatible and the companion remains framework,
question, renderer, and API independent.

The M3 scenario factory is the next boundary after the domain and solver prerequisites. It creates only bounded, deterministic initial conditions from a versioned platform policy and `GenerationSeed`; it does not call the solver or generate final states. Policy values remain separate from CAPS metadata, and explicit axis/family provenance preserves replayability.

Canonical assessments keep authoring data separate from submissions and marking results. Every assessable `QuestionPart` owns a stable identifier, response specification, expected answer, and marking scheme. Memorandum entries are derived from those parts by `QuestionPartId`; learner responses and marking results carry the same explicit identifier. No relationship depends on display order or renderer geometry.

Technical SVG renderers consume validated scenario and solver objects and may only transform values into display coordinates. The projectile renderer is separate from the solver, uses physical screen orientation independently of mathematical sign convention, and emits safe deterministic SVG without raster, script, remote, or renderer-specific assessment dependencies.

See ADRs 0001–0011 in `docs/adr/`.

M4 Issue #56 adds `mechanics.newton_solver` as the authoritative numerical
boundary after the authored #55 scenario. `NewtonSolver` consumes an immutable
`NewtonScenario` and returns frozen, typed resultant, dynamics, weight,
contact, string and gravity results. It uses the scenario's explicit Cartesian
or surface-aligned basis, `math.fsum`, a shared absolute tolerance of `1e-9`,
and no display rounding or hidden gravitational field. A valid authored model
can still be unsolvable: unresolved components, inconsistent authored values,
unsupported geometry/constraints and numerical overflow/underflow are reported
through typed `NewtonSolveError` reasons. The package is framework-independent
and imports no generation, rendering, question, marking or API layers.

M4 Issue #55 introduces a separate `mechanics.newtons_laws` package for authored
Newton facts: bodies, explicit 1D/2D bases, signed/unknown force components,
source/target ownership, selected system membership, and composed contact,
friction, light-string, third-law and gravitational relationships. Frozen
objects validate structural meaning; an underdetermined scenario remains valid.
Authored acceleration and field inputs are separate from bodies and future
solver results. The package imports no other physics engine and leaves existing
value objects unchanged. Numerical validation belongs to #56; generation,
diagrams, questions and routing remain #57–#61. See the
[Newton domain contract](docs/domains/physical-sciences/newtons-laws-domain.md).


M4 Issue #57 adds `mechanics.newton_generation` as the authored-input factory
boundary after the #56 solver. `NewtonProblemFactory` uses immutable typed
inputs, shared `GenerationSeed`/`Difficulty`, local `random.Random`, bounded
versioned policy pools and `GenerationProvenance` to create only authored
`NewtonScenario` variants. It invokes `NewtonSolver` for acceptance checks but
never copies Newton equations, stores solver answers, mutates unknowns, or adds
rendering, question, marking or API concerns. Family-specific output types keep
contact, string, gravitation, third-law and unknown-force data explicit.

M4 Issue #58 adds `rendering.svg.newton.NewtonSvgRenderer` as a downstream
technical-visual boundary. It consumes authored Newton scenarios and optional
explicit validated data, maps declared Cartesian or surface directions to
screen coordinates, and emits deterministic accessible SVG. Free-body views
select forces through `NewtonScenario.forces_on`, so third-law partners acting
on another body cannot leak into the selected body. Learner-safe visibility
defaults hide numbers and derived values; fixed arrow geometry prevents hidden
magnitudes being inferred. The renderer performs no Newton calculations and
does not call generation, questions, marking or API layers. See
`docs/domains/physical-sciences/newtons-laws-rendering.md`.

M4 Issue #59 adds `NewtonCalculationQuestionGenerator` after the generated
problem and solver boundaries. It maps only successful `NewtonSolver` results
to canonical `QuestionPart`, `ResponseSpecification`, `ExpectedAnswer`,
`MarkingScheme`, `VisualReference` and `GenerationProvenance` values. Prompts
expose authored givens and sign conventions while preserving unknown inputs;
question IDs and provenance contain no answers. Newton III validation has no
numeric question template, conceptual templates are owned by active #60, and
API routing, automatic marking and printing remain outside this layer.

M4 Issue #60 adds `NewtonConceptualQuestionGenerator` as the conceptual
question boundary. It emits deterministic canonical questions whose
`ExpectedAnswer` contains concept tokens and whose marking criteria describe
those concepts declaratively. It may consume an authored scenario and attach a
learner-safe #58 visual, but it performs no numerical physics, automatic
marking, API routing, or PDF generation.
