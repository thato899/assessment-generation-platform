"""Structural tests for the authored Work, Energy & Power domain."""

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
    ForceEnergyClassification,
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
    WorkEnergyAssumptions,
    WorkEnergyContext,
    WorkEnergyScenario,
)


@pytest.mark.parametrize(
    "factory, values",
    [
        (Mass, (True, "2", float("nan"), float("inf"))),
        (ForceMagnitude, (-1, True, "2", float("nan"))),
        (Displacement, (-1, True, "2", float("inf"))),
        (Speed, (-1, True, "2", float("nan"))),
        (TimeInterval, (0, -1, True, "2", float("inf"))),
        (MassFlowRate, (0, -1, True, "2", float("nan"))),
        (GravitationalFieldMagnitude, (0, -1, True, "2", float("inf"))),
        (AngleDegrees, (-1, 181, True, "2", float("nan"))),
    ],
)
def test_value_objects_reject_invalid_numeric_inputs(factory, values):
    for value in values:
        with pytest.raises(ValueError):
            factory(value)


def test_value_objects_normalize_numeric_inputs_and_preserve_semantics():
    assert Mass(2).value == 2.0
    assert ForceMagnitude(0).value == 0.0
    assert SignedForce(-2).value == -2.0
    assert Displacement(0).value == 0.0
    assert Speed(0).value == 0.0
    assert RelativeHeight(-3).value == -3.0
    assert SignedEnergy(-4).value == -4.0
    assert UnknownValue.UNKNOWN != 0


def test_angle_bounds_are_authored_without_trigonometry():
    assert AngleDegrees(0).value == 0.0
    assert AngleDegrees(90).value == 90.0
    assert AngleDegrees(180).value == 180.0
    assert AngleDegrees(37.5).value == 37.5


def contribution(identifier: str = "push", **overrides: object) -> WorkContribution:
    values: dict[str, object] = {
        "identifier": identifier,
        "force_magnitude": ForceMagnitude(10),
        "displacement": Displacement(2),
        "angle": AngleDegrees(0),
    }
    values.update(overrides)
    return WorkContribution(**values)  # type: ignore[arg-type]


def test_work_contributions_are_ordered_authored_facts_and_do_not_store_work():
    first = contribution("first")
    second = contribution("second", angle=UnknownValue.UNKNOWN)
    model = NetWorkInput([second, first])
    assert tuple(item.identifier for item in model.contributions) == ("second", "first")
    assert model.contributions[1].force_magnitude == ForceMagnitude(10)
    assert not hasattr(first, "work")
    with pytest.raises(ValueError, match="unique"):
        NetWorkInput((first, first))
    with pytest.raises(ValueError, match="ordered"):
        NetWorkInput({first})  # type: ignore[arg-type]


def test_work_semantic_classification_and_contact_are_explicit():
    model = contribution(
        classification=ForceEnergyClassification.NON_CONSERVATIVE,
        contact=ContactCondition(True),
    )
    assert model.classification is ForceEnergyClassification.NON_CONSERVATIVE
    assert model.contact == ContactCondition(True)
    with pytest.raises(ValueError):
        ContactCondition(1)  # type: ignore[arg-type]


def test_along_plane_input_is_explicit_scalar_data():
    model = AlongPlaneWorkInput(SignedForce(-4), Displacement(3))
    assert model.resultant_force == SignedForce(-4)
    assert model.displacement == Displacement(3)
    assert not hasattr(model, "work")


def test_states_reference_levels_and_unknowns_remain_structural():
    level = ReferenceLevel("ground")
    initial = KineticState("initial", EnergyState.INITIAL, Mass(2), UnknownValue.UNKNOWN)
    final = KineticState("final", EnergyState.FINAL, Mass(2), Speed(4))
    initial_height = HeightState(
        "h0", EnergyState.INITIAL, level, RelativeHeight(-1), GravitationalFieldMagnitude(9.8)
    )
    final_height = HeightState(
        "h1", EnergyState.FINAL, level, UnknownValue.UNKNOWN, GravitationalFieldMagnitude(9.8)
    )
    context = MechanicalEnergyContext(initial, final, initial_height, final_height)
    assert context.non_conservative_work is UnknownValue.UNKNOWN
    assert initial.speed is UnknownValue.UNKNOWN
    with pytest.raises(ValueError):
        MechanicalEnergyContext(
            initial,
            final,
            initial_height,
            dataclasses.replace(final_height, reference_level=ReferenceLevel("other")),
        )


def test_work_energy_context_keeps_multiple_unknowns_without_solving():
    initial = KineticState("i", EnergyState.INITIAL, UnknownValue.UNKNOWN, Speed(0))
    final = KineticState("f", EnergyState.FINAL, UnknownValue.UNKNOWN, UnknownValue.UNKNOWN)
    context = WorkEnergyContext(
        initial,
        final,
        UnknownValue.UNKNOWN,
        NetWorkInput((contribution(force_magnitude=UnknownValue.UNKNOWN),)),
    )
    assert context.net_work is UnknownValue.UNKNOWN


def test_power_inputs_require_authored_units_and_no_efficiency_field():
    average = AveragePowerInput(SignedEnergy(20), TimeInterval(4))
    constant = ConstantSpeedPowerInput(SignedForce(10), Speed(2), SurfaceContext.INCLINED)
    pump = PumpingPowerInput(MassFlowRate(3), Displacement(10), GravitationalFieldMagnitude(9.8))
    assert average.time == TimeInterval(4)
    assert constant.surface is SurfaceContext.INCLINED
    assert pump.mass_flow_rate == MassFlowRate(3)
    assert not hasattr(pump, "efficiency")


def test_scenario_validates_references_and_is_immutable():
    level = ReferenceLevel("ground")
    height = HeightState(
        "h", EnergyState.INITIAL, level, RelativeHeight(0), GravitationalFieldMagnitude(9.8)
    )
    scenario = WorkEnergyScenario("scenario", reference_levels=(level,), height_states=(height,))
    assert scenario.height_states == (height,)
    with pytest.raises(AttributeError):
        scenario.identifier = "other"  # type: ignore[misc]
    with pytest.raises(ValueError, match="unknown reference"):
        WorkEnergyScenario("bad", height_states=(height,))


def test_assumptions_do_not_infer_irrelevant_flags():
    assumptions = WorkEnergyAssumptions(near_earth_field=True)
    assert assumptions.near_earth_field is True
    assert assumptions.constant_speed is None
    with pytest.raises(ValueError):
        WorkEnergyAssumptions(constant_mass=1)  # type: ignore[arg-type]


def test_domain_package_has_no_framework_or_solver_imports():
    package = (
        Path(__file__).parents[2]
        / "src"
        / "assessment_platform"
        / "domains"
        / "physical_sciences"
        / "mechanics"
        / "work_energy_power"
    )
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in {"dataclasses", "enum", "math"} for alias in node.names)
            elif (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module != "__future__"
            ):
                assert node.module in {"dataclasses", "enum", "math"}
