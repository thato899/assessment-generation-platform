# Momentum change, impulse, force, and contact time

Issue #37 adds the framework-independent `MomentumImpulseRelationshipSolver`.
It is authoritative for generic one-dimensional Momentum & Impulse
relationships, whether or not the input came from a collision. Later
generation, question, and API layers must consume these results rather than
duplicate the equations.

## Semantic types and results

The domain keeps `Momentum`, `MomentumChange`, `Impulse`, `Newtons`, and
`Seconds` distinct. `MomentumChange` is signed final momentum minus signed
initial momentum. `Impulse` remains a different type even though the
impulse-momentum theorem makes their numeric values equal. `Newtons` stores a
signed average/resultant force, and `Seconds` stores a strictly positive
interaction interval.

Typed immutable inputs and results identify supplied and derived quantities:
`MomentumChangeInput`, `MomentumChangeResult`, `ForceTimeInput`,
`ImpulseResult`, `ForceTimeResult`, and `ContactTimeResult`.

## Relationships

For mass `m`, initial velocity `v_i`, and final velocity `v_f`:

`p_i = m v_i`

`p_f = m v_f`

`change in momentum = p_f - p_i`

The impulse-momentum theorem is represented as:

`J = change in momentum`

For a signed average/resultant force `F` over positive contact time `t`:

`J = F t`

and Newton's second law in momentum form is represented at the average level:

`F = change in momentum / t`

The solver also derives `t = J/F` when the signed impulse and force have
compatible directions. It does not introduce instantaneous calculus or a
time-dependent force function.

## Sign, axis, and validity policy

All scalar quantities retain their mathematical signs under an explicit
`PositiveAxis`. A direction reversal is therefore a signed change, not a
magnitude difference: changing `+10` momentum to `-6` gives `-16`, not `4`.
Equivalent RIGHT-positive and LEFT-positive descriptions negate velocity,
momentum, momentum change, impulse, and force while preserving positive
contact time.

Contact time must be strictly positive. Opposite impulse/force signs are
rejected rather than converted with `abs()`. Zero impulse with positive time
produces zero force, and zero force with positive time produces zero impulse.
Deriving time from both zero impulse and zero force is underdetermined; a
non-zero impulse with zero force is invalid. Non-finite values, zero or
negative time, and invalid semantic types are rejected explicitly.

Calculations use full finite values and the repository tolerance of `1e-9`
where relationship consistency is validated. No intermediate rounding occurs.
Results are immutable and repeated calls are deterministic.

## Boundaries

This solver remains separate from Issue #36 constrained collision solving and
does not require a collision input. It does not expand the #32 scenario
factory, render SVG (#39), generate calculation or conceptual/safety
questions (#40/#41), or change the API (#42). No new ADR is needed; ADR 0011
continues to govern authored-versus-derived interaction data.
