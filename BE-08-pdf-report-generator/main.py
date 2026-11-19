import os
import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from report_data import get_report_data, DB_PATH
from renderer import render_report_to_pdf, REPORTS_DIR

app = FastAPI(
    title="BE-08: PDF Report Generator API",
    description="Query SQL, render to PDF, and serve by link with idempotency and background job capability.",
    version="1.0.0",
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
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/reports")
def generate_report(payload: Optional[ReportCreateRequest] = None, response: Response = None):
    force = payload.force if payload else False
    today_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Stage 5 Idempotency check:
    # If a report was already generated today and force is False, return existing report (200 OK)
    if not force:
        cursor.execute(
            """
            SELECT id, path, created_at 
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
                "file": f"/reports/{existing['id']}/file",
                "message": "Report already generated today (idempotent result)",
                "created_at": existing["created_at"],
            }

    # Step 1: Query SQL data
    data = get_report_data()

    # Step 2: Reserve record ID to name file deterministically
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)",
        ("pending", created_at),
    )
    report_id = cursor.lastrowid
    conn.commit()

    # Step 3: Render to reports/<id>.pdf
    filename = f"sales-report-{report_id}-{today_date}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)
    render_report_to_pdf(data, pdf_path)

    # Step 4: Update database row with file path
    cursor.execute("UPDATE reports SET path = ? WHERE id = ?", (pdf_path, report_id))
    conn.commit()
    conn.close()

    if response:
        response.status_code = status.HTTP_201_CREATED

    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file",
        "created_at": created_at,
    }


@app.get("/reports")
def list_reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, created_at FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    reports = []
    for r in rows:
        reports.append({
            "id": r["id"],
            "created_at": r["created_at"],
            "file": f"/reports/{r['id']}/file",
            "exists": os.path.exists(r["path"]),
        })
    return {"reports": reports}


@app.get("/reports/{report_id}")
def get_report_metadata(report_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found")

    return {
        "id": row["id"],
        "path": row["path"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file",
    }


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not os.path.exists(row["path"]):
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
