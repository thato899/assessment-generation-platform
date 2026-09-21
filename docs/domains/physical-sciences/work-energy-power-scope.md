# Work, Energy & Power scope contract

## Curriculum identity

| Field | Value |
| --- | --- |
| Curriculum | CAPS |
| Subject | Physical Sciences |
| Grade | 12 |
| Domain | Mechanics |
| Topic identifier | `work-energy-and-power` |
| Topic name | Work, Energy & Power |
| CAPS placement | Grade 12 Physics (Mechanics), Term 2 |

The stable identifier is reused from the existing CAPS topic metadata in
`src/assessment_platform/curriculum/caps/physical_sciences.py`. No alias is
introduced.

## Authoritative basis

The primary source is the South African Department of Basic Education,
[Physical Sciences Grades 10–12 CAPS](https://www.education.gov.za/Portals/0/CD/National%20Curriculum%20Statements%20and%20Vocational/CAPS%20FET%20%20PHYSICAL%20SCIENCE%20WEB.pdf),
Section 3, Grade 12 Physics (Mechanics), Term 2, pages 117–120 (PDF pages
121–124). CAPS allocates 10 hours to Work, Energy & Power. The DBE
[Grade 12 Work Energy and Power self-study guide](https://www.education.gov.za/SelfStudyGuidesGrade10-12.aspx)
and the [DBE digital-content listing](https://www.education.gov.za/Curriculum/LearningandTeachingSupportMaterials%28LTSM%29/DigitalContent/StateOwnedTextbooksGrade10to12.aspx)
are supplementary orientation only; they do not replace CAPS.

CAPS states that Grade 12 Mechanics covers work, the work-energy theorem,
conservation of energy with non-conservative forces present, and power. The
term schedule specifies the bounded requirements below.

## Approved scope

### Work

- Define work done by a force as `W = F Δx cos θ`.
- Treat work as a scalar measured in joules.
- Calculate each force contribution and add the scalar contributions to obtain
  net work.
- Preserve positive, negative, and zero work: parallel, antiparallel, and
  perpendicular force-displacement relations are explicit authored cases.
- Permit a bounded authored angle between force and displacement. The domain
  stores force and displacement magnitudes plus their angle relationship; it
  does not require a general vector algebra package.
- Support the CAPS alternate method for forces along a plane: author the
  resultant force along the displacement and the displacement along the plane,
  then calculate net work as their product.

### Work-energy theorem

- Represent the theorem as net work causing a change in kinetic energy.
- Apply it to horizontal and inclined planes, both frictionless and rough,
  when the authored forces, displacement, and assumptions determine the result.
- Keep contact-work semantics explicit: a contact force contributes work only
  when it remains in contact over the authored displacement.
- Do not infer a force resultant from Newton-domain objects or silently solve
  an underspecified free-body problem.

### Energy and conservation

- Treat kinetic energy as scalar, using authored mass and speed; direction of a
  velocity is not part of the kinetic-energy result.
- Represent gravitational potential-energy change only for a near-Earth,
  authored height change with an explicit reference level and gravitational
  field. A universal gravitational potential model is outside this contract.
- Distinguish conservative and non-conservative forces. With only conservative
  forces, mechanical energy is conserved; with non-conservative forces,
  mechanical energy may change while total system energy remains conserved.
- Support bounded mechanical-energy relationships with explicit initial and
  final kinetic/potential states and authored non-conservative work or energy
  change. Friction may be a non-conservative work contribution when authored.
- Do not create a thermodynamics engine, heat-transfer model, or arbitrary
  force-position integral.

### Power

- Define power as the rate at which work is done and measure it in watts.
- Support average power from work over an authored positive time interval.
- Support CAPS constant-speed rough horizontal and rough inclined contexts using
  an authored force along motion and average speed (`P_av = F v_av`) where the
  assumptions establish the required force.
- Support the minimum electric-motor power required to pump water from an
  authored borehole depth at an authored rate. The future domain must make
  mass flow, height/depth, gravitational field, and any efficiency assumption
  explicit; it must not invent a motor model.

## Representation decisions

The smallest CAPS-sufficient authored representation is scalar quantities plus
explicit relationships:

- force magnitude, displacement magnitude, and an angle relationship for each
  work contribution;
- an optional scalar force along a plane for the alternate net-work method;
- mass and speed states for kinetic energy;
- height difference, reference level, and authored near-Earth gravitational
  field for gravitational potential energy;
- initial/final energy states and explicit non-conservative work or energy
  change for conservation relationships;
- positive time, average speed, force, and pumping inputs for power.

General 2D force vectors, arbitrary vector addition, variable forces, path
integrals, and hidden direction inference are not required by this bounded
contract. Surface diagrams may show a horizontal or inclined context, but
visual geometry remains downstream of authored scalar relationships.

## Assumptions and applicability

A future scenario must declare the inertial/reference frame, constant-mass
assumption where used, near-Earth field where used, reference level for height,
friction/contact state, constant-force or constant-speed assumptions, and
whether a contact remains engaged. Unknown values remain unknown. Structurally
valid but underdetermined relationships are preserved by the domain and
rejected by the solver and question generator.

## Explicit exclusions

This contract excludes rotational work, torque, springs unless a later CAPS
review adds them to this topic, thermodynamics, relativistic energy,
variable-mass systems, fluid dynamics, arbitrary 3D vectors, arbitrary
force-position functions or calculus/integration, general Newton free-body
solving, automatic/free-text marking, PDF/printing, LMS adapters, a new API
version, and M6 Mathematics work. The final implementation issue may narrow
these exclusions only with new curriculum evidence.

## Boundary with existing engines

M5 remains a separate Work/Energy/Power domain and solver. It may reuse core
assessment, seed, provenance, response, marking, visual-reference, and
learner-projection types. It may reuse low-level SI value objects when their
invariants are identical. It must not depend on Newton question generators,
Newton application routing, or Newton solver internals. If a work problem needs
force information, the scenario authors the scalar force/work contribution or
a future shared mechanics capability is introduced as an explicitly reviewed
boundary; no hidden cross-domain calculation is allowed.
