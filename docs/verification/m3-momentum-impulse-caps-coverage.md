# M3 Momentum & Impulse CAPS coverage verification

## Scope and basis

This verification covers the Grade 12 CAPS topic represented by the
repository's `momentum-and-impulse` curriculum topic. The topic metadata in
`src/assessment_platform/curriculum/caps/physical_sciences.py` names
momentum, Newton's second law in momentum form, conservation of momentum,
elastic/inelastic collisions, and impulse. The matrix distinguishes evidence
from concepts that are only partially represented or deferred.

## Evidence matrix

| CAPS concept | Domain / solver | Generator / rubric | Renderer / API | Tests | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Momentum as `p = mv` | `Momentum`, `MomentumBody`, `MomentumImpulseSolver` | Body-momentum calculation; definition | API reachable | `test_momentum_impulse_solver.py`, question/conceptual tests | COVERED | Solver supplies the answer. |
| Momentum is a vector | Signed velocity, `PositiveAxis`, `PhysicalDirection` | Vector-concept rubric | Axis-aware SVG/API path | `test_momentum_impulse.py`, conceptual tests | COVERED | Direction and sign remain distinct. |
| Initial and total momentum | Aggregate solver | Body and system calculation templates | API calculation path | solver, generation, question tests | COVERED | Total is signed. |
| Final momentum | Aggregate solution | No standalone final-total question | Internal solver only | `test_momentum_impulse_solver.py` | PARTIALLY COVERED | Available as solver state, not independently exposed as a #40 template. |
| Change in momentum: speeding up, slowing, stopping, reversal | Relationship solver | Momentum-change template | API path | relationship and generation corpus tests | COVERED | Signed `final - initial` is authoritative. |
| Newton II in momentum form | Relationship solver | Newton II conceptual rubric; force calculation | API reachable | relationship/conceptual tests | COVERED | Uses rate of change of momentum, not only `F = ma`. |
| System and environment | `SystemBoundary` | System/environment rubric | API prompt path | domain/conceptual tests | COVERED | Conceptual distinction is rubric-backed. |
| Internal and external forces | System boundary semantics | Internal/external rubric | No dedicated visual required | conceptual rubric test | COVERED | No numeric inference is made. |
| Isolated system | `SystemBoundary(isolated=True)` | Isolated-system rubric | API reachable | domain/conceptual tests | COVERED | External impulse is rejected for isolated systems. |
| Conservation of total linear momentum | Aggregate/constrained solvers | Conservation rubric; total-momentum calculation | API reachable | solver/conceptual tests | COVERED | Isolated-system condition is explicit. |
| One-dimensional two-body collisions | `MomentumInteraction`, constrained solver | Collision templates | Before/after SVG and API | interaction/solver/generation tests | COVERED | More than two bodies are rejected for constrained solving. |
| Elastic collision | Complete-state validation/classification | Classification calculation; collision rubric | API reachable for complete-state path | constrained solver/conceptual tests | PARTIALLY COVERED | Requires complete validated isolated final state; no general two-unknown solver is claimed. |
| Inelastic collision | Constrained classification | Elastic/inelastic rubric | API reachable | solver/conceptual tests | COVERED | Not equated with sticking. |
| Perfectly inelastic / sticking | `CommonFinalVelocityConstraint` | Common-final-velocity calculation; terminology rubric | Sticking SVG/API path | sticking solver/generation/question tests | COVERED | Only explicit sticking constraints represent it. |
| Impulse | `Impulse`, relationship solver | Impulse calculation; theorem rubric | API reachable | relationship/question tests | COVERED | Impulse remains distinct from `MomentumChange`. |
| Impulse vector nature | Signed `Impulse`, axis propagation | No dedicated impulse-vector template | Axis-aware internal behavior | signed relationship tests | PARTIALLY COVERED | Signed behavior exists; dedicated conceptual template is deferred. |
| `J = F Δt` | Force-time relationship solver | Impulse-from-force-time template | API reachable | force-time tests | COVERED | Generator delegates the calculation. |
| Force calculation | Relationship solver | Average/resultant-force template | API reachable | relationship/question tests | COVERED | Signed force and positive time are preserved. |
| Contact-time calculation | Relationship solver | Contact-time template | API reachable | relationship/question tests | COVERED | Invalid sign and zero cases are rejected. |
| Safety applications | Domain-independent concept | Airbag stopping-time rubric | API prompt reachable | safety and API tests | COVERED | Rubric requires same impulse/change, longer time, lower force, and reduced injury. |

## Audits and evidence

The path is `AssessmentGenerationRequest` → `AssessmentGenerationService` →
`MomentumProblemFactory` → existing solver/question generator → canonical
`Question`/`Assessment` → learner DTO. Application/API code contains no
Momentum equations. Explicit and omitted seed tests establish deterministic
behavior; the factory's local RNG and stable provenance are covered by #38.

The learner projection omits `ExpectedAnswer`, `MarkingScheme`, memo data,
rubric criteria, solver objects, and answer-bearing provenance. Renderer tests
cover deterministic IDs, escaping, accessibility metadata, axis direction,
hidden derived values, and SVG safety.

An interaction-less two-body scenario remains underdetermined and is rejected
by `ConstrainedMomentumSolver`; the missing-final-velocity template applies
only to the typed known-final-velocity generated problem. No general
two-unknown final-state question is generated.

## Regression evidence

- Full suite: 588 passed.
- Momentum-focused regression suite: 327 passed.
- Code coverage: 91% (`pytest --cov=assessment_platform`).
- Ruff, mypy, build, and `pip check`: pass.

## Known limitations and deferrals

The verified scope does not include two-dimensional or relativistic momentum,
arbitrary N-body constrained collision solving, general two-unknown elastic
collision solving, time-varying force functions, automatic free-text marking,
printable assessment output, LMS adapters, or a dedicated impulse-vector
conceptual template. These are not counted as covered capabilities.

## M3 readiness

Issues #28, #30, #32, #35, #36, #37, #38, #39, #40, #41, and #42 are complete.
The implemented M3 scope is evidence-backed across domain models,
authoritative solvers, generation, rendering, canonical questions, and the
learner-safe API. Partial areas and explicit deferrals are recorded above;
this document does not claim universal CAPS coverage.
