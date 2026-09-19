"""Application orchestration for the first supported assessment generator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from assessment_platform.core import (
    Assessment,
    AssessmentRequest,
    AssessmentType,
    Difficulty,
    GenerationSeed,
    MemoEntry,
    Question,
)
from assessment_platform.curriculum.caps.physical_sciences import (
    CAPS,
    GRADE_12,
    PHYSICAL_SCIENCES,
    CurriculumTopic,
    get_caps_physical_sciences,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    vertical_projectile_question_generator as question_generator_module,
)
from assessment_platform.domains.physical_sciences.mechanics import (
    vertical_projectile_scenario_factory as scenario_factory_module,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    VerticalProjectileScenario,
)
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile_solver import (
    VerticalProjectileSolution,
    VerticalProjectileSolver,
)

VERTICAL_PROJECTILE_TOPIC_ID = "vertical-projectile-motion-1d"
DEFAULT_GENERATION_SEED = GenerationSeed(0)
SUPPORTED_DIFFICULTIES = frozenset(Difficulty)
SUPPORTED_ASSESSMENT_TYPE = AssessmentType.QUESTION
SUPPORTED_QUESTION_COUNT = 1


class GenerationApplicationError(ValueError):
    """Safe, stable application failure intended for boundary mapping."""

    def __init__(self, code: str, message: str, field: tuple[str, ...] = ()) -> None:
        self.code = code
        self.message = message
        self.field = field
        super().__init__(message)


class ScenarioFactory(Protocol):
    def generate(
        self, request: scenario_factory_module.ScenarioGenerationInput
    ) -> VerticalProjectileScenario: ...


class QuestionGenerator(Protocol):
    def generate(
        self,
        scenario: VerticalProjectileScenario,
        solution: VerticalProjectileSolution,
        curriculum_topic: CurriculumTopic,
        seed: GenerationSeed | None = None,
        include_visuals: bool = True,
    ) -> Question: ...


class CurriculumProvider(Protocol):
    def topic(self, identifier: str) -> CurriculumTopic: ...


class AssessmentGenerationService:
    """Coordinate the supported domain pipeline without owning subject logic."""

    def __init__(
        self,
        curriculum: CurriculumProvider | None = None,
        scenario_factory: ScenarioFactory | None = None,
        question_generator: QuestionGenerator | None = None,
        solver_factory: Callable[
            [VerticalProjectileScenario], VerticalProjectileSolver
        ] = VerticalProjectileSolver,
    ) -> None:
        self._curriculum = curriculum or get_caps_physical_sciences()
        self._scenario_factory = (
            scenario_factory or scenario_factory_module.VerticalProjectileScenarioFactory()
        )
        self._question_generator = (
            question_generator or question_generator_module.VerticalProjectileQuestionGenerator()
        )
        self._solver_factory = solver_factory

    def generate(self, request: AssessmentRequest) -> Assessment:
        self._validate_request(request)
        effective_seed = request.seed or DEFAULT_GENERATION_SEED
        topic = self._topic()

        try:
            scenario = self._scenario_factory.generate(
                scenario_factory_module.ScenarioGenerationInput(
                    seed=effective_seed, difficulty=request.difficulty
                )
            )
        except ValueError as error:
            raise GenerationApplicationError(
                "unsupported_configuration",
                "The requested generation configuration is not supported.",
            ) from error

        solver = self._solver_factory(scenario)
        solution = solver.solve()
        validation = solver.validate(solution)
        if not validation.valid:
            raise GenerationApplicationError(
                "generation_failed",
                "The generated physical solution failed validation.",
            )

        try:
            question = self._question_generator.generate(
                scenario,
                solution,
                topic,
                seed=effective_seed,
                include_visuals=request.include_visuals,
            )
        except ValueError as error:
            raise GenerationApplicationError(
                "generation_failed",
                "The assessment could not be generated for this configuration.",
            ) from error

        if not isinstance(question, Question):
            raise GenerationApplicationError(
                "generation_failed",
                "The generation engine returned an invalid assessment question.",
            )
        return Assessment(
            identifier=f"assessment-v1-{question.identifier}",
            assessment_type=request.assessment_type,
            curriculum=topic.reference,
            questions=(question,),
            seed=effective_seed,
        )

    @staticmethod
    def memorandum_for(assessment: Assessment) -> tuple[MemoEntry, ...]:
        """Return canonical memorandum data for a trusted teacher-side caller."""

        if not isinstance(assessment, Assessment):
            raise ValueError("assessment must be an Assessment")
        return assessment.memorandum

    def _topic(self) -> CurriculumTopic:
        try:
            return self._curriculum.topic(VERTICAL_PROJECTILE_TOPIC_ID)
        except (AttributeError, KeyError) as error:
            raise GenerationApplicationError(
                "generation_failed",
                "The configured curriculum does not provide the supported topic.",
            ) from error

    @staticmethod
    def _validate_request(request: AssessmentRequest) -> None:
        if not isinstance(request, AssessmentRequest):
            raise GenerationApplicationError(
                "invalid_request", "The application command is invalid."
            )
        if request.curriculum != CAPS:
            raise GenerationApplicationError(
                "unsupported_curriculum",
                "The generation engine supports CAPS only.",
                ("curriculum",),
            )
        if request.subject != PHYSICAL_SCIENCES:
            raise GenerationApplicationError(
                "unsupported_subject",
                "The generation engine supports Physical Sciences only.",
                ("subject",),
            )
        if request.grade != GRADE_12:
            raise GenerationApplicationError(
                "unsupported_grade",
                "The generation engine supports Grade 12 only.",
                ("grade",),
            )
        if request.topic.value != VERTICAL_PROJECTILE_TOPIC_ID:
            raise GenerationApplicationError(
                "unsupported_topic",
                "The generation engine supports vertical projectile motion only.",
                ("topic",),
            )
        if request.assessment_type is not SUPPORTED_ASSESSMENT_TYPE:
            raise GenerationApplicationError(
                "unsupported_assessment_type",
                "The first generation path supports assessment_type=question only.",
                ("assessment_type",),
            )
        if request.question_count != SUPPORTED_QUESTION_COUNT:
            raise GenerationApplicationError(
                "unsupported_question_count",
                "The first generation path supports question_count=1 only.",
                ("question_count",),
            )
        if request.difficulty not in SUPPORTED_DIFFICULTIES:
            raise GenerationApplicationError(
                "unsupported_difficulty",
                "The requested difficulty is not supported.",
                ("difficulty",),
            )
