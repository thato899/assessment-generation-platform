from assessment_platform.core import Difficulty, GenerationSeed
from assessment_platform.curriculum.caps.physical_sciences import get_caps_physical_sciences
from assessment_platform.domains.physical_sciences.mechanics import (
    MomentumGenerationFamily,
    MomentumProblemFactory,
    MomentumProblemGenerationInput,
    MomentumQuestionGenerator,
    MomentumQuestionOptions,
)


def generate(family, seed=7):
    return MomentumProblemFactory().generate(
        MomentumProblemGenerationInput(GenerationSeed(seed), family, Difficulty.MODERATE)
    )


def generator(include_visuals=True):
    topic = get_caps_physical_sciences().topic("momentum-and-impulse")
    return MomentumQuestionGenerator(topic, MomentumQuestionOptions(include_visuals))


def test_body_and_system_questions_are_solver_backed_and_deterministic():
    problem = generate(MomentumGenerationFamily.INITIAL_MOMENTUM)
    first = generator().generate(problem)
    second = generator().generate(problem)
    assert first == second
    assert len(first.parts) == 2
    assert first.parts[0].expected_answer is not None
    assert first.parts[0].expected_answer.unit == "kg·m·s⁻¹"
    assert first.provenance is not None
    assert first.provenance.template_ids


def test_collision_question_hides_requested_answer_from_visual():
    problem = generate(MomentumGenerationFamily.STICKING_COLLISION, 11)
    question = generator().generate(problem)
    assert question.visuals
    expected = question.parts[0].expected_answer
    assert expected is not None
    assert str(expected.value) not in question.visuals[0].content


def test_visuals_can_be_omitted():
    question = generator(False).generate(generate(MomentumGenerationFamily.MOMENTUM_CHANGE))
    assert question.visuals == ()
