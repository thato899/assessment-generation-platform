from assessment_platform.core import GenerationSeed, ResponseKind
from assessment_platform.curriculum.caps.physical_sciences import get_caps_physical_sciences
from assessment_platform.domains.physical_sciences.mechanics import (
    ConceptualTemplate,
    MomentumConceptualQuestionGenerator,
)


def make_generator():
    topic = get_caps_physical_sciences().topic("momentum-and-impulse")
    return MomentumConceptualQuestionGenerator(topic)


def test_conceptual_questions_are_deterministic_and_structured():
    generator = make_generator()
    first = generator.generate(ConceptualTemplate.CONSERVATION, GenerationSeed(4))
    second = generator.generate(ConceptualTemplate.CONSERVATION, GenerationSeed(4))
    assert first == second
    part = first.parts[0]
    assert part.response_specification is not None
    assert part.expected_answer is not None
    assert part.marking_scheme is not None
    assert sum(item.marks for item in part.marking_scheme.criteria) == part.marks


def test_newton_template_assesses_rate_of_change_not_only_f_equals_ma():
    question = make_generator().generate(ConceptualTemplate.NEWTON_MOMENTUM)
    assert "rate of change of momentum" in str(question.parts[0].expected_answer.value)


def test_safety_rubric_contains_time_and_force_causality():
    question = make_generator().generate(ConceptualTemplate.SAFETY)
    descriptions = " ".join(item.description for item in question.parts[0].marking_scheme.criteria)
    assert "stopping/contact time" in descriptions
    assert "average force" in descriptions
    assert question.parts[0].response_specification.kind is ResponseKind.LONG_TEXT


def test_inelastic_template_does_not_equate_all_inelastic_collisions_with_sticking():
    question = make_generator().generate(ConceptualTemplate.ELASTIC_INELASTIC)
    descriptions = " ".join(item.description for item in question.parts[0].marking_scheme.criteria)
    assert "not as every inelastic collision" in descriptions
