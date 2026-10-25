"""
Repository Layer — Data Access Gateway (PostgreSQL & SQLite)

Matches `src/repositories/tasks.repository.js` from the FlyRank Layered Architecture
specification. Dynamically delegates to `postgres_repository` when `DATABASE_URL`
is configured for PostgreSQL (Week 3 Assignment A3 / BE-04), or falls back to
SQLite (`database.py` from A2).

The routes (`src/routes/`) and service layer (`src/services/`) remain 100% UNCHANGED,
proving the power of clean layered architecture.
"""

import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Ensure environment variables from .env are available
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def _is_postgres() -> bool:
    url = os.getenv("DATABASE_URL", "")
    return url.startswith("postgres://") or url.startswith("postgresql://")


if _is_postgres():
    from src.repositories import postgres_repository as active_backend
else:
    import database as active_backend


def initialize_storage() -> None:
    """Initialize schema and seed starter data if empty."""
    if _is_postgres():
        active_backend.initialize_storage()
    else:
        active_backend.init_db()


def find_all(
    done: bool | None = None,
    search: str | None = None,
    sort_by_title: bool = False,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return all tasks matching optional filters and pagination."""
    if _is_postgres():
        return active_backend.find_all(
            done=done,
            search=search,
            sort_by_title=sort_by_title,
            limit=limit,
            offset=offset,
        )
    return active_backend.list_tasks_from_db(
        done=done,
        search=search,
        sort_by_title=sort_by_title,
        limit=limit,
        offset=offset,
    )


def find_by_id(task_id: int) -> dict[str, Any] | None:
    """Return a single task dictionary by ID, or None if not found."""
    if _is_postgres():
        return active_backend.find_by_id(task_id)
    return active_backend.get_task_from_db(task_id)


def create(title: str) -> dict[str, Any]:
    """Insert a new task and return the created row."""
    if _is_postgres():
        return active_backend.create(title)
    return active_backend.create_task_in_db(title)


def update(
    task_id: int,
    title: str | None = None,
    done: bool | None = None,
) -> dict[str, Any] | None:
    """Update a task's title and/or done status, or return None if missing."""
    if _is_postgres():
        return active_backend.update(task_id=task_id, title=title, done=done)
    return active_backend.update_task_in_db(task_id=task_id, title=title, done=done)


def remove(task_id: int) -> bool:
    """Delete a task row by ID. Returns True if deleted, False if missing."""
    if _is_postgres():
        return active_backend.remove(task_id)
    return active_backend.delete_task_from_db(task_id)


def get_stats() -> dict[str, int]:
    """Return total, done, and open counts computed via SQL aggregation."""
    if _is_postgres():
        return active_backend.get_stats()
    return active_backend.get_stats_from_db()


def reset() -> list[dict[str, Any]]:
    """Restore table back to the 3 starter tasks."""
    if _is_postgres():
        return active_backend.reset()
    return active_backend.reset_tasks_in_db()


def check_health() -> bool:
    """Perform database health ping."""
    if _is_postgres():
        return active_backend.check_health()
    return True
