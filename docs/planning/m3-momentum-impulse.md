# M3 Momentum & Impulse plan

## Planning status

The M3 foundation is complete:

- Issue #28 defines the framework-independent one-dimensional initial-state
  domain.
- Issue #30 provides the authoritative aggregate Momentum & Impulse solver.
- Issue #32 provides deterministic bounded initial-condition generation.

Issues #35 through #40 are complete. Issue #41 is the active implementation
issue; Issues #42-#43 remain `status:backlog` until their
dependencies are complete.
No downstream production implementation is selected by this plan.

The authoritative curriculum reference is the repository's DBE CAPS Physical
Sciences representation. Numeric generation pools remain platform policy and
are not presented as CAPS requirements.

## Architectural decision

M3 will extend the existing layered boundary in dependency order. A question
generator must never repair an underdetermined physical problem. The domain
must represent enough independent interaction/final-state information before
the solver may derive a missing final quantity. The solver remains the sole
source of numerical answers; generation, rendering, question authoring,
application orchestration, and API projection consume validated results.

The current solver's aggregate final momentum is sufficient for aggregate
questions, but not for an arbitrary individual final velocity, kinetic-energy
comparison, or collision classification. Those outcomes require explicit
interaction constraints and a constrained solver path.

## Planned issue sequence

| Order | Issue | Responsibility | Dependencies | Status |
| --- | --- | --- | --- | --- |
| 1 | #35 | Solvable one-dimensional interaction/final-state domain model | #28, #30, #32 | complete |
| 2 | #36 | Constrained one-dimensional collision solver and validation | #35 | complete |
| 3 | #37 | Impulse, force, contact-time, and momentum-change solver | #35, #36 | complete |
| 4 | #38 | Extended deterministic generation policy for solvable interactions | #35, #36, #37 | complete |
| 5 | #39 | Deterministic Momentum & Impulse technical SVG renderer | #35, #36, #37, #38 | complete |
| 6 | #40 | Deterministic calculation question generator | #35, #36, #37, #38, #39 | complete |
| 7 | #41 | CAPS conceptual question templates and rubrics | #2, #16, #40 | in-progress |
| 8 | #42 | Application service and existing v1 API integration | #2, #6, #16, #38, #39, #40, #41 | backlog |
| 9 | #43 | CAPS coverage matrix and M3 exit verification | #2, #35, #36, #37, #38, #39, #40, #41, #42 | backlog |

The renderer is intentionally placed before generated questions so visual
question support can be decided from a safe, data-derived adapter. If a later
review proves visuals are optional for a particular question family, the
question generator may consume no visual for that family without moving
physics or rendering logic into the generator.

## Dependency graph

```text
M3 Foundations [DONE]
  #28 domain model
  #30 aggregate solver
  #32 initial scenario factory
          |
          v
  #35 interaction/final-state constraints
          |
          v
  #36 constrained collision solver + validation
          |
          v
  #37 impulse/force/time solver [DONE]
          |
          v
  #38 extended deterministic problem policy
          |
          v
  #39 technical Momentum SVG renderer
          |
          v
  +-------+----------------+
  |                        |
  v                        v
#40 calculation       #41 conceptual templates
    questions             and rubrics
  +-----------+------------+
              v
       #42 application/API
              |
              v
       #43 CAPS exit verification
```

## CAPS coverage target

The target is to map each concept to a domain capability, authoritative
solver result, generation family, canonical question/rubric, automated test,
and API behavior where applicable. A concept not implemented at M3 exit must
be explicitly deferred with its reason and destination.

| CAPS area | Planned support |
| --- | --- |
| Momentum | Definition, `p = mv`, signed/vector reasoning, initial/final/change in momentum through #35-#40 and #41 where conceptual. |
| Newton II in momentum form | Net/resultant force as rate of momentum change, speeding up, slowing down, and reversal through #37 and supported question templates in #40/#41. |
| Systems and conservation | System/environment, internal/external forces, isolated systems, total linear momentum, two-object 1D interactions, and explicit sign convention through #35-#40. |
| Elastic/inelastic | Complete-state kinetic-energy comparison and explicit perfectly inelastic/common-final-velocity semantics through #36; insufficient states remain unclassified. |
| Impulse | Force × contact time, vector impulse, impulse-momentum theorem, force/time/change-in-momentum calculations through #37, #38, and #40. |
| Safety | Deterministic conceptual templates and explicit rubric criteria for stopping/contact time versus average force through #37, #40, and #41. |

## Domain capability matrix

| Capability | Current foundation | Planned issue |
| --- | --- | --- |
| Initial bodies, signed velocity, axis, system boundary | `MomentumScenario` | Done: #28 |
| Body/aggregate initial momentum and aggregate impulse | `MomentumImpulseSolver` | Done: #30 |
| Deterministic initial-condition policy | `MomentumScenarioFactory` | Done: #32 |
| Known final velocity constraint | Not represented | #35 |
| Common final velocity/sticking constraint | Not represented | #35 |
| Complete supplied final state | Not represented | #35 |
| Constrained final-state solving and validation | Not available | #36 |
| Elastic/inelastic comparison from complete state | Not available | #36 |
| Momentum change, force, and contact time | `MomentumImpulseRelationshipSolver` | Done: #37 |
| Solvable interaction generation | `MomentumProblemFactory` | In progress: #38 |
| Technical Momentum visual | Not available | #39 |
| Canonical numerical questions | Not available | #40 |
| Canonical conceptual questions/rubrics | Not available | #41 |
| Application/API capability | Not available | #42 |
| Coverage evidence and exit decision | Not available | #43 |

## Question-family plan

Question templates may be added only when an authoritative solver result
exists for the expected answer.

| Family | Required authoritative result | Planned issue | Safety boundary |
| --- | --- | --- | --- |
| Body momentum | `BodyMomentumResult` | #40 | Use signed value and explicit axis. |
| Total system momentum | `initial_total_momentum` or validated aggregate result | #40 | Do not add magnitudes. |
| Change in momentum | #37 momentum-change result | #40 | Preserve vector sign, including reversal. |
| Impulse | `Impulse` or #37 derived impulse | #40 | Keep impulse semantically distinct from momentum. |
| Average resultant force | #37 force result | #40 | Require valid contact time. |
| Contact time | #37 time result | #40 | Require valid non-zero force. |
| Missing final velocity | #36 constrained final-state result | #40 | Never select for two unknown final velocities. |
| Common final velocity | #36 explicit perfectly inelastic result | #40 | Only for an explicit sticking constraint. |
| Collision classification | #36 complete-state energy comparison | #40 | Do not classify incomplete states. |
| CAPS conceptual reasoning | Canonical rubric criteria, with solver data where needed | #41 | No LLM-authoritative marking. |

Every generated part must use stable IDs, a response specification,
machine-readable expected answers, and an exact marking scheme. Learner
projections must omit teacher-side answers and answer-revealing visual data.

## Platform generation policy

CAPS supplies the curriculum concepts and applicability boundary. The
platform must decide and document bounded pools for masses, speeds, forces,
times, impulses, interaction categories, difficulty, and template selection.
Those pools are not CAPS numeric requirements. Policy versions, seeds,
selected families, axes, and provenance must remain explicit and replayable.

The existing Issue #32 policy remains compatible. Issue #38 may extend it only
for interaction families that #35-#37 can validate and solve. The factory
must not precompute expected answers or hide missing constraints.

## Deferred and out of scope for M3

- Two-dimensional, relativistic, rotational, variable-mass, or arbitrary
  N-body collision mechanics.
- LLM-authoritative physics or marking.
- LMS integrations, PDF/print engines, and unrelated subject engines.
- Automatic learner marking; M3 produces expected answers and marking schemes
  only.
- A Momentum-specific public API; integration uses the existing versioned
  assessment endpoint.

## M3 definition of done

M3 is complete only when:

1. authoritative CAPS concepts are mapped to real capabilities;
2. deterministic one-dimensional domain scenarios and policies exist;
3. solver-authoritative answers cover every generated question;
4. underdetermined collision results are never fabricated;
5. both positive-axis conventions and signed vector changes are correct;
6. momentum and impulse remain distinct semantic types;
7. required constrained collision behavior is represented and validated;
8. impulse/force/contact-time relationships are represented and solved;
9. safe deterministic visuals are available where required;
10. canonical questions have response specifications;
11. expected answers and marking schemes are machine-readable;
12. learner-safe projections exclude teacher-side data;
13. supported API generation is deterministic and accurately documented;
14. projectile generation remains backward compatible;
15. comprehensive domain, solver, factory, renderer, question, API, and
    regression tests pass; and
16. the CAPS coverage matrix and documentation reflect actual support and
    explicit deferrals.
