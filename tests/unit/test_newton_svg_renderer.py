from __future__ import annotations

from xml.etree import ElementTree

import pytest

from assessment_platform.core.models import Difficulty, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics import (
    DEFAULT_NEWTON_PROBLEM_FACTORY,
    NewtonGenerationFamily,
    NewtonGenerationInput,
)
from assessment_platform.domains.physical_sciences.mechanics.newtons_laws import (
    BodyReference,
    CartesianCoordinates,
    CartesianDirection,
    Contact,
    EnvironmentReference,
    Force,
    ForceKind,
    ForceVector,
    Friction,
    FrictionRegime,
    Kilograms,
    NewtonAssumptions,
    NewtonBody,
    Newtons,
    NewtonScenario,
    Surface,
    SurfaceCoordinates,
    SurfaceDirection,
    SystemBoundary,
    UnknownValue,
)
from assessment_platform.rendering.svg.newton import (
    NewtonDiagramKind,
    NewtonRenderOptions,
    NewtonSvgRenderer,
    NewtonVisibilityOptions,
)

ASSUMPTIONS = NewtonAssumptions(True, True, True)
EARTH = EnvironmentReference("earth")


def make_scenario(
    *,
    identifier: str = "diagram",
    axes: tuple[CartesianDirection, ...] = (CartesianDirection.RIGHT,),
    forces: tuple[Force, ...] = (),
    bodies: tuple[NewtonBody, ...] = (NewtonBody("A", Kilograms(2)),),
    surfaces: tuple[Surface, ...] = (),
    contacts: tuple[Contact, ...] = (),
    coordinates: CartesianCoordinates | SurfaceCoordinates | None = None,
) -> NewtonScenario:
    coordinates = coordinates or CartesianCoordinates(axes)
    return NewtonScenario(
        identifier=identifier,
        bodies=bodies,
        coordinates=coordinates,
        system=SystemBoundary(tuple(body.identifier for body in bodies)),
        assumptions=ASSUMPTIONS,
        environment=(EARTH,),
        forces=forces,
        surfaces=surfaces,
        contacts=contacts,
    )


def applied(identifier: str, value: Newtons | UnknownValue, target: str = "A") -> Force:
    return Force(
        identifier,
        ForceKind.APPLIED,
        target,
        EARTH,
        ForceVector(CartesianCoordinates((CartesianDirection.RIGHT,)), (value,)),
    )


def test_deterministic_valid_svg_and_accessibility() -> None:
    scenario = make_scenario(forces=(applied("push", Newtons(8)),))
    options = NewtonRenderOptions(
        visibility=NewtonVisibilityOptions(show_coordinate_axes=True),
    )
    first = NewtonSvgRenderer().render(scenario, options).markup
    assert first == NewtonSvgRenderer().render(scenario, options).markup
    root = ElementTree.fromstring(first)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.find("{http://www.w3.org/2000/svg}title") is not None
    assert root.find("{http://www.w3.org/2000/svg}desc") is not None
    assert "<script" not in first
    assert "foreignObject" not in first
    assert "javascript:" not in first


def test_cartesian_sign_and_declared_direction_change_screen_vector() -> None:
    renderer = NewtonSvgRenderer()
    right = renderer.render(make_scenario(forces=(applied("push", Newtons(3)),))).markup
    left = renderer.render(
        make_scenario(
            identifier="left",
            axes=(CartesianDirection.LEFT,),
            forces=(
                Force(
                    "push",
                    ForceKind.APPLIED,
                    "A",
                    EARTH,
                    ForceVector(CartesianCoordinates((CartesianDirection.LEFT,)), (Newtons(3),)),
                ),
            ),
        )
    ).markup
    assert 'x2="452.000"' in right
    assert 'x2="308.000"' in left


def test_two_dimensional_cartesian_mapping_and_free_body_ownership() -> None:
    coordinates = CartesianCoordinates((CartesianDirection.LEFT, CartesianDirection.DOWN))
    scenario = NewtonScenario(
        identifier="ownership",
        bodies=(NewtonBody("A", Kilograms(1)), NewtonBody("B", Kilograms(1))),
        coordinates=coordinates,
        system=SystemBoundary(("A",)),
        assumptions=ASSUMPTIONS,
        environment=(EARTH,),
        forces=(
            Force(
                "B-on-A",
                ForceKind.APPLIED,
                "A",
                BodyReference("B"),
                ForceVector(coordinates, (Newtons(2), Newtons(0))),
            ),
            Force(
                "A-on-B",
                ForceKind.APPLIED,
                "B",
                BodyReference("A"),
                ForceVector(coordinates, (Newtons(2), Newtons(0))),
            ),
        ),
    )
    a_svg = NewtonSvgRenderer().render(scenario, NewtonRenderOptions(body_id="A")).markup
    b_svg = NewtonSvgRenderer().render(scenario, NewtonRenderOptions(body_id="B")).markup
    assert "B-on-A" in a_svg and "A-on-B" not in a_svg
    assert 'id="force-B-on-A"' in a_svg
    assert 'id="force-A-on-B"' in b_svg
    assert 'id="force-B-on-A"' not in b_svg


def test_hostile_labels_are_escaped_and_ids_are_safe() -> None:
    scenario = make_scenario(identifier='x<unsafe>&"', forces=(applied('force"<&', Newtons(2)),))
    svg = NewtonSvgRenderer().render(scenario).markup
    ElementTree.fromstring(svg)
    assert "&lt;unsafe&gt;&amp;&quot;" in svg
    assert "<script" not in svg
    assert "onload=" not in svg


def test_unknown_force_is_not_zero_or_solver_derived_and_geometry_is_fixed() -> None:
    renderer = NewtonSvgRenderer()
    first = renderer.render(
        make_scenario(forces=(applied("unknown", UnknownValue.UNKNOWN),))
    ).markup
    second = renderer.render(
        make_scenario(identifier="other", forces=(applied("unknown", UnknownValue.UNKNOWN),))
    ).markup
    assert "0 N" not in first
    assert "?" in first
    assert "unknown" in first
    assert 'x2="' not in first or 'id="force-unknown"' not in first
    assert first.replace("other", "diagram") != second


def test_normal_unknown_has_structural_surface_direction_without_value() -> None:
    surface = Surface("plane", EARTH, 30)
    contact = Contact("contact", "A", "plane", Friction(FrictionRegime.NONE))
    coordinates = SurfaceCoordinates(
        "plane", (SurfaceDirection.ALONG_RIGHT, SurfaceDirection.NORMAL_OUT)
    )
    normal = Force(
        "normal",
        ForceKind.NORMAL,
        "A",
        EARTH,
        ForceVector(coordinates, (Newtons(0), UnknownValue.UNKNOWN)),
        "contact",
    )
    scenario = make_scenario(
        surfaces=(surface,), contacts=(contact,), forces=(normal,), coordinates=coordinates
    )
    svg = NewtonSvgRenderer().render(scenario).markup
    assert 'id="force-normal"' in svg
    assert "?" not in svg
    assert "0 N" not in svg


def test_surface_coordinates_and_inclination_are_display_only() -> None:
    surface = Surface("incline", EARTH, 25)
    coords = SurfaceCoordinates(
        "incline", (SurfaceDirection.ALONG_RIGHT, SurfaceDirection.NORMAL_OUT)
    )
    force = Force(
        "along", ForceKind.APPLIED, "A", EARTH, ForceVector(coords, (Newtons(-4), Newtons(2)))
    )
    scenario = make_scenario(surfaces=(surface,), forces=(force,), coordinates=coords)
    svg = (
        NewtonSvgRenderer()
        .render(
            scenario,
            NewtonRenderOptions(visibility=NewtonVisibilityOptions(show_surface_inclination=True)),
        )
        .markup
    )
    assert "25 deg" in svg
    assert "mg =" not in svg
    assert "sin(" not in svg
    assert "cos(" not in svg


def test_string_is_one_straight_line_and_system_boundary_uses_authored_membership() -> None:
    from assessment_platform.domains.physical_sciences.mechanics.newtons_laws import (
        StringConnection,
    )

    bodies = (NewtonBody("A", Kilograms(1)), NewtonBody("B", Kilograms(1)))
    scenario = NewtonScenario(
        identifier="string",
        bodies=bodies,
        coordinates=CartesianCoordinates((CartesianDirection.RIGHT,)),
        system=SystemBoundary(("A",)),
        assumptions=ASSUMPTIONS,
        environment=(EARTH,),
        strings=(StringConnection("cord", ("A", "B"), EARTH, True, True, True),),
    )
    svg = (
        NewtonSvgRenderer()
        .render(
            scenario,
            NewtonRenderOptions(
                diagram_kind=NewtonDiagramKind.FORCE_DIAGRAM,
                visibility=NewtonVisibilityOptions(show_system_boundary=True),
            ),
        )
        .markup
    )
    assert svg.count('id="string-cord"') == 1
    assert 'id="string-system-boundary"' in svg
    assert "pulley" not in svg


def test_hidden_numeric_value_does_not_appear_anywhere() -> None:
    force = applied("hidden", Newtons(37.125))
    scenario = make_scenario(forces=(force,))
    svg = NewtonSvgRenderer().render(scenario).markup
    assert "37.125" not in svg
    visible = (
        NewtonSvgRenderer()
        .render(
            scenario,
            NewtonRenderOptions(
                visibility=NewtonVisibilityOptions(
                    show_numeric_values=True, show_known_givens=True
                ),
            ),
        )
        .markup
    )
    assert "37.125" in visible


def test_two_body_fbd_requires_explicit_body_and_result_identity_is_checked() -> None:
    bodies = (
        NewtonBody("A", Kilograms(1)),
        NewtonBody("B", Kilograms(1)),
    )
    scenario = make_scenario(bodies=bodies)
    with pytest.raises(ValueError, match="body_id"):
        NewtonSvgRenderer().render(scenario)
    with pytest.raises(ValueError, match="scenario identifier"):
        NewtonSvgRenderer().render(
            scenario, NewtonRenderOptions(diagram_kind=NewtonDiagramKind.FORCE_DIAGRAM), object()
        )


@pytest.mark.parametrize("family", tuple(NewtonGenerationFamily))
def test_all_issue_57_generated_families_render_as_force_diagrams(
    family: NewtonGenerationFamily,
) -> None:
    generated = DEFAULT_NEWTON_PROBLEM_FACTORY.generate(
        NewtonGenerationInput(
            seed=GenerationSeed(11), family=family, difficulty=Difficulty.INTRODUCTORY
        )
    )
    document = NewtonSvgRenderer().render(
        generated.scenario,
        NewtonRenderOptions(diagram_kind=NewtonDiagramKind.FORCE_DIAGRAM),
    )
    ElementTree.fromstring(document.markup)
