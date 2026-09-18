# Architecture

The platform is a layered modular monolith initially: framework-independent domain and curriculum modules are exposed through an application boundary and a thin FastAPI adapter. Subject modules own scenarios, solvers, question generation, and validation. Rendering consumes validated domain objects. Integrations remain ports/adapters.

```text
api/v1 -> application -> domain engines + curriculum
                         |             |
                         +-> validation +-> rendering
```

Stable concepts will include AssessmentRequest, Assessment, Question, Scenario, Diagram, Solution, MarkingRubric, CurriculumReference, Difficulty, and GenerationSeed. The initial endpoint is `POST /api/v1/assessments/generate`; it is schema-validated but deliberately unimplemented in M0.

The Physical Sciences vertical-projectile scenario is a framework-independent domain model. It owns explicit SI value objects and coordinate sign conventions; it contains no trajectory calculations. Future solvers, validators, renderers, and generators must consume the same scenario instance.

See ADRs 0001–0004 in `docs/adr/`.
