"""Analytical and boundary tests for the authoritative M5 solver."""

import ast
import dataclasses
from pathlib import Path

import pytest

from assessment_platform.domains.physical_sciences.mechanics.work_energy_power import (
    AlongPlaneWorkInput,
    AngleDegrees,
    AveragePowerInput,
    ConstantSpeedPowerInput,
    ContactCondition,
    Displacement,
    EnergyState,
    ForceMagnitude,
    GravitationalFieldMagnitude,
    HeightState,
    KineticState,
    Mass,
    MassFlowRate,
    MechanicalEnergyContext,
    NetWorkInput,
    PumpingPowerInput,
    ReferenceLevel,
    RelativeHeight,
    SignedEnergy,
    SignedForce,
    Speed,
    SurfaceContext,
    TimeInterval,
    UnknownValue,
    WorkContribution,
    WorkEnergyContext,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power_solver import (
    VALIDATION_TOLERANCE,
    FailureReason,
    PowerKind,
    Watts,
    WorkEnergySolveError,
    WorkEnergySolver,
)

SOLVER = WorkEnergySolver()


def contribution(identifier: str = "force", **overrides: object) -> WorkContribution:
    values: dict[str, object] = {
        "identifier": identifier,
        "force_magnitude": ForceMagnitude(10),
        "displacement": Displacement(2),
        "angle": AngleDegrees(0),
    }
    values.update(overrides)
    return WorkContribution(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("angle, expected", [(0, 20), (90, 0), (180, -20), (60, 10)])
def test_work_by_force_preserves_sign_and_cardinal_angles(angle: float, expected: float) -> None:
    result = SOLVER.work_by_force(contribution(angle=AngleDegrees(angle)))
    assert result.work.value == pytest.approx(expected)
    if angle == 90:
        assert result.work.value == 0.0


def test_work_zero_force_and_displacement_are_zero() -> None:
    assert SOLVER.work_by_force(contribution(force_magnitude=ForceMagnitude(0))).work.value == 0.0
    assert SOLVER.work_by_force(contribution(displacement=Displacement(0))).work.value == 0.0


@pytest.mark.parametrize("field", ["force_magnitude", "displacement", "angle"])
def test_unknown_direct_work_input_is_underdetermined(field: str) -> None:
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.work_by_force(contribution(**{field: UnknownValue.UNKNOWN}))
    assert error.value.reason is FailureReason.UNDERDETERMINED


def test_contact_not_maintained_is_unsupported() -> None:
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.work_by_force(contribution(contact=ContactCondition(False)))
    assert error.value.reason is FailureReason.UNSUPPORTED


def test_net_work_is_ordered_and_does_not_mutate_input() -> None:
    authored = NetWorkInput(
        (
            contribution("positive"),
            contribution("negative", angle=AngleDegrees(180)),
            contribution("perpendicular", angle=AngleDegrees(90)),
        )
    )
    before = dataclasses.asdict(authored)
    result = SOLVER.net_work(authored)
    assert tuple(item.contribution_id for item in result.contributions) == (
        "positive",
        "negative",
        "perpendicular",
    )
    assert result.net_work.value == 0.0
    assert dataclasses.asdict(authored) == before


def test_net_work_unknown_contribution_does_not_return_partial_result() -> None:
    authored = NetWorkInput(
        (contribution(), contribution("unknown", displacement=UnknownValue.UNKNOWN))
    )
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.net_work(authored)
    assert error.value.reason is FailureReason.UNDERDETERMINED


@pytest.mark.parametrize("force, displacement, expected", [(4, 3, 12), (-4, 3, -12), (0, 3, 0)])
def test_along_plane_work_is_signed_scalar(
    force: float, displacement: float, expected: float
) -> None:
    result = SOLVER.along_plane_work(
        AlongPlaneWorkInput(SignedForce(force), Displacement(displacement))
    )
    assert result.work.value == expected


def test_along_plane_unknowns_are_underdetermined() -> None:
    with pytest.raises(WorkEnergySolveError) as force_error:
        SOLVER.along_plane_work(AlongPlaneWorkInput(UnknownValue.UNKNOWN, Displacement(2)))
    with pytest.raises(WorkEnergySolveError) as displacement_error:
        SOLVER.along_plane_work(AlongPlaneWorkInput(SignedForce(2), UnknownValue.UNKNOWN))
    assert force_error.value.reason is FailureReason.UNDERDETERMINED
    assert displacement_error.value.reason is FailureReason.UNDERDETERMINED


def test_kinetic_energy_uses_speed_magnitude_only() -> None:
    state = KineticState("initial", EnergyState.INITIAL, Mass(4), Speed(3))
    assert SOLVER.kinetic_energy(state).kinetic_energy.value == 18.0
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.kinetic_energy(
            KineticState("unknown", EnergyState.INITIAL, UnknownValue.UNKNOWN, Speed(3))
        )
    assert error.value.reason is FailureReason.UNDERDETERMINED


def test_potential_energy_uses_authored_height_and_field() -> None:
    level = ReferenceLevel("ground")
    for height, expected in [(2, 39.2), (0, 0), (-2, -39.2)]:
        state = HeightState(
            "height",
            EnergyState.INITIAL,
            level,
            RelativeHeight(height),
            GravitationalFieldMagnitude(9.8),
        )
        assert SOLVER.potential_energy(Mass(2), state).potential_energy.value == expected
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.potential_energy(
            Mass(2),
            HeightState(
                "unknown", EnergyState.INITIAL, level, RelativeHeight(1), UnknownValue.UNKNOWN
            ),
        )
    assert error.value.reason is FailureReason.UNDERDETERMINED


def kinetic(identifier: str, state: EnergyState, speed: object) -> KineticState:
    return KineticState(identifier, state, Mass(2), speed)  # type: ignore[arg-type]


def height(identifier: str, state: EnergyState, value: object, field: object = 9.8) -> HeightState:
    authored_field = (
        field
        if isinstance(field, (GravitationalFieldMagnitude, UnknownValue))
        else GravitationalFieldMagnitude(field)  # type: ignore[arg-type]
    )
    return HeightState(
        identifier,
        state,
        ReferenceLevel("ground"),
        value,  # type: ignore[arg-type]
        authored_field,
    )


def test_work_energy_derives_and_validates_net_work() -> None:
    context = WorkEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(3)),
        kinetic("f", EnergyState.FINAL, Speed(5)),
        SignedEnergy(16),
    )
    result = SOLVER.work_energy(context)
    assert result.net_work.value == 16
    assert result.final_kinetic_energy.value - result.initial_kinetic_energy.value == 16
    assert SOLVER.validate_work_energy_result(context, result).valid
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.work_energy(dataclasses.replace(context, net_work=SignedEnergy(15)))
    assert error.value.reason is FailureReason.INCONSISTENT


def test_work_energy_solves_one_unknown_speed_without_mutation() -> None:
    final = kinetic("f", EnergyState.FINAL, UnknownValue.UNKNOWN)
    context = WorkEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(3)), final, SignedEnergy(16)
    )
    result = SOLVER.work_energy(context)
    assert result.final_state.speed == Speed(5)
    assert isinstance(final.speed, UnknownValue)
    initial_unknown = WorkEnergyContext(
        kinetic("i", EnergyState.INITIAL, UnknownValue.UNKNOWN),
        kinetic("f", EnergyState.FINAL, Speed(5)),
        SignedEnergy(16),
    )
    assert SOLVER.work_energy(initial_unknown).initial_state.speed == Speed(3)


def test_work_energy_reconciles_work_input_and_authored_net_work() -> None:
    context = WorkEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(0)),
        kinetic("f", EnergyState.FINAL, Speed(10)),
        SignedEnergy(20),
        NetWorkInput((contribution(),)),
    )
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.work_energy(context)
    assert error.value.reason is FailureReason.INCONSISTENT


def test_work_energy_rejects_negative_derived_speed_squared() -> None:
    context = WorkEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(2)),
        kinetic("f", EnergyState.FINAL, UnknownValue.UNKNOWN),
        SignedEnergy(-5),
    )
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.work_energy(context)
    assert error.value.reason is FailureReason.INCONSISTENT


def test_mechanical_energy_derives_nonconservative_work_and_solves_speed() -> None:
    context = MechanicalEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(0)),
        kinetic("f", EnergyState.FINAL, Speed(2)),
        height("h0", EnergyState.INITIAL, RelativeHeight(0)),
        height("h1", EnergyState.FINAL, RelativeHeight(0)),
    )
    assert SOLVER.mechanical_energy(context).non_conservative_work.value == 4
    unknown_final = MechanicalEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(0)),
        kinetic("f", EnergyState.FINAL, UnknownValue.UNKNOWN),
        height("h0", EnergyState.INITIAL, RelativeHeight(0)),
        height("h1", EnergyState.FINAL, RelativeHeight(0)),
        SignedEnergy(4),
    )
    assert SOLVER.mechanical_energy(unknown_final).final_kinetic_energy.value == 4


def test_mechanical_energy_rejects_mismatched_fields_and_work() -> None:
    with pytest.raises(WorkEnergySolveError) as field_error:
        SOLVER.mechanical_energy(
            MechanicalEnergyContext(
                kinetic("i", EnergyState.INITIAL, Speed(0)),
                kinetic("f", EnergyState.FINAL, Speed(0)),
                height("h0", EnergyState.INITIAL, RelativeHeight(0), 9.8),
                height("h1", EnergyState.FINAL, RelativeHeight(0), 9.81),
            )
        )
    assert field_error.value.reason is FailureReason.INCONSISTENT
    context = MechanicalEnergyContext(
        kinetic("i", EnergyState.INITIAL, Speed(0)),
        kinetic("f", EnergyState.FINAL, Speed(2)),
        height("h0", EnergyState.INITIAL, RelativeHeight(0)),
        height("h1", EnergyState.FINAL, RelativeHeight(0)),
        SignedEnergy(5),
    )
    with pytest.raises(WorkEnergySolveError) as work_error:
        SOLVER.mechanical_energy(context)
    assert work_error.value.reason is FailureReason.INCONSISTENT


def test_power_families_preserve_sign_and_pumping_is_nonnegative() -> None:
    assert (
        SOLVER.average_power(AveragePowerInput(SignedEnergy(20), TimeInterval(4))).power.value == 5
    )
    assert (
        SOLVER.average_power(AveragePowerInput(SignedEnergy(-20), TimeInterval(4))).power.value
        == -5
    )
    constant = SOLVER.constant_speed_power(
        ConstantSpeedPowerInput(SignedForce(-4), Speed(3), SurfaceContext.INCLINED)
    )
    assert constant.kind is PowerKind.CONSTANT_SPEED and constant.power.value == -12
    pumping = SOLVER.pumping_power(
        PumpingPowerInput(MassFlowRate(2), Displacement(5), GravitationalFieldMagnitude(10))
    )
    assert pumping.power.value == 100 and isinstance(pumping.power, Watts)


@pytest.mark.parametrize(
    "operation, authored",
    [
        (SOLVER.average_power, AveragePowerInput(UnknownValue.UNKNOWN, TimeInterval(1))),
        (
            SOLVER.constant_speed_power,
            ConstantSpeedPowerInput(UnknownValue.UNKNOWN, Speed(1), SurfaceContext.HORIZONTAL),
        ),
        (
            SOLVER.pumping_power,
            PumpingPowerInput(
                UnknownValue.UNKNOWN, Displacement(1), GravitationalFieldMagnitude(10)
            ),
        ),
    ],
)
def test_power_unknowns_are_underdetermined(operation, authored) -> None:
    with pytest.raises(WorkEnergySolveError) as error:
        operation(authored)
    assert error.value.reason is FailureReason.UNDERDETERMINED


def test_checked_arithmetic_maps_overflow_to_numerical_range() -> None:
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.work_by_force(
            WorkContribution("huge", ForceMagnitude(1e308), Displacement(1e308), AngleDegrees(0))
        )
    assert error.value.reason is FailureReason.NUMERICAL_RANGE
    with pytest.raises(WorkEnergySolveError) as error:
        SOLVER.kinetic_energy(KineticState("huge", EnergyState.INITIAL, Mass(1e308), Speed(1e308)))
    assert error.value.reason is FailureReason.NUMERICAL_RANGE


def test_tampered_results_fail_validation_and_results_are_frozen() -> None:
    authored = contribution()
    result = SOLVER.work_by_force(authored)
    assert not SOLVER.validate_work_result(
        authored, dataclasses.replace(result, work=SignedEnergy(999))
    ).valid
    state = kinetic("i", EnergyState.INITIAL, Speed(3))
    energy = SOLVER.kinetic_energy(state)
    tampered = dataclasses.replace(energy, kinetic_energy=type(energy.kinetic_energy)(999))
    assert not SOLVER.validate_kinetic_energy_result(state, tampered).valid
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.work = SignedEnergy(2)  # type: ignore[misc]


def test_all_result_validation_boundaries_reject_tampering() -> None:
    along = AlongPlaneWorkInput(SignedForce(4), Displacement(3))
    along_result = SOLVER.along_plane_work(along)
    assert SOLVER.validate_along_plane_result(along, along_result).valid
    assert not SOLVER.validate_along_plane_result(
        along, dataclasses.replace(along_result, work=SignedEnergy(1))
    ).valid
    level = ReferenceLevel("ground")
    height_state = HeightState(
        "h", EnergyState.INITIAL, level, RelativeHeight(2), GravitationalFieldMagnitude(9.8)
    )
    potential = SOLVER.potential_energy(Mass(2), height_state)
    assert SOLVER.validate_potential_energy_result(Mass(2), height_state, potential).valid
    assert not SOLVER.validate_potential_energy_result(
        Mass(2), height_state, dataclasses.replace(potential, potential_energy=SignedEnergy(1))
    ).valid
    average = AveragePowerInput(SignedEnergy(20), TimeInterval(4))
    average_result = SOLVER.average_power(average)
    assert SOLVER.validate_power_result(average, average_result).valid
    assert not SOLVER.validate_power_result(
        average, dataclasses.replace(average_result, power=Watts(1))
    ).valid
    pumping = PumpingPowerInput(MassFlowRate(2), Displacement(5), GravitationalFieldMagnitude(10))
    pumping_result = SOLVER.pumping_power(pumping)
    assert SOLVER.validate_pumping_power_result(pumping, pumping_result).valid
    assert not SOLVER.validate_pumping_power_result(
        pumping, dataclasses.replace(pumping_result, power=Watts(1))
    ).valid


def test_solver_package_has_no_forbidden_dependencies() -> None:
    package = (
        Path(__file__).parents[2]
        / "src"
        / "assessment_platform"
        / "domains"
        / "physical_sciences"
        / "mechanics"
        / "work_energy_power_solver"
    )
    forbidden = (
        "fastapi",
        "pydantic",
        "application",
        "rendering",
        "newton_solver",
        "momentum_impulse_solver",
        "vertical_projectile_solver",
    )
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(not alias.name.lower().startswith(forbidden) for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                assert not node.module.lower().startswith(forbidden)


def test_tolerance_is_internal_and_stable() -> None:
    assert VALIDATION_TOLERANCE == 1e-9
