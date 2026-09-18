# Architecture

The platform is a layered modular monolith initially: framework-independent domain and curriculum modules are exposed through an application boundary and a thin FastAPI adapter. Subject modules own scenarios, solvers, question generation, and validation. Rendering consumes validated domain objects. Integrations remain ports/adapters.

```text
api/v1 -> application -> domain engines + curriculum
                         |             |
                         +-> validation +-> rendering
```

Stable concepts will include AssessmentRequest, Assessment, Question, Scenario, Diagram, Solution, MarkingRubric, CurriculumReference, Difficulty, and GenerationSeed. The versioned endpoint `POST /api/v1/assessments/generate` is defined by explicit boundary DTOs and is deliberately unavailable until a generation application service exists. DTOs map to framework-independent core value objects; FastAPI and Pydantic do not cross into the domain layer.

The learner response projection excludes expected answers, marking schemes, memorandum entries, and worked solutions. Teacher-side memorandum data has a separate boundary DTO and must not be nested into learner responses. The contract uses stable identifiers, explicit seed semantics, safe error codes, and a new API version for breaking changes. See API documentation and ADR 0008.

The Physical Sciences vertical-projectile scenario is a framework-independent domain model. It owns explicit SI value objects and coordinate sign conventions; it contains no trajectory calculations. Future solvers, validators, renderers, and generators must consume the same scenario instance.

Canonical assessments keep authoring data separate from submissions and marking results. Every assessable `QuestionPart` owns a stable identifier, response specification, expected answer, and marking scheme. Memorandum entries are derived from those parts by `QuestionPartId`; learner responses and marking results carry the same explicit identifier. No relationship depends on display order or renderer geometry.

Technical SVG renderers consume validated scenario and solver objects and may only transform values into display coordinates. The projectile renderer is separate from the solver, uses physical screen orientation independently of mathematical sign convention, and emits safe deterministic SVG without raster, script, remote, or renderer-specific assessment dependencies.

See ADRs 0001–0004 in `docs/adr/`.
