# Work, Energy & Power calculation-question generation

Issue #78 packages each generated M5 authored problem as one canonical Grade
12 CAPS calculation question. `WorkEnergyCalculationQuestionGenerator` owns
wording, stable question/part IDs, response specifications, expected-answer
packaging, marking criteria, provenance, optional Issue #77 visuals, and safe
applicability failures.

The generator requires the exact `work-energy-and-power` CAPS Grade 12
Physical Sciences Mechanics topic. It receives an already generated
`GeneratedWorkEnergyProblem`; it does not select seeds, mutate scenarios, or
recalculate physics. Every numeric `ExpectedAnswer` comes directly from
`WorkEnergySolver`, with learner tolerance `0.01` kept separate from the
solver's internal consistency tolerance.

The 13 generated families each have one calculation template. Work, energy,
speed, and power units use `J`, `m/s`, and `W`. Signed solver semantics are
preserved. Prompts expose authored givens only; unknown targets remain a
request to calculate and never become zero. Scenario metadata and provenance
contain only answer-free curriculum, family, difficulty, generator, seed, and
template identity.

When `include_visuals=True`, supported families attach one safe SVG from the
Issue #77 renderer with numeric visibility disabled. Average power intentionally
has no visual. When disabled, prompts, parts, answers, IDs, metadata, and
provenance remain unchanged. The module adds no API route, conceptual rubric,
automatic marking, worked-solution engine, PDF output, or new generation
policy.
