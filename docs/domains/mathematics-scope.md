# Mathematics foundation scope contract

## Status

This document records the planning boundary for M6 Mathematics Foundation. It
is not a curriculum implementation and does not introduce Mathematics runtime
code, metadata, an API route, or assessment generation.

## CAPS basis and traceability

The primary authority is the South African Department of Basic Education,
[Mathematics Grades 10-12 CAPS](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20_%20MATHEMATICS%20_%20GR%2010-12%20_%20Web_1133.pdf).
The relevant evidence is:

| CAPS location | Planning implication |
| --- | --- |
| Section 3, pp. 12-13 (PDF pp. 16-17), overview of topics | Algebra/equations, patterns, functions and graphs, finance, calculus, probability, geometry, trigonometry, and statistics are distinct curriculum areas. M6 must not collapse them into one subject engine. |
| Section 3.1.1, p. 12 (PDF p. 16), Functions overview | Function work progresses across Grades 10-12 from relationships and multiple representations to formal functions, including polynomial, exponential, logarithmic, and rational functions. This supports M7 as the first topic engine, not as part of M6. |
| Grade 10, Term 2, p. 24 (PDF p. 28), Functions | Tables, graphs, words, formulae, domain, range, and prescribed basic graphs are curriculum concepts for the future Functions engine. They are outside the M6 evaluator contract. |
| Grade 11, Term 2, p. 32 (PDF p. 36), Functions | Parameter changes and average rate of change are topic-level function work and remain M7 concerns. |
| Grade 12, Term 1, p. 40 (PDF p. 44), Functions | Formal function definitions and inverses are explicitly Grade 12 function content and remain M7 concerns. |

The CAPS weighting table also treats Functions and Graphs, Algebra and
Equations, Patterns and Sequences, and other areas as separate content areas.
M6 therefore provides reusable mathematical semantics only; it does not claim
coverage of any one CAPS topic.

## M6 boundary

M6 may define a small, framework-independent foundation for:

- typed unit-free scalar values and supported number domains;
- exact versus approximate results and stable comparison/serialization rules;
- immutable arithmetic expressions or bounded relationships with explicit
  operands and operators; and
- deterministic evaluation and typed validation outcomes for supported,
  undefined, underdetermined, inconsistent, unsupported, and out-of-range
  inputs.

The first implementation slice must remain deliberately small enough to prove
these contracts with representative arithmetic and bounded relationships. It
must not become a general-purpose symbolic algebra system.

## M6/M7 boundary

M7 owns the first Mathematics topic engine: Functions. In particular, M7 must
own function-domain concepts, graph/representation models, transformations,
inverses, and function-specific curriculum metadata and generation. M6 may
provide scalar and expression primitives that M7 consumes, but M6 must not
encode function graphs, curriculum examples, function families, or function
question templates.

The following are explicitly deferred beyond M6 unless a later reviewed scope
decision changes the boundary:

- functions, graphs, transformations, and inverses;
- calculus, limits, and rates of change as a topic engine;
- geometry, trigonometry, vectors, matrices, statistics, probability, and
  financial mathematics;
- unrestricted symbolic solving or computer-algebra behavior; and
- assessment questions, marking, rendering, PDF output, and API routing.

## Architectural constraints

M6 modules must remain independent of FastAPI, Pydantic, rendering,
assessment orchestration, and Physical Sciences engines. Curriculum placement
belongs to future Mathematics metadata; the foundation owns mathematical
meaning, invariants, deterministic evaluation, and typed failures only.

This contract is the Phase A exit evidence for the M6 plan. Before runtime
implementation begins, the remaining M6 contract questions in
[`docs/planning/m6-mathematics-foundation.md`](../planning/m6-mathematics-foundation.md)
must be resolved and reviewed.
