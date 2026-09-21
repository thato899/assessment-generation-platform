"""Immutable authored Work, Energy & Power scenarios."""

from __future__ import annotations

from dataclasses import dataclass

from .relationships import (
    AlongPlaneWorkInput,
    AveragePowerInput,
    ConstantSpeedPowerInput,
    HeightState,
    KineticState,
    MechanicalEnergyContext,
    NetWorkInput,
    PumpingPowerInput,
    ReferenceLevel,
    WorkEnergyAssumptions,
    WorkEnergyContext,
)
from .values import identifier


def _sequence[T](value: object, expected: type, name: str) -> tuple[T, ...]:
    if not isinstance(value, (tuple, list)):
        raise ValueError(f"{name} must be an ordered sequence")
    result = tuple(value)
    if any(not isinstance(item, expected) for item in result):
        raise ValueError(f"{name} contains an invalid value")
    return result


@dataclass(frozen=True, slots=True)
class WorkEnergyScenario:
    """Authored facts for one M5 problem; no derived answer is stored."""

    identifier: str
    work_inputs: tuple[NetWorkInput | AlongPlaneWorkInput, ...] = ()
    kinetic_states: tuple[KineticState, ...] = ()
    reference_levels: tuple[ReferenceLevel, ...] = ()
    height_states: tuple[HeightState, ...] = ()
    work_energy_contexts: tuple[WorkEnergyContext, ...] = ()
    mechanical_energy_contexts: tuple[MechanicalEnergyContext, ...] = ()
    average_power_inputs: tuple[AveragePowerInput, ...] = ()
    constant_speed_power_inputs: tuple[ConstantSpeedPowerInput, ...] = ()
    pumping_power_inputs: tuple[PumpingPowerInput, ...] = ()
    assumptions: WorkEnergyAssumptions = WorkEnergyAssumptions()

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", identifier(self.identifier, "scenario identifier"))
        for name, expected in (
            ("kinetic_states", KineticState),
            ("reference_levels", ReferenceLevel),
            ("height_states", HeightState),
            ("work_energy_contexts", WorkEnergyContext),
            ("mechanical_energy_contexts", MechanicalEnergyContext),
            ("average_power_inputs", AveragePowerInput),
            ("constant_speed_power_inputs", ConstantSpeedPowerInput),
            ("pumping_power_inputs", PumpingPowerInput),
        ):
            values: tuple[object, ...] = _sequence(getattr(self, name), expected, name)
            object.__setattr__(self, name, values)
        if not isinstance(self.work_inputs, (tuple, list)):
            raise ValueError("work_inputs must be an ordered sequence")
        work_inputs = tuple(self.work_inputs)
        if any(not isinstance(item, (NetWorkInput, AlongPlaneWorkInput)) for item in work_inputs):
            raise ValueError("work_inputs contains an unsupported authored input")
        object.__setattr__(self, "work_inputs", work_inputs)
        if not isinstance(self.assumptions, WorkEnergyAssumptions):
            raise ValueError("assumptions must be WorkEnergyAssumptions")
        self._validate_unique_ids()
        self._validate_references()

    def _validate_unique_ids(self) -> None:
        for name in ("kinetic_states", "reference_levels", "height_states"):
            values = getattr(self, name)
            ids = tuple(item.identifier for item in values)
            if len(ids) != len(set(ids)):
                raise ValueError(f"{name} identifiers must be unique")

    def _validate_references(self) -> None:
        levels = {level.identifier for level in self.reference_levels}
        for state in self.height_states:
            if state.reference_level.identifier not in levels:
                raise ValueError("height state references an unknown reference level")
        state_ids = {state.identifier for state in self.kinetic_states}
        for work_context in self.work_energy_contexts:
            if work_context.initial_state.identifier not in state_ids:
                raise ValueError("work-energy context references an unknown initial state")
            if work_context.final_state.identifier not in state_ids:
                raise ValueError("work-energy context references an unknown final state")
        height_ids = {state.identifier for state in self.height_states}
        for mechanical_context in self.mechanical_energy_contexts:
            if mechanical_context.initial_state.identifier not in state_ids:
                raise ValueError("mechanical-energy context references an unknown initial state")
            if mechanical_context.final_state.identifier not in state_ids:
                raise ValueError("mechanical-energy context references an unknown final state")
            if mechanical_context.initial_height.identifier not in height_ids:
                raise ValueError("mechanical-energy context references an unknown initial height")
            if mechanical_context.final_height.identifier not in height_ids:
                raise ValueError("mechanical-energy context references an unknown final height")

    def reference_level(self, identifier_value: str) -> ReferenceLevel:
        for level in self.reference_levels:
            if level.identifier == identifier_value:
                return level
        raise ValueError("unknown reference level")


__all__ = ["WorkEnergyScenario"]
