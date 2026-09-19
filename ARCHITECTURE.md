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

Canonical assessments keep authoring data separate from submissions and marking results. Every assessable `QuestionPart` owns a stable identifier, response specification, expected answer, and marking scheme. Memorandum entries are derived from those parts by `QuestionPartId`; learner responses and marking results carry the same explicit identifier. No relationship depends on display order or renderer geometry.

Technical SVG renderers consume validated scenario and solver objects and may only transform values into display coordinates. The projectile renderer is separate from the solver, uses physical screen orientation independently of mathematical sign convention, and emits safe deterministic SVG without raster, script, remote, or renderer-specific assessment dependencies.

See ADRs 0001–0004 in `docs/adr/`.
