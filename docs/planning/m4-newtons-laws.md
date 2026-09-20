# M4 Newton's Laws planning

## Planning status

M4 is the next planned milestone after M3 Momentum & Impulse. This document
is planning-only; no Newton's Laws production implementation is included.
The repository roadmap identifies M4 as Newton's Laws, while the official DBE
CAPS Physical Sciences document places the core Newton's Laws content in the
Grade 11 sequence and refers to Grade 12 consolidation and integrated
problem-solving. Issue #44 must validate the exact Grade 12 applicability and
curriculum metadata before domain scope is frozen.

Authoritative basis: [DBE CAPS Physical Sciences Grades 10–12](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf), especially the Newton's Laws and application material and Grade 12 consolidation guidance. The project must retain the official grade distinction rather than silently relabel Grade 11 content as Grade 12.

## Proposed scope to validate

Subject to #44's evidence review, the milestone should cover Newton's Laws
and applications in the repository's one-dimensional mechanics boundary:

- Newton's first, second, and third laws and their application;
- net/resultant force, mass, acceleration, and signed/vector reasoning;
- weight/gravitational force, normal force, friction, applied force, and
  tension where the authoritative scope requires them;
- free-body/force diagrams and explicit system/environment assumptions;
- static versus kinetic friction if confirmed applicable;
- horizontal and inclined-plane cases only if confirmed by the authoritative
  CAPS mapping;
- deterministic numerical relationships and conceptual explanations.

Potential exclusions pending #44 include rotational dynamics, fluid forces,
non-inertial frames, arbitrary three-dimensional rigid-body mechanics,
unbounded contact/friction models, and university-level calculus. The engine
must state assumptions such as ideal strings, contact conditions, friction
model, and gravitational field rather than infer them.

## Architecture boundaries

Reuse the canonical `Assessment`, `Question`, `QuestionPart`, response,
answer, marking, seed, provenance, visual-reference, learner-projection,
curriculum-lookup, and API error infrastructure. Reuse SVG safety,
accessibility, and deterministic-ID conventions where semantics are shared.

Newton-specific domain concepts must remain separate from Momentum models;
shared mass, force, direction, and small SI value objects should be composed
only where their invariants genuinely match. The solver is authoritative for
all numerical results. Generation, renderers, question authors, and the API
must not duplicate Newton equations.

## Planned issue sequence

| Order | Issue | Responsibility | Dependencies | Initial status |
| --- | --- | --- | --- | --- |
| 1 | #44 | Validate CAPS Newton's Laws scope and curriculum metadata | M3 complete | ready |
| 2 | #45 | Define framework-independent Newton domain and force representations | #44 | backlog |
| 3 | #46 | Implement authoritative deterministic Newton solver and validation | #45 | backlog |
| 4 | #47 | Implement deterministic Newton scenario-generation policy/factory | #45, #46 | backlog |
| 5 | #48 | Implement safe deterministic force/free-body SVG renderer | #45, #46, #47 | backlog |
| 6 | #49 | Implement solver-backed calculation question generator | #45–#48 | backlog |
| 7 | #50 | Implement conceptual templates and machine-readable rubrics | #44, #49 | backlog |
| 8 | #51 | Integrate Newton generation into the existing application/API | #44, #47–#50 | backlog |
| 9 | #52 | Verify CAPS coverage, regressions, and M4 readiness | #44–#51 | backlog |

## Dependency graph

```text
#44 CAPS scope and metadata
          |
          v
#45 domain and force representations
          |
          v
#46 authoritative solver
          |
          v
#47 deterministic scenario generation
          |
          v
#48 force/free-body renderer
          |
          v
#49 calculation questions
          |
          v
#50 conceptual questions and rubrics
          |
          v
#51 application/API integration
          |
          v
#52 final CAPS coverage verification
```

## Responsibilities by layer

- Curriculum: authoritative topic identifier, grade applicability, concepts,
  assumptions, exclusions, and assessment metadata.
- Domain: immutable bodies, forces, interactions, coordinate/sign conventions,
  contact/friction assumptions, and validated invariants.
- Solver: net/resultant forces, acceleration, equilibrium, and supported force
  relationships; no question wording or rendering.
- Generation: bounded masses, force magnitudes, angles/coefficients only after
  #44 scope approval; local seeded randomness and stable provenance.
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
check; underdetermined systems must be rejected.

## Planned conceptual families

Evaluate definitions and applications of Newton's first/second/third laws,
net/resultant force, system/environment, action-reaction pairs, mass versus
weight, friction distinctions, free-body-diagram reasoning, and assumptions.
Rubrics must be concept-based, deterministic, and separate from automatic
marking.

## Risks and deferred items

The main risk is curriculum-grade ambiguity: Newton's Laws are core Grade 11
content in the official document, while M4 is a repository roadmap milestone
with Grade 12 consolidation relevance. #44 is intentionally first and ready
to resolve this. Other risks are force-diagram semantics, friction/contact
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
