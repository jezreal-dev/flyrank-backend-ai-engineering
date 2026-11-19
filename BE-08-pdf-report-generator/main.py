import os
import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import inngest
import inngest.fast_api

from report_data import get_report_data, DB_PATH
from renderer import render_report_to_pdf, REPORTS_DIR

app = FastAPI(
    title="BE-08: PDF Report Generator API",
    description="Query SQL, render to PDF, and serve by link with idempotency and Inngest background job capability.",
    version="1.0.0",
)

inngest_client = inngest.Inngest(
    app_id="pdf-report-generator",
    is_production=False,
)


class ReportCreateRequest(BaseModel):
    force: Optional[bool] = False


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def startup_event():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'done',
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute("PRAGMA table_info(reports)")
    columns = [col[1] for col in cursor.fetchall()]
    if "status" not in columns:
        cursor.execute("ALTER TABLE reports ADD COLUMN status TEXT NOT NULL DEFAULT 'done'")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Inngest Background Job & Cron Stretch (A7 Pattern)
# ---------------------------------------------------------------------------
@inngest_client.create_function(
    fn_id="generate-pdf-report-job",
    trigger=inngest.TriggerEvent(event="report/generate"),
)
async def generate_pdf_report_job(ctx: inngest.Context) -> dict:
    report_id = ctx.event.data.get("report_id")

    # Step 1: Query Aggregation Data
    async def step_query():
        return get_report_data()

    data = await ctx.step.run("query-sql-data", step_query)

    # Step 2: Render PDF
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"sales-report-{report_id}-{today_date}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)

    async def step_render():
        render_report_to_pdf(data, pdf_path)
        return {"path": pdf_path, "size_bytes": os.path.getsize(pdf_path)}

    render_result = await ctx.step.run("render-html-to-pdf", step_render)

    # Step 3: Store & Update DB Status to 'done'
    async def step_store():
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE reports SET path = ?, status = 'done' WHERE id = ?", (pdf_path, report_id))
        conn.commit()
        conn.close()
        return {"status": "done", "file": f"/reports/{report_id}/file"}

    return await ctx.step.run("store-artifact-and-finalize", step_store)


@inngest_client.create_function(
    fn_id="weekly-monday-report-cron",
    trigger=inngest.TriggerCron(cron="0 8 * * 1"),
)
async def weekly_monday_report_cron(ctx: inngest.Context) -> dict:
    """Cron: Generates sales report automatically every Monday at 08:00 AM UTC."""
    today_date = datetime.now().strftime("%Y-%m-%d")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO reports (path, status, created_at) VALUES (?, 'pending', ?)", ("pending", created_at))
    cron_report_id = c.lastrowid
    conn.commit()
    conn.close()

    data = get_report_data()
    filename = f"sales-report-cron-{cron_report_id}-{today_date}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)
    render_report_to_pdf(data, pdf_path)

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE reports SET path = ?, status = 'done' WHERE id = ?", (pdf_path, cron_report_id))
    conn.commit()
    conn.close()

    return {"message": "Monday 08:00 AM scheduled report generated successfully", "report_id": cron_report_id}


# Mount Inngest endpoint
inngest.fast_api.serve(app, inngest_client, [generate_pdf_report_job, weekly_monday_report_cron])


# ---------------------------------------------------------------------------
# HTTP Endpoints (Stages 0, 4, 5)
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/reports")
def generate_report(payload: Optional[ReportCreateRequest] = None, response: Response = None):
    """
    Synchronous generation endpoint (Stage 4 & 5).
    Runs query -> render -> store pipeline, returns 201 Created.
    Idempotent: if a report was already generated today, returns existing ID with 200 OK.
    """
    force = payload.force if payload else False
    today_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Stage 5 Idempotency check:
    if not force:
        cursor.execute(
            """
            SELECT id, path, status, created_at 
            FROM reports 
            WHERE substr(created_at, 1, 10) = ? 
            ORDER BY id DESC LIMIT 1
            """,
            (today_date,),
        )
        existing = cursor.fetchone()
        if existing and os.path.exists(existing["path"]):
            conn.close()
            if response:
                response.status_code = status.HTTP_200_OK
            return {
                "id": existing["id"],
                "status": existing["status"],
                "file": f"/reports/{existing['id']}/file",
                "message": "Report already generated today (idempotent result)",
                "created_at": existing["created_at"],
            }

    # Step 1: Query SQL data
    data = get_report_data()

    # Step 2: Reserve record ID to name file deterministically
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO reports (path, status, created_at) VALUES (?, 'done', ?)",
        ("pending", created_at),
    )
    report_id = cursor.lastrowid
    conn.commit()

    # Step 3: Render to reports/<id>.pdf
    filename = f"sales-report-{report_id}-{today_date}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)
    render_report_to_pdf(data, pdf_path)

    # Step 4: Update database row with file path
    cursor.execute("UPDATE reports SET path = ?, status = 'done' WHERE id = ?", (pdf_path, report_id))
    conn.commit()
    conn.close()

    if response:
        response.status_code = status.HTTP_201_CREATED

    return {
        "id": report_id,
        "status": "done",
        "file": f"/reports/{report_id}/file",
        "created_at": created_at,
    }


def execute_report_job_sync(report_id: int):
    """Fallback runner for background job when Inngest dev server is not connected."""
    try:
        data = get_report_data()
        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"sales-report-{report_id}-{today_date}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, filename)
        render_report_to_pdf(data, pdf_path)
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE reports SET path = ?, status = 'done' WHERE id = ?", (pdf_path, report_id))
        conn.commit()
        conn.close()
    except Exception as e:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE reports SET status = 'failed' WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()


@app.post("/reports/async", status_code=status.HTTP_202_ACCEPTED)
async def generate_report_async(background_tasks: BackgroundTasks, payload: Optional[ReportCreateRequest] = None):
    """
    Stretch: Asynchronous background job generation (A7 Pattern).
    Returns 202 Accepted immediately with status 'pending'.
    Inngest executes query -> render -> store in the background (with FastAPI background task fallback).
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (path, status, created_at) VALUES (?, 'pending', ?)",
        ("pending", created_at),
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Attempt to dispatch to Inngest background event queue
    try:
        await inngest_client.send(
            inngest.Event(
                name="report/generate",
                data={"report_id": report_id},
            )
        )
        dispatch_mode = "inngest"
    except Exception:
        # Fallback to local background task if Inngest dev daemon is not active
        background_tasks.add_task(execute_report_job_sync, report_id)
        dispatch_mode = "background_worker"

    return {
        "id": report_id,
        "status": "pending",
        "file": f"/reports/{report_id}/file",
        "dispatch_mode": dispatch_mode,
        "message": "Report generation enqueued. Poll GET /reports/:id for status completion.",
        "created_at": created_at,
    }


@app.get("/reports")
def list_reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, status, created_at FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    reports = []
    for r in rows:
        reports.append({
            "id": r["id"],
            "status": r["status"],
            "created_at": r["created_at"],
            "file": f"/reports/{r['id']}/file",
            "exists": os.path.exists(r["path"]),
        })
    return {"reports": reports}


@app.get("/reports/{report_id}")
def get_report_metadata(report_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, status, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found")

    return {
        "id": row["id"],
        "status": row["status"],
        "path": row["path"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file",
    }


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, status FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found")

    if row["status"] == "pending":
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"id": row["id"], "status": "pending", "message": "Report is still being rendered in the background. Please retry shortly."},
        )

    if not os.path.exists(row["path"]):
        raise HTTPException(status_code=404, detail=f"PDF file for report #{report_id} not found on disk")

    download_filename = os.path.basename(row["path"])
    return FileResponse(
        path=row["path"],
        media_type="application/pdf",
        filename=download_filename,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
