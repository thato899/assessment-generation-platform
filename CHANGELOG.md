# Changelog

## Unreleased

- Add Issue #60 deterministic Grade 11 Newton conceptual templates with
  machine-readable concept tokens, reconciled declarative rubrics, stable IDs,
  provenance, response specifications, and optional #58 visuals. Keep numeric
  physics, automatic marking, API routing, and printable output outside this
  boundary.


- Add Issue #58 deterministic, learner-safe Newton force and free-body SVG
  rendering with authored ownership, Cartesian/surface direction mapping,
  stable accessible IDs, escaping, fixed hidden-value geometry, and no physics
  calculations. Issue #59 is complete; conceptual questions are active in #60.

- Add Issue #59 solver-backed Newton calculation question generation with
  canonical assessment parts, structured numeric answers, reconciled marking
  schemes, deterministic IDs/provenance, explicit givens, and optional safe
  SVG visuals. API routing, automatic marking and printing remain deferred to #61-#62.

- Add Issue #57 deterministic Newton scenario generation with versioned typed
  policy/input/output models, local seed isolation, stable provenance and
  solver-backed validation for the approved bounded families. Authored unknowns
  remain intact; rendering, questions, marking and API routing remain deferred.

- Add the Issue #56 deterministic Newton solver with immutable typed results
  for resultants, Newton II dynamics, equilibrium, one-unknown force solving,
  authored-field weight, contact/normal/friction, straight light strings,
  third-law validation and universal-gravity magnitude. Explicitly reject
  underdetermined, inconsistent, unsupported and numerical-range outcomes;
  generation, rendering, questions, marking and API routing remain deferred.

- Add immutable, framework-independent Newton domain inputs with explicit
  units, 1D/2D coordinates, force ownership, contact/friction, light-string,
  third-law and gravity relationships. Preserve underdetermined states without
  inferring physics; Newton API routing remains unavailable.
- Add evidence-backed CAPS Newton's Laws curriculum metadata and a Grade 11
  versus Grade 12 scope contract; no Newton production or API implementation
  is included.
- Add deterministic, framework-independent Momentum & Impulse relationships
  for signed momentum change, impulse, average force, and contact time.
- Add the versioned Issue #38 Momentum & Impulse problem-generation companion
  with bounded difficulty pools, typed relationship/collision outputs,
  deterministic provenance, both positive-axis conventions, and solver-backed
  constrained final-state validation. The Issue #32 scenario factory remains
  backward compatible.
- Add deterministic constrained two-body Momentum collision solving for known
  final velocity, common final velocity, and complete authored final states,
  including typed validation results and isolated-state classification.
- Add framework-independent Momentum interaction constraint models for
  authored final-state information without collision calculations.
- Add ADR 0011 documenting the separation of authored Momentum interaction
  constraints from solver-derived results.
- Added a deterministic Momentum & Impulse scenario factory with versioned platform policy, supported initial-condition families, explicit axis selection, stable provenance, and seed replay. It does not generate solver outputs or final collision states.
- Added the deterministic Momentum & Impulse solver boundary for signed body momentum, aggregate system totals, external impulse effects, validation, and explicit underdetermined-collision handling. No Momentum API or question generation is included.
- Added the first framework-independent Momentum & Impulse domain models: explicit masses, signed velocities, axis conventions, body identities, system boundaries, and distinct momentum/impulse values. No solver or API support is included yet.
- Add evidence-based M3 CAPS coverage verification and explicit limitation documentation.
- Complete M3 Momentum & Impulse verification and add planning for the next
  M4 Newton's Laws milestone.
- Bootstrapped the Python/FastAPI repository, API v1 shell, validation, tests, governance documentation, and CI/security configuration.
- Added framework-independent core assessment value objects and models with validation tests.
- Added CAPS Grade 12 Physical Sciences Mechanics curriculum metadata and deterministic lookup tests.
- Added an immutable vertical projectile scenario model with explicit SI units, sign conventions, assumptions, and validation tests.
- Added deterministic vertical projectile position/velocity calculations, event detection, root selection, and solution validation.
- Added canonical question-part response specifications, expected answers, marking schemes, learner responses, marking results, and ID-derived memorandum entries.
- Added a safe deterministic SVG renderer for one-dimensional vertical projectile diagrams.
- Defined the versioned v1 assessment-generation API contract with explicit boundary DTOs, deterministic seed semantics, safe validation errors, and learner-safe response projections.
- Added deterministic CAPS vertical-projectile question generation with solver-derived canonical question parts, structured answers, marking schemes, optional SVG references, and provenance metadata.
- Added a deterministic, policy-driven vertical-projectile scenario factory with typed generation inputs, four supported scenario families, seed replay, and provenance metadata.
- Added the first application/API generation path for one deterministic CAPS Grade 12 Physical Sciences vertical-projectile question with solver validation, canonical assessment composition, learner-safe projection, stable unsupported-configuration errors, and visual controls.
- Add Issue #57 deterministic Newton scenario generation with versioned typed
  policy/input/output models, local seed isolation, stable provenance and
  solver-backed validation for the approved bounded families. Authored unknowns
  remain intact; rendering, questions, marking and API routing remain deferred.

- Add deterministic, learner-safe Momentum & Impulse SVG rendering with
  explicit final-value visibility controls.
- Add solver-backed canonical Momentum & Impulse calculation question
  generation with structured answers, marking schemes, and optional visuals.
- Add deterministic CAPS-aligned conceptual Momentum & Impulse templates and
  machine-readable rubrics.
- Add Momentum & Impulse routing to the existing learner-safe v1 assessment
  generation service and API.
