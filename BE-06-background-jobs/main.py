"""
BE-06 / Assignment A7: Your First Background Job
FastAPI application with Inngest background job orchestration.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Report API - Background Jobs",
    description="FastAPI service demonstrating the 202 Accepted + background worker + polling pattern with Inngest.",
    version="1.0.0",
)


@app.get("/health", summary="Health check endpoint")
def health_check() -> JSONResponse:
    """Stage 0: Return health status code 200 and ok json."""
    return JSONResponse(status_code=200, content={"status": "ok"})
