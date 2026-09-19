"""Deterministic one-dimensional momentum-change and force-time relationships."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    Kilograms,
    MetresPerSecond,
    Momentum,
    MomentumChange,
    Newtons,
    PositiveAxis,
    Seconds,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse_solver import (
    VALIDATION_TOLERANCE,
)


def _valid_axis(value: PositiveAxis) -> None:
    if not isinstance(value, PositiveAxis):
        raise ValueError("positive_axis must be explicit")


def _close(first: float, second: float) -> bool:
    return isfinite(first) and isfinite(second) and abs(first - second) <= VALIDATION_TOLERANCE


@dataclass(frozen=True, slots=True)
class MomentumChangeInput:
    """Initial and final velocity data for one body's momentum change."""

    mass: Kilograms
    initial_velocity: MetresPerSecond
    final_velocity: MetresPerSecond
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        if not isinstance(self.mass, Kilograms):
            raise ValueError("mass must be Kilograms")
        if not isinstance(self.initial_velocity, MetresPerSecond):
            raise ValueError("initial_velocity must be MetresPerSecond")
        if not isinstance(self.final_velocity, MetresPerSecond):
            raise ValueError("final_velocity must be MetresPerSecond")
        _valid_axis(self.positive_axis)


@dataclass(frozen=True, slots=True)
class ForceTimeInput:
    """Signed average/resultant force and positive contact time."""

    force: Newtons
    contact_time: Seconds
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        if not isinstance(self.force, Newtons):
            raise ValueError("force must be Newtons")
        if not isinstance(self.contact_time, Seconds):
            raise ValueError("contact_time must be Seconds")
        _valid_axis(self.positive_axis)


@dataclass(frozen=True, slots=True)
class MomentumChangeResult:
    """Initial momentum, final momentum, and their signed difference."""

    initial_momentum: Momentum
    final_momentum: Momentum
    momentum_change: MomentumChange
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        if not isinstance(self.initial_momentum, Momentum):
            raise ValueError("initial_momentum must be Momentum")
        if not isinstance(self.final_momentum, Momentum):
            raise ValueError("final_momentum must be Momentum")
        if not isinstance(self.momentum_change, MomentumChange):
            raise ValueError("momentum_change must be MomentumChange")
        if not _close(
            self.momentum_change.value,
            self.final_momentum.value - self.initial_momentum.value,
        ):
            raise ValueError("momentum_change must equal final minus initial momentum")
        _valid_axis(self.positive_axis)


@dataclass(frozen=True, slots=True)
class ImpulseResult:
    """Impulse and the signed momentum change it represents."""

    impulse: Impulse
    momentum_change: MomentumChange
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        if not isinstance(self.impulse, Impulse):
            raise ValueError("impulse must be Impulse")
        if not isinstance(self.momentum_change, MomentumChange):
            raise ValueError("momentum_change must be MomentumChange")
        if not _close(self.impulse.value, self.momentum_change.value):
            raise ValueError("impulse must equal the momentum change")
        _valid_axis(self.positive_axis)


@dataclass(frozen=True, slots=True)
class ForceTimeResult:
    """Signed force, positive time, and the resulting impulse/change."""

    force: Newtons
    contact_time: Seconds
    impulse: Impulse
    momentum_change: MomentumChange
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        if not isinstance(self.force, Newtons):
            raise ValueError("force must be Newtons")
        if not isinstance(self.contact_time, Seconds):
            raise ValueError("contact_time must be Seconds")
        if not isinstance(self.impulse, Impulse):
            raise ValueError("impulse must be Impulse")
        if not isinstance(self.momentum_change, MomentumChange):
            raise ValueError("momentum_change must be MomentumChange")
        if not _close(self.impulse.value, self.force.value * self.contact_time.value):
            raise ValueError("impulse must equal force multiplied by contact time")
        if not _close(self.impulse.value, self.momentum_change.value):
            raise ValueError("impulse must equal the momentum change")
        _valid_axis(self.positive_axis)


@dataclass(frozen=True, slots=True)
class ContactTimeResult:
    """Positive contact time derived from compatible impulse and force."""

    contact_time: Seconds
    impulse: Impulse
    force: Newtons
    momentum_change: MomentumChange
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        if not isinstance(self.contact_time, Seconds):
            raise ValueError("contact_time must be Seconds")
        if not isinstance(self.impulse, Impulse):
            raise ValueError("impulse must be Impulse")
        if not isinstance(self.force, Newtons):
            raise ValueError("force must be Newtons")
        if not isinstance(self.momentum_change, MomentumChange):
            raise ValueError("momentum_change must be MomentumChange")
        if not _close(self.impulse.value, self.force.value * self.contact_time.value):
            raise ValueError("impulse must equal force multiplied by contact time")
        if not _close(self.impulse.value, self.momentum_change.value):
            raise ValueError("impulse must equal the momentum change")
        _valid_axis(self.positive_axis)


class MomentumImpulseRelationshipSolver:
    """Authoritative deterministic solver for one-dimensional relationships."""

    def calculate_momentum_change(
        self, input_data: MomentumChangeInput
    ) -> MomentumChangeResult:
        if not isinstance(input_data, MomentumChangeInput):
            raise ValueError("input_data must be MomentumChangeInput")
        initial = Momentum(input_data.mass.value * input_data.initial_velocity.value)
        final = Momentum(input_data.mass.value * input_data.final_velocity.value)
        change = MomentumChange(final.value - initial.value)
        return MomentumChangeResult(initial, final, change, input_data.positive_axis)

    def calculate_impulse_from_momentum_change(
        self, result: MomentumChangeResult
    ) -> ImpulseResult:
        if not isinstance(result, MomentumChangeResult):
            raise ValueError("result must be MomentumChangeResult")
        impulse = Impulse(result.momentum_change.value)
        return ImpulseResult(impulse, result.momentum_change, result.positive_axis)

    def calculate_impulse_from_force_time(
        self, input_data: ForceTimeInput
    ) -> ImpulseResult:
        if not isinstance(input_data, ForceTimeInput):
            raise ValueError("input_data must be ForceTimeInput")
        impulse = Impulse(input_data.force.value * input_data.contact_time.value)
        change = MomentumChange(impulse.value)
        return ImpulseResult(impulse, change, input_data.positive_axis)

    def calculate_force_from_impulse(
        self,
        impulse: Impulse,
        contact_time: Seconds,
        positive_axis: PositiveAxis,
    ) -> ForceTimeResult:
        if not isinstance(impulse, Impulse):
            raise ValueError("impulse must be Impulse")
        if not isinstance(contact_time, Seconds):
            raise ValueError("contact_time must be Seconds")
        _valid_axis(positive_axis)
        force = Newtons(impulse.value / contact_time.value)
        change = MomentumChange(impulse.value)
        return ForceTimeResult(force, contact_time, impulse, change, positive_axis)

    def calculate_force_from_momentum_change(
        self,
        result: MomentumChangeResult,
        contact_time: Seconds,
    ) -> ForceTimeResult:
        if not isinstance(result, MomentumChangeResult):
            raise ValueError("result must be MomentumChangeResult")
        return self.calculate_force_from_impulse(
            Impulse(result.momentum_change.value), contact_time, result.positive_axis
        )

    def calculate_contact_time_from_impulse(
        self,
        impulse: Impulse,
        force: Newtons,
        positive_axis: PositiveAxis,
    ) -> ContactTimeResult:
        if not isinstance(impulse, Impulse):
            raise ValueError("impulse must be Impulse")
        if not isinstance(force, Newtons):
            raise ValueError("force must be Newtons")
        _valid_axis(positive_axis)
        contact_time = self._contact_time(impulse.value, force.value)
        return ContactTimeResult(
            contact_time,
            impulse,
            force,
            MomentumChange(impulse.value),
            positive_axis,
        )

    def calculate_contact_time_from_momentum_change(
        self,
        result: MomentumChangeResult,
        force: Newtons,
    ) -> ContactTimeResult:
        if not isinstance(result, MomentumChangeResult):
            raise ValueError("result must be MomentumChangeResult")
        return self.calculate_contact_time_from_impulse(
            Impulse(result.momentum_change.value), force, result.positive_axis
        )

    @staticmethod
    def _contact_time(impulse: float, force: float) -> Seconds:
        if force == 0:
            if impulse == 0:
                raise ValueError(
                    "contact time is underdetermined when impulse and force are both zero"
                )
            raise ValueError("non-zero impulse cannot be produced by zero force")
        ratio = impulse / force
        if ratio <= 0:
            raise ValueError("impulse and force must have compatible signs for positive time")
        if not isfinite(ratio):
            raise ValueError("contact time must be finite")
        return Seconds(ratio)
