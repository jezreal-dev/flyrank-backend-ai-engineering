"""
BE-06 / Assignment A7: Your First Background Job
FastAPI application with Inngest background job orchestration.
"""

import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import inngest
import inngest.fast_api

app = FastAPI(
    title="Report API - Background Jobs",
    description="FastAPI service demonstrating the 202 Accepted + background worker + polling pattern with Inngest.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Stage 0: Health Check Endpoint
# ---------------------------------------------------------------------------
@app.get("/health", summary="Health check endpoint")
def health_check() -> JSONResponse:
    """Stage 0: Return health status code 200 and ok json."""
    return JSONResponse(status_code=200, content={"status": "ok"})


# ---------------------------------------------------------------------------
# Stage 1: Inngest Client & say-hello Worker Function
# ---------------------------------------------------------------------------
inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
)


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    """Stage 1: Sleep 5 seconds in background, then return greeting."""
    await ctx.step.sleep("sleep-5s", datetime.timedelta(seconds=5))
    return "Hello from the background!"


# Serve Inngest functions at /api/inngest
inngest.fast_api.serve(app, inngest_client, [say_hello])
