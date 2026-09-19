from enum import StrEnum
from typing import Annotated, Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from assessment_platform.application import (
    AssessmentGenerationService,
    GenerationApplicationError,
)
from assessment_platform.core import (
    AssessmentRequest as DomainAssessmentRequest,
)
from assessment_platform.core import (
    AssessmentType,
    Difficulty,
    GenerationSeed,
    Grade,
    Subject,
    Topic,
)

router = APIRouter(prefix="/api/v1")

CurriculumId = str
SubjectId = str
GradeId = int
TopicId = str


class DifficultyId(StrEnum):
    INTRODUCTORY = "introductory"
    MODERATE = "moderate"
    ADVANCED = "advanced"


class AssessmentTypeId(StrEnum):
    QUESTION = "question"
    QUIZ = "quiz"
    PRACTICE_SET = "practice_set"
    WORKSHEET = "worksheet"
    HOMEWORK = "homework"
    TEST = "test"
    DIAGNOSTIC = "diagnostic"
    EXAMINATION = "examination"


class AssessmentGenerationRequest(BaseModel):
    """Stable v1 request DTO; separate from framework-independent domain models."""

    model_config = ConfigDict(extra="forbid")

    curriculum: CurriculumId = Field(
        description="Curriculum identifier; the first engine supports CAPS."
    )
    subject: SubjectId = Field(
        description="Subject identifier; the first engine supports physical-sciences."
    )
    grade: GradeId = Field(ge=1, le=12, description="Grade identifier.")
    topic: TopicId = Field(description="Stable CAPS topic identifier.")
    assessment_type: AssessmentTypeId = Field(description="Requested assessment form.")
    question_count: Annotated[int, Field(ge=1, le=100)]
    difficulty: DifficultyId
    include_visuals: bool = True
    seed: Annotated[int | None, Field(ge=0, le=2**63 - 1)] = None

    def to_domain(self) -> DomainAssessmentRequest:
        return DomainAssessmentRequest(
            curriculum=self.curriculum,
            subject=Subject(self.subject),
            grade=Grade(self.grade),
            topic=Topic(self.topic),
            assessment_type=AssessmentType(self.assessment_type.value),
            question_count=self.question_count,
            difficulty=Difficulty(self.difficulty.value),
            include_visuals=self.include_visuals,
            seed=GenerationSeed(self.seed) if self.seed is not None else None,
        )


class ResponseSpecificationDto(BaseModel):
    kind: str
    suggested_line_count: int = 0
    expects_working: bool = False
    expects_final_answer: bool = False
    expects_units: bool = False
    required_fields: tuple[str, ...] = ()


class LearnerQuestionPartDto(BaseModel):
    """Learner-safe projection with no expected-answer or memo fields."""

    question_part_id: str
    prompt: str
    maximum_marks: int
    response_specification: ResponseSpecificationDto


class LearnerQuestionDto(BaseModel):
    question_id: str
    prompt: str
    parts: tuple[LearnerQuestionPartDto, ...]


class VisualAssetDto(BaseModel):
    asset_id: str
    media_type: Literal["image/svg+xml"]
    content: str


class AssessmentGenerationResponse(BaseModel):
    """Learner-safe response for the supported v1 generation path."""

    api_version: Literal["v1"] = "v1"
    assessment_id: str
    effective_seed: int
    curriculum: CurriculumId
    subject: SubjectId
    grade: GradeId
    topic: TopicId
    assessment_type: AssessmentTypeId
    questions: tuple[LearnerQuestionDto, ...]
    visuals: tuple[VisualAssetDto, ...] = ()


class TeacherMemoEntryDto(BaseModel):
    """Teacher/memorandum projection; never included in learner DTOs."""

    question_part_id: str
    expected_answer: dict[str, object]
    marking_scheme: dict[str, object]


class ErrorDetailDto(BaseModel):
    field: tuple[str | int, ...] = ()
    message: str


class ErrorDto(BaseModel):
    code: str
    message: str
    details: tuple[ErrorDetailDto, ...] = ()


class ErrorResponse(BaseModel):
    error: ErrorDto


class GenerationUnavailableResponse(ErrorResponse):
    pass


generation_service = AssessmentGenerationService()


@router.get("/health", tags=["service"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@router.post(
    "/assessments/generate",
    status_code=200,
    response_model=AssessmentGenerationResponse,
    responses={
        200: {"model": AssessmentGenerationResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["assessments"],
    summary="Request an assessment generation",
)
def generate_assessment(request: AssessmentGenerationRequest) -> AssessmentGenerationResponse:
    assessment = generation_service.generate(request.to_domain())
    if assessment.seed is None or len(assessment.questions) != 1:
        raise GenerationApplicationError(
            "generation_failed", "The generation engine returned an incomplete assessment."
        )
    question = assessment.questions[0]
    parts: list[LearnerQuestionPartDto] = []
    for part in question.parts:
        if part.response_specification is None:
            raise GenerationApplicationError(
                "generation_failed", "The generation engine returned an incomplete question."
            )
        specification = part.response_specification
        parts.append(
            LearnerQuestionPartDto(
                question_part_id=part.identifier,
                prompt=part.prompt,
                maximum_marks=part.marks,
                response_specification=ResponseSpecificationDto(
                    kind=specification.kind.value,
                    suggested_line_count=specification.suggested_line_count,
                    expects_working=specification.expects_working,
                    expects_final_answer=specification.expects_final_answer,
                    expects_units=specification.expects_units,
                    required_fields=specification.required_fields,
                ),
            )
        )
    visuals = tuple(
        VisualAssetDto(
            asset_id=visual.identifier,
            media_type="image/svg+xml",
            content=visual.content,
        )
        for visual in question.visuals
    )
    return AssessmentGenerationResponse(
        assessment_id=assessment.identifier,
        effective_seed=assessment.seed.value,
        curriculum=request.curriculum,
        subject=request.subject,
        grade=request.grade,
        topic=request.topic,
        assessment_type=request.assessment_type,
        questions=(
            LearnerQuestionDto(
                question_id=question.identifier,
                prompt=question.prompt,
                parts=tuple(parts),
            ),
        ),
        visuals=visuals,
    )
