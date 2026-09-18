from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1")

class AssessmentRequest(BaseModel):
    curriculum: str = Field(pattern="^CAPS$")
    subject: str = Field(pattern="^[a-z-]+$")
    grade: int = Field(ge=10, le=12)
    topic: str
    assessment_type: str = Field(pattern="^(question|quiz|practice_set|worksheet|test)$")
    question_count: int = Field(ge=1, le=100)
    difficulty: str = Field(pattern="^(introductory|moderate|advanced)$")
    include_visuals: bool = True
    seed: int | None = None

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}

@router.post("/assessments/generate", status_code=501)
def generate_assessment(_: AssessmentRequest) -> dict[str, str]:
    return {"error": "assessment generation is not implemented in the bootstrap milestone"}

