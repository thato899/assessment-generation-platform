from __future__ import annotations

import pytest

from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.curriculum.caps.physical_sciences import get_caps_physical_sciences
from assessment_platform.domains.physical_sciences.mechanics import (
    DEFAULT_NEWTON_PROBLEM_FACTORY,
    NewtonCalculationQuestionGenerator,
    NewtonGenerationFamily,
    NewtonGenerationInput,
    NewtonQuestionOptions,
)
from assessment_platform.domains.physical_sciences.mechanics.newton_solver import NewtonSolver
from assessment_platform.domains.physical_sciences.mechanics.newtons_laws import UnknownValue

TOPIC = get_caps_physical_sciences().topic("newtons-laws")


def generate(family: NewtonGenerationFamily, seed: int = 17):
    return DEFAULT_NEWTON_PROBLEM_FACTORY.generate(
        NewtonGenerationInput(GenerationSeed(seed), family, Difficulty.MODERATE)
    )


def generator(include_visuals: bool = True) -> NewtonCalculationQuestionGenerator:
    return NewtonCalculationQuestionGenerator(TOPIC, NewtonQuestionOptions(include_visuals))


@pytest.mark.parametrize(
    "family",
    tuple(
        family
        for family in NewtonGenerationFamily
        if family is not NewtonGenerationFamily.THIRD_LAW
    ),
)
def test_supported_generated_families_create_canonical_questions(
    family: NewtonGenerationFamily,
) -> None:
    question = generator().generate(generate(family))
    assert question.identifier.startswith("newton-question-v1-")
    assert question.parts
    assert question.provenance is not None
    assert question.provenance.generator_id.endswith("question-generator")
    assert question.provenance.template_ids
    assert question.visuals
    for part in question.parts:
        assert part.response_specification is not None
        assert part.expected_answer is not None
        assert part.marking_scheme is not None
        assert sum(item.marks for item in part.marking_scheme.criteria) == part.marks


def test_question_generation_is_deterministic_and_ids_do_not_contain_answers() -> None:
    problem = generate(NewtonGenerationFamily.UNIVERSAL_GRAVITATION, 3)
    first = generator().generate(problem)
    second = generator().generate(problem)
    assert first == second
    assert first.provenance == second.provenance
    expected = first.parts[0].expected_answer
    assert expected is not None
    assert (
        expected.value
        == NewtonSolver(problem.scenario).gravitational_force("gravity").magnitude.value
    )
    assert str(expected.value) not in first.identifier
    assert all(str(expected.value) not in part.identifier for part in first.parts)


def test_unknown_force_stays_unknown_and_answer_is_not_in_prompt_or_visual() -> None:
    problem = generate(NewtonGenerationFamily.UNKNOWN_FORCE, 17)
    unknown = next(
        force for force in problem.scenario.forces if force.identifier == problem.force_id
    )
    assert unknown.vector.components[0] is UnknownValue.UNKNOWN
    question = generator().generate(problem)
    answer = question.parts[0].expected_answer
    assert answer is not None
    assert str(answer.value) not in question.prompt
    assert question.visuals
    assert str(answer.value) not in question.visuals[0].content


def test_solver_signed_results_and_authored_givens_are_preserved() -> None:
    problem = generate(NewtonGenerationFamily.CONNECTED_BODIES, 3)
    question = generator(False).generate(problem)
    result = NewtonSolver(problem.scenario).connected_bodies(problem.request)
    assert question.parts[0].expected_answer is not None
    assert (
        question.parts[0].expected_answer.value == result.bodies[0].acceleration.components[0].value
    )
    assert question.parts[1].expected_answer is not None
    assert question.parts[1].expected_answer.value == result.tension.value
    assert "light" in question.prompt
    assert "inextensible" in question.prompt
    assert question.visuals == ()


def test_contact_templates_use_contact_solver_results_without_mu_n_shortcut() -> None:
    problem = generate(NewtonGenerationFamily.LIMITING_STATIC_FRICTION, 3)
    question = generator(False).generate(problem)
    result = NewtonSolver(problem.scenario).contact_forces(problem.contact_id)
    assert question.parts[0].expected_answer is not None
    assert question.parts[0].expected_answer.value == result.friction.magnitude.value  # type: ignore[union-attr]
    assert "μ" not in question.prompt
    assert "mu" not in question.prompt.lower()


def test_third_law_has_no_numeric_question_template() -> None:
    with pytest.raises(ValueError, match="no supported"):
        generator(False).generate(generate(NewtonGenerationFamily.THIRD_LAW))


def test_topic_and_option_validation() -> None:
    with pytest.raises(ValueError, match="Newton"):
        NewtonCalculationQuestionGenerator(
            get_caps_physical_sciences().topic("momentum-and-impulse")
        )
    with pytest.raises(ValueError, match="boolean"):
        NewtonQuestionOptions(include_visuals=1)  # type: ignore[arg-type]
