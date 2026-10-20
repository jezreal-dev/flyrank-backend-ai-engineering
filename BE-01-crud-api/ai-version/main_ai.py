"""
AI Single-Shot Version (Quarantined in ai-version/ for Stage 6 Comparison)
"""

from pathlib import Path
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import uvicorn

app = FastAPI(title="Task API (AI Single-Shot SQLite Version)", version="1.0")

DB_FILE = Path(__file__).resolve().parent / "tasks_ai.db"

INITIAL_TASKS = [
    ("Read the FastAPI docs", 1),
    ("Build a CRUD API", 0),
    ("Test every endpoint with curl", 0),
]


def db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_db():
    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0)"
    )
    cur.execute("SELECT COUNT(*) FROM tasks")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", INITIAL_TASKS)
    conn.commit()
    conn.close()


setup_db()


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title is required and cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v is not None else None


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Title is required and cannot be empty"},
    )


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(
    done: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: Optional[int] = Query(default=None, ge=0),
    offset: int = Query(default=0, ge=0),
):
    conn = db_conn()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    tasks = [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]
    filtered = [
        t
        for t in tasks
        if (done is None or t["done"] == done)
        and (not search or search.lower() in t["title"].lower())
    ]
    return filtered[offset : offset + limit if limit is not None else None]


@app.get("/tasks/{id}")
def retrieve_task(id: int):
    conn = db_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    conn = db_conn()
    cur = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (body.title, 0))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "title": body.title, "done": False}


@app.put("/tasks/{id}")
def update_task(id: int, body: TaskUpdate):
    conn = db_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    if body.title is None and body.done is None:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Request body must include 'title' and/or 'done'"
        )
    new_title = body.title if body.title is not None else row["title"]
    new_done = int(body.done) if body.done is not None else row["done"]
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done, id)
    )
    conn.commit()
    conn.close()
    return {"id": id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    conn = db_conn()
    cur = conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return Response(status_code=204)


@app.get("/stats")
def stats():
    conn = db_conn()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    done_count = sum(1 for r in rows if r["done"])
    return {"total": len(rows), "done": done_count, "open": len(rows) - done_count}


@app.post("/reset")
def reset():
    conn = db_conn()
    conn.execute("DELETE FROM tasks")
    conn.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", INITIAL_TASKS)
    conn.commit()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return {
        "message": "Tasks reset to starter state",
        "tasks": [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
