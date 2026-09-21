# Assessment generation application service

`AssessmentGenerationService` is the framework-independent orchestration
boundary between API DTOs and subject-domain engines.

## Current pipeline

For the supported v1 request, the service performs this sequence:

```text
AssessmentGenerationRequest
        |
        v
AssessmentRequest
        |
        v
CAPS topic lookup
        |
        v
ScenarioGenerationInput -> VerticalProjectileScenarioFactory
        |
        v
VerticalProjectileScenario -> VerticalProjectileSolver
        |
        v
validated VerticalProjectileSolution
        |
        v
VerticalProjectileQuestionGenerator
        |
        v
canonical Question -> canonical Assessment
        |
        v
learner-safe API projection
```

For Grade 12 Work, Energy & Power, exact route validation is followed by
deterministic seed parity: an even seed invokes the context-free conceptual
generator, while an odd seed invokes `WorkEnergyProblemFactory` and then the
calculation question generator. The existing projectile, Momentum, and Newton
branches retain their established orchestration. The application performs no
M5 physics calculations.

The service supports the exact approved CAPS grade/topic pairs: Grade 12
`vertical-projectile-motion-1d`, Grade 12 `momentum-and-impulse`, Grade 11
`newtons-laws`, and Grade 12 `work-energy-and-power`. It deliberately supports
`assessment_type=question` and `question_count=1` only because the current
domain generators return one canonical `Question`; question parts are not
treated as independent questions.

For Work, Energy & Power the service owns only deterministic semantic routing.
An even effective seed selects a `WorkEnergyConceptualTemplate` and invokes
the context-free conceptual generator. An odd effective seed passes a
`WorkEnergyGenerationInput` with the request seed and difficulty to the
injected `WorkEnergyProblemFactory`, which owns family selection, then passes
the generated problem to `WorkEnergyCalculationQuestionGenerator`. The
application performs no Work, Energy & Power calculations.

## Boundaries and safety

The service does not contain kinematics, SVG geometry, question-template,
marking, PDF, or LMS logic. It rejects unsupported configuration with stable
application error codes. A generated solution must pass solver validation
before the question generator is called.

The canonical `Assessment` retains expected answers, marking schemes,
question-part IDs, visuals, provenance, and `Assessment.memorandum`. The API
adapter creates a learner-safe projection that excludes expected answers,
marking schemes, memorandum entries, worked solutions, and answer-revealing
visual labels. Memorandum data is available only through the trusted
application-side `memorandum_for` operation pending a separately authorized
teacher contract.

The service uses the explicit request seed or deterministic default seed `0`.
The scenario factory and question generator retain their own versioned
provenance, so reproducibility is guaranteed for the current engine and policy
versions; changing those versions requires a deliberate reproducibility
boundary decision.
