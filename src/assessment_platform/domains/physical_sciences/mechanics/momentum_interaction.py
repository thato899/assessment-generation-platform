"""Framework-independent authored constraints for Momentum interactions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    MetresPerSecond,
    MomentumScenario,
)


def _identifier(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


class InteractionConstraintKind(StrEnum):
    """Explicit authored information about an interaction's final state."""

    KNOWN_FINAL_VELOCITY = "known-final-velocity"
    COMMON_FINAL_VELOCITY = "common-final-velocity"
    COMPLETE_FINAL_STATE = "complete-final-state"


@dataclass(frozen=True, slots=True)
class FinalBodyState:
    """An authored post-interaction velocity for one identified body."""

    body_identifier: str
    final_velocity: MetresPerSecond

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "body_identifier",
            _identifier(self.body_identifier, "final body identifier"),
        )
        if not isinstance(self.final_velocity, MetresPerSecond):
            raise ValueError("final velocity must be MetresPerSecond")


@dataclass(frozen=True, slots=True)
class KnownFinalVelocityConstraint:
    """An authored final velocity for one named body."""

    body_identifier: str
    final_velocity: MetresPerSecond

    @property
    def kind(self) -> InteractionConstraintKind:
        return InteractionConstraintKind.KNOWN_FINAL_VELOCITY

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "body_identifier",
            _identifier(self.body_identifier, "known final-velocity body identifier"),
        )
        if not isinstance(self.final_velocity, MetresPerSecond):
            raise ValueError("known final velocity must be MetresPerSecond")


@dataclass(frozen=True, slots=True)
class CommonFinalVelocityConstraint:
    """An explicit perfectly inelastic/sticking constraint for two bodies."""

    body_identifiers: tuple[str, ...]

    @property
    def kind(self) -> InteractionConstraintKind:
        return InteractionConstraintKind.COMMON_FINAL_VELOCITY

    def __post_init__(self) -> None:
        identifiers = tuple(
            _identifier(identifier, "common final-velocity body identifier")
            for identifier in self.body_identifiers
        )
        if len(identifiers) != 2:
            raise ValueError("common final velocity currently requires exactly two bodies")
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("common final-velocity body identifiers must be unique")
        object.__setattr__(self, "body_identifiers", identifiers)


@dataclass(frozen=True, slots=True)
class CompleteFinalStateConstraint:
    """Authored final velocities for every body in an interaction."""

    final_states: tuple[FinalBodyState, ...]

    @property
    def kind(self) -> InteractionConstraintKind:
        return InteractionConstraintKind.COMPLETE_FINAL_STATE

    def __post_init__(self) -> None:
        states = tuple(self.final_states)
        if not states or any(not isinstance(state, FinalBodyState) for state in states):
            raise ValueError("complete final state must contain FinalBodyState values")
        identifiers = tuple(state.body_identifier for state in states)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("complete final-state body identifiers must be unique")
        object.__setattr__(self, "final_states", states)


InteractionConstraint = (
    KnownFinalVelocityConstraint
    | CommonFinalVelocityConstraint
    | CompleteFinalStateConstraint
)
_CONSTRAINT_TYPES = (
    KnownFinalVelocityConstraint,
    CommonFinalVelocityConstraint,
    CompleteFinalStateConstraint,
)


@dataclass(frozen=True, slots=True)
class MomentumInteraction:
    """Initial scenario plus explicit authored post-interaction information.

    The interaction is separate from ``MomentumScenario`` so existing initial
    states remain valid and the current aggregate solver can remain unchanged.
    This model represents constraints only; it does not calculate any result.
    """

    identifier: str
    scenario: MomentumScenario
    constraint: InteractionConstraint

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "identifier", _identifier(self.identifier, "interaction identifier")
        )
        if not isinstance(self.scenario, MomentumScenario):
            raise ValueError("interaction scenario must be a MomentumScenario")
        if not isinstance(self.constraint, _CONSTRAINT_TYPES):
            raise ValueError("interaction constraint must be supported")

        body_identifiers = tuple(body.identifier for body in self.scenario.bodies)
        available = set(body_identifiers)
        if isinstance(self.constraint, KnownFinalVelocityConstraint):
            if self.constraint.body_identifier not in available:
                raise ValueError("known final-velocity body is not part of the scenario")
        elif isinstance(self.constraint, CommonFinalVelocityConstraint):
            if not set(self.constraint.body_identifiers).issubset(available):
                raise ValueError("common final-velocity body is not part of the scenario")
        elif not set(
            state.body_identifier for state in self.constraint.final_states
        ) == available:
            raise ValueError("complete final state must cover every scenario body exactly once")
