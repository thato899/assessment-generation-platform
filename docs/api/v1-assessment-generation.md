# Assessment generation API v1

The versioned boundary is `POST /api/v1/assessments/generate`. It defines the
request and response contract without claiming that every request is
generatable. The current implementation returns `503
generation_engine_unavailable` until the application layer has both a
generation service and a deterministic scenario-creation capability. The
vertical-projectile question generator itself exists but requires a validated
scenario input.

## Request

The request requires these explicit identifiers:

- `curriculum`: currently `CAPS`
- `subject`: currently `physical-sciences`
- `grade`: currently `12`
- `topic`: a supported CAPS topic identifier
- `assessment_type`: `question`, `quiz`, `practice_set`, `worksheet`,
  `homework`, `test`, `diagnostic`, or `examination`
- `question_count`: an integer from 1 through 100
- `difficulty`: `introductory`, `moderate`, or `advanced`
- `include_visuals`: whether visual assets may be included, defaulting to `true`
- `seed`: an optional non-negative 64-bit integer

Unknown fields are rejected. These DTOs are boundary types; the mapper creates
the framework-independent core `AssessmentRequest` value objects without
putting FastAPI or Pydantic into the domain model.

If `seed` is supplied, it is the requested deterministic generation seed. The
same future generator inputs, implementation version, and seed must produce
the same result. The API response reserves `effective_seed` so a later
implementation can expose the seed used when one was not supplied.

## Response boundary

The successful response is versioned with `api_version: "v1"` and contains
stable assessment and question identifiers, prompts, mark totals, response
specifications, and optional deterministic visual asset references. Learner
question DTOs intentionally contain no expected answers, marking schemes,
memorandum entries, or worked solutions.

Teacher/memorandum data is represented separately by `TeacherMemoEntryDto` and
is not part of the learner response projection. A future authenticated teacher
workflow must expose it through a separately designed contract.

## Errors and compatibility

Validation failures return HTTP 422 with the stable error code
`invalid_request`, a safe message, and field-level details. An unavailable
generation engine returns HTTP 503 with `generation_engine_unavailable`.
Internal exception details, framework paths, and implementation objects are
not exposed. Breaking changes require a new `/api/v2/` namespace.

The contract has no LMS, database-table, subject-engine, renderer, or
framework dependency. It is a boundary for a later application service, not a
claim that assessment generation is already implemented.
