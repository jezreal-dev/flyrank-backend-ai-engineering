# ==============================================================================
# FLYRANK BACKEND AI ENGINEERING TRACK
# - Week 1/2 (Assignment A1 / BE-01): Build Your First CRUD API (FastAPI)
# - Week 3   (Assignment A2 / BE-02): Connecting Your CRUD to SQLite (tasks.db)
# ==============================================================================

from pathlib import Path  # [Week 3 · Stage 0] Used to resolve the path to tasks.db on disk
import sqlite3            # [Week 3 · Stage 0] Python's built-in serverless SQLite driver
from typing import Any    # [Week 1/2 · Stage 3] Type hints for request payloads
from fastapi import Body, FastAPI, Query, Response  # [Week 1/2] Core FastAPI utilities
from fastapi.responses import JSONResponse          # [Week 1/2 · Stage 2] Custom {"error": "..."} responses
import uvicorn            # [Week 1/2 · Stage 0] ASGI server to run the FastAPI app

# [Week 1/2 · Stage 0 & Stage 5] Initialize FastAPI application with Swagger UI metadata
app = FastAPI(
    title="Task API",
    version="1.0",
    description="A clean SQLite-backed CRUD API for managing tasks (Assignment BE-01 / W3-A2).",
)

# ------------------------------------------------------------------------------
# [Week 3 · Stage 0] DATABASE SETUP & SEEDING (SQLite)
# ------------------------------------------------------------------------------
# Path to the single-file SQLite database stored alongside main.py
DB_PATH = Path(__file__).resolve().parent / "tasks.db"

# [Week 1/2 · Stage 2] Original 3 starter tasks (now also used to seed SQLite in Week 3)
STARTER_TASKS = [
    {"id": 1, "title": "Read the FastAPI docs", "done": True},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Test every endpoint with curl", "done": False},
]


def get_connection() -> sqlite3.Connection:
    """[Week 3 · Stage 0] Open a connection to tasks.db (creates the file if missing)."""
    conn = sqlite3.connect(DB_PATH)
    # sqlite3.Row lets us access columns by name like a dictionary: row["title"]
    conn.row_factory = sqlite3.Row
    return conn


def row_to_task(row: sqlite3.Row) -> dict[str, Any]:
    """[Week 3 · Stage 1] Convert a SQLite row (where done is 0/1) into the API's JSON dict shape."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def init_db() -> None:
    """[Week 3 · Stage 0] Create the tasks table if missing and seed 3 tasks only when empty."""
    # 'with get_connection() as conn:' automatically wraps these SQL statements in a transaction
    with get_connection() as conn:
        # 1. Create the 'tasks' table if it does not already exist on disk
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        # 2. Count existing rows so restarting the server never duplicates starter tasks
        row_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if row_count == 0:
            # 3. Seed the 3 starter tasks using parameterized placeholders (?, ?)
            # Note: SQLite stores booleans as integers (True -> 1, False -> 0)
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [(t["title"], int(t["done"])) for t in STARTER_TASKS],
            )


# [Week 3 · Stage 0] Run database initialization and seeding when the app starts
init_db()
# Note: The Week 1/2 in-memory `tasks` list has been completely retired in Week 3 · Stage 3!


# ------------------------------------------------------------------------------
# [Week 1/2 · Stage 0 & Stage 1] SYSTEM & HEALTH ENDPOINTS
# ------------------------------------------------------------------------------
@app.get("/", summary="API root metadata", tags=["System"])
def read_root():
    """[Week 1/2 · Stage 1] Return the API name, version, and primary resource endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", tags=["System"])
def health_check():
    """[Week 1/2 · Stage 1] Return service health status."""
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# [Week 3 · Stage 1] DATABASE READ ENDPOINTS (Replaces Week 1/2 in-memory reads)
# ------------------------------------------------------------------------------
@app.get("/tasks", summary="List all tasks", tags=["Tasks"])
def get_tasks(
    done: bool | None = Query(default=None, description="Filter by completion status (true/false)"),
    search: str | None = Query(default=None, description="Case-insensitive keyword search in task title"),
    limit: int | None = Query(default=None, ge=0, description="Maximum number of tasks to return"),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip for pagination"),
):
    """[Week 3 · Stage 1] Fetch all tasks from SQLite (`SELECT * FROM tasks`) with optional filters."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    result = [row_to_task(row) for row in rows]

    # [Week 1/2 · Stage 5] Optional query filters (will be upgraded to SQL WHERE/LIKE in Week 3 Extras)
    if done is not None:
        result = [t for t in result if t["done"] is done]
    if search is not None and search.strip():
        keyword = search.strip().lower()
        result = [t for t in result if keyword in t["title"].lower()]
    if offset:
        result = result[offset:]
    if limit is not None:
        result = result[:limit]
    return result


@app.get("/tasks/{id}", summary="Get a single task by ID", tags=["Tasks"])
def get_task(id: int):
    """[Week 3 · Stage 1] Fetch one task by `id` using a parameterized query (`WHERE id = ?`)."""
    with get_connection() as conn:
        # '?' is a parameterized placeholder: passes (id,) safely as data, preventing SQL injection
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if row is None:
        # [Week 1/2 · Stage 2] Keep the exact 404 error contract
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    return row_to_task(row)


# ------------------------------------------------------------------------------
# [Week 3 · Stage 2] DATABASE CREATE ENDPOINT (Replaces Week 1/2 list.append)
# ------------------------------------------------------------------------------
@app.post("/tasks", status_code=201, summary="Create a new task", tags=["Tasks"])
def create_task(
    payload: dict[str, Any] | None = Body(
        default=None,
        openapi_examples={
            "normal": {
                "summary": "A valid new task",
                "value": {"title": "Ship BE-01 assignment"},
            }
        },
    )
):
    """[Week 3 · Stage 2] Validate `title` (Week 1/2 rules) and insert new row into SQLite."""
    # [Week 1/2 · Stage 3] Validation rules remain 100% unchanged
    if not isinstance(payload, dict):
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"},
        )

    # [Week 3 · Stage 2] Insert into tasks.db using parameterized placeholders (?, ?)
    clean_title = title.strip()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (clean_title, 0),
        )
        # SQLite automatically assigns the next INTEGER PRIMARY KEY id
        new_id = cursor.lastrowid

    return {"id": new_id, "title": clean_title, "done": False}


# ------------------------------------------------------------------------------
# [Week 3 · Stage 3] DATABASE UPDATE & DELETE ENDPOINTS (Replaces Week 1/2 in-memory mutations)
# ------------------------------------------------------------------------------
@app.put("/tasks/{id}", summary="Update an existing task", tags=["Tasks"])
def update_task(
    id: int,
    payload: dict[str, Any] | None = Body(
        default=None,
        openapi_examples={
            "update_both": {
                "summary": "Update title and completion status",
                "value": {"title": "Build a production CRUD API", "done": True},
            }
        },
    ),
):
    """[Week 3 · Stage 3] Update a task's `title` and/or `done` in SQLite (`UPDATE tasks SET ... WHERE id = ?`)."""
    # [Week 3 · Stage 3] 1. Check if the task exists in tasks.db
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if row is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

    # [Week 1/2 · Stage 4] 2. Validate request body (rules remain 100% identical to Assignment 1)
    if not isinstance(payload, dict) or ("title" not in payload and "done" not in payload):
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must include 'title' and/or 'done'"},
        )

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title cannot be empty"},
            )
    if "done" in payload:
        if not isinstance(payload["done"], bool):
            return JSONResponse(
                status_code=400,
                content={"error": "'done' must be a boolean"},
            )

    # [Week 3 · Stage 3] 3. Merge updated fields with existing row values and run SQL UPDATE
    new_title = payload["title"].strip() if "title" in payload else row["title"]
    new_done = payload["done"] if "done" in payload else bool(row["done"])

    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, int(new_done), id),
        )

    return {"id": id, "title": new_title, "done": new_done}


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task by ID", tags=["Tasks"])
def delete_task(id: int):
    """[Week 3 · Stage 3] Delete a task from SQLite (`DELETE FROM tasks WHERE id = ?`)."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
        deleted_rows = cursor.rowcount

    # If rowcount is 0, no row matched that ID -> return 404
    if deleted_rows == 0:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    return Response(status_code=204)


# ------------------------------------------------------------------------------
# [Week 1/2 · Stage 5 & Week 3] EXTRAS ENDPOINTS (Backed by SQLite)
# ------------------------------------------------------------------------------
@app.get("/stats", summary="Get task statistics", tags=["Extras"])
def get_stats():
    """[Week 1/2 · Stage 5 / Week 3] Return counts of total, completed (`done`), and remaining (`open`) tasks."""
    with get_connection() as conn:
        rows = conn.execute("SELECT done FROM tasks").fetchall()
    total = len(rows)
    done_count = sum(1 for r in rows if r["done"])
    open_count = total - done_count
    return {"total": total, "done": done_count, "open": open_count}


@app.post("/reset", summary="Reset tasks to starter data", tags=["Extras"])
def reset_tasks():
    """[Week 1/2 · Stage 5 / Week 3] Restore the SQLite `tasks` table to the original 3 starter tasks."""
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks")
        conn.executemany(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            [(t["id"], t["title"], int(t["done"])) for t in STARTER_TASKS],
        )
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    return {"message": "Tasks reset to starter state", "tasks": [row_to_task(r) for r in rows]}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
