# Momentum & Impulse conceptual questions

Issue #41 adds `MomentumConceptualQuestionGenerator` for deterministic CAPS
conceptual templates. It authors canonical `Question` and `QuestionPart`
objects with structured concept-oriented `ExpectedAnswer` values and
declarative `MarkingScheme` criteria. It does not calculate physics, evaluate
learner text, call an LLM, alter the API, or produce printable output.

Supported templates cover momentum definitions and vector meaning, Newton's
second law in momentum form, system/environment and internal/external forces,
isolated systems, conservation of linear momentum, elastic/inelastic
terminology, the impulse-momentum theorem, and stopping-time safety
applications. Rubrics explicitly preserve the distinction between inelastic
and perfectly inelastic collisions and require the causal safety chain from
longer stopping time to lower average force.

IDs, template provenance, and optional seed handling are deterministic.
Conceptual questions use semantic short- or long-text response types. No
automatic marking is implemented; API integration remains deferred to #42.
