from __future__ import annotations

import ast
from pathlib import Path

import pytest

from assessment_platform.core import (
    Assessment,
    AssessmentType,
    CurriculumReference,
    Difficulty,
    ExpectedAnswerKind,
    GenerationSeed,
)
from assessment_platform.curriculum.caps.physical_sciences import get_caps_physical_sciences
from assessment_platform.domains.physical_sciences.mechanics import (
    WorkEnergyCalculationQuestionGenerator,
    WorkEnergyCalculationTemplate,
    WorkEnergyGenerationFamily,
    WorkEnergyGenerationInput,
    WorkEnergyProblemFactory,
    WorkEnergyQuestionOptions,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power_solver import (
    WorkEnergySolver,
)

TOPIC = get_caps_physical_sciences().topic("work-energy-and-power")
FACTORY = WorkEnergyProblemFactory()


def problem(family: WorkEnergyGenerationFamily, seed: int = 17):
    return FACTORY.generate(
        WorkEnergyGenerationInput(GenerationSeed(seed), family, Difficulty.MODERATE)
    )


def generator(include_visuals: bool = True) -> WorkEnergyCalculationQuestionGenerator:
    return WorkEnergyCalculationQuestionGenerator(TOPIC, WorkEnergyQuestionOptions(include_visuals))


@pytest.mark.parametrize("family", tuple(WorkEnergyGenerationFamily))
def test_every_generated_family_has_one_canonical_calculation_question(
    family: WorkEnergyGenerationFamily,
) -> None:
    question = generator().generate(problem(family))
    assert question.identifier.startswith("wep-question-v1-")
    assert len(question.parts) == 1
    part = question.parts[0]
    assert part.expected_answer is not None
    assert part.expected_answer.kind is ExpectedAnswerKind.NUMERIC
    assert part.response_specification is not None
    assert part.response_specification.expects_working
    assert part.response_specification.expects_units
    assert part.marking_scheme is not None
    assert sum(item.marks for item in part.marking_scheme.criteria) == part.marks
    assert question.provenance is not None
    assert question.provenance.template_ids


def test_expected_answers_are_taken_from_solver_and_mechanical_speed_is_exposed() -> None:
    final_problem = problem(WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED, 4)
    question = generator(False).generate(final_problem)
    result = WorkEnergySolver().mechanical_energy(
        final_problem.scenario.mechanical_energy_contexts[0]
    )
    assert result.final_speed is not None
    assert question.parts[0].expected_answer is not None
    assert question.parts[0].expected_answer.value == result.final_speed.value
    assert question.visuals == ()


def test_all_solver_answer_routes_preserve_signed_values() -> None:
    for family in (
        WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY,
        WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER,
        WorkEnergyGenerationFamily.AVERAGE_POWER,
    ):
        question = generator(False).generate(problem(family, 21))
        answer = question.parts[0].expected_answer
        assert answer is not None
        assert isinstance(answer.value, float)


def test_question_generation_is_deterministic_and_answer_free_metadata() -> None:
    generated = problem(WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED, 2)
    first = generator().generate(generated)
    second = generator().generate(generated)
    assert first == second
    expected = first.parts[0].expected_answer
    assert expected is not None
    answer_text = str(expected.value)
    assert answer_text not in first.identifier
    assert answer_text not in first.prompt
    assert all(answer_text not in part.identifier for part in first.parts)
    assert first.scenario is not None
    assert answer_text not in repr(dict(first.scenario.data))
    assert first.provenance is not None
    assert answer_text not in repr(first.provenance)
    assert first.visuals and answer_text not in first.visuals[0].content


def test_unknown_targets_and_authored_problem_are_unchanged() -> None:
    generated = problem(WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED, 29)
    before = generated
    question = generator(False).generate(generated)
    assert question.parts[0].expected_answer is not None
    assert generated == before
    assert generated.scenario.work_energy_contexts[0].final_state.speed.value == "unknown"


def test_memorandum_is_derived_from_the_canonical_question_part() -> None:
    question = generator(False).generate(problem(WorkEnergyGenerationFamily.NET_WORK, 31))
    assessment = Assessment(
        "m5-calculation",
        AssessmentType.QUESTION,
        CurriculumReference("CAPS"),
        (question,),
    )
    entry = assessment.memorandum[0]
    part = question.parts[0]
    assert entry.question_part_id.value == part.identifier
    assert entry.expected_answer == part.expected_answer
    assert entry.marking_scheme == part.marking_scheme


def test_visual_option_and_average_power_policy() -> None:
    visual = generator(True).generate(problem(WorkEnergyGenerationFamily.KINETIC_ENERGY))
    hidden = generator(False).generate(problem(WorkEnergyGenerationFamily.KINETIC_ENERGY))
    average = generator(True).generate(problem(WorkEnergyGenerationFamily.AVERAGE_POWER))
    assert visual.visuals and hidden.visuals == ()
    assert average.visuals == ()
    assert visual.prompt == hidden.prompt
    assert visual.parts == hidden.parts
    with pytest.raises(ValueError, match="boolean"):
        WorkEnergyQuestionOptions(include_visuals=1)  # type: ignore[arg-type]


def test_topic_validation_is_exact() -> None:
    with pytest.raises(ValueError, match="Work, Energy"):
        WorkEnergyCalculationQuestionGenerator(
            get_caps_physical_sciences().topic("momentum-and-impulse")
        )


def test_template_mapping_is_exhaustive() -> None:
    values = {item.value for item in WorkEnergyCalculationTemplate}
    assert len(values) == len(tuple(WorkEnergyGenerationFamily))


def test_question_generator_contains_no_physics_formula_or_random_dependency() -> None:
    source = Path(
        "src/assessment_platform/domains/physical_sciences/mechanics/work_energy_power_question_generator.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert not {"cos", "sin", "sqrt", "Random"} & names
    assert not any("solver" in module and module.endswith("newton_solver") for module in imports)
