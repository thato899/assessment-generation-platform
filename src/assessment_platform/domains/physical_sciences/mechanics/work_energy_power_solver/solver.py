"""Authoritative deterministic Work, Energy & Power calculations."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import sqrt

from assessment_platform.core import ValidationResult

from ..work_energy_power import (
    AlongPlaneWorkInput,
    AveragePowerInput,
    ConstantSpeedPowerInput,
    GravitationalFieldMagnitude,
    HeightState,
    KineticEnergy,
    KineticState,
    Mass,
    MechanicalEnergyContext,
    NetWorkInput,
    PumpingPowerInput,
    SignedEnergy,
    Speed,
    UnknownValue,
    WorkContribution,
    WorkEnergyContext,
    WorkEnergyScenario,
)
from ._numerical import (
    VALIDATION_TOLERANCE,
    cardinal_cosine,
    close,
    consistent,
    operation,
    total,
)
from .results import (
    AlongPlaneWorkResult,
    FailureReason,
    KineticEnergyResult,
    MechanicalEnergyResult,
    NetWorkResult,
    PotentialEnergyResult,
    PowerKind,
    PowerResult,
    PumpingPowerResult,
    Watts,
    WorkEnergyResult,
    WorkEnergySolveError,
    WorkResult,
)


def _known(value: object, name: str) -> float:
    if isinstance(value, UnknownValue):
        raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, f"unknown {name}")
    numeric = getattr(value, "value", None)
    if isinstance(numeric, bool) or not isinstance(numeric, (int, float)):
        raise ValueError(f"{name} has an invalid authored type")
    return float(numeric)


def _invalid(message: str) -> ValidationResult:
    return ValidationResult(False, (message,))


@dataclass(frozen=True, slots=True)
class WorkEnergySolver:
    """Stateless numerical authority; an optional scenario scopes future callers."""

    scenario: WorkEnergyScenario | None = None

    def __post_init__(self) -> None:
        if self.scenario is not None and not isinstance(self.scenario, WorkEnergyScenario):
            raise ValueError("scenario must be WorkEnergyScenario or None")

    def work_by_force(self, contribution: WorkContribution) -> WorkResult:
        if not isinstance(contribution, WorkContribution):
            raise ValueError("contribution must be WorkContribution")
        if (
            contribution.contact is not None
            and not contribution.contact.maintained_over_displacement
        ):
            raise WorkEnergySolveError(
                FailureReason.UNSUPPORTED,
                "contact force applicability is not maintained over the displacement",
            )
        force = _known(contribution.force_magnitude, "force magnitude")
        displacement = _known(contribution.displacement, "displacement")
        angle = _known(contribution.angle, "force-displacement angle")
        cosine = cardinal_cosine(angle)
        value = operation(
            lambda: force * displacement * cosine,
            "work calculation overflow",
        )
        return WorkResult(contribution.identifier, SignedEnergy(value))

    def work(self, contribution: WorkContribution) -> WorkResult:
        return self.work_by_force(contribution)

    def net_work(self, authored: NetWorkInput) -> NetWorkResult:
        if not isinstance(authored, NetWorkInput):
            raise ValueError("authored net work must be NetWorkInput")
        results = tuple(self.work_by_force(item) for item in authored.contributions)
        value = total(tuple(item.work.value for item in results))
        return NetWorkResult(results, SignedEnergy(value))

    def along_plane_work(self, authored: AlongPlaneWorkInput) -> AlongPlaneWorkResult:
        if not isinstance(authored, AlongPlaneWorkInput):
            raise ValueError("authored along-plane input must be AlongPlaneWorkInput")
        force = _known(authored.resultant_force, "along-plane resultant force")
        displacement = _known(authored.displacement, "along-plane displacement")
        value = operation(lambda: force * displacement, "along-plane work overflow")
        from ..work_energy_power import Displacement, SignedForce

        return AlongPlaneWorkResult(
            SignedForce(force), Displacement(displacement), SignedEnergy(value)
        )

    def kinetic_energy(self, state: KineticState) -> KineticEnergyResult:
        if not isinstance(state, KineticState):
            raise ValueError("state must be KineticState")
        if isinstance(state.mass, UnknownValue) or isinstance(state.speed, UnknownValue):
            raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "mass or speed is unknown")
        state_mass = state.mass
        state_speed = state.speed
        assert isinstance(state_mass, Mass) and isinstance(state_speed, Speed)
        value = operation(
            lambda: (
                0.5 * float(state_mass.value) * float(state_speed.value) * float(state_speed.value)
            ),
            "kinetic-energy calculation overflow",
        )
        return KineticEnergyResult(state.identifier, state_mass, state_speed, KineticEnergy(value))

    def potential_energy(
        self, mass: Mass | UnknownValue, state: HeightState
    ) -> PotentialEnergyResult:
        if not isinstance(state, HeightState):
            raise ValueError("height state must be HeightState")
        if isinstance(mass, UnknownValue):
            raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "mass is unknown")
        if isinstance(state.height, UnknownValue):
            raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "relative height is unknown")
        if isinstance(state.gravitational_field, UnknownValue):
            raise WorkEnergySolveError(
                FailureReason.UNDERDETERMINED, "gravitational field is unknown"
            )
        height = state.height
        field = state.gravitational_field
        assert not isinstance(height, UnknownValue)
        assert not isinstance(field, UnknownValue)
        value = operation(
            lambda: float(mass.value) * float(field.value) * float(height.value),
            "potential-energy calculation overflow",
        )
        return PotentialEnergyResult(
            state.identifier,
            state.reference_level.identifier,
            mass,
            field,
            height,
            SignedEnergy(value),
        )

    def gravitational_potential_energy(
        self, mass: Mass | UnknownValue, state: HeightState
    ) -> PotentialEnergyResult:
        return self.potential_energy(mass, state)

    def _effective_net_work(self, context: WorkEnergyContext) -> SignedEnergy:
        if not isinstance(context, WorkEnergyContext):
            raise ValueError("context must be WorkEnergyContext")
        derived: SignedEnergy | None = None
        if context.work_input is not None:
            if isinstance(context.work_input, NetWorkInput):
                derived = self.net_work(context.work_input).net_work
            else:
                derived = self.along_plane_work(context.work_input).work
        authored = context.net_work
        if isinstance(authored, SignedEnergy) and derived is not None:
            consistent(authored.value, derived.value, "authored net work disagrees with work input")
            return authored
        if isinstance(authored, SignedEnergy):
            return authored
        if derived is not None:
            return derived
        raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "net work is unknown")

    @staticmethod
    def _mass_pair(initial: KineticState, final: KineticState) -> Mass:
        if isinstance(initial.mass, UnknownValue) or isinstance(final.mass, UnknownValue):
            raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "mass is unknown")
        consistent(initial.mass.value, final.mass.value, "initial and final masses disagree")
        return initial.mass

    @staticmethod
    def _target_speed(energy: float, mass: Mass, name: str) -> float:
        if energy < -VALIDATION_TOLERANCE:
            raise WorkEnergySolveError(
                FailureReason.INCONSISTENT, f"derived {name} squared is negative"
            )
        bounded = 0.0 if abs(energy) <= VALIDATION_TOLERANCE else energy
        squared = operation(lambda: 2.0 * bounded / mass.value, f"{name} calculation overflow")
        if squared < -VALIDATION_TOLERANCE:
            raise WorkEnergySolveError(
                FailureReason.INCONSISTENT, f"derived {name} squared is negative"
            )
        return operation(lambda: sqrt(max(0.0, squared)), f"{name} calculation overflow")

    def work_energy(self, context: WorkEnergyContext) -> WorkEnergyResult:
        if not isinstance(context, WorkEnergyContext):
            raise ValueError("context must be WorkEnergyContext")
        net_work = self._effective_net_work(context)
        mass = self._mass_pair(context.initial_state, context.final_state)
        initial_known = not isinstance(context.initial_state.speed, UnknownValue)
        final_known = not isinstance(context.final_state.speed, UnknownValue)
        if not initial_known and not final_known:
            raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "both speeds are unknown")
        initial = context.initial_state
        final = context.final_state
        if initial_known and final_known:
            initial_ke = self.kinetic_energy(initial).kinetic_energy
            final_ke = self.kinetic_energy(final).kinetic_energy
            delta = operation(
                lambda: final_ke.value - initial_ke.value,
                "kinetic-energy change overflow",
            )
            consistent(net_work.value, delta, "net work disagrees with kinetic-energy change")
        elif not final_known:
            initial_ke = self.kinetic_energy(initial).kinetic_energy
            target = operation(
                lambda: initial_ke.value + net_work.value, "final kinetic energy overflow"
            )
            speed = self._target_speed(target, mass, "final speed")
            final = replace(final, mass=mass, speed=Speed(speed))
            final_ke = self.kinetic_energy(final).kinetic_energy
        else:
            final_ke = self.kinetic_energy(final).kinetic_energy
            target = operation(
                lambda: final_ke.value - net_work.value, "initial kinetic energy overflow"
            )
            speed = self._target_speed(target, mass, "initial speed")
            initial = replace(initial, mass=mass, speed=Speed(speed))
            initial_ke = self.kinetic_energy(initial).kinetic_energy
        return WorkEnergyResult(initial, final, net_work, initial_ke, final_ke)

    def mechanical_energy(self, context: MechanicalEnergyContext) -> MechanicalEnergyResult:
        if not isinstance(context, MechanicalEnergyContext):
            raise ValueError("context must be MechanicalEnergyContext")
        mass = self._mass_pair(context.initial_state, context.final_state)
        if isinstance(context.initial_height.gravitational_field, UnknownValue) or isinstance(
            context.final_height.gravitational_field, UnknownValue
        ):
            raise WorkEnergySolveError(
                FailureReason.UNDERDETERMINED, "gravitational field is unknown"
            )
        consistent(
            context.initial_height.gravitational_field.value,
            context.final_height.gravitational_field.value,
            "initial and final gravitational fields disagree",
        )
        initial_field = context.initial_height.gravitational_field
        final_field = context.final_height.gravitational_field
        assert isinstance(initial_field, GravitationalFieldMagnitude)
        assert isinstance(final_field, GravitationalFieldMagnitude)
        initial_speed_unknown = isinstance(context.initial_state.speed, UnknownValue)
        final_speed_unknown = isinstance(context.final_state.speed, UnknownValue)
        initial_height_unknown = isinstance(context.initial_height.height, UnknownValue)
        final_height_unknown = isinstance(context.final_height.height, UnknownValue)
        unknowns = sum(
            (
                initial_speed_unknown,
                final_speed_unknown,
                initial_height_unknown,
                final_height_unknown,
            )
        )
        nonconservative = context.non_conservative_work
        if unknowns > 1:
            raise WorkEnergySolveError(
                FailureReason.UNDERDETERMINED, "multiple mechanical-energy unknowns"
            )
        if unknowns == 1 and isinstance(nonconservative, UnknownValue):
            raise WorkEnergySolveError(FailureReason.UNDERDETERMINED, "energy transfer is unknown")
        initial = context.initial_state
        final = context.final_state
        initial_height = context.initial_height
        final_height = context.final_height
        if not initial_speed_unknown:
            initial_ke = self.kinetic_energy(initial).kinetic_energy
        else:
            initial_ke = None
        if not final_speed_unknown:
            final_ke = self.kinetic_energy(final).kinetic_energy
        else:
            final_ke = None
        if not initial_height_unknown:
            initial_pe = self.potential_energy(mass, initial_height).potential_energy
        else:
            initial_pe = None
        if not final_height_unknown:
            final_pe = self.potential_energy(mass, final_height).potential_energy
        else:
            final_pe = None
        if unknowns == 1:
            assert isinstance(nonconservative, SignedEnergy)
            if final_speed_unknown:
                assert initial_ke is not None and initial_pe is not None and final_pe is not None
                known_initial_ke = initial_ke
                known_initial_pe = initial_pe
                known_final_pe = final_pe
                target = operation(
                    lambda: (
                        float(known_initial_ke.value)
                        + float(known_initial_pe.value)
                        + float(nonconservative.value)
                        - float(known_final_pe.value)
                    ),
                    "final kinetic energy overflow",
                )
                speed = self._target_speed(target, mass, "final speed")
                from ..work_energy_power import Speed

                final = replace(final, speed=Speed(speed))
                final_ke = self.kinetic_energy(final).kinetic_energy
            elif initial_speed_unknown:
                assert final_ke is not None and initial_pe is not None and final_pe is not None
                known_final_ke = final_ke
                known_initial_pe = initial_pe
                known_final_pe = final_pe
                target = operation(
                    lambda: (
                        float(known_final_ke.value)
                        + float(known_final_pe.value)
                        - float(nonconservative.value)
                        - float(known_initial_pe.value)
                    ),
                    "initial kinetic energy overflow",
                )
                speed = self._target_speed(target, mass, "initial speed")
                from ..work_energy_power import Speed

                initial = replace(initial, speed=Speed(speed))
                initial_ke = self.kinetic_energy(initial).kinetic_energy
            elif final_height_unknown:
                assert initial_ke is not None and initial_pe is not None and final_ke is not None
                known_initial_ke = initial_ke
                known_initial_pe = initial_pe
                known_final_ke = final_ke
                target = operation(
                    lambda: (
                        float(known_initial_ke.value)
                        + float(known_initial_pe.value)
                        + float(nonconservative.value)
                        - float(known_final_ke.value)
                    ),
                    "final potential energy overflow",
                )
                height = operation(
                    lambda: target / (float(mass.value) * float(final_field.value)),
                    "final height calculation overflow",
                )
                from ..work_energy_power import RelativeHeight

                final_height = replace(final_height, height=RelativeHeight(height))
                final_pe = self.potential_energy(mass, final_height).potential_energy
            else:
                assert final_ke is not None and initial_ke is not None and final_pe is not None
                known_final_ke = final_ke
                known_final_pe = final_pe
                known_initial_ke = initial_ke
                target = operation(
                    lambda: (
                        float(known_final_ke.value)
                        + float(known_final_pe.value)
                        - float(nonconservative.value)
                        - float(known_initial_ke.value)
                    ),
                    "initial potential energy overflow",
                )
                height = operation(
                    lambda: target / (float(mass.value) * float(initial_field.value)),
                    "initial height calculation overflow",
                )
                from ..work_energy_power import RelativeHeight

                initial_height = replace(initial_height, height=RelativeHeight(height))
                initial_pe = self.potential_energy(mass, initial_height).potential_energy
        else:
            assert initial_ke is not None and final_ke is not None
            assert initial_pe is not None and final_pe is not None
            derived = SignedEnergy(
                operation(
                    lambda: final_ke.value + final_pe.value - initial_ke.value - initial_pe.value,
                    "non-conservative work overflow",
                )
            )
            if isinstance(nonconservative, SignedEnergy):
                consistent(
                    nonconservative.value,
                    derived.value,
                    "authored non-conservative work disagrees with energy change",
                )
            else:
                nonconservative = derived
        assert isinstance(nonconservative, SignedEnergy)
        assert initial_ke is not None and final_ke is not None
        assert initial_pe is not None and final_pe is not None
        return MechanicalEnergyResult(
            initial.identifier,
            final.identifier,
            initial_height.reference_level.identifier,
            initial_ke,
            final_ke,
            initial_pe,
            final_pe,
            nonconservative,
        )

    def average_power(self, authored: AveragePowerInput) -> PowerResult:
        if not isinstance(authored, AveragePowerInput):
            raise ValueError("average power input must be AveragePowerInput")
        work = _known(authored.work, "work")
        time = _known(authored.time, "time")
        return PowerResult(
            PowerKind.AVERAGE, Watts(operation(lambda: work / time, "average power overflow"))
        )

    def constant_speed_power(self, authored: ConstantSpeedPowerInput) -> PowerResult:
        if not isinstance(authored, ConstantSpeedPowerInput):
            raise ValueError("constant-speed input must be ConstantSpeedPowerInput")
        force = _known(authored.force_along_motion, "force along motion")
        speed = _known(authored.speed, "speed")
        return PowerResult(
            PowerKind.CONSTANT_SPEED,
            Watts(operation(lambda: force * speed, "constant-speed power overflow")),
        )

    def pumping_power(self, authored: PumpingPowerInput) -> PumpingPowerResult:
        if not isinstance(authored, PumpingPowerInput):
            raise ValueError("pumping power input must be PumpingPowerInput")
        rate = _known(authored.mass_flow_rate, "mass flow rate")
        lift = _known(authored.lift, "pumping lift")
        field = _known(authored.gravitational_field, "gravitational field")
        value = operation(lambda: rate * field * lift, "pumping power overflow")
        if value < 0:
            raise WorkEnergySolveError(
                FailureReason.INCONSISTENT, "minimum pumping power is negative"
            )
        return PumpingPowerResult(Watts(value))

    def validate_work_result(
        self, contribution: WorkContribution, result: WorkResult
    ) -> ValidationResult:
        if not isinstance(result, WorkResult) or result.contribution_id != getattr(
            contribution, "identifier", None
        ):
            return _invalid("work result ownership is inconsistent")
        try:
            expected = self.work_by_force(contribution)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if close(result.work.value, expected.work.value)
            else _invalid("work result disagrees with authored contribution")
        )

    def validate_net_work_result(
        self, authored: NetWorkInput, result: NetWorkResult
    ) -> ValidationResult:
        if not isinstance(result, NetWorkResult):
            return _invalid("net-work result has an invalid type")
        try:
            expected = self.net_work(authored)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        if result.contributions != expected.contributions:
            return _invalid("net-work contribution results disagree with authored input")
        return (
            ValidationResult(True, ())
            if close(result.net_work.value, expected.net_work.value)
            else _invalid("net-work result disagrees with authored input")
        )

    def validate_along_plane_result(
        self, authored: AlongPlaneWorkInput, result: AlongPlaneWorkResult
    ) -> ValidationResult:
        if not isinstance(result, AlongPlaneWorkResult):
            return _invalid("along-plane result has an invalid type")
        try:
            expected = self.along_plane_work(authored)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("along-plane result disagrees with authored input")
        )

    def validate_kinetic_energy_result(
        self, state: KineticState, result: KineticEnergyResult
    ) -> ValidationResult:
        if not isinstance(result, KineticEnergyResult):
            return _invalid("kinetic-energy result has an invalid type")
        try:
            expected = self.kinetic_energy(state)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("kinetic-energy result disagrees with authored state")
        )

    def validate_potential_energy_result(
        self, mass: Mass | UnknownValue, state: HeightState, result: PotentialEnergyResult
    ) -> ValidationResult:
        if not isinstance(result, PotentialEnergyResult):
            return _invalid("potential-energy result has an invalid type")
        try:
            expected = self.potential_energy(mass, state)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("potential-energy result disagrees with authored state")
        )

    def validate_work_energy_result(
        self, context: WorkEnergyContext, result: WorkEnergyResult
    ) -> ValidationResult:
        if not isinstance(result, WorkEnergyResult):
            return _invalid("work-energy result has an invalid type")
        try:
            expected = self.work_energy(context)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("work-energy result disagrees with authored context")
        )

    def validate_mechanical_energy_result(
        self, context: MechanicalEnergyContext, result: MechanicalEnergyResult
    ) -> ValidationResult:
        if not isinstance(result, MechanicalEnergyResult):
            return _invalid("mechanical-energy result has an invalid type")
        try:
            expected = self.mechanical_energy(context)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("mechanical-energy result disagrees with authored context")
        )

    def validate_power_result(
        self, authored: AveragePowerInput | ConstantSpeedPowerInput, result: PowerResult
    ) -> ValidationResult:
        if not isinstance(result, PowerResult):
            return _invalid("power result has an invalid type")
        try:
            expected = (
                self.average_power(authored)
                if isinstance(authored, AveragePowerInput)
                else self.constant_speed_power(authored)
            )
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("power result disagrees with authored input")
        )

    def validate_pumping_power_result(
        self, authored: PumpingPowerInput, result: PumpingPowerResult
    ) -> ValidationResult:
        if not isinstance(result, PumpingPowerResult):
            return _invalid("pumping-power result has an invalid type")
        try:
            expected = self.pumping_power(authored)
        except (ValueError, WorkEnergySolveError) as error:
            return _invalid(str(error))
        return (
            ValidationResult(True, ())
            if result == expected
            else _invalid("pumping-power result disagrees with authored input")
        )


__all__ = ["WorkEnergySolver"]
