# Newton's Laws application and API integration

Issue #61 exposes the completed Newton pipeline through the existing
`AssessmentGenerationService` and `POST /api/v1/assessments/generate` route.
The route remains the existing v1 contract; no Newton-specific endpoint,
request field, response DTO, or API version was added.

## Exact route matrix

The application validates the grade/topic pair as one route:

| Grade | Topic | Result |
| --- | --- | --- |
| 11 | `newtons-laws` | supported |
| 12 | `newtons-laws` | `unsupported_topic` |
| 12 | `vertical-projectile-motion-1d` | supported |
| 12 | `momentum-and-impulse` | supported |
| 11 | `vertical-projectile-motion-1d` | `unsupported_topic` |
| 11 | `momentum-and-impulse` | `unsupported_topic` |
| 10 | `newtons-laws` | `unsupported_grade` |

Newton remains Grade 11 curriculum ownership. Grade 12 consolidation and
examinability do not change that route.

## Orchestration and determinism

The service retrieves the CAPS topic, applies the effective seed, preserves the
requested `Difficulty`, and delegates to the existing Newton factory and
question generators. It performs no force, acceleration, friction, tension, or
gravitation calculation.

For the internal deterministic policy, an even effective seed selects a
`NewtonConceptualTemplate`; an odd effective seed selects a supported numeric
Newton generation family and `NewtonCalculationQuestionGenerator`. Conceptual
visual requests use a deterministic authored third-law context generated with
the same seed and difficulty. No global random state is touched.

Explicit seeds are used unchanged. An omitted seed uses
`DEFAULT_GENERATION_SEED = GenerationSeed(0)`. Identical requests therefore
produce identical canonical assessments and learner JSON.

`include_visuals=False` produces no visual assets. When enabled, the existing
#58 renderer output attached by the #59/#60 generators is passed through
unchanged.

## Canonical and learner-safe boundaries

Newton returns the existing canonical `Assessment` with an
`assessment-v1-...` identifier, `AssessmentType.QUESTION`, the Grade 11
Newton `CurriculumReference`, exactly one canonical `Question`, and the
effective seed. `AssessmentGenerationService.memorandum_for(...)` continues
to derive trusted teacher memorandum entries from canonical question-part IDs.

The existing API projection exposes only question IDs, prompts, parts, marks,
response specifications, and safe visual assets. It does not expose
`ExpectedAnswer`, `MarkingScheme`, rubric criteria, concept tokens, memo data,
solver results, scenario data, provenance, worked solutions, or hidden SVG
answer values. Internal canonical questions retain those structures for trusted
teacher-side memorandum use.

Errors remain stable and sanitized: invalid command, unsupported curriculum,
subject, grade, exact grade/topic route, assessment type, question count, and
difficulty are reported as application errors without stack traces or private
Newton details.

Projectile and Momentum routes keep their existing request and response
behaviour. Automatic marking, LMS integrations, new request knobs, API redesign,
and #62 CAPS/readiness verification remain out of scope.
