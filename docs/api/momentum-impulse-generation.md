# Momentum & Impulse API generation

The existing `POST /api/v1/assessments/generate` endpoint now accepts the
existing CAPS topic identifier `momentum-and-impulse` for Grade 12 Physical
Sciences. The request schema is unchanged: use `assessment_type: "question"`,
`question_count: 1`, an existing difficulty value, an optional non-negative
seed, and `include_visuals` as usual.

The application service resolves the curriculum topic, creates a deterministic
typed problem through `MomentumProblemFactory`, and delegates to the Issue
#40 calculation or Issue #41 conceptual generator. A deterministic seed
selects the conceptual/calculation path; omitted seeds retain the existing
default seed of zero. Numeric pools and physics remain owned by the domain
factory and solvers.

The response is the existing learner-safe v1 projection. It includes question
prompts, marks, response specifications, and safe SVG visuals when produced;
it omits `ExpectedAnswer`, `MarkingScheme`, memo entries, rubrics, solver
objects, and answer-bearing provenance. `include_visuals: false` omits the
visual list. Unsupported curriculum, subject, grade, topic, assessment type,
and question count continue to use the existing stable 422 error shape.

The vertical-projectile route remains unchanged. Final M3 coverage verification
is deferred to Issue #43.
