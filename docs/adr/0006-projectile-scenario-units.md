# ADR 0006: Explicit units and sign conventions in projectile scenarios

Status: accepted. The vertical projectile model uses small immutable SI value objects and an explicit positive direction. This prevents downstream components from guessing whether a numeric value is metres, metres per second, or metres per second squared, while avoiding a general-purpose units framework before it is needed. The scenario validates representation invariants only; trajectory calculations remain the solver's responsibility.
