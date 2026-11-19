"""
BE-06 / Assignment A7: Your First Background Job
FastAPI application with Inngest background job orchestration.

Pattern: Accept Fast (202 Accepted) -> Background Worker (Inngest) -> Status Endpoint (Polling)
"""

import datetime
import os
from pathlib import Path
import uuid
from typing import Any

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
import inngest
import inngest.fast_api

app = FastAPI(
    title="Report API - Background Jobs",
    description="FastAPI service demonstrating the 202 Accepted + background worker + polling pattern with Inngest.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-Memory Storage & Outbox
# ---------------------------------------------------------------------------
# Format: {report_id: {"id": str, "topic": str, "status": "pending"|"done"|"failed", "result": Optional[str], "created_at": str}}
reports: dict[str, dict[str, Any]] = {}

OUTBOX_DIR = Path(__file__).parent / "outbox"
OUTBOX_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Stage 0: Health Check Endpoint
# ---------------------------------------------------------------------------
@app.get("/health", summary="Health check endpoint", tags=["System"])
def health_check() -> JSONResponse:
    """Stage 0: Return health status code 200 and ok json."""
    return JSONResponse(status_code=200, content={"status": "ok"})


# ---------------------------------------------------------------------------
# Inngest Client Setup (Stage 1)
# ---------------------------------------------------------------------------
inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
)


# ---------------------------------------------------------------------------
# Stage 1: say-hello Worker Function
# ---------------------------------------------------------------------------
@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    """Stage 1: Sleep 5 seconds in background, then return greeting."""
    await ctx.step.sleep("sleep-5s", datetime.timedelta(seconds=5))
    return "Hello from the background!"


# ---------------------------------------------------------------------------
# Stage 3: Jobs Fail. Watch the Retry & Bad Input Rejection
# ---------------------------------------------------------------------------
# Requirement: A wrong input must be rejected at the door; only a wrong moment deserves a retry.
# - topic == 'fail': raises RuntimeError('The report oven is broken!') and retries with backoff (retries=2).
# - missing topic: returns 400 Bad Request immediately at the door, with no Inngest event dispatched.
@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,  # Stage 3: Retry up to 2 times (3 attempts total) with exponential backoff
    concurrency=[inngest.Concurrency(limit=2)],  # Stretch: concurrency limit of 2
)
async def make_report(ctx: inngest.Context) -> dict[str, Any]:
    """
    Stage 2: Asynchronous report generation.
    - Durable Step 1: Sleep 8 seconds (stand-in for slow AI / heavy report generation).
    - Durable Step 2: Build report result, update in-memory state, write outbox proof.
    Stage 3:
    - If topic == 'fail', raises an exception to trigger automated retry with backoff.
    """
    event_data = ctx.event.data or {}
    report_id = event_data.get("id")
    topic = event_data.get("topic", "")

    # Step 1: Durable sleep (8 seconds)
    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))

    # Step 2: Build report
    async def build() -> dict[str, Any]:
        # Stage 3: Failure simulation to demonstrate retries and backoff
        if str(topic).strip().lower() == "fail":
            if report_id in reports:
                reports[report_id]["status"] = "failed"
                reports[report_id]["error"] = "The report oven is broken!"
            raise RuntimeError("The report oven is broken!")

        # Stretch: Idempotency check — survive running twice without re-building
        existing = reports.get(report_id)
        if existing and existing.get("status") == "done":
            return existing

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result_text = (
            f"Comprehensive Market & Intelligence Report for topic: '{topic}'. "
            f"Synthesized from 12 background sources with 99.4% confidence."
        )

        report_record = {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "result": result_text,
            "completed_at": now,
        }
        reports[report_id] = report_record

        # Optional Extra: write outbox file stand-in for email notification
        outbox_file = OUTBOX_DIR / f"{report_id}.txt"
        outbox_file.write_text(
            f"To: user@example.com\nSubject: Your Report '{topic}' is Ready\n\n{result_text}\n"
        )

        return report_record

    return await ctx.step.run("build-report", build)


# ---------------------------------------------------------------------------
# Stage 4: The Clock Knocks - First Cron Job (heartbeat)
# ---------------------------------------------------------------------------
# Cron Expression: * * * * * (runs on schedule every minute on the clock alone)
# Answers for README:
# - Run every day at 08:00: 0 8 * * *
# - Run every Sunday at 22:00: 0 22 * * 0
@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),  # Runs every minute on the clock
)
async def heartbeat(ctx: inngest.Context) -> dict[str, int]:
    """
    Stage 4: Periodic cron heartbeat running on schedule (* * * * *).
    Logs summary count of reports across states: pending, done, failed.
    """
    async def log_summary() -> dict[str, int]:
        pending_count = sum(1 for r in reports.values() if r.get("status") == "pending")
        done_count = sum(1 for r in reports.values() if r.get("status") == "done")
        failed_count = sum(1 for r in reports.values() if r.get("status") == "failed")

        summary = {
            "pending": pending_count,
            "done": done_count,
            "failed": failed_count,
            "total": len(reports),
        }
        print(
            f"[HEARTBEAT CRON] Reports Status -> Pending: {pending_count} | Done: {done_count} | Failed: {failed_count} | Total: {len(reports)}"
        )
        return summary

    return await ctx.step.run("log-summary", log_summary)


# ---------------------------------------------------------------------------
# Stage 2: POST /reports (Accept Fast - 202 Accepted)
# ---------------------------------------------------------------------------
@app.post("/reports", status_code=202, summary="Create a new report background job", tags=["Reports"])
async def create_report(payload: dict[str, Any] = Body(default=None)) -> JSONResponse:
    """
    Stage 2: The Fast Door.
    - Validates topic (Stage 3: rejects missing/empty topic with 400 immediately).
    - Creates order ticket with status 'pending'.
    - Dispatches 'report/requested' event to Inngest.
    - Returns 202 Accepted in milliseconds without blocking.
    """
    # Stage 3: Bad input rejected at the door — never send event for bad input!
    if not isinstance(payload, dict):
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})

    topic = payload.get("topic")
    if not isinstance(topic, str) or not topic.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Topic is required and cannot be empty"},
        )

    topic_clean = topic.strip()
    report_id = uuid.uuid4().hex[:8]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Save initial pending state
    reports[report_id] = {
        "id": report_id,
        "topic": topic_clean,
        "status": "pending",
        "created_at": now,
    }

    # Dispatch event to background worker
    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": topic_clean},
        )
    )

    # Return 202 Accepted immediately (<50ms)
    return JSONResponse(
        status_code=202,
        content={"id": report_id, "status": "pending"},
    )


# ---------------------------------------------------------------------------
# Stage 2: GET /reports/{id} (Status Polling Endpoint)
# ---------------------------------------------------------------------------
@app.get("/reports/{report_id}", summary="Get report status and result", tags=["Reports"])
def get_report_status(report_id: str) -> JSONResponse:
    """
    Stage 2: Status Polling Endpoint.
    - Unknown ID -> 404 Not Found.
    - First reports 'pending', later reports 'done' + result (or 'failed' + error).
    """
    report = reports.get(report_id)
    if not report:
        return JSONResponse(
            status_code=404,
            content={"error": f"Report '{report_id}' not found"},
        )

    return JSONResponse(status_code=200, content=report)


# ---------------------------------------------------------------------------
# Optional Extra: GET /reports (List all reports)
# ---------------------------------------------------------------------------
@app.get("/reports", summary="List all reports", tags=["Reports"])
def list_reports() -> JSONResponse:
    """Optional Extra: Returns all reports and their current statuses."""
    return JSONResponse(status_code=200, content=list(reports.values()))


# ---------------------------------------------------------------------------
# Mount Inngest Serve Handler
# ---------------------------------------------------------------------------
inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report, heartbeat],
)
