# Newton's Laws conceptual questions

Issue #60 adds the deterministic, framework-independent conceptual question
boundary for the CAPS Grade 11 Physical Sciences `newtons-laws` topic. The
implementation is `NewtonConceptualQuestionGenerator` in
`mechanics.newton_conceptual_questions`.

## Responsibility and boundaries

The generator creates canonical `Question` objects with stable identifiers,
versioned `GenerationProvenance`, a response specification, an immutable
`ExpectedAnswer`, and a reconciled declarative `MarkingScheme`. It describes
what a scientifically correct response must contain; it does not parse learner
text or award marks. Numeric values, equations, force solving, solver calls,
API routing, PDF output, and unsupported curriculum content remain outside
this boundary.

The canonical answer is a tuple of machine-readable concept tokens. Token
order is deterministic and tokens express meaning rather than an exact phrase,
so later learner-safe or marking layers can choose their own response handling.
Each criterion has an explicit identifier, description, and mark value, and the
sum of criterion marks equals the part mark total.

## Template families

The version-1 inventory covers:

- Newton's First, Second, and Third Laws;
- action-reaction pairing and zero-resultant motion;
- equilibrium and non-equilibrium;
- mass versus weight and weight versus apparent weight;
- normal force, static versus kinetic friction, and the limiting static value;
- system versus environment and internal versus external forces;
- free-body diagrams and force/system diagrams;
- force-type identification and light, taut, inextensible strings;
- universal gravitation and apparent weightlessness; and
- explicit modelling assumptions (inertial frame, constant mass, and neglected
  air resistance).

Newton I requires rest or constant velocity, a zero resultant for unchanged
motion, and the distinction that a non-zero resultant changes motion. Newton II
requires the resultant force, its acceleration relationship and direction, and
the constant-mass condition. Newton III requires one interaction, equal
magnitude, opposite direction, simultaneous pairing, and different bodies.
Action-reaction prompts identify the authored source and target when a source
scenario is supplied; a pair is never treated as two forces on one body.

Mass is an inertial property in kilograms, while weight is a gravitational
force in newtons that depends on the authored field. Apparent weight refers to
the relevant support/contact force and may change without gravity changing.
Normal force is a contact force perpendicular to the surface and is not
defined as universally equal to weight. Static friction adapts to the tendency
to slide up to its limiting value; kinetic friction applies while sliding.
System, environment, internal, and external classifications follow the chosen
boundary. An FBD isolates one body and includes forces acting on that body,
including authored ownership and source-context semantics when available.

## Determinism, context, and visuals

The generator id is
`caps-grade-11-newton-conceptual-question-generator`, version `1`. IDs are
derived from the template and, for contextual questions, a sanitised authored
scenario identifier. Seeds are preserved in provenance and no global random
state is used. A supplied `NewtonGeneratedProblem` or `NewtonScenario` adds
only authored scenario identity, system membership, and relevant ownership
context to the prompt and concept criteria; numeric givens are not copied into
conceptual answers.

When `include_visuals` is enabled and a scenario is supplied, the generator
delegates to the existing Issue #58 `NewtonSvgRenderer` for a deterministic
force diagram or selected-body FBD. The visual is learner-safe: it does not
leak hidden magnitudes or derived answers. The default is no visual.

The generator has no dependency on `NewtonSolver`, numeric calculation
templates, automatic marking, the application API, or printable-document
layers. Those concerns remain deferred to the later M4 issues; #61 is the next
planned integration item after review of #60.
