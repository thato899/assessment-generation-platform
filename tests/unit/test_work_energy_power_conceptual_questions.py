from __future__ import annotations

# ruff: noqa: E501
import ast
from pathlib import Path

import pytest

from assessment_platform.core import ExpectedAnswerKind, GenerationSeed, ResponseKind
from assessment_platform.curriculum.caps.physical_sciences import get_caps_physical_sciences
from assessment_platform.domains.physical_sciences.mechanics import (
    WorkEnergyConceptualQuestionGenerator,
    WorkEnergyConceptualQuestionOptions,
    WorkEnergyConceptualTemplate,
)
from assessment_platform.domains.physical_sciences.mechanics.work_energy_power_conceptual_questions import (
    _SPECS,
    GENERATOR_ID,
    GENERATOR_VERSION,
)

TOPIC = get_caps_physical_sciences().topic("work-energy-and-power")


def generator(include_visuals: bool = False) -> WorkEnergyConceptualQuestionGenerator:
    return WorkEnergyConceptualQuestionGenerator(
        TOPIC, WorkEnergyConceptualQuestionOptions(include_visuals)
    )


@pytest.mark.parametrize("template", tuple(WorkEnergyConceptualTemplate))
def test_every_template_has_one_structured_reconciled_conceptual_question(
    template: WorkEnergyConceptualTemplate,
) -> None:
    question = generator().generate(template, GenerationSeed(4))
    assert question.identifier == f"wep-conceptual-v1-{template.value}"
    assert question.prompt
    assert len(question.parts) == 1
    part = question.parts[0]
    assert part.identifier == f"{question.identifier}.response"
    assert part.response_specification is not None
    assert part.response_specification.kind in (ResponseKind.SHORT_TEXT, ResponseKind.LONG_TEXT)
    assert not part.response_specification.expects_working
    assert not part.response_specification.expects_units
    assert part.response_specification.expects_final_answer
    assert part.expected_answer is not None
    assert part.expected_answer.kind is ExpectedAnswerKind.TEXT
    assert isinstance(part.expected_answer.value, tuple)
    assert part.expected_answer.value == _SPECS[template].concepts
    assert part.marking_scheme is not None
    assert part.marking_scheme.maximum_marks == part.marks
    assert sum(item.marks for item in part.marking_scheme.criteria) == part.marks
    assert question.provenance is not None
    assert question.provenance.generator_id == GENERATOR_ID
    assert question.provenance.generator_version == GENERATOR_VERSION
    assert question.provenance.seed == GenerationSeed(4)
    assert question.provenance.template_ids == (template.value,)
    assert question.scenario is None
    assert question.visuals == ()


def test_inventory_is_exhaustive_and_each_spec_is_valid() -> None:
    assert set(_SPECS) == set(WorkEnergyConceptualTemplate)
    for template, spec in _SPECS.items():
        assert spec.prompt
        assert spec.concepts
        assert len(spec.concepts) == len(set(spec.concepts)), template
        assert all(token and " " not in token for token in spec.concepts)
        assert spec.criteria
        keys = [item[0] for item in spec.criteria]
        assert len(keys) == len(set(keys)), template
        assert all(key and description and marks > 0 for key, description, marks in spec.criteria)
        assert sum(item[2] for item in spec.criteria) > 0


def test_misconception_protections_are_explicit() -> None:
    def concepts(template: WorkEnergyConceptualTemplate) -> set[str]:
        return set(_SPECS[template].concepts)

    assert {"force_alone_insufficient", "force_displacement_relationship"} <= concepts(
        WorkEnergyConceptualTemplate.WORK_DEFINITION
    )
    assert {"work_is_scalar", "signed_value_without_direction_vector"} <= concepts(
        WorkEnergyConceptualTemplate.WORK_IS_SCALAR
    )
    assert "large_force_not_sufficient" in concepts(
        WorkEnergyConceptualTemplate.PERPENDICULAR_ZERO_WORK
    )
    assert "zero_net_work_not_necessarily_rest" in concepts(
        WorkEnergyConceptualTemplate.NET_WORK_AND_KINETIC_ENERGY
    )
    assert "negative_allowed" in concepts(
        WorkEnergyConceptualTemplate.POTENTIAL_ENERGY_REFERENCE_LEVEL
    )
    assert {"mechanical_energy_may_change", "total_energy_conserved"} <= concepts(
        WorkEnergyConceptualTemplate.MECHANICAL_VS_TOTAL_ENERGY
    )
    assert "efficiency_outside_model" in concepts(
        WorkEnergyConceptualTemplate.PUMPING_POWER_ASSUMPTIONS
    )


def test_generation_is_deterministic_and_visual_option_does_not_add_context() -> None:
    first = generator(True).generate(WorkEnergyConceptualTemplate.MECHANICAL_VS_TOTAL_ENERGY)
    second = generator(True).generate(WorkEnergyConceptualTemplate.MECHANICAL_VS_TOTAL_ENERGY)
    without_visuals = generator(False).generate(
        WorkEnergyConceptualTemplate.MECHANICAL_VS_TOTAL_ENERGY
    )
    assert first == second == without_visuals
    assert first.visuals == ()
    assert first.provenance is not None
    assert first.provenance.seed is None


def test_concept_tokens_and_rubrics_are_not_learner_prompt_content() -> None:
    for template in WorkEnergyConceptualTemplate:
        question = generator().generate(template)
        part = question.parts[0]
        assert all(token not in question.prompt for token in part.expected_answer.value)  # type: ignore[union-attr]
        assert all(criterion.identifier not in question.prompt for criterion in part.marking_scheme.criteria)  # type: ignore[union-attr]
        assert question.scenario is None
        assert question.prompt == part.prompt


def test_expected_answers_are_semantic_tokens_and_no_scoring_api_exists() -> None:
    question = generator().generate(WorkEnergyConceptualTemplate.POWER_AS_RATE)
    answer = question.parts[0].expected_answer
    assert answer is not None
    assert answer.kind is ExpectedAnswerKind.TEXT
    assert isinstance(answer.value, tuple)
    assert all(isinstance(token, str) for token in answer.value)
    assert not hasattr(generator(), "mark")
    assert not hasattr(generator(), "evaluate")
    assert not hasattr(generator(), "score")


def test_topic_options_template_and_seed_boundaries_are_validated() -> None:
    with pytest.raises(ValueError, match="Work, Energy"):
        WorkEnergyConceptualQuestionGenerator(
            get_caps_physical_sciences().topic("momentum-and-impulse")
        )
    with pytest.raises(ValueError, match="boolean"):
        WorkEnergyConceptualQuestionOptions(include_visuals=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="options"):
        WorkEnergyConceptualQuestionGenerator(TOPIC, object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="template"):
        generator().generate("work" )  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="seed"):
        generator().generate(WorkEnergyConceptualTemplate.WORK_DEFINITION, 4)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="topic"):
        WorkEnergyConceptualQuestionGenerator(object())  # type: ignore[arg-type]


def test_conceptual_module_has_no_solver_or_numerical_formula_dependency() -> None:
    path = Path(
        "src/assessment_platform/domains/physical_sciences/mechanics/"
        "work_energy_power_conceptual_questions.py"
    )
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert not any("solver" in module for module in modules)
    assert not any("work_energy_power_question_generator" in module for module in modules)
    assert not {"cos", "sin", "sqrt", "Random"} & names
    assert "WorkEnergySolver" not in source
    assert "ResponseKind.NUMERIC" not in source
    assert "ResponseKind.CALCULATION" not in source
