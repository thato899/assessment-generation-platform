from __future__ import annotations

import pytest

from assessment_platform.core import Difficulty, GenerationSeed, ResponseKind
from assessment_platform.curriculum.caps.physical_sciences import get_caps_physical_sciences
from assessment_platform.domains.physical_sciences.mechanics import (
    DEFAULT_NEWTON_PROBLEM_FACTORY,
    NewtonConceptualQuestionGenerator,
    NewtonConceptualQuestionOptions,
    NewtonConceptualTemplate,
    NewtonGenerationFamily,
    NewtonGenerationInput,
)
from assessment_platform.domains.physical_sciences.mechanics.newton_conceptual_questions import (
    _SPECS,
)

TOPIC = get_caps_physical_sciences().topic("newtons-laws")


def generator(include_visuals: bool = False) -> NewtonConceptualQuestionGenerator:
    return NewtonConceptualQuestionGenerator(
        TOPIC, NewtonConceptualQuestionOptions(include_visuals)
    )


@pytest.mark.parametrize("template", tuple(NewtonConceptualTemplate))
def test_every_conceptual_template_returns_structured_reconciled_question(
    template: NewtonConceptualTemplate,
) -> None:
    question = generator().generate(template, GenerationSeed(4))
    assert question.identifier.startswith("newton-conceptual-v1-")
    assert question.parts
    part = question.parts[0]
    assert part.response_specification is not None
    assert part.expected_answer is not None
    assert part.expected_answer.kind.value == "text"
    assert isinstance(part.expected_answer.value, tuple)
    assert part.marking_scheme is not None
    assert sum(item.marks for item in part.marking_scheme.criteria) == part.marks
    assert question.provenance is not None
    assert question.provenance.template_ids == (template.value,)


def test_conceptual_generation_is_deterministic_and_does_not_use_numeric_solver() -> None:
    first = generator().generate(NewtonConceptualTemplate.NEWTON_THIRD_LAW, GenerationSeed(8))
    second = generator().generate(NewtonConceptualTemplate.NEWTON_THIRD_LAW, GenerationSeed(8))
    assert first == second
    assert first.parts[0].response_specification.kind is ResponseKind.LONG_TEXT
    assert first.parts[0].expected_answer.value == (
        "same_interaction",
        "equal_magnitude",
        "opposite_direction",
        "different_bodies",
    )


def test_misconception_protections_are_encoded_in_concepts_and_rubrics() -> None:
    first = generator().generate(NewtonConceptualTemplate.NEWTON_FIRST_LAW)
    first_text = " ".join(first.parts[0].expected_answer.value)  # type: ignore[union-attr]
    assert "rest_or_constant_velocity" in first_text
    assert "nonzero_resultant_changes_motion" in first_text
    third = generator().generate(NewtonConceptualTemplate.NEWTON_THIRD_LAW)
    third_text = " ".join(item.description for item in third.parts[0].marking_scheme.criteria)  # type: ignore[union-attr]
    assert "different bodies" in third_text
    assert "same body" not in third_text
    friction = generator().generate(NewtonConceptualTemplate.STATIC_FRICTION_LIMIT)
    friction_text = " ".join(item.description for item in friction.parts[0].marking_scheme.criteria)  # type: ignore[union-attr]
    assert "need not be at its limit" in friction_text


def test_conceptual_specs_have_no_numeric_solver_or_answer_leakage() -> None:
    text = " ".join(
        [spec.prompt for spec in _SPECS.values()]
        + [criterion[1] for spec in _SPECS.values() for criterion in spec.criteria]
    )
    assert "NewtonSolver" not in text
    assert "F_net" not in text
    assert "N = mg" not in text
    assert "calculate" not in text.lower()


def test_context_preserves_authored_system_and_action_reaction_ownership() -> None:
    problem = DEFAULT_NEWTON_PROBLEM_FACTORY.generate(
        NewtonGenerationInput(
            GenerationSeed(3), NewtonGenerationFamily.THIRD_LAW, Difficulty.MODERATE
        )
    )
    question = generator().generate(
        NewtonConceptualTemplate.ACTION_REACTION_PAIR,
        context=problem,
    )
    assert problem.scenario.identifier in question.prompt
    assert "exerts a force" in question.prompt
    assert "authored_source_target" in question.parts[0].expected_answer.value  # type: ignore[union-attr]
    assert question.scenario is not None
    assert question.scenario.data["system_body_ids"] == problem.scenario.system.body_ids


def test_optional_contextual_visual_is_safe_and_deterministic() -> None:
    problem = DEFAULT_NEWTON_PROBLEM_FACTORY.generate(
        NewtonGenerationInput(
            GenerationSeed(3), NewtonGenerationFamily.THIRD_LAW, Difficulty.MODERATE
        )
    )
    first = generator(True).generate(NewtonConceptualTemplate.FREE_BODY_DIAGRAM, context=problem)
    second = generator(True).generate(NewtonConceptualTemplate.FREE_BODY_DIAGRAM, context=problem)
    assert first == second
    assert first.visuals
    svg = first.visuals[0].content
    assert "<script" not in svg
    assert "foreignObject" not in svg
    assert "javascript:" not in svg
    assert "37.125" not in svg


def test_invalid_topic_options_and_context_are_rejected() -> None:
    with pytest.raises(ValueError, match="Newton"):
        NewtonConceptualQuestionGenerator(
            get_caps_physical_sciences().topic("momentum-and-impulse")
        )
    with pytest.raises(ValueError, match="boolean"):
        NewtonConceptualQuestionOptions(include_visuals=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="context"):
        generator().generate(NewtonConceptualTemplate.NEWTON_FIRST_LAW, context=object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="options"):
        NewtonConceptualQuestionGenerator(TOPIC, object())  # type: ignore[arg-type]
