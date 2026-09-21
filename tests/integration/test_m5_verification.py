"""Focused evidence checks for the bounded M5 verification boundary."""

from __future__ import annotations

import copy
import random
import re
from pathlib import Path
from xml.etree import ElementTree

from fastapi.testclient import TestClient

from assessment_platform.application import AssessmentGenerationService
from assessment_platform.core import (
    AssessmentRequest,
    AssessmentType,
    Difficulty,
    GenerationSeed,
    Topic,
)
from assessment_platform.curriculum.caps.physical_sciences import (
    CAPS,
    GRADE_12,
    PHYSICAL_SCIENCES,
    WORK_ENERGY_POWER_TOPIC_ID,
    get_caps_physical_sciences,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    WorkEnergyGenerationFamily,
    WorkEnergyGenerationInput,
    WorkEnergyProblemFactory,
    WorkEnergySolver,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power import (
    UnknownValue,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power_solver import (
    FailureReason,
    WorkEnergySolveError,
)
from assessment_platform.main import app
from assessment_platform.rendering.svg.work_energy_power import (
    WorkEnergyDiagramKind,
    WorkEnergyRenderOptions,
    WorkEnergySvgRenderer,
)

ROOT = Path(__file__).resolve().parents[2]
FACTORY = WorkEnergyProblemFactory()
CLIENT = TestClient(app)
FORBIDDEN_LEARNER_KEYS = {
    "expected_answer",
    "marking_scheme",
    "rubric",
    "criteria",
    "memo",
    "memorandum",
    "solution",
    "solver",
    "scenario",
    "provenance",
    "concepts",
    "correct_choice",
    "worked_solution",
}


def _recursive_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in _recursive_keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in _recursive_keys(child)}
    return set()


def _request(seed: int | None) -> AssessmentRequest:
    return AssessmentRequest(
        CAPS,
        PHYSICAL_SCIENCES,
        GRADE_12,
        Topic(WORK_ENERGY_POWER_TOPIC_ID),
        AssessmentType.QUESTION,
        1,
        Difficulty.MODERATE,
        True,
        GenerationSeed(seed) if seed is not None else None,
    )


def test_caps_metadata_matches_the_approved_m5_boundary() -> None:
    topic = get_caps_physical_sciences().topic(WORK_ENERGY_POWER_TOPIC_ID)

    assert topic.reference.curriculum == CAPS
    assert topic.reference.grade == GRADE_12
    assert topic.reference.subject == PHYSICAL_SCIENCES
    assert topic.reference.phase == "FET"
    assert topic.domain.identifier == "mechanics"
    assert topic.assessment_metadata == (
        "Grade 12",
        "Physics",
        "Mechanics",
        "Term 2",
        "10 hours",
    )


def test_all_thirteen_generation_families_are_explicit_and_replayable() -> None:
    families = tuple(WorkEnergyGenerationFamily)
    assert len(families) == 13
    assert {family.value for family in families} == {
        "work-by-force",
        "net-work",
        "along-plane-work",
        "kinetic-energy",
        "gravitational-potential-energy",
        "work-energy-net-work",
        "work-energy-final-speed",
        "work-energy-initial-speed",
        "mechanical-energy-non-conservative-work",
        "mechanical-energy-final-speed",
        "average-power",
        "constant-speed-power",
        "pumping-power",
    }
    for family in families:
        request = WorkEnergyGenerationInput(GenerationSeed(42), family, Difficulty.MODERATE)
        first = FACTORY.generate(request)
        second = FACTORY.generate(request)
        assert first == second
        assert first.family is family
        assert not hasattr(first, "answer")
        assert not hasattr(first, "solver_result")


def test_solver_preserves_unknown_authored_targets_and_global_rng() -> None:
    request = WorkEnergyGenerationInput(
        GenerationSeed(42), WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED, Difficulty.MODERATE
    )
    problem = FACTORY.generate(request)
    before = copy.deepcopy(problem.scenario)
    random.seed(1234)
    rng_before = random.getstate()

    result = WorkEnergySolver().work_energy(problem.scenario.work_energy_contexts[0])

    assert problem.scenario == before
    assert random.getstate() == rng_before
    assert result.final_state.speed is not UnknownValue.UNKNOWN
    assert problem.scenario.work_energy_contexts[0].final_state.speed is UnknownValue.UNKNOWN


def test_solver_failure_reasons_remain_explicit_for_unresolved_inputs() -> None:
    problem = FACTORY.generate(
        WorkEnergyGenerationInput(
            GenerationSeed(7), WorkEnergyGenerationFamily.WORK_BY_FORCE, Difficulty.MODERATE
        )
    )
    contribution = problem.scenario.work_inputs[0].contributions[0]
    from dataclasses import replace

    unresolved = replace(contribution, force_magnitude=UnknownValue.UNKNOWN)
    try:
        WorkEnergySolver().work_by_force(unresolved)
    except WorkEnergySolveError as error:
        assert error.reason is FailureReason.UNDERDETERMINED
    else:  # pragma: no cover - protects the audit if solver semantics regress
        raise AssertionError("unknown authored force must not be fabricated as zero")


def test_renderer_is_accessible_xml_and_does_not_execute_input() -> None:
    problem = FACTORY.generate(
        WorkEnergyGenerationInput(
            GenerationSeed(7), WorkEnergyGenerationFamily.WORK_BY_FORCE, Difficulty.MODERATE
        )
    )
    document = WorkEnergySvgRenderer().render(
        problem.scenario,
        WorkEnergyRenderOptions(diagram_kind=WorkEnergyDiagramKind.WORK_CONTRIBUTIONS),
    )
    root = ElementTree.fromstring(document.markup)
    content = document.markup.lower()

    assert root.attrib["role"] == "img"
    assert "aria-labelledby" in root.attrib
    assert "<title" in content and "<desc" in content
    assert "<script" not in content
    assert "foreignobject" not in content
    assert "javascript:" not in content
    assert not re.search(r"\son[a-z]+\s*=", content)


def test_application_and_api_preserve_internal_memo_and_learner_safety() -> None:
    service = AssessmentGenerationService()
    for seed in (0, 1):
        assessment = service.generate(_request(seed))
        memo = assessment.memorandum
        assert len(memo) == sum(len(question.parts) for question in assessment.questions)
        assert all(
            entry.question_part_id.value == part.identifier
            for entry, part in zip(memo, assessment.questions[0].parts, strict=True)
        )

        response = CLIENT.post(
            "/api/v1/assessments/generate",
            json={
                "curriculum": CAPS,
                "subject": PHYSICAL_SCIENCES.value,
                "grade": 12,
                "topic": WORK_ENERGY_POWER_TOPIC_ID,
                "assessment_type": "question",
                "question_count": 1,
                "difficulty": Difficulty.MODERATE.value,
                "include_visuals": True,
                "seed": seed,
            },
        )
        assert response.status_code == 200
        assert not FORBIDDEN_LEARNER_KEYS & _recursive_keys(response.json())


def test_numerical_equations_are_confined_to_the_solver_boundary() -> None:
    application = (
        ROOT / "src/assessment_platform/application/assessment_generation.py"
    ).read_text()
    api = (ROOT / "src/assessment_platform/api/v1/__init__.py").read_text()
    assert "WorkEnergySolver" not in application
    assert "WorkEnergySolver" not in api
    assert not re.search(r"\bwork\s*/\s*time\b", application + api, re.IGNORECASE)
    assert not re.search(r"\bforce\s*\*\s*speed\b", application + api, re.IGNORECASE)

    solver_directory = (
        ROOT
        / "src/assessment_platform/domains/physical_sciences/mechanics"
        / "work_energy_power_solver"
    )
    solver_text = "\n".join(
        path.read_text()
        for path in solver_directory.glob("*.py")
    )
    assert "work / time" in solver_text
    assert "force * speed" in solver_text
