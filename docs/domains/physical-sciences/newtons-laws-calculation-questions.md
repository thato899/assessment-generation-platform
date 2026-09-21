# Newton's Laws calculation questions

Issue #59 provides `NewtonCalculationQuestionGenerator` in
`assessment_platform.domains.physical_sciences.mechanics.newton_question_generator`.
It consumes a typed Issue #57 generated problem, asks `NewtonSolver` for the
authoritative result, and packages that result into the canonical assessment
model. It does not contain a Newton equation or a second numerical solver.

## Templates and family mapping

The generator supports these numeric templates:

| Generated family | Calculation templates |
| --- | --- |
| Newton II | signed resultant force, signed acceleration |
| Equilibrium | zero signed resultant force |
| Unknown force | one signed component per authored axis |
| Weight | signed authored-field weight component |
| Contact normal | normal force, apparent weight |
| Static friction | required signed static friction, apparent weight |
| Limiting static friction | limiting friction magnitude, apparent weight |
| Kinetic friction | kinetic friction magnitude, apparent weight |
| Inclined plane | surface-normal force, apparent weight |
| Connected bodies | common signed acceleration, string tension |
| Universal gravitation | scalar gravitational-force magnitude |

Newton III is intentionally unsupported here: the solver validates an authored
third-law pair but does not derive a new numeric quantity. Its calculation
question belongs nowhere in this issue; conceptual treatment is owned by active #60. Unsupported, underdetermined, inconsistent and numerical-range solver
outcomes raise before a `Question` is returned.

## Canonical model and authority

Each returned `Question` contains immutable `QuestionPart` values with a
calculation `ResponseSpecification`, numeric `ExpectedAnswer`, and explicit
`MarkingScheme`. Criteria marks always sum to the part's marks. The learner
tolerance is the existing assessment numeric policy (`0.01`); the solver's
`1e-9` validation tolerance remains an internal physics-validation policy and
is not reused automatically for learner marking.

Expected answers preserve solver signs and full floating-point values. The
question prompt exposes masses, authored known forces, field values, contact
regimes/coefficient data, string assumptions, separation and the positive
direction needed by the selected solver operation. Unknown authored components
remain `?` and are never replaced in the scenario.

Question IDs use the generated problem identifier, generator version and
semantic template IDs. Part IDs append the template and axis role. No answer,
timestamp, UUID or process hash is used. `GenerationProvenance` retains the
question generator, source seed and template IDs; `Scenario.data` records the
source generation identity and curriculum metadata without expected answers.
The curriculum reference is the Grade 11 `newtons-laws` topic; Grade 12 is
retained as consolidation and selected examinability context.

## Visuals and learner safety

`NewtonQuestionOptions(include_visuals=True)` attaches the merged #58
`NewtonSvgRenderer` with a force-diagram request and its learner-safe defaults.
`include_visuals=False` attaches no `VisualReference`. Renderer output does not
show derived answers, and distinctive expected values are absent from the
prompt, IDs, provenance, scenario data and SVG. Visuals remain technical SVG;
no PDF, DOCX, API routing or automatic marking is added.

## Boundaries and deferred work

Marking schemes describe criteria only; this issue does not evaluate learner
responses or award marks. Conceptual Newton First/Second/Third Law templates,
conceptual rubrics are owned by #60; API integration, printing and final CAPS
verification remain deferred to #61-#62. Generation policy remains owned by #57 and numerical authority
remains owned by #56.
