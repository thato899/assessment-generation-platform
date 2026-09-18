from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from assessment_platform.api.v1 import router

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
