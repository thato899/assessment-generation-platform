# M4 Newton's Laws CAPS coverage verification

## Verification status

This verification was performed on the post-#61 `main` baseline, merge
`7a3d8b835df770166f69c62a722ab63508aabb6f`, and the
`feature/issue-62-newton-m4-verification` branch. Issues #54 through #61 are
implemented and merged. The verification covers the approved bounded M4 scope;
it does not claim universal Newton mechanics coverage.

## Authoritative curriculum basis

The [Issue #54 scope contract](../domains/physical-sciences/newtons-laws-scope.md)
uses the official [DBE CAPS Physical Sciences Grades 10–12
document](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf).
The approved topic identifier is `newtons-laws`.

Newton's Laws are Grade 11 core instructional content. Grade 12 is represented
as consolidation, integrated problem solving, and selected examinability of
Grade 11 content. The application route preserves Grade 11 ownership: only
`(Grade 11, newtons-laws)` is supported.

## M4 implementation chain

```text
CAPS scope (#54)
  -> immutable authored Newton domain (#55)
  -> authoritative deterministic solver (#56)
  -> seeded scenario factory (#57)
  -> safe SVG renderer (#58)
  -> numeric questions (#59) and conceptual rubrics (#60)
  -> existing v1 application/API route (#61)
  -> canonical Assessment and learner-safe projection
```

## CAPS coverage matrix

| CAPS requirement | Scope/domain evidence | Solver | Generation | Visual | Calculation questions | Conceptual questions | API | Tests | Status / notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Signed resultants and net force | `ForceVector`, explicit Cartesian 1D/2D bases | Signed resultant and body dynamics | Newton II and equilibrium families | Signed semantic arrows | Resultant and equilibrium templates | Zero-resultant and equilibrium templates | Grade 11 route | Solver, generation, renderer, question, conceptual, API suites | **Complete within authored 1D/2D bound** |
| 2. Force types: weight, normal, friction, applied, tension | `ForceKind`, source/target ownership, contacts and strings | Weight/contact/friction/tension operations | Weight, contact, friction, connected families | Type-safe labels and ownership | All supported force calculation templates | Force-type identification | Newton route | Domain and all Newton layer suites | **Complete within stated bounded cases** |
| 3. Force diagrams | Authored bodies, forces, environments, systems | Not applicable | All generated families produce authored scenarios | Deterministic force diagrams, labels, boundaries | Optional #58 visuals | Force-diagram interpretation | Safe visual projection | Renderer safety and family corpus tests | **Complete** |
| 4. Free-body diagrams | `NewtonScenario.free_body_for` isolates one body | Ownership is validated by domain/solver | Generated bodies can be selected | Selected-body FBD excludes forces on other bodies | Optional renderer output | FBD and force-diagram distinction | Safe visual projection | FBD ownership and API leakage tests | **Complete within one selected authored body** |
| 5. Newton I | Curriculum concepts and assumptions | Equilibrium/zero-acceleration semantics | Equilibrium family | Diagram support | No standalone numeric First-Law formula template | Newton I token/rubric requires rest or constant velocity, zero resultant, and non-zero resultant changing motion | Conceptual path | Conceptual template and solver equilibrium tests | **Conceptual and equilibrium support; no standalone numeric First-Law template** |
| 6. Newton II | Mass, force, acceleration, inertial/constant-mass assumptions | Authoritative Newton II dynamics and authored acceleration validation | Newton II and unknown-force families | Signed force/acceleration context | Resultant and acceleration templates | Newton II token/rubric | Calculation or conceptual path | Solver, generation, question, conceptual, API tests | **Complete within constant-mass 1D/2D bound** |
| 7. Newton III | Third-law pair reverses source/target ownership | Equal/opposite numerical validation | Newton III family | Partner forces remain on their own bodies | No standalone derived Newton III numeric template | Newton III and action-reaction templates require same interaction, equal magnitude, opposite direction, different bodies | Conceptual path | Domain, solver, renderer, calculation refusal, conceptual tests | **Complete concept/validation support; numeric derivation intentionally absent** |
| 8. Equilibrium and non-equilibrium | Explicit selected system and force facts | Zero resultant and equilibrium validation | Equilibrium family | Authored arrows | Equilibrium resultant template | Dynamic equilibrium and non-equilibrium distinction | Route exposed | Solver, generation, question, conceptual tests | **Complete; equilibrium includes rest or constant velocity** |
| 9. Horizontal force cases | Cartesian RIGHT/LEFT 1D basis | Signed 1D components | Newton II, unknown, contact/friction families | Cartesian mapping | Resultant, acceleration, unknown and contact templates | Relevant conceptual families | Newton route | Domain, solver, generation, renderer, question, API tests | **Complete within bounded single-body/two-body cases** |
| 10. Inclined-plane cases | `SurfaceCoordinates`, authored inclination and ALONG/NORMAL directions | Contact/friction in surface basis; Cartesian inclined contact explicitly unsupported | Inclined-plane family | Surface mapping is display-only | Inclined normal calculation template | Normal/friction concepts | Newton route | Surface solver, generation, renderer and question tests | **Supported with surface-aligned basis; no duplicate trig or Cartesian inclined-contact inference** |
| 11. Vertical force cases | 2D Cartesian UP/DOWN and authored gravitational fields | Weight, normal, apparent-weight and dynamics operations | Weight/contact/Newton II families | Vertical semantic directions | Weight, normal, apparent-weight and acceleration templates | Weight, apparent-weight, weightlessness concepts | Newton route | Solver contact/weight, generation, question, API tests | **Supported where authored field/force data determine the result** |
| 12. Static friction | Contact/friction regime and signed authored force | Required balance with `0 <= f_s <=` the static limit | Static-friction family | Contact labels and directions | Static-friction template | Static friction adapts and is not always limiting | Newton route | Static-friction bound and misconception tests | **Complete within authored contact model** |
| 13. Limiting static friction | Distinct `LIMITING_STATIC` regime | Maximum static value and threshold validation | Limiting-static family | Contact diagram | Limiting-static template | Static-limit concept | Newton route | Limiting-friction solver/generation/question/concept tests | **Complete and distinct from ordinary static friction** |
| 14. Kinetic friction | Distinct `KINETIC` regime and tangent direction | Magnitude/direction validation | Kinetic-friction family | Contact diagram | Kinetic-friction template | Static/kinetic distinction | Newton route | Kinetic friction tests | **Supported within authored sliding-contact assumptions** |
| 15. Mass versus weight | `Kilograms`, authored gravitational field, force units | Weight uses authored field only | Weight family | Authored field/force context | Weight calculation | Mass/weight concept with kg versus N and field dependence | Newton route | Domain, solver, generation, question, conceptual tests | **Complete within authored-field model** |
| 16. Apparent weight | Contact normal/support relationship | Apparent weight from actual support force | Contact families | Contact diagram | Apparent-weight part | Weight versus apparent weight distinction | Newton route | Contact solver/question/concept/API tests | **Complete; support force is not silently equated to gravity** |
| 17. Weightlessness | Contact/support semantics | Zero support result where authored conditions allow | Contact families | Safe contact visual | Apparent-weight calculation context | Weightlessness concept explicitly permits gravity | Newton route | Apparent-weight and conceptual misconception tests | **Conceptual and supported-contact result; not a zero-gravity claim** |
| 18. Light string/two-body systems | Exactly two bodies, straight taut inextensible string | Common acceleration and signed tension | Connected-bodies family | Straight string and system boundary | Acceleration and tension templates | Light-string assumptions | Newton route | Domain, solver, generation, renderer, question tests | **Complete for bounded straight two-body case** |
| 19. Universal gravitation | Two-body interaction and positive separation | Scalar magnitude with fixed DBE constant | Universal-gravitation family | Authored interaction visual without invented vector | Gravitational magnitude template | Universal-gravitation concept | Newton route | Gravity solver/range, generation, renderer, question, conceptual tests | **Magnitude-only; line-of-centres vector direction is not authored** |
| 20. System/environment | `SystemBoundary`, `EnvironmentReference` | External resultant by membership | System-bearing generated scenarios | System boundaries | Contextual prompts | System/environment concept | Newton route | Domain, solver, conceptual, API tests | **Complete** |
| 21. Internal/external forces | Source/target membership semantics | Classification derives from selected system | Authored scenario context | Ownership-preserving diagrams | Context retained in numeric prompts | Internal/external concept | Newton route | Domain, solver, conceptual tests | **Complete within explicit system boundary** |
| 22. Action/reaction ownership | `ThirdLawPair` and reversed ownership invariants | Numerical equal/opposite validation | Newton III family | Partner arrows on different bodies | Numeric template intentionally rejected | Action/reaction concept and authored ownership | Newton route | Domain, solver, renderer, conceptual, API tests | **Complete except standalone numeric derivation** |
| 23. Assumptions | `NewtonAssumptions`, contact/friction and string declarations | Applicability checks enforce assumptions | All generated families use versioned assumptions | Renderer displays authored context only | Prompts preserve relevant assumptions | Inertial frame, constant mass, air resistance, contact and string concepts | Newton route | Domain, generation, question, conceptual tests | **Complete for approved assumptions; unsupported cases remain explicit** |

## Layer-by-layer audit

### #54 curriculum

`physical_sciences.py` provides the stable Grade 11 `newtons-laws` topic,
concepts, constraints, and assessment metadata. The scope contract preserves
Grade 12 consolidation and examinability without changing ownership. Curriculum
lookup tests cover the metadata and the API route tests enforce the exact
grade/topic matrix.

### #55 domain

The Newton domain is frozen and framework-independent. It models SI values,
1D/2D Cartesian and surface coordinates, signed components, unknown values,
bodies, force source/target ownership, systems/environments, surfaces,
contacts/friction, strings, third-law pairs, authored accelerations, fields,
and gravitational interactions. Structural validity is separate from numerical
solvability; unknown components are never interpreted as zero.

### #56 solver

`NewtonSolver` is the numerical authority for signed resultants, Newton II,
equilibrium, one-unknown-per-axis solving, authored acceleration validation,
weight, normal/contact, apparent weight, static/limiting/kinetic friction,
straight-string connected bodies, third-law validation, and scalar universal
gravitation. Failures are explicit `UNDERDETERMINED`, `INCONSISTENT`,
`UNSUPPORTED`, or `NUMERICAL_RANGE` outcomes. Results and scenarios are
immutable and independently validated.

### #57 generation

`NewtonProblemFactory` advertises and tests all twelve families: Newton II,
unknown force, equilibrium, weight, normal contact, static friction, limiting
static friction, kinetic friction, inclined plane, connected bodies, universal
gravitation, and Newton III. Local seeded randomness, stable IDs/provenance,
bounded difficulty pools, authored unknown preservation, and solver-backed
acceptance are covered by 22 generation tests.

### #58 renderer

`NewtonSvgRenderer` emits deterministic valid SVG with accessibility metadata,
safe escaping, Cartesian/surface direction mapping, system boundaries, strings,
and selected-body FBD ownership. Unknown/hidden values use fixed geometry and
do not appear in text, IDs, metadata, or attributes. Renderer tests cover
hostile labels, script-related payloads, hidden values, directions, FBDs, and
all generated families.

### #59 calculation questions

`NewtonCalculationQuestionGenerator` delegates answers to `NewtonSolver` and
covers signed resultants, acceleration, unknown force, weight, normal,
apparent weight, static/limiting/kinetic friction, inclined normal, connected
acceleration, tension, and universal-gravity magnitude. It preserves authored
givens, signs, units, tolerances, stable IDs, provenance, and reconciled marks.
Newton III validation has no standalone derived numeric template by design.
The 17-test calculation suite covers applicability refusal and answer leakage.

### #60 conceptual questions

`NewtonConceptualQuestionGenerator` contains 20 deterministic templates with
concept-token `ExpectedAnswer`s and declarative rubrics. Marks reconcile with
part totals; Newton I/II/III terminology and misconceptions about action/reaction,
normal force, static friction, equilibrium, and weightlessness are tested. The
generator performs no numerical solving or automatic marking and can attach
safe #58 visuals.

### #61 application/API

The existing v1 request and response DTOs are unchanged. The application
enforces the exact route matrix, uses `GenerationSeed(0)` when omitted, selects
conceptual for even seeds and calculation for odd seeds, preserves difficulty
and visuals, composes the canonical `Assessment`, and retains trusted
memorandum derivation. Learner JSON contains only the established question,
part, response-specification, and safe visual fields. Sixty focused
application/API tests provide 97% combined coverage.

## Determinism audit

**PASS.** Evidence includes generation replay/provenance tests, calculation
question replay and semantic-ID tests, conceptual replay tests, byte-identical
SVG tests, application repeated-request tests, API repeated-JSON tests,
omitted-seed tests resolving to zero, and global `random` state checks. Seeds
are explicit `GenerationSeed` values; generators use local RNG instances.
Inspection found no `uuid4`, timestamps, process-dependent hash IDs, or global
random calls in the M4 pipeline.

## Sign/vector audit

**PASS within the stated bound.** Domain and solver tests cover RIGHT/LEFT,
UP/DOWN, signed 1D and 2D components, independent axes, negative support and
force signs, and surface ALONG/NORMAL coordinates. Renderer tests verify that
semantic directions and negative components change screen vectors without
recalculating physics. Unknown values remain distinct from zero. M4 does not
claim arbitrary 3D vector mechanics.

## Solvability audit

**PASS.** Structurally valid but underdetermined scenarios are preserved by the
domain and rejected by the solver or question generator before an answer is
returned. Tests cover underdetermined axes, inconsistent authored acceleration,
unsupported Cartesian inclined contact, invalid orientations, friction bounds,
slack/extensible/wrong-direction strings, unknown coefficients, third-law
unknown components, and numerical overflow/underflow. No silent fallback or
fabricated zero result is used.

## Answer-leakage audit

**PASS.** Generation tests confirm unknown authored fields remain unknown.
Renderer tests confirm distinctive hidden values are absent from text, title,
description, IDs, attributes, metadata, and answer-dependent geometry.
Calculation tests confirm requested values do not appear in prompts, IDs,
provenance, scenario data, or SVG. Concept tokens and rubrics remain in the
canonical question only. API structural tests recursively reject expected
answers, marking schemes, rubrics, criteria, concepts, memo, solution, solver,
scenario, provenance, and worked-answer keys; both conceptual tokens and a
calculation answer are checked explicitly.

## Security audit

The existing `.github/workflows/ci.yml` quality and `dependency-audit` jobs
remain the security mechanism. Ruff, mypy, build, pip check, and CI checks pass.
SVG tests cover hostile-label escaping, executable-content strings,
`javascript:`, event-handler-like labels, and `foreignObject` absence; API tests
cover sanitized errors without tracebacks or private package details. No
secrets, remote SVG resources, or new dependencies were added by M4.

The local `pip-audit --local` command was also run after installing the
repository's documented audit tool. It reported 25 advisories in six packages
(`anyio`, `click`, `idna`, `pip`, `pytest`, and `starlette`) from the current
environment, plus the editable project itself is not published to PyPI. These
are dependency-baseline findings outside the Newton implementation and are
recorded for dependency maintenance; no M4 code introduced them. The #72 PR CI
dependency-audit result is authoritative and passed; the quality workflow also
passed.

## Regression audit

Post-#61 targeted results:

- Newton domain/solver/generation/rendering/questions/conceptual/application/API:
  388 passed.
- Vertical Projectile domain/solver/generation/questions/renderer: 161 passed.
- Momentum domain/solver/generation/questions/renderer: 351 passed.
- Core and curriculum tests are included in the full run.
- Full suite: 933 passed.

Projectile and Momentum API contracts, health, OpenAPI, learner projection,
determinism, and safe-error regressions remain green.

## Quality gate results

- Full `pytest`: **933 passed**.
- Overall coverage: **93%** (`pytest --cov=assessment_platform`).
- Application/API focused coverage: **97%** across 60 tests.
- Newton module coverage: domain package 100%; solver modules 84–98%; scenario
  generation 93%; renderer 93%; calculation questions 93%; conceptual
  questions 95%; application 97%; API v1 98%.
- Ruff: **pass**.
- mypy: **pass**.
- Wheel build: **pass**.
- `pip check`: **pass**.
- `git diff --check`: **pass**.
- Existing CI quality and dependency-audit workflows: **pass on #61 and #72**;
  #72 is the final verification of this branch.

## Partial and deferred capabilities

These are explicit bounds, not unreported failures:

- Newton III standalone derived numeric calculation: intentionally deferred;
  authored pair validation and conceptual assessment are supported.
- Universal-gravity vector direction: not derived; only scalar magnitude is
  supported because the authored domain does not contain line-of-centres
  geometry.
- Arbitrary 3D mechanics: unsupported; M4 is authored 1D/2D Cartesian or
  2D surface-coordinate mechanics.
- Rotational dynamics, torque, rigid bodies: unsupported.
- Fluid/drag forces and variable-mass systems: unsupported.
- Non-inertial-frame solving: unsupported; approved assumptions require an
  inertial frame.
- Arbitrary N-body systems: unsupported.
- Pulleys, pulley networks, slack strings, extensible strings, and arbitrary
  string networks: unsupported; only one straight taut inextensible light
  string joining two bodies is supported.
- Arbitrary contact/friction engines: unsupported beyond the authored normal,
  static, limiting-static, kinetic, and surface-aligned cases.
- Automatic or free-text learner marking: deferred.
- PDF/print generation and LMS adapters: deferred.
- Assessment forms beyond the one-question v1 route: deferred.
- M5 Work, Energy & Power and later mathematics work: not started.

## Blocking findings

No Newton correctness, routing, learner-safety, solvability, or regression
blocker was found. The dependency advisories reported by the local audit are
pre-existing environment/package-maintenance findings and are not caused by
M4; they should be resolved through dependency maintenance rather than by
expanding this verification issue.

## M4 readiness conclusion

The approved bounded M4 scope is evidence-backed across curriculum, domain,
solver, generation, rendering, calculation questions, conceptual questions,
and the existing application/API route. Partial and deferred capabilities are
explicit, and no blocking M4 implementation gap was found.

**M4 verification is complete and M4 is ready for completion pending merge of
the Issue #62 PR.**
