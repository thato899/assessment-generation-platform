from fastapi import FastAPI

from assessment_platform.api.v1 import router

app = FastAPI(title="Assessment Generation Platform", version="0.1.0")
app.include_router(router)
