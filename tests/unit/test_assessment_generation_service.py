import random

import pytest

from assessment_platform.application.assessment_generation import (
    DEFAULT_GENERATION_SEED,
    AssessmentGenerationService,
    GenerationApplicationError,
)
from assessment_platform.core import (
    AssessmentRequest,
    AssessmentType,
    Difficulty,
    GenerationSeed,
    Grade,
    Subject,
    Topic,
    ValidationResult,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    ScenarioGenerationInput,
    VerticalProjectileScenarioFactory,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    vertical_projectile_question_generator as question_generator_module,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    VerticalProjectileScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    VerticalProjectileSolution,
    VerticalProjectileSolver,
)


def request(
    *,
    seed: int | None = 18472,
    difficulty: Difficulty = Difficulty.MODERATE,
    **overrides: object,
) -> AssessmentRequest:
    values: dict[str, object] = {
        "curriculum": "CAPS",
        "subject": Subject("physical-sciences"),
        "grade": Grade(12),
        "topic": Topic("vertical-projectile-motion-1d"),
        "assessment_type": AssessmentType.QUESTION,
        "question_count": 1,
        "difficulty": difficulty,
        "include_visuals": True,
        "seed": GenerationSeed(seed) if seed is not None else None,
    }
    values.update(overrides)
    return AssessmentRequest(**values)  # type: ignore[arg-type]


class SpyFactory:
    def __init__(self) -> None:
        self.delegate = VerticalProjectileScenarioFactory()
        self.requests: list[ScenarioGenerationInput] = []

    def generate(self, generation_input: ScenarioGenerationInput) -> VerticalProjectileScenario:
        self.requests.append(generation_input)
        return self.delegate.generate(generation_input)


class SpyQuestionGenerator:
    def __init__(self) -> None:
        self.delegate = question_generator_module.VerticalProjectileQuestionGenerator()
        self.calls: list[tuple[VerticalProjectileScenario, VerticalProjectileSolution]] = []

    def generate(
        self,
        scenario: VerticalProjectileScenario,
        solution: VerticalProjectileSolution,
        curriculum_topic,
        seed=None,
        include_visuals=True,
    ):
        self.calls.append((scenario, solution))
        return self.delegate.generate(
            scenario, solution, curriculum_topic, seed=seed, include_visuals=include_visuals
        )


def test_service_runs_factory_solver_validation_generator_and_composition() -> None:
    factory = SpyFactory()
    generator = SpyQuestionGenerator()
    service = AssessmentGenerationService(
        scenario_factory=factory,
        question_generator=generator,
    )

    assessment = service.generate(request())

    assert len(factory.requests) == 1
    assert factory.requests[0].seed == GenerationSeed(18472)
    assert factory.requests[0].difficulty is Difficulty.MODERATE
    assert len(generator.calls) == 1
    scenario, solution = generator.calls[0]
    assert scenario.seed == GenerationSeed(18472)
    assert VerticalProjectileSolver(scenario).validate(solution).valid
    assert assessment.identifier == f"assessment-v1-{assessment.questions[0].identifier}"
    assert assessment.curriculum.curriculum == "CAPS"
    assert assessment.curriculum.topic is not None
    assert assessment.curriculum.topic.value == "vertical-projectile-motion-1d"
    assert assessment.seed == GenerationSeed(18472)
    assert assessment.memorandum
    assert all(entry.expected_answer is not None for entry in assessment.memorandum)


def test_service_uses_default_seed_without_global_randomness() -> None:
    factory = SpyFactory()
    service = AssessmentGenerationService(scenario_factory=factory)
    random.seed(20260919)
    before = random.getstate()

    assessment = service.generate(request(seed=None))

    assert random.getstate() == before
    assert factory.requests[0].seed == DEFAULT_GENERATION_SEED
    assert assessment.seed == DEFAULT_GENERATION_SEED


@pytest.mark.parametrize("difficulty", list(Difficulty))
def test_each_public_difficulty_reaches_the_factory_policy(difficulty: Difficulty) -> None:
    factory = SpyFactory()
    service = AssessmentGenerationService(scenario_factory=factory)

    assessment = service.generate(request(difficulty=difficulty, seed=7))
    assert assessment.questions[0].scenario is not None
    scenario_data = assessment.questions[0].scenario.data
    profile = factory.delegate.policy.profile_for(difficulty)

    assert factory.requests[0].difficulty is difficulty
    assert (
        scenario_data["initial_velocity_m_per_s"] == 0
        or abs(scenario_data["initial_velocity_m_per_s"]) in profile.initial_speeds
    )
    assert (
        scenario_data["launch_position_m"] == 0
        or scenario_data["launch_position_m"] in profile.elevated_heights
    )


def test_application_does_not_request_down_positive_elevated_scenarios() -> None:
    factory = SpyFactory()
    service = AssessmentGenerationService(scenario_factory=factory)

    service.generate(request(seed=3))

    assert factory.requests[0].positive_direction.value == "up"
    assert factory.requests[0].family is None


@pytest.mark.parametrize("seed", range(8))
def test_application_seed_corpus_produces_valid_questions(seed: int) -> None:
    assessment = AssessmentGenerationService().generate(request(seed=seed))

    assert assessment.seed == GenerationSeed(seed)
    assert assessment.questions[0].parts
    assert assessment.questions[0].scenario is not None


def test_solution_validation_failure_stops_before_question_generation() -> None:
    factory = SpyFactory()
    generator = SpyQuestionGenerator()

    class InvalidSolver:
        def solve(self) -> VerticalProjectileSolution:
            return VerticalProjectileSolution("invalid", ())

        def validate(self, _solution: VerticalProjectileSolution) -> ValidationResult:
            return ValidationResult(False, ("invalid solution",))

    service = AssessmentGenerationService(
        scenario_factory=factory,
        question_generator=generator,
        solver_factory=lambda _scenario: InvalidSolver(),  # type: ignore[arg-type]
    )

    with pytest.raises(GenerationApplicationError, match="failed validation") as error:
        service.generate(request())

    assert error.value.code == "generation_failed"
    assert generator.calls == []


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("curriculum", "OTHER", "unsupported_curriculum"),
        ("subject", Subject("mathematics"), "unsupported_subject"),
        ("grade", Grade(11), "unsupported_grade"),
        ("topic", Topic("momentum-and-impulse"), "unsupported_topic"),
        ("assessment_type", AssessmentType.QUIZ, "unsupported_assessment_type"),
        ("question_count", 2, "unsupported_question_count"),
    ],
)
def test_unsupported_application_configuration_is_stable(
    field: str, value: object, code: str
) -> None:
    with pytest.raises(GenerationApplicationError) as error:
        AssessmentGenerationService().generate(request(**{field: value}))

    assert error.value.code == code
    assert error.value.field == (field,)


def test_trusted_memorandum_projection_uses_canonical_assessment_relationships() -> None:
    service = AssessmentGenerationService()
    assessment = service.generate(request(seed=42))

    entries = service.memorandum_for(assessment)

    assert tuple(entry.question_part_id.value for entry in entries) == tuple(
        part.identifier for part in assessment.questions[0].parts
    )
