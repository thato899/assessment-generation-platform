# M5 Work, Energy & Power CAPS coverage verification

## Verification status

This document verifies the approved, bounded M5 Work, Energy & Power slice
after Issue #83 merged. It adds evidence and regression checks only; it does
not add physics capability, a solver operation, a generation family, a renderer
family, an API route, or marking behavior.

The verification branch is
`feature/issue-84-work-energy-power-m5-verification`. Issue #84 is in progress
while this review PR is prepared. M5 is **ready for completion pending merge of
the Issue #84 verification PR** if the review remains clean. This document does
not claim universal Work, Energy & Power coverage.

## Authoritative curriculum basis

The primary source is the [DBE Physical Sciences Grades 10–12 CAPS
PDF](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf),
Section 3, Grade 12 Physics (Mechanics), Term 2, CAPS pages 117–120 (PDF
pages 121–124). The section allocates 10 hours to Work, Energy & Power and
specifies work, the work-energy theorem, conservation with non-conservative
forces, and power. The repository topic identifier is
`work-energy-and-power`. The DBE self-study guide is supplementary only.

## M5 implementation chain

| Layer | Issue / PR | Actual merge SHA |
| --- | --- | --- |
| CAPS scope and metadata | #73 / PR #86 | `17e6147c6fd2e60a74e94b9c99d2b8dbc897dd34` |
| Authored immutable domain | #74 / PR #87 | `9fb5da21a41ec8385dffc20c4971e968efdad82e` |
| Authoritative solver | #75 / PR #88 | `4b7bc2220ea962f6f115232729a5e0ccb52d4856` |
| Deterministic scenario factory | #76 / PR #89 | `2f0d3cb801bd8d29abca3bfa6d2f871bbe1f25bf` |
| Safe technical SVG renderer | #77 / PR #90 | `045a4c587b43d939e3dc70296e95d5bd3a708b04` |
| Calculation questions | #78 / PR #91 | `fccc3713ce2ed0827194ed077e67f95eb254522d` |
| Conceptual questions and rubrics | #82 / PR #92 | `0683927498e1720256431c040381016a65bebda4` |
| Existing application/API integration | #83 / PR #93 | `98fca9e5a80b1152a570a0baaf41f51dfb452532` |
| Final verification | #84 / this PR | pending |

The resulting path is CAPS metadata → immutable authored domain → deterministic
solver → deterministic scenario factory → safe technical SVG → solver-backed
calculation questions → conceptual questions and rubrics → existing v1
application/API route → this verification.

## CAPS coverage matrix

| CAPS requirement | Scope/domain evidence | Solver evidence | Generation evidence | Visual evidence | Calculation-question evidence | Conceptual-question evidence | API evidence | Tests | Status / notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Work as scalar | `WorkContribution`, scalar `SignedEnergy` | `work_by_force` | `WORK_BY_FORCE` | Force/displacement schematic | Work-by-force family | Scalar-work templates | Grade 12 route | Solver and conceptual tests | Complete within stated bound |
| Force-displacement relationship | Authored magnitude, displacement, angle | Cardinal-angle work operation | Bounded angle pools | Authored angle orientation only | Work-by-force prompt | Definition template | Existing endpoint | Solver/question tests | Complete |
| Positive work | Signed energy | 0° result | Positive angle/force pools | Direction only | Numeric expected answer | Sign rubric | Learner-safe projection | Sign parameterization | Complete |
| Negative work | Signed energy | 180° and signed contributions | Anti-parallel pools | Direction only | Numeric expected answer | Sign rubric | Learner-safe projection | Sign parameterization | Complete |
| Zero work | Zero force/displacement and 90° | Exact cardinal zero | Zero and perpendicular pools | No answer-dependent geometry | Numeric expected answer | Zero-work and perpendicular templates | Learner-safe projection | Solver/conceptual tests | Complete |
| Perpendicular force and zero work | `AngleDegrees(90)` | Exact cardinal cosine | 90° pool | Angle semantics only | Work-by-force family | Perpendicular template | Existing endpoint | Solver/conceptual tests | Complete |
| Individual work contributions | Ordered `NetWorkInput` | Per-contribution results | Net-work family | Contribution diagram | Net-work family | Individual versus net template | Existing endpoint | Solver/generation/question tests | Complete |
| Net work | Scalar tuple of contributions | `math.fsum` total | `NET_WORK` | Contribution schematic | Net-work family | Net-work template | Existing endpoint | Solver/generation tests | Complete |
| Work-energy theorem | `WorkEnergyContext` | `work_energy` | Three theorem families | Motion-state schematic | Three theorem templates | Theorem interpretation | Odd effective seed | Solver/generation/question/API tests | Complete within one-unknown bound |
| Kinetic energy | `KineticState`, `Mass`, `Speed` | `kinetic_energy` | `KINETIC_ENERGY` | Schematic motion state | Kinetic-energy family | Kinetic concept template | Existing endpoint | Solver/generation/question tests | Complete within stated bound |
| Horizontal-plane cases | Explicit scalar displacement/surface context | Direct scalar and constant-speed operations | Horizontal policy values | Horizontal surface schematic | Along-plane and power families | Surface-context template | Existing endpoint | Generation/renderer/question tests | Complete within stated bound |
| Inclined-plane cases | `SurfaceContext.INCLINED`, along-plane input | Along-plane scalar work | Inclined constant-speed values | Incline is schematic; no invented angle | Along-plane and constant-speed families | Surface-context template | Existing endpoint | Generation/renderer/question tests | Complete within stated bound |
| Frictionless cases | Zero/non-conservative work and explicit assumptions | Energy relationship accepts zero transfer | Bounded zero pools | Authored-only visuals | Work-energy/mechanical families | Friction and conservation concepts | Existing endpoint | Solver/generation/conceptual tests | Complete within stated bound |
| Rough/friction cases | Signed work and non-conservative context | Signed non-conservative energy | Non-conservative families | Force/displacement schematic | Mechanical-energy families | Friction template | Existing endpoint | Solver/generation/question tests | Complete within stated bound |
| Gravitational potential-energy change | `HeightState`, `RelativeHeight`, field | `potential_energy` | Gravitational-potential family | Reference-level diagram | Potential-energy family | Reference-level template | Existing endpoint | Solver/generation/question tests | Complete within explicit field bound |
| Explicit reference level | `ReferenceLevel` and state references | Reference identity retained in result | Authored reference level | Reference line and label | Authored prompt | Reference-level concept | Learner projection omits internals | Domain/solver/renderer tests | Complete |
| Conservative forces | `ForceEnergyClassification` and energy context | Zero non-conservative case validates conservation | Mechanical-energy family | No inferred force classification | Mechanical-energy family | Conservative-force template | Existing endpoint | Domain/solver/conceptual tests | Complete within stated bound |
| Non-conservative forces | Signed non-conservative work | Mechanical energy change is validated | Non-conservative-work family | Authored context only | Mechanical-energy family | Non-conservative template | Existing endpoint | Solver/generation/question tests | Complete within stated bound |
| Conservation with non-conservative work | `MechanicalEnergyContext` | Signed transfer reconciled | Mechanical-energy families | Height/motion schematic | Solver-backed numeric answer | Mechanical-versus-total concept | Existing endpoint | Solver/question/conceptual tests | Complete within stated bound |
| Mechanical-energy interpretation | Kinetic + potential states | `mechanical_energy` result | Mechanical-energy families | Height and motion diagrams | Mechanical-energy families | Mechanical versus total template | Existing endpoint | Solver/conceptual tests | Complete within stated bound |
| Mechanical vs total energy | Context and explicit non-conservative work | No thermodynamics inference | Bounded non-conservative family | No hidden energy geometry | Authored-only prompt | Dedicated conceptual template | Existing endpoint | Conceptual tests | Conceptual only by design |
| Power as rate | `AveragePowerInput` | `average_power` owns work/time | Average-power family | No visual by policy | Average-power family | Power-rate template | Existing endpoint | Solver/generation/question/API tests | Complete within stated bound |
| Equal work in different times | Work/time inputs | Average power operation | Time pools | No visual required | Average-power family | Same-work-different-time template | Existing endpoint | Solver/conceptual tests | Complete within stated bound |
| Constant-speed rough-surface power | `ConstantSpeedPowerInput` | Authored force-along-motion × speed | Constant-speed family | Horizontal/inclined category only | Constant-speed family | Constant-speed context template | Existing endpoint | Solver/generation/renderer tests | Complete within stated bound |
| Horizontal constant-speed context | `SurfaceContext.HORIZONTAL` | No Newton force solving | Horizontal policy values | Horizontal schematic | Constant-speed family | Conceptual context | Existing endpoint | Generation/renderer/API tests | Complete within stated bound |
| Inclined constant-speed context | `SurfaceContext.INCLINED` | No fake incline angle | Inclined policy values | Schematic incline only | Constant-speed family | Conceptual context | Existing endpoint | Generation/renderer/API tests | Complete within stated bound |
| Minimum ideal pumping/borehole power | `PumpingPowerInput` | `pumping_power` | Pumping family | Pump/lift schematic | Pumping family | Pumping assumptions template | Existing endpoint | Solver/generation/question/renderer tests | Complete within explicit ideal-input bound |
| Explicit gravitational field | `GravitationalFieldMagnitude` | Field is required; no hidden `g` | Field pools | Optional authored label | Potential/pumping families | Pumping assumptions | Existing endpoint | Domain/solver/generation tests | Complete |
| Mass-flow/lifting context | `MassFlowRate`, lift, field | Pumping operation | Pumping family | Water/lift schematic | Pumping family | Pumping assumptions | Existing endpoint | Solver/generation/question tests | Complete within stated bound |
| Relevant model assumptions | Frozen `WorkEnergyAssumptions` | Applicability/failure checks | Versioned policy | Authored labels only | Prompts preserve givens | Declarative assumption rubrics | Route has no hidden mode | Domain/solver/generation/question tests | Complete within stated bound |

## Layer-by-layer audit

The curriculum layer records Grade 12, Physical Sciences, Mechanics, Term 2,
10 hours, and the stable topic identifier. The authored domain consists of
frozen, slotted `WorkContribution`, `NetWorkInput`, `AlongPlaneWorkInput`,
`KineticState`, `HeightState`, `ReferenceLevel`, explicit gravitational fields,
`WorkEnergyContext`, `MechanicalEnergyContext`, `AveragePowerInput`,
`ConstantSpeedPowerInput`, `PumpingPowerInput`, `WorkEnergyAssumptions`, and
`UnknownValue`. It has no framework dependency, solver equation, hidden field,
or coupling to Newton, Momentum, or Projectile modules.

The #75 `WorkEnergySolver` is the only M5 numerical authority. The factory,
question generators, application, API, and renderer do not duplicate physical
equations. Source review found `cos` in the renderer only for authored angle
orientation and the numerical work/power/energy expressions only inside the
solver package. The renderer uses schematic geometry and does not infer answer
magnitudes.

## Curriculum audit

**PASS.** The repository metadata and focused verification test agree with the
DBE basis: CAPS, Grade 12, Physical Sciences, Mechanics, Term 2,
`work-energy-and-power`, and 10 hours. The evidence boundary is CAPS pages
117–120 (PDF pages 121–124); no Grade 10 energy prerequisite or unrelated
Grade 11 topic is counted as M5 coverage.

## Domain audit

**PASS.** The authored package contains the required immutable typed inputs and
assumptions listed in the matrix. `UnknownValue.UNKNOWN` is distinct from zero,
reference levels and gravitational fields are explicit, and construction is
structural only. No FastAPI, Pydantic, solver, generator, renderer, question,
or cross-domain import enters the authored package.

## Failure semantics audit

**PASS.** The solver exposes `UNDERDETERMINED`, `INCONSISTENT`, `UNSUPPORTED`,
and `NUMERICAL_RANGE`. Unknown values, contradictory authored states,
unsupported contact applicability, negative derived speed-squared, and checked
arithmetic failures are rejected explicitly. There is no silent repair,
arbitrary absolute-value conversion, or fabricated zero result.

## Work-energy theorem audit

**PASS within the stated bound.** Net-work, final-speed, and initial-speed
targets are represented. Both authored speeds are validated against net work;
exactly one unknown speed is derived when the other speed, mass, and net work
are authored. Two unknown speeds, contradictory states, and negative derived
speed-squared fail explicitly. The solver-created result is transient and the
authored `UnknownValue` remains unchanged.

## Potential/reference audit

**PASS.** Potential energy requires an authored mass, signed relative height,
reference level, and positive gravitational-field magnitude. Positive, zero,
and negative relative heights are preserved; no hidden `9.8` or `9.81` is
introduced. Mechanical-energy contexts require a shared reference level and
consistent field across initial and final states.

## Mechanical-energy audit

**PASS within the stated bound.** The solver reconciles kinetic plus
gravitational potential energy with signed non-conservative work and supports a
conservative zero-transfer case. It distinguishes mechanical energy from total
system energy conceptually and does not implement thermodynamics, springs, or
unbounded energy models. Final speed remains solver-owned.

## Power audit

**PASS within the stated bound.** Average power is solver-owned work divided by
positive authored time and is intentionally visual-free. Constant-speed power
uses authored force along motion and speed with a horizontal/inclined category;
it does not solve Newton forces or infer an incline angle. Pumping power uses
explicit mass flow, lift, and field for minimum ideal power, with no motor
efficiency, density conversion, pressure, or electrical model.

## Generation audit

**PASS.** The enum contains exactly 13 current families: work by force, net
work, along-plane work, kinetic energy, gravitational potential energy, three
work-energy targets, two mechanical-energy targets, average power,
constant-speed power, and pumping power. The factory uses local seeded random,
stable IDs/provenance, difficulty profiles, bounded deterministic retry, and
solver-backed acceptance. It stores no solver result and includes no answer in
IDs or provenance.

## Calculation-question audit

**PASS.** All 13 calculation families have solver-derived numeric
`ExpectedAnswer`s, SI units, stable question and part IDs, reconciled marks,
calculation response specifications, authored-only prompts, safe optional
visuals, and no duplicated equation. The 164 focused M5 tests include the
calculation generator corpus and refusal/answer-leakage checks.

## Memorandum audit

**PASS.** Both even-seed conceptual and odd-seed calculation application paths
produce canonical internal `Assessment.memorandum` entries. Each
`MemoEntry.question_part_id` equals the corresponding `QuestionPartId` and
retains the expected answer and marking scheme internally. No memo HTTP endpoint
is exposed.

## Determinism audit

**PASS.** The factory uses local `random.Random(seed.value)`, stable family
identifiers, versioned provenance, and bounded retries. Calculation and
conceptual generators replay equal immutable questions. The application uses
the effective seed, defaults omitted seeds to `GenerationSeed(0)`, and selects
conceptual questions for even seeds and calculation questions for odd seeds.
The focused verification test and existing generation/API tests confirm global
`random` state is unchanged.

## Numerical-authority audit

**PASS.** Checked finite arithmetic, `math.fsum`, exact cardinal-angle handling,
and the solver's `1e-9` validation tolerance are centralized in
`work_energy_power_solver`. Results are frozen and independently validated.
No intermediate answer rounding, hidden gravitational constant, answer-bearing
scenario field, or duplicate calculation exists outside that package.

## Solvability audit

**PASS within the approved model.** Direct operations require authored known
inputs. Work-energy solving accepts both authored speeds for validation or one
unknown initial/final speed; mechanical-energy solving accepts at most one
unknown speed or relative height with a shared authored field and mass. Power
operations require their explicit positive-time, speed, force, lift, field, or
mass-flow inputs. Unknowns remain `UnknownValue.UNKNOWN` and are never treated
as zero. The solver reports `UNDERDETERMINED`, `INCONSISTENT`, `UNSUPPORTED`,
and `NUMERICAL_RANGE` explicitly without fallback repair.

## Immutability audit

**PASS.** Domain, generation metadata, questions, solver results, and SVG
documents are frozen/slotted where their contracts require it. Solver calls,
factory acceptance, question generation, rendering, and application composition
operate on authored snapshots; the focused verification test confirms an
unknown final-speed target and global random state remain unchanged.

## Sign/reference-level audit

**PASS within the scalar/along-plane bound.** Work preserves positive,
negative, zero, perpendicular, and intermediate-angle signs. Net work is a
signed scalar sum. Along-plane work preserves a signed resultant. Relative
height may be positive, zero, or negative and is always tied to an authored
reference level and field. Inclined visuals communicate category and
orientation without inventing a numeric angle.

## Answer-leakage audit

**PASS.** Calculation prompts, IDs, provenance, scenario metadata, and SVGs do
not contain expected numeric answers. Conceptual answers are semantic token
tuples held in canonical internal parts and are absent from learner JSON.
Learner API projection recursively excludes expected answers, marking schemes,
rubrics, criteria, memo/memorandum, solution, solver, scenario, provenance,
concepts, correct-choice data, and worked solutions. Canonical internal
memoranda retain `ExpectedAnswer` and `MarkingScheme` entries linked by
`QuestionPartId`; no memo HTTP endpoint exists.

## Renderer safety audit

**PASS.** The renderer emits deterministic XML with `role="img"`, title,
description, `aria-labelledby`, escaped text, sanitized IDs, fixed geometry,
and no scripts, `foreignObject`, `javascript:`, event handlers, or remote
resources. Unknown values are shown as unknown and never as zero. Average
power intentionally has no visual. Manual visual inspection was **NOT
PERFORMED** because no browser or visual inspection surface was available in
the execution environment; XML and hostile-input tests provide automated
evidence instead.

## Conceptual learner-safety audit

The conceptual generator has 17 templates. Each has `ExpectedAnswerKind.TEXT`,
semantic concept tokens, declarative reconciled criteria, and only SHORT_TEXT or
LONG_TEXT response specifications. It has no solver dependency, numerical
equation, automatic marking, or API-specific behavior. Concept-token leakage is
checked both in generator tests and representative API responses.

## API learner-projection audit

The endpoint remains `POST /api/v1/assessments/generate`; no new endpoint or
version was added. The exact supported matrix is Grade 11 `newtons-laws` and
Grade 12 `vertical-projectile-motion-1d`, `momentum-and-impulse`, and
`work-energy-and-power`. M5 uses even effective seeds for conceptual output,
odd seeds for calculation output, omitted seed `0`, unchanged calculation
difficulty, and the existing visual preference. Application/API code imports no
M5 solver and contains no M5 equations. Invalid routes and generation errors
are returned as stable sanitized errors.

## Security audit

**PASS.** No secrets or new dependencies were added. SVG hostile-input tests
cover escaping and executable-content strings. API errors contain no traceback
or private implementation detail. CI quality and dependency-audit workflows
pass. Any local dependency advisories are environment/package-maintenance
findings and are not M5 defects; repository CI remains authoritative.

## Architecture/import-boundary audit

**PASS.** The authored domain and solver depend only on M5 domain contracts,
core validation where documented, and the standard library. Generation depends
on the M5 solver for acceptance but not on rendering, questions, API, or other
subject solvers. Rendering consumes authored scenarios only. Questions consume
solver results and authored prompts. Application/API code performs routing and
projection only. No cross-domain numerical dependency was found.

## Concept-token API leakage audit

**PASS.** Representative even-seed responses were compared with their internal
concept-token tuples; no raw token appears in learner JSON. Representative
odd-seed responses contain neither the calculation `ExpectedAnswer` object nor
the transient solver result. The recursive forbidden-key check is part of the
focused verification test and the existing API contract suite.

## Regression audit

Counts below are from this branch, not historical records:

- M5 focused domain/solver/generation/renderer/question/conceptual and #84
  verification tests: **164 passed**.
- Vertical Projectile regressions: **152 passed**.
- Momentum regressions: **351 passed**.
- Newton regressions: **328 passed**.
- Application/API plus core/curriculum regressions: **97 passed**.
- Post-#83 main baseline: **1,104 passed**. Final #84 branch full suite: **1,111 passed**.

## Quality-gate results

The final branch results are recorded in the PR and status file:

- `pytest -q`: **1,111 passed**.
- Coverage command: PASS; **90% total coverage** (6,277 statements, 613 missed).
  The application service remains **96%** and the API module **98%**.
- `ruff check src tests`: PASS.
- `mypy src`: PASS.
- `python -m build --wheel --outdir .artifacts`: PASS.
- `python -m pip check`: PASS.
- `git diff --check`: PASS.
- Repository CI quality and dependency audit: required PR gate; status recorded
  after push.
- Local `pip-audit --local`: 25 known vulnerabilities in the current environment
  (`anyio`, `click`, `idna`, `pip`, `pytest`, and `starlette`); the editable
  project is not published on PyPI. These are pre-existing environment/package
  maintenance findings, not M5 defects, and repository CI is authoritative.

## Partial and deferred capabilities

This verification deliberately does not claim support for springs or spring
potential energy, motor efficiency, variable-force integration, arbitrary
force-position functions, rotational work/energy, torque, thermodynamics, fluid
pressure or full fluid dynamics, arbitrary 3D mechanics, automatic numeric or
free-text marking, PDF/printing, LMS adapters, multi-question forms beyond the
current v1 route, database persistence, authentication, or M6 Mathematics
work. The pumping family is minimum ideal power with explicit mass flow, lift,
and field; it has no efficiency, density conversion, pressure, or electrical
model. Average-power output has no visual by design. These are documented
limitations or deferred scope, not verification failures.

## Blocking findings

**None identified.** No answer leakage, duplicated conflicting physics, broken
supported CAPS route, same-seed nondeterminism, unsafe SVG/API exposure, or
Projectile/Momentum/Newton regression was found. The lack of manual visual
inspection is a documented non-blocking limitation.

## M5 readiness conclusion

The approved bounded M5 Work, Energy & Power scope is evidence-backed across
curriculum, authored domain, solver, deterministic generation, safe rendering,
calculation questions, conceptual rubrics, and the existing v1 application/API
route. Deferred capabilities are explicit, and no blocking M5 implementation
gap was found.

**M5 is ready for completion pending merge of the Issue #84 verification PR.**
