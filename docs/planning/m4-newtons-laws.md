# M4 Newton's Laws planning

## Planning status

M4 is the current milestone after completed M3 Momentum & Impulse. Issue #54
is merged and closed; Issue #55 authored domain implementation is merged and closed at `2f6adeb`.
Issue #56 deterministic solver is implemented and in review. Issues #57-#62 remain backlog. Generation and downstream pipeline work remains deferred.
The repository roadmap identifies M4 as Newton's Laws, while the official DBE
CAPS Physical Sciences document places the core Newton's Laws content in the
Grade 11 sequence and refers to Grade 12 consolidation and integrated
problem-solving. Issue #54 validated the exact Grade 12 applicability and
curriculum metadata before domain implementation. The resulting scope
contract is recorded in
`docs/domains/physical-sciences/newtons-laws-scope.md`.

Authoritative basis: [DBE CAPS Physical Sciences Grades 10–12](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf), especially the Newton's Laws and application material and Grade 12 consolidation guidance. The project must retain the official grade distinction rather than silently relabel Grade 11 content as Grade 12.

## Approved scope

Issue #54 establishes a Grade 11-owned Newton's Laws topic with Grade 12
consolidation, integrated-problem-solving, and selected-examinability
relevance. The bounded supported scope, relationships, exclusions, and later
layer requirements are recorded in the dedicated scope contract.

## Architecture boundaries

Reuse the canonical `Assessment`, `Question`, `QuestionPart`, response,
answer, marking, seed, provenance, visual-reference, learner-projection,
curriculum-lookup, and API error infrastructure. Reuse SVG safety,
accessibility, and deterministic-ID conventions where semantics are shared.

Newton-specific domain concepts must remain separate from Momentum models;
shared mass, force, direction, and small SI value objects should be composed
only where their invariants genuinely match. The solver is authoritative for
all numerical results. Issue #56 now provides immutable typed results, explicit
underdetermination/inconsistency failures, deterministic tolerance handling,
and the bounded contact, string, third-law and gravity calculations in scope.
Generation, renderers, question authors, and the API
must not duplicate Newton equations.

## Planned issue sequence

| Order | Issue | Responsibility | Dependencies | Current status |
| --- | --- | --- | --- | --- |
| 1 | #54 | Validate CAPS Newton's Laws scope and curriculum metadata | M3 complete | complete |
| 2 | #55 | Define framework-independent Newton domain and force representations | #54 | complete |
| 3 | #56 | Implement authoritative deterministic Newton solver and validation | #55 | in review |
| 4 | #57 | Implement deterministic Newton scenario-generation policy/factory | #55, #56 | backlog |
| 5 | #58 | Implement safe deterministic force/free-body SVG renderer | #55, #56, #57 | backlog |
| 6 | #59 | Implement solver-backed calculation question generator | #55–#58 | backlog |
| 7 | #60 | Implement conceptual templates and machine-readable rubrics | #54, #59 | backlog |
| 8 | #61 | Integrate Newton generation into the existing application/API | #54, #57–#60 | backlog |
| 9 | #62 | Verify CAPS coverage, regressions, and M4 readiness | #54–#61 | backlog |

## Dependency graph

```text
#54 CAPS scope and metadata
          |
          v
#55 domain and force representations
          |
          v
#56 authoritative solver
          |
          v
#57 deterministic scenario generation
          |
          v
#58 force/free-body renderer
          |
          v
#59 calculation questions
          |
          v
#60 conceptual questions and rubrics
          |
          v
#61 application/API integration
          |
          v
#62 final CAPS coverage verification
```

## Responsibilities by layer

- Curriculum: authoritative topic identifier, grade applicability, concepts,
  assumptions, exclusions, and assessment metadata.
- Domain: immutable bodies, forces, interactions, coordinate/sign conventions,
  contact/friction assumptions, and validated invariants.
- Solver: net/resultant forces, acceleration, equilibrium, and supported force
  relationships; no question wording or rendering.
- Generation: bounded masses, force magnitudes, angles/coefficients only after
  #54 scope approval; local seeded randomness and stable provenance.
- Renderer: force arrows, body/system boundaries, labels, free-body diagrams,
  safe escaping, deterministic IDs, and no answer leakage.
- Questions: calculation templates, conceptual templates, structured answers,
  declarative rubrics, and explicit applicability.
- API: orchestration and learner-safe projection only; no equations.

## Planned calculation families

After scope validation, evaluate body net force and acceleration, equilibrium
and resultant-force cases, weight/normal/friction/tension relationships,
Newton II applications, and supported force-diagram interpretations. Every
family requires an authoritative solver result and a structural applicability
check; the solver must decline underdetermined requests for results. The #55
domain permits structurally valid underdetermined scenarios.

## Planned conceptual families

Evaluate definitions and applications of Newton's first/second/third laws,
net/resultant force, system/environment, action-reaction pairs, mass versus
weight, friction distinctions, free-body-diagram reasoning, and assumptions.
Rubrics must be concept-based, deterministic, and separate from automatic
marking.

## Risks and deferred items

The main risk is curriculum-grade ambiguity: Newton's Laws are core Grade 11
content in the official document, while M4 is a repository roadmap milestone
with Grade 12 consolidation relevance. #54 resolved this before #55 began.
Remaining risks are force-diagram semantics, friction/contact
assumptions, and avoiding accidental coupling to Momentum.

M3 partial findings remain documented in
`docs/verification/m3-momentum-impulse-caps-coverage.md`. They are not being
implemented in this planning execution. A standalone final-total-momentum
template and impulse-vector conceptual template remain optional M3.x/future
enhancements unless later generic assessment work makes them necessary.

## M4 definition of done

M4 is complete only when the approved CAPS scope is mapped to implementation,
deterministic domain and solver behavior, validated generation, safe technical
visuals where needed, canonical calculation and conceptual questions,
learner-safe API integration, regression tests, and a final evidence matrix.
The milestone must preserve all M3 and projectile behavior and explicitly
document unsupported physics, assumptions, and future enhancements.
