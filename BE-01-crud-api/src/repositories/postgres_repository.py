"""
Repository Layer — PostgreSQL Data Access (`psycopg` 3)

Week 3 (Assignment A3 / BE-04: Containerize Your Stack)
Implements the exact same interface as the SQLite repository (`tasks_repository.py`)
and the in-memory repository from A1. Routes and services remain 100% untouched.

Every query uses parameterized placeholders (%s) — user inputs are never concatenated
into SQL strings.
"""

import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load .env file from the project directory if present
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DEFAULT_DATABASE_URL = "postgresql://postgres:dev@127.0.0.1:5433/tasks"

STARTER_TASKS = [
    {"title": "Read the FastAPI docs", "done": True},
    {"title": "Build a CRUD API", "done": False},
    {"title": "Test every endpoint with curl", "done": False},
]


def get_database_url() -> str:
    """Retrieve and normalize DATABASE_URL from environment."""
    url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    # SQLAlchemy and older Heroku conventions use postgres://; psycopg requires postgresql://
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def get_connection() -> psycopg.Connection:
    """Open a PostgreSQL connection with dictionary row access."""
    return psycopg.connect(get_database_url(), row_factory=dict_row)


def initialize_storage() -> None:
    """
    Ensure the `tasks` table and starter seed rows exist on application startup.
    Idempotent: safe to run repeatedly across container and app restarts.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);")

            cur.execute("SELECT COUNT(*) FROM tasks;")
            count = cur.fetchone()["count"]
            if count == 0:
                for task in STARTER_TASKS:
                    cur.execute(
                        "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                        (task["title"], task["done"]),
                    )
        conn.commit()


def find_all(
    done: bool | None = None,
    search: str | None = None,
    sort_by_title: bool = False,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return all tasks matching optional filters, search query, and pagination."""
    query = "SELECT id, title, done FROM tasks"
    conditions: list[str] = []
    params: list[Any] = []

    if done is not None:
        conditions.append("done = %s")
        params.append(done)

    if search is not None and search.strip():
        conditions.append("title ILIKE %s")
        params.append(f"%{search.strip()}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_by_title:
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY id ASC"

    if limit is not None:
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
    elif offset > 0:
        query += " OFFSET %s"
        params.append(offset)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def find_by_id(task_id: int) -> dict[str, Any] | None:
    """Return a single task dictionary by ID, or None if not found."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s;",
                (task_id,),
            )
            row = cur.fetchone()
            return dict(row) if row is not None else None


def create(title: str) -> dict[str, Any]:
    """Insert a new task into PostgreSQL and return the created row."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (title, False),
            )
            created = cur.fetchone()
        conn.commit()
        return dict(created)


def update(
    task_id: int,
    title: str | None = None,
    done: bool | None = None,
) -> dict[str, Any] | None:
    """Update a task's title and/or done status in PostgreSQL, returning None if missing."""
    existing = find_by_id(task_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (new_title, new_done, task_id),
            )
            updated = cur.fetchone()
        conn.commit()
        return dict(updated) if updated is not None else None


def remove(task_id: int) -> bool:
    """Delete a task by ID. Returns True if a row was deleted, False if missing."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted


def get_stats() -> dict[str, int]:
    """Compute total, done, and open counts directly via PostgreSQL aggregation."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM tasks;")
            total = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS done_count FROM tasks WHERE done = TRUE;")
            done_count = cur.fetchone()["done_count"]

    return {"total": total, "done": done_count, "open": total - done_count}


def reset() -> list[dict[str, Any]]:
    """Restore the PostgreSQL table back to the 3 starter tasks."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks;")
            cur.execute("ALTER SEQUENCE tasks_id_seq RESTART WITH 1;")
            for task in STARTER_TASKS:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                    (task["title"], task["done"]),
                )
        conn.commit()
    return find_all()


def check_health() -> bool:
    """Verify database connectivity with a lightweight ping (SELECT 1)."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return cur.fetchone() is not None
    except Exception:
        return False
