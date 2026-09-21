# M5 Work, Energy & Power planning

Issue #77 is merged as the authored-only technical SVG renderer. Issue #78 is
the active solver-backed calculation-question generator; #82 remains deferred.

## Planning status

M4 Newton's Laws is complete after PR #72 merged at
`20b763ccde63ede025d97c3ee2aa772400e1b9f5`; Issue #62 is closed. M5
planning is complete through PR #85, and the #73 curriculum contract merged at
PR #86 (`17e6147c6fd2e60a74e94b9c99d2b8dbc897dd34`). Issue #74 owns the
framework-independent authored domain and merged via PR #87 at
`9fb5da21a41ec8385dffc20c4971e968efdad82e`. Issue #75 owns the numerical
solver and merged via PR #88 at `4b7bc2220ea962f6f115232729a5e0ccb52d4856`.
Issue #76 owns deterministic scenario generation, Issue #77 owns the merged
technical renderer, and Issue #78 owns the active calculation-question layer.
API and conceptual work remain deferred.

The M5 GitHub milestone `M5 - Work, Energy & Power` exists. The proposed issue
sequence below is planned on top of the existing M4 pipeline and is tracked by
separate implementation issues. Issue #78 is the active implementation and
review item for solver-backed calculation questions.

## Authoritative CAPS basis and placement

The primary authority is the DBE [Physical Sciences Grades 10–12 CAPS
PDF](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf),
Section 3, Grade 12 Physics (Mechanics), Term 2, pages 117–120 (PDF pages
121–124). CAPS assigns 10 hours to Work, Energy & Power in Grade 12. It names
work, the work-energy theorem, conservation of energy with non-conservative
forces present, and power. The [DBE Work Energy and Power self-study guide](https://www.education.gov.za/SelfStudyGuidesGrade10-12.aspx)
and DBE digital-content listing are supplementary support references only.

The stable repository topic identifier is the existing
`work-energy-and-power` entry in the CAPS Physical Sciences curriculum metadata.
The topic is Grade 12, Mechanics, and is distinct from Grade 10 introductory
energy content and Grade 11 Newton's Laws ownership.

## Approved planning scope

The detailed curriculum and architecture contract is
[work-energy-power-scope.md](../domains/physical-sciences/work-energy-power-scope.md).
The planned engine will cover:

- scalar work from authored force, displacement, and angle relationships;
- signed positive, negative, and zero work, individual contributions, and net
  work;
- the alternate along-plane resultant method;
- kinetic energy and the work-energy theorem on horizontal and inclined,
  frictionless and rough cases;
- near-Earth gravitational potential-energy changes with authored height,
  reference level, and field;
- mechanical-energy relationships with explicit conservative and
  non-conservative work/energy data; and
- average power, constant-speed rough-surface power, and bounded minimum
  motor/pumping power with explicit mass-flow, depth, and field inputs.
  Motor efficiency is not a CAPS requirement and is deferred as a non-ideal
  extension.

The solver must remain the sole numerical authority. It must report explicit
underdetermined, inconsistent, unsupported, and numerical-range failures using
the established conventions rather than fabricating zeros or hidden values.

## Architecture boundaries

M5 follows the established pipeline:

```text
CAPS scope and metadata
        |
        v
authored immutable Work/Energy/Power domain
        |
        v
authoritative deterministic solver
        |
        v
bounded deterministic scenario factory
        |
        v
safe technical renderer where justified
        |
        v
solver-backed calculation questions
        |
        v
conceptual questions and declarative rubrics
        |
        v
existing application/API route
        |
        v
final CAPS coverage verification
```

The #74 domain and later solver remain framework-independent. Application/API layers
orchestrate and project learner-safe data; they do not calculate work, energy,
or power. Generation does not copy equations. Rendering consumes authored
values and does not infer physics.

M5 must not tightly couple to `NewtonConceptualQuestionGenerator`, Newton
application routing, or Newton solver internals. It may reuse low-level value
objects only where units and invariants match exactly. Work scenarios author
scalar force contributions, displacement, angles, and energy/power inputs; any
future shared mechanics capability requires a separate reviewed boundary.

## Reuse decisions

Reuse from the platform core:

- `Assessment`, `Question`, `QuestionPart`, response specifications, expected
  answer and marking models;
- `GenerationSeed`, `GenerationProvenance`, `VisualReference`, difficulty, and
  learner-safe API projection infrastructure;
- generic validation, deterministic-ID, curriculum-reference, and SVG safety
  helpers where their contracts are subject-independent.

Issue #74 uses local M5 value objects because the existing Newton and Momentum
quantities have different semantic invariants. Newton force ownership, contact
solving, string solving, question generation, and application routing are not
reused.

Momentum and projectile domain models remain separate. No shared abstraction is
created merely because two classes have similar names.

The current solver contract is documented in
[work-energy-power-solver.md](../domains/physical-sciences/work-energy-power-solver.md).

## Proposed issue sequence

The implementation order is:

| Order | Responsibility | Issue |
| --- | --- | --- |
| A | Validate CAPS Work, Energy & Power scope and curriculum metadata | #73 |
| B | Define immutable framework-independent Work/Energy/Power domain representations | #74 |
| C | Implement the authoritative deterministic solver and validation | #75 |
| D | Implement bounded deterministic scenario-generation policy/factory | #76 |
| E | Implement a safe deterministic technical SVG renderer where justified | #77 |
| F | Implement solver-backed calculation question generation | #78 |
| G | Implement conceptual templates and machine-readable rubrics | #82 |
| H | Integrate the approved route into the existing application/API | #83 |
| I | Verify CAPS coverage, regressions, security, and M5 readiness | #84 |

Issues #79–#81 were duplicate creations caused by a command timeout and are
closed as duplicates of #82–#84. They are not part of the M5 dependency graph.

## Dependency graph

```text
A #73 CAPS scope and metadata
          |
          v
#74 authored domain representations
          |
          v
#75 authoritative solver
          |
          v
#76 deterministic scenario factory
          |
          v
#77 technical renderer (only justified visuals)
          |
          v
#78 calculation questions
          |
          v
#82 conceptual questions/rubrics
          |
          v
#83 application/API integration
          |
          v
#84 final CAPS verification
```

## Calculation-family plan

Future calculation questions must map one-to-one to successful solver results:

- work by one force for parallel, antiparallel, perpendicular, and bounded-angle
  authored relationships;
- scalar individual-force contributions and net work;
- work by a resultant force along a horizontal or inclined plane;
- kinetic energy and change in kinetic energy;
- initial/final speed, mass, or net work through the work-energy theorem, with
  one authored unknown per independent relationship;
- gravitational potential-energy change with an explicit near-Earth field and
  reference-level convention;
- conservative/mechanical-energy relationships with explicit non-conservative
  work or energy change;
- average power from work and positive time;
- constant-speed rough horizontal/inclined power using authored force and speed;
  and
- minimum motor/pumping power for an authored water mass/rate, depth, and
  near-Earth field; non-ideal efficiency is outside the CAPS requirement.

Unsupported angles, missing reference levels, hidden contact assumptions,
multiple unknowns, inconsistent authored states, and numerical overflow or
underflow must fail explicitly.

## Conceptual-family plan

Evaluate definitions and misconceptions without performing numerical physics:

- work as a scalar and the meaning of positive, negative, zero, and
  perpendicular work;
- individual work versus net work and positive/negative net energy change;
- work-energy theorem interpretation;
- kinetic versus potential energy and reference levels;
- conservative versus non-conservative forces and mechanical versus total energy;
- friction as an appropriate non-conservative work contribution;
- power as a rate, including equal work in different times producing different
  power; and
- constant-speed surface and motor/pumping assumptions.

Conceptual answers should use machine-readable concept tokens and declarative
rubrics, as in the completed Newton and Momentum boundaries.

## Renderer plan

Do not require SVG for every M5 question. A future renderer should be added only
if a visual materially clarifies an authored relationship. Candidate technical
visuals are force/displacement and angle diagrams, rough horizontal or inclined
surfaces, height/reference-level diagrams, and simple energy-state schematics.
All visuals must be deterministic, data-derived, accessible, safely escaped,
and free of answer-dependent geometry or hidden values. No generative imagery
is planned.

## API integration plan

Reuse `POST /api/v1/assessments/generate`; do not add an M5-specific endpoint or
API version. After scope and implementation issues are complete, the likely
route is Grade 12 plus the existing `work-energy-and-power` topic identifier.
The exact route, assessment-type policy, seed behavior, difficulty handling,
and learner projection must be specified in the API issue after the domain and
question contracts exist. No API code changes are part of this planning branch.

## Risks and deferred items

Risks include mixing Grade 10 energy prerequisites with the Grade 12 topic,
under-specifying reference levels or pumping inputs, duplicating Newton
force-solving equations, and adding diagrams that expose answers. The bounded
scalar representation deliberately avoids a general vector or calculus engine.

Unless later CAPS evidence requires otherwise, rotational work/torque, springs
and spring potential energy (not present in the approved Grade 12 Work, Energy
& Power pages), motor-efficiency modelling, thermodynamics, relativistic energy,
variable-mass systems, fluid dynamics,
3D vector geometry, arbitrary force-position functions, automatic/free-text
marking, PDF/printing, LMS adapters, a new API version, and M6 Mathematics work
remain outside M5.

## M5 definition of done

M5 is complete only when:

- the approved CAPS scope and stable topic metadata are documented;
- immutable authored domain models preserve units, assumptions, unknowns, and
  reference levels without calculating results;
- the deterministic solver is authoritative, replayable, independently
  validates results, and reports explicit failure states;
- generation is bounded, deterministic, solver-validated, and does not leak
  answers or mutate authored inputs;
- technical visuals are included only where justified and are safe,
  deterministic, accessible, and learner-safe;
- calculation questions consume solver results and conceptual questions use
  declarative rubrics without duplicating equations;
- the existing API integrates the approved route with stable errors and a
  learner-safe projection;
- unsupported and deferred physics are explicit;
- Projectile, Momentum, and Newton regressions remain green; and
- a final CAPS coverage matrix records evidence, tests, assumptions, and
  remaining limitations.

M5 planning remains the scope and dependency reference. Numerical solving is
merged through Issue #77; Issue #78 is active and later issues remain deferred
until that review is complete.
