"""
Storage Layer — Week 3 (Assignment A2: Connecting Your CRUD to SQLite)

Handles all SQLite database connections, schema setup, seeding, and parameterized
SQL queries so the API layer (`main.py`) remains completely decoupled from SQL.
"""

from pathlib import Path
import sqlite3
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "tasks.db"

STARTER_TASKS = [
    {"id": 1, "title": "Read the FastAPI docs", "done": True},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Test every endpoint with curl", "done": False},
]


def get_connection() -> sqlite3.Connection:
    """Open a connection to tasks.db with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_task(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite row (where `done` is 0 or 1) into a task dict."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def init_db() -> None:
    """Create the tasks table + index if missing, and seed starter tasks once."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        # Stretch Goal: Index on `done` to speed up status filtering queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done)")

        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [(t["title"], int(t["done"])) for t in STARTER_TASKS],
            )


def list_tasks_from_db(
    done: bool | None = None,
    search: str | None = None,
    sort_by_title: bool = False,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Query tasks using SQL WHERE, LIKE, ORDER BY, and LIMIT/OFFSET."""
    query = "SELECT id, title, done FROM tasks"
    conditions: list[str] = []
    params: list[Any] = []

    if done is not None:
        conditions.append("done = ?")
        params.append(int(done))

    if search is not None and search.strip():
        conditions.append("title LIKE ?")
        params.append(f"%{search.strip()}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_by_title:
        query += " ORDER BY title COLLATE NOCASE ASC"
    else:
        query += " ORDER BY id ASC"

    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    elif offset > 0:
        query += " LIMIT -1 OFFSET ?"
        params.append(offset)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_task(row) for row in rows]


def get_task_from_db(task_id: int) -> dict[str, Any] | None:
    """Fetch a single task by primary key ID, or return None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return _row_to_task(row) if row is not None else None


def create_task_in_db(title: str) -> dict[str, Any]:
    """Insert a new task row and return the created task with its assigned ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        new_id = cursor.lastrowid
    return {"id": new_id, "title": title, "done": False}


def update_task_in_db(
    task_id: int,
    title: str | None = None,
    done: bool | None = None,
) -> dict[str, Any] | None:
    """Update an existing task's title and/or done status, or return None if missing."""
    existing = get_task_from_db(task_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]

    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, int(new_done), task_id),
        )
    return {"id": task_id, "title": new_title, "done": new_done}


def delete_task_from_db(task_id: int) -> bool:
    """Delete a task by ID. Returns True if a row was deleted, False if not found."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def get_stats_from_db() -> dict[str, int]:
    """Compute total, done, and open task counts directly in SQL."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done_count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE done = 1"
        ).fetchone()[0]
    return {"total": total, "done": done_count, "open": total - done_count}


def reset_tasks_in_db() -> list[dict[str, Any]]:
    """Restore the tasks table to the original 3 starter tasks in a single transaction."""
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks")
        conn.executemany(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            [(t["id"], t["title"], int(t["done"])) for t in STARTER_TASKS],
        )
    return list_tasks_from_db()
