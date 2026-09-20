# Momentum & Impulse calculation question generation

Issue #40 adds `MomentumQuestionGenerator`, which consumes typed outputs from
`MomentumProblemFactory`, delegates every numerical result to the existing
aggregate, constrained-collision, or relationship solver, and returns the
canonical core `Question` model. It supports body and system momentum,
momentum change, impulse, average force, contact time, uniquely constrained
final velocity, explicit sticking common velocity, and classification from a
complete validated state.

Template applicability is structural: each generated problem family maps to
its own template, and underdetermined collision problems have no final-state
template. IDs and provenance are deterministic and contain no answer values.
Calculation parts use `ResponseKind.CALCULATION`, structured numeric or text
`ExpectedAnswer` values with the existing tolerance, and declarative marking
schemes whose criteria total the part marks.

Prompts communicate the positive axis and signed SI data. Optional visuals
reuse `MomentumSvgRenderer`; learner-safe rendering hides requested derived
answers. Conceptual templates and rubrics (#41), API integration (#42), and
automatic marking remain deferred.
