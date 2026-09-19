from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from assessment_platform.api.v1 import router
from assessment_platform.application import GenerationApplicationError

app = FastAPI(title="Assessment Generation Platform", version="0.1.0")
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": tuple(
                str(item) if not isinstance(item, int) else item for item in error["loc"]
            ),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_request",
                "message": "The request did not satisfy the v1 API contract.",
                "details": details,
            }
        },
    )


@app.exception_handler(GenerationApplicationError)
async def generation_application_error_handler(
    _: Request, exc: GenerationApplicationError
) -> JSONResponse:
    status_code = 500 if exc.code == "generation_failed" else 422
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": [
                    {"field": exc.field, "message": exc.message}
                ]
                if exc.field
                else [],
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "generation_failed",
                "message": "Assessment generation failed.",
                "details": [],
            }
        },
    )
