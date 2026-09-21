# Assessment generation API v1

The versioned boundary is `POST /api/v1/assessments/generate`. It supports one
deterministic learner-safe question for each approved CAPS Physical Sciences
route: Grade 12 vertical projectile motion, Momentum & Impulse, Work, Energy &
Power, and Grade 11 Newton's Laws.

## Supported capability

| Field | Supported value |
| --- | --- |
| `curriculum` | `CAPS` |
| `subject` | `physical-sciences` |
| `grade` | `12` |
| `topic` | one of the approved topic IDs in the route matrix below |
| `assessment_type` | `question` |
| `question_count` | `1` |
| `difficulty` | `introductory`, `moderate`, or `advanced` |

The Work, Energy & Power route uses the exact Grade 12 topic identifier
`work-energy-and-power`. The supported grade/topic pairs are Grade 12
`vertical-projectile-motion-1d`, Grade 12 `momentum-and-impulse`, Grade 11
`newtons-laws`, and Grade 12 `work-energy-and-power`.

The request is mapped to the framework-independent application service. The
service selects the CAPS topic, passes a typed `ScenarioGenerationInput` to
the deterministic vertical-projectile scenario factory, validates the
authoritative solver result, invokes the question generator, and composes one
canonical `Assessment`.

## Request

The request contains these boundary fields:

- `curriculum`, `subject`, `grade`, and `topic` stable identifiers;
- `assessment_type`, which must be `question` for the supported paths;
- `question_count`, which must be `1`;
- `difficulty`, mapped directly to the Issue #24 factory profile;
- `include_visuals`, defaulting to `true`; and
- an optional non-negative 64-bit `seed`.

An explicit seed is preserved as the generation seed. When omitted, the
application uses the documented deterministic default seed `0` and returns
`effective_seed: 0`. No timestamps, UUIDs, process state, or module-global
randomness are used.

Positive-direction and scenario-family options are not public v1 request
fields. The application therefore uses the factory's supported default
coordinate policy and does not expose the factory's down-positive elevated
limitation as an API transformation or hidden fallback.

## Successful response

The response is versioned with `api_version: "v1"` and contains the stable
assessment and question identifiers, prompts, marks, semantic response
specifications, effective seed, curriculum metadata, and optional visual
assets. It is a learner-safe projection only.

For Work, Energy & Power, the effective seed selects the question type
deterministically: even seeds select a context-free conceptual template and
odd seeds pass through the scenario factory and calculation question
generator. Request difficulty is propagated to calculation generation;
conceptual templates are not difficulty-parameterized. The omitted default
seed is `0`, so it selects a conceptual question.

`include_visuals=true` carries safe deterministic SVG output only when the
selected calculation family has a justified Issue #77 diagram. Average power
intentionally has no visual. Conceptual Work, Energy & Power questions have
no visuals even when `include_visuals=true`. In all routes,
`include_visuals=false` returns no visual assets.

The canonical assessment remains complete inside the application boundary,
including expected answers, marking schemes, question-part IDs, provenance,
and memorandum derivation. The learner response never serializes those
teacher-side fields. `AssessmentGenerationService.memorandum_for` provides
canonical memorandum entries to a trusted future teacher-side caller; no
unauthenticated teacher endpoint is exposed by this issue.

## Determinism and responsibility boundaries

For the same request, effective seed, current factory/generator versions, and
curriculum configuration, the canonical assessment and learner projection are
semantically identical. The scenario factory owns initial-condition policy,
the solver owns all trajectory calculations, the question generator owns
template applicability and canonical question parts, and the API adapter only
maps DTOs and projections. See the scenario-generation documentation for
numeric pools and the down-positive elevated limitation.

## Errors and compatibility

Malformed DTOs return HTTP 422 with `invalid_request` and safe field details.
Well-formed but unsupported combinations return HTTP 422 with stable codes
such as `unsupported_subject`, `unsupported_topic`,
`unsupported_assessment_type`, or `unsupported_question_count`.
Unexpected generation failures return HTTP 500 with the sanitized
`generation_failed` error. Internal exception details, framework paths, and
implementation objects are not exposed.

The previous HTTP 503 `generation_engine_unavailable` response is no longer
returned for the supported generation paths. Future engines and capabilities
remain unsupported and must be added deliberately rather than being routed
through this service.

The canonical application assessment retains expected answers, marking
schemes, provenance, and memorandum derivation for both M5 question types;
there is no memo endpoint. No automatic marking, teacher authorization,
learner submissions, printable documents, LMS integration, or additional
subjects/topics are implemented.
