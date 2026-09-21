"""Focused safety and authored-geometry checks for the M5 renderer."""
# ruff: noqa: E501

from __future__ import annotations

from xml.etree import ElementTree

import pytest

from assessment_platform.core.models import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    WorkEnergyGenerationFamily,
    WorkEnergyGenerationInput,
    WorkEnergyProblemFactory,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power import (
    AlongPlaneWorkInput,
    AngleDegrees,
    Displacement,
    EnergyState,
    ForceMagnitude,
    KineticState,
    NetWorkInput,
    SignedForce,
    UnknownValue,
    WorkContribution,
    WorkEnergyScenario,
)
from assessment_platform.rendering.svg.work_energy_power import (
    WorkEnergyDiagramKind,
    WorkEnergyRenderOptions,
    WorkEnergySvgRenderer,
    WorkEnergyVisibilityOptions,
)


def contribution(identifier: str = "force<&\"'") -> WorkContribution:
    return WorkContribution(identifier, ForceMagnitude(12), Displacement(3), AngleDegrees(60))


def test_deterministic_accessible_safe_svg_and_escaping() -> None:
    scenario = WorkEnergyScenario("scenario<&\"'", work_inputs=(NetWorkInput((contribution(),)),))
    options = WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.WORK_CONTRIBUTIONS)
    first = WorkEnergySvgRenderer().render(scenario, options).markup
    assert first == WorkEnergySvgRenderer().render(scenario, options).markup
    root = ElementTree.fromstring(first)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["role"] == "img"
    assert root.attrib["aria-labelledby"]
    assert root.find("{http://www.w3.org/2000/svg}title") is not None
    assert root.find("{http://www.w3.org/2000/svg}desc") is not None
    assert "&lt;" in first and "&amp;" in first
    lowered = first.lower()
    assert all(token not in lowered for token in ("<script", "foreignobject", "javascript:", "onload=", "onclick="))
    assert 'id="wep-force-' in first


def test_dimensions_and_explicit_numeric_visibility() -> None:
    scenario = WorkEnergyScenario("diagram", work_inputs=(NetWorkInput((contribution("force"),)),))
    with pytest.raises(ValueError):
        WorkEnergyRenderOptions(width=419)
    hidden = WorkEnergySvgRenderer().render(
        scenario, WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.WORK_CONTRIBUTIONS)
    ).markup
    assert "12 N" not in hidden and "60°" not in hidden
    visible = WorkEnergySvgRenderer().render(
        scenario,
        WorkEnergyRenderOptions(
            diagram_kind=WorkEnergyDiagramKind.WORK_CONTRIBUTIONS,
            visibility=WorkEnergyVisibilityOptions(show_numeric_values=True, show_angle_labels=True),
        ),
    ).markup
    assert "12" in visible and "60" in visible


@pytest.mark.parametrize("angle, expected", [(0, ('x2="339.000"', 'y2="105.000"')), (90, ('x2="275.000"', 'y2="41.000"')), (180, ('x2="211.000"', 'y2="105.000"'))])
def test_authored_angle_controls_direction_with_fixed_length(angle: int, expected: tuple[str, str]) -> None:
    item = WorkContribution("force", ForceMagnitude(37.125), Displacement(99), AngleDegrees(angle))
    scenario = WorkEnergyScenario("diagram", work_inputs=(NetWorkInput((item,)),))
    svg = WorkEnergySvgRenderer().render(scenario).markup
    assert expected[0] in svg and expected[1] in svg
    assert "37.125" not in svg


def test_unknown_angle_and_unknown_motion_are_not_guessed() -> None:
    item = WorkContribution("force", ForceMagnitude(1), Displacement(1), UnknownValue.UNKNOWN)
    kinetic = KineticState("initial", EnergyState.INITIAL, UnknownValue.UNKNOWN, UnknownValue.UNKNOWN)
    scenario = WorkEnergyScenario("diagram", work_inputs=(NetWorkInput((item,)),), kinetic_states=(kinetic,))
    assert "force direction ?" in WorkEnergySvgRenderer().render(
        scenario, WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.WORK_CONTRIBUTIONS)
    ).markup
    motion = WorkEnergySvgRenderer().render(
        scenario, WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.MOTION_STATES)
    ).markup
    assert "speed" in motion and "?" in motion and "0 m/s" not in motion


def test_signed_along_plane_direction_and_zero() -> None:
    positive = WorkEnergyScenario("positive", work_inputs=(AlongPlaneWorkInput(SignedForce(2), Displacement(3)),))
    negative = WorkEnergyScenario("negative", work_inputs=(AlongPlaneWorkInput(SignedForce(-2), Displacement(3)),))
    zero = WorkEnergyScenario("zero", work_inputs=(AlongPlaneWorkInput(SignedForce(0), Displacement(3)),))
    renderer = WorkEnergySvgRenderer()
    p = renderer.render(positive, WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.ALONG_PLANE)).markup
    n = renderer.render(negative, WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.ALONG_PLANE)).markup
    z = renderer.render(zero, WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.ALONG_PLANE)).markup
    assert 'x1="430.000" y1="245.000" x2="494.000"' in p
    assert 'x1="494.000" y1="245.000" x2="430.000"' in n
    assert "resultant force = 0" in z


def test_generated_family_corpus_and_average_power_no_visual() -> None:
    factory = WorkEnergyProblemFactory()
    mapping = {
        WorkEnergyGenerationFamily.WORK_BY_FORCE: WorkEnergyDiagramKind.WORK_CONTRIBUTIONS,
        WorkEnergyGenerationFamily.NET_WORK: WorkEnergyDiagramKind.WORK_CONTRIBUTIONS,
        WorkEnergyGenerationFamily.ALONG_PLANE_WORK: WorkEnergyDiagramKind.ALONG_PLANE,
        WorkEnergyGenerationFamily.KINETIC_ENERGY: WorkEnergyDiagramKind.MOTION_STATES,
        WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY: WorkEnergyDiagramKind.HEIGHT_STATES,
        WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK: WorkEnergyDiagramKind.MOTION_STATES,
        WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED: WorkEnergyDiagramKind.MOTION_STATES,
        WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED: WorkEnergyDiagramKind.MOTION_STATES,
        WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK: WorkEnergyDiagramKind.HEIGHT_STATES,
        WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED: WorkEnergyDiagramKind.HEIGHT_STATES,
        WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER: WorkEnergyDiagramKind.CONSTANT_SPEED_SURFACE,
        WorkEnergyGenerationFamily.PUMPING_POWER: WorkEnergyDiagramKind.PUMPING,
    }
    for index, family in enumerate(WorkEnergyGenerationFamily):
        generated = factory.generate(WorkEnergyGenerationInput(GenerationSeed(700 + index), family, Difficulty.INTRODUCTORY))
        if family is WorkEnergyGenerationFamily.AVERAGE_POWER:
            assert family not in mapping
            continue
        document = WorkEnergySvgRenderer().render(
            generated.scenario, WorkEnergyRenderOptions(diagram_kind=mapping[family])
        )
        ElementTree.fromstring(document.markup)
        assert document.markup == WorkEnergySvgRenderer().render(
            generated.scenario, WorkEnergyRenderOptions(diagram_kind=mapping[family])
        ).markup
        assert "javascript:" not in document.markup.lower()
