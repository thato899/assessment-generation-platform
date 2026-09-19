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

The service supports CAPS, Physical Sciences, Grade 12, and
`vertical-projectile-motion-1d`. It deliberately supports
`assessment_type=question` and `question_count=1` only because the current
domain generator returns one scenario-based `Question`; question parts are
not treated as independent questions.

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
