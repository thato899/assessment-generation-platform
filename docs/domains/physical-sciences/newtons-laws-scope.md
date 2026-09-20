# Newton's Laws CAPS scope

Issue #54 establishes the curriculum boundary for the M4 Newton's Laws
milestone. This document is a curriculum and architecture contract only. It
does not implement Newton domain objects, equations, solvers, generation,
rendering, questions, or API routing.

## Authoritative source and grade placement

The authority is the South African Department of Basic Education's official
[CAPS Physical Sciences Grades 10–12 PDF](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf).

The source places Newton's Laws and their applications in the Grade 11
Mechanics sequence. Grade 11 includes vectors, force types, force/free-body
diagrams, Newton's first/second/third laws, applications, and universal
gravitation (CAPS pp. 61–66; Sections 3, Grade 11 Physics). Grade 12 term 4
explicitly consolidates the Grade 11 Newton laws and applications and calls
for integrated problem solving (CAPS p. 141). The Grade 12 assessment section
also lists Newton's Laws and their application as selected Grade 11 content
that is examinable in the Grade 12 final examination (CAPS p. 149).

Therefore the authoritative metadata is:

- core instructional grade: Grade 11;
- Grade 12 relationship: consolidation, integrated application, and selected
  examinability rather than first formal instruction;
- stable topic identifier: `newtons-laws`;
- subject/domain: Physical Sciences / Mechanics.

## Evidence matrix

| CAPS location | Grade | Concept or requirement | M4 decision |
| --- | --- | --- | --- |
| Overview of topics, p. 10 | 11 | Newton's Laws, universal gravitation, force types, force diagrams, free-body diagrams, equilibrium and non-equilibrium | Include in the Grade 11 topic metadata and M4 contract |
| Mechanics, pp. 61–62 | 11 | Resultants, vector components, and force types including weight, normal, friction, applied force, and tension | Include bounded one-/two-dimensional force representations |
| Mechanics, p. 63 | 11 | Force diagrams, free-body diagrams, component resolution, and net-force components | Require semantic diagrams and explicit axis/component data later |
| Mechanics, pp. 64–65 | 11 | Newton I/II/III, `F_net = ma`, equilibrium/non-equilibrium, horizontal/inclined/vertical cases, and two masses joined by a light string | Include as bounded later domain/solver families |
| Mechanics, pp. 62–63 | 11 | Static/kinetic friction, maximum static friction, and friction proportional to normal force | Include the stated static/kinetic relationships; defer arbitrary contact models |
| Mechanics, p. 66 | 11 | Universal gravitation, weight, `W = mg`, mass versus weight, and weightlessness | Include the stated scalar relationships and distinctions |
| Grade 12 term 4, p. 141 | 12 | Consolidation of Grade 11 Newton laws and applications; integrated problem solving | Record as Grade 12 use, not core topic ownership |
| Assessment, p. 149 | 12 | Selected Grade 11 Newton content is examinable in the Grade 12 final examination | Preserve Grade 11 metadata and record Grade 12 assessment relevance |

## Supported M4 scope

The following is the approved bounded scope for later M4 implementation:

- Newton's first, second, and third laws, including precise action-reaction
  pair reasoning;
- net/resultant force, equilibrium, non-equilibrium, mass, acceleration, and
  signed/vector reasoning;
- force types explicitly named by CAPS: weight, normal, friction, applied
  push/pull, and tension;
- force diagrams and free-body diagrams for a declared object or system;
- one- and two-dimensional force components with a declared coordinate axis;
- static friction, maximum static friction, and kinetic/dynamic friction using
  the CAPS relationships;
- bounded single-body horizontal, inclined-plane, and vertical-motion cases;
- bounded two-body systems joined by a light/negligible-mass string;
- weight near Earth's surface, mass versus weight, apparent weight,
  weightlessness, and Newton's law of universal gravitation;
- conceptual and calculation assessment of the above, subject to structural
  solvability and explicit assumptions.

The later engine must make these assumptions explicit: selected system and
environment, coordinate axes, contact conditions, friction regime, light
string when applicable, and gravitational data. It must preserve SI units,
signed/vector quantities, and the distinction between physical direction and
mathematical sign.

## Relationships and units

Later components may use only relationships justified by the approved CAPS
scope, with applicability checked before calculation:

- vector resultant: `F_net = ΣF`, resolved per declared axis;
- constant-mass Newton II: `F_net = ma`;
- static friction: `0 ≤ f_s ≤ μ_s N`, with limiting value `f_s,max = μ_s N`;
- kinetic/dynamic friction: `f_k = μ_k N`;
- weight near a gravitational field: `W = mg`;
- universal gravitation: `F = G m₁m₂ / d²`.

Force is measured in newtons, mass in kilograms, acceleration and `g` in
metres per second squared, and distance in metres. Force and acceleration are
vectors; mass, distance, and the friction coefficients are scalars. A later
solver must not silently apply a formula outside its stated assumptions or
fabricate an answer for an underdetermined system.

## Force and diagram semantics

Force kinds must remain distinguishable in later domain models. A normal force
acts perpendicular to the contact surface; friction acts parallel to the
contact surface and opposes motion or its impending direction; weight is the
gravitational force exerted by the relevant body; applied force and tension
retain their source semantics.

A force diagram represents the object(s) of interest and the forces acting on
them. A free-body diagram isolates the object of interest as a dot and draws
the acting forces as arrows. Third-law partners act on different bodies and
must not be combined as two arrows on one body's free-body diagram. Arrow
direction, label, body/system ownership, and mathematical sign are separate
pieces of meaning.

## Explicit exclusions and deferrals

The following are outside the approved M4 boundary unless a later curriculum
decision reopens them:

- rotational dynamics, torque, angular momentum, and rigid-body mechanics;
- fluid forces, drag, and variable-mass systems;
- non-inertial frames and university-level calculus-based dynamics;
- arbitrary three-dimensional mechanics or unconstrained vector geometry;
- arbitrary multi-pulley and general multi-body constraint systems;
- a general contact/friction engine beyond the stated CAPS relationships;
- automatic free-text marking, printable documents, and LMS adapters;
- public API topic routing before the dedicated integration issue.

These exclusions bound architecture; they do not deny the Grade 11 CAPS
requirements listed above.

## Requirements for later issues

- Issue #55 must represent bodies, force kinds, vectors, axes, system
  boundaries, assumptions, and action-reaction ownership without importing a
  framework or the Momentum models semantically.
- Issue #56 must be the sole authority for supported numerical results and
  reject underdetermined or inapplicable cases.
- Issue #57 may generate only bounded, seeded scenarios accepted by the
  solver; curriculum metadata and numeric pools remain separate.
- Issue #58 must render validated force/free-body data safely and must not
  leak hidden answers.
- Issues #59 and #60 must create canonical calculation/conceptual questions
  from solver results and approved concepts, with deterministic IDs and
  machine-readable semantics.
- Issue #61 must add routing only after the complete pipeline exists and must
  preserve learner-safe projections and existing API behavior.

## Issue #54 non-goals

Issue #54 merged in PR #64 at `703de9acf8f334be6eafae0249cc8868f8215c66`.
Issue #55 now supplies the [authored domain contract](newtons-laws-domain.md)
within this approved scope. Its structural validation permits underdetermined
inputs; #56 will determine solvability and numerical consistency. The curriculum
grade placement and supported/deferred scope above are unchanged.

Issue #54 made no Newton topic available through the generation API, added no
Newton solver or renderer, and created no production force/scenario/question
classes. Its implementation changes were curriculum metadata plus scope
regression coverage. No ADR was required: the existing curriculum
reference and modular-domain decisions are sufficient.
