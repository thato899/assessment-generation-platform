# Vertical-projectile question generation

`VerticalProjectileQuestionGenerator` creates one canonical Grade 12 CAPS
Physical Sciences `Question` from validated domain data. It is a domain
service, not an HTTP handler, document renderer, solver, or marking engine.

## Inputs and outputs

The generator accepts:

- a `VerticalProjectileScenario`;
- a `VerticalProjectileSolution` produced and validated by
  `VerticalProjectileSolver`;
- the authoritative CAPS `CurriculumTopic` for
  `vertical-projectile-motion-1d`;
- an optional existing `GenerationSeed`; and
- an `include_visuals` option.

It returns one immutable canonical `Question`. Its stem contains the scenario
givens and CAPS assumptions. Its parts contain stable IDs, semantic response
specifications, structured expected answers, and declarative marking schemes.
The canonical assessment layer derives `MemoEntry` values from those parts.

## Template applicability

The first generator uses a deterministic coverage-oriented template set:

- acceleration direction, always;
- time to maximum height and maximum height, only when the solver reports a
  maximum-height event;
- return time to launch position, only when a later return event is distinct
  from ground impact; and
- ground-impact time and signed impact velocity, only when the solver reports
  a ground-impact event.

This means downward launches and dropped objects do not receive invented
turning-point or return questions. A scenario with fewer than two applicable
parts is rejected instead of producing a misleading assessment.

## Answers, marks, and determinism

Numeric expected answers use authoritative solver values, explicit SI units,
and a documented 0.01 tolerance. Display wording is separate from those
values. Calculation parts request working, a final answer, and units; the
impact-velocity part uses a numeric response; the acceleration part uses short
text. Marking criteria are explicit and total exactly the part maximum without
prescribing one brittle method.

Template selection is deterministic and currently seed-independent so the
pedagogical coverage does not vary accidentally. The supplied seed is retained
in `GenerationProvenance` together with the generator version and selected
template IDs. No global random state, timestamp, or random UUID is used.

## Visual integration and boundaries

When visuals are requested, the generator calls `ProjectileSvgRenderer` with
numeric event labels disabled to avoid answer leakage. The resulting SVG is
carried as a core `VisualReference`; the generator does not redraw it or
recalculate its physical values. Visuals are omitted when disabled.

The implementation remains limited to one generated question. API success
responses, assessment composition, learner marking, printable documents,
adaptive difficulty, LLM generation, and LMS integration remain future work.
