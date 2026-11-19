"""
Quarantined AI-Generated Version of Background Job API (Stage 6 Bonus Rematch)

Prompt used to generate this implementation:
"Build a production-grade FastAPI service using Inngest for background jobs.
Requirements:
1. GET /health returning 200 OK.
2. Inngest client with app_id 'report-api' and serve endpoint at /api/inngest.
3. say-hello function triggered by test/hello that sleeps 5s and returns greeting.
4. POST /reports that accepts {'topic': str}, validates that topic exists (400 if missing),
   saves to in-memory dict with status 'pending', dispatches 'report/requested' event,
   and immediately returns 202 Accepted with {'id': id, 'status': 'pending'}.
5. make-report background function triggered by 'report/requested' with 2 steps:
   - step.sleep('do-the-slow-work', 8s)
   - step.run('build-report') that sets status to 'done'. If topic == 'fail', raise an error.
   Configure retries to 2.
6. GET /reports/{id} status endpoint returning 404 for unknown IDs, or the saved report.
7. heartbeat cron function running on '* * * * *' schedule that logs summary counts."
"""

import asyncio
from datetime import timedelta
import uuid
from typing import Any, Dict

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
import inngest
import inngest.fast_api

app = FastAPI(title="AI-Generated Report API")
client = inngest.Inngest(app_id="report-api", is_production=False)

reports_db: Dict[str, Dict[str, Any]] = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello_fn(ctx: inngest.Context):
    await ctx.step.sleep("sleep-5s", timedelta(seconds=5))
    return "Hello from the background!"


@client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report_fn(ctx: inngest.Context):
    data = ctx.event.data or {}
    report_id = data.get("id")
    topic = data.get("topic")

    await ctx.step.sleep("do-the-slow-work", timedelta(seconds=8))

    async def _build():
        if topic == "fail":
            raise ValueError("The report oven is broken!")
        record = {
            "id": report_id,
            "topic": topic,
            "status": "done",
            "result": f"Report for {topic}",
        }
        reports_db[report_id] = record
        return record

    return await ctx.step.run("build-report", _build)


@client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat_fn(ctx: inngest.Context):
    async def _log():
        pending = sum(1 for r in reports_db.values() if r.get("status") == "pending")
        done = sum(1 for r in reports_db.values() if r.get("status") == "done")
        failed = sum(1 for r in reports_db.values() if r.get("status") == "failed")
        print(f"[Cron Heartbeat] Pending: {pending}, Done: {done}, Failed: {failed}")
        return {"pending": pending, "done": done, "failed": failed}

    return await ctx.step.run("log", _log)


@app.post("/reports", status_code=202)
async def create_report(payload: dict = Body(None)):
    if not payload or not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Missing request body")
    topic = payload.get("topic")
    if not topic or not str(topic).strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    report_id = str(uuid.uuid4())[:8]
    reports_db[report_id] = {
        "id": report_id,
        "topic": topic,
        "status": "pending",
    }

    await client.send(
        inngest.Event(name="report/requested", data={"id": report_id, "topic": topic})
    )

    return JSONResponse(
        status_code=202,
        content={"id": report_id, "status": "pending"},
    )


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


inngest.fast_api.serve(
    app,
    client,
    [say_hello_fn, make_report_fn, heartbeat_fn],
)
