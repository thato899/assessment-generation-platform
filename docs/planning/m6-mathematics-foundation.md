# M6 Mathematics Foundation planning

## Planning status

M6 starts after the completed M5 Work, Energy & Power milestone. This document
is the planning and scope contract only. It introduces no Mathematics runtime
package, solver, generator, question templates, API route, or curriculum
implementation.

The M6 GitHub milestone `M6 - Mathematics Foundation` exists and currently has
no issues. This plan is intended to be reviewed before implementation issues
are created or assigned. Dependabot maintenance remains separate from M6
feature scope.

## Purpose and boundary

M6 establishes the smallest framework-independent mathematical foundation that
future Mathematics subject engines can depend on. The foundation must make
number domains, exactness, evaluation, validation, determinism, and failure
semantics explicit before M7 Functions introduces function-specific models or
generation.

M6 is not a complete school Mathematics engine. It is a reusable semantic
boundary for bounded mathematical relationships and their authoritative
evaluation.

## Approved planning scope

The planned foundation will define, subject to CAPS and repository review:

- typed scalar number/value semantics, including the supported numeric domains,
  units-free assumptions, exact versus approximate results, and conversion
  rules;
- immutable mathematical expressions or relationships with explicit operands,
  operators, precedence, and supported domain constraints;
- deterministic evaluation and validation with typed outcomes for valid,
  undefined, underdetermined, inconsistent, unsupported, and out-of-range
  cases;
- bounded input policies and seed semantics for future deterministic scenario
  generation, without embedding curriculum content in the evaluator; and
- testable interfaces that later Mathematics topics can consume without
  depending on FastAPI, Pydantic, rendering, or assessment orchestration.

The first implementation slice must be deliberately small. It should prove
the value and failure contracts with representative arithmetic and algebraic
relationships before any broad symbolic manipulation is considered.

## Architectural boundaries

```text
CAPS Mathematics scope and metadata
                |
                v
framework-independent mathematical values/expressions
                |
                v
authoritative deterministic evaluator and validation
                |
                v
future bounded scenario generation
                |
                v
future topic engines (M7 Functions and later)
                |
                v
existing assessment/application/API layers, only when separately approved
```

The mathematical foundation owns meaning, invariants, evaluation, and typed
failures. Curriculum metadata owns grade/topic placement and CAPS traceability.
Generation owns bounded authored inputs and reproducibility. The application
and API may orchestrate a future approved topic, but must not calculate
mathematical results. Renderers, question generators, marking, printable output,
and LMS adapters remain downstream concerns.

No M6 module may import FastAPI, Pydantic, an API adapter, a renderer, or a
subject-specific Physics engine. Existing Physics value objects and solvers
remain unchanged; apparent similarities do not justify a cross-subject numeric
abstraction without a separate reviewed ADR.

## Proposed issue sequence

| Order | Responsibility | Exit evidence |
| --- | --- | --- |
| A | Validate CAPS Mathematics placement and the M6/M7 boundary | scope contract and source traceability |
| B | Define immutable numeric/value semantics and exactness policy | domain contract and focused tests |
| C | Define bounded expression/relationship representations | representation contract and invalid-state tests |
| D | Implement the authoritative deterministic evaluator | typed results/failures and arithmetic/algebra tests |
| E | Define deterministic input-generation policy seams | seed/replay contract, without a topic generator |
| F | Verify architecture, regressions, security, and M6 readiness | coverage matrix and quality-gate evidence |

The sequence is intentionally planning-first. No issue should add functions,
graphs, broad symbolic algebra, assessment questions, or API routing until the
foundation contract and its non-goals have been reviewed.

## Dependency graph

```text
A CAPS scope and M6/M7 boundary
              |
              v
B value and exactness semantics
              |
              v
C expression/relationship representations
              |
              v
D authoritative evaluator
              |
              v
E deterministic input-policy seams
              |
              v
F final verification and readiness decision
```

Generation, question, rendering, and API work are intentionally absent from
the M6 graph. They may be proposed only after a separate scope decision.

## Initial mathematical contract questions

The scope issue must resolve these questions before implementation:

- Which number domains are required first: integers, rational values, bounded
  real approximations, or a smaller subset?
- Which operations are authoritative initially, and how are division by zero,
  invalid roots, overflow, and non-finite values represented?
- Are fractions preserved exactly, and where is decimal approximation allowed?
- Does an unknown represent an authored missing value, a symbolic variable, or
  both? These meanings must not be conflated.
- Which relationships are solvable in M6, and which are explicitly deferred to
  M7 or later symbolic capabilities?
- What precision, rounding, comparison tolerance, and serialization rules are
  stable enough for assessment use?
- Which deterministic seed and provenance contracts can be reused from the
  core without making the mathematical domain assessment-aware?

## Explicit non-goals

M6 does not include:

- functions, function graphs, transformations, or calculus;
- a general-purpose computer algebra system or unrestricted symbolic solving;
- matrices, vectors, statistics, probability, geometry, trigonometry, or
  financial mathematics unless later scope evidence explicitly adds them;
- question generation, conceptual rubrics, automatic/free-text marking, PDF,
  or learner-submission workflows;
- a new API version or route;
- changes to the existing Physical Sciences engines; or
- LLM-generated or approximate answers without an authoritative typed result.

## M6 definition of done

M6 planning is complete only when:

- the CAPS-backed Mathematics scope and M6/M7 boundary are documented;
- numeric domains, exactness, unknowns, precision, and failure semantics are
  explicit;
- the proposed immutable representation and evaluator boundaries are reviewed;
- the dependency sequence and deferred capabilities are recorded;
- the foundation remains framework-independent and deterministic; and
- a final verification matrix records tests, regressions, security checks, and
  remaining limitations.

The planning PR must remain unmerged pending review. It must contain no
Mathematics runtime implementation.
