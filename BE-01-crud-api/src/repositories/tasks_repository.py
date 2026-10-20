"""
Repository Layer — Data Access Only (`tasks.db` SQLite)

Matches `src/repositories/tasks.repository.js` from the FlyRank Layered Architecture
example, upgraded for Week 3 (Assignment A2) to persist tasks in SQLite (`tasks.db`).
The routes and service layers never import `sqlite3` or write SQL—they only call
`find_all`, `find_by_id`, `create`, `update`, `remove`, `get_stats`, and `reset`.
"""

from typing import Any

from database import (
    create_task_in_db,
    delete_task_from_db,
    get_stats_from_db,
    get_task_from_db,
    init_db,
    list_tasks_from_db,
    reset_tasks_in_db,
    update_task_in_db,
)


def initialize_storage() -> None:
    """Ensure the SQLite `tasks` table and starter seed rows exist."""
    init_db()


def find_all(
    done: bool | None = None,
    search: str | None = None,
    sort_by_title: bool = False,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Return all tasks matching the optional SQL filters and pagination."""
    return list_tasks_from_db(
        done=done,
        search=search,
        sort_by_title=sort_by_title,
        limit=limit,
        offset=offset,
    )


def find_by_id(task_id: int) -> dict[str, Any] | None:
    """Return a single task dictionary by ID, or None if not found."""
    return get_task_from_db(task_id)


def create(title: str) -> dict[str, Any]:
    """Insert a new task into SQLite and return the created row."""
    return create_task_in_db(title)


def update(
    task_id: int,
    title: str | None = None,
    done: bool | None = None,
) -> dict[str, Any] | None:
    """Update a task's title and/or done status in SQLite, or return None if missing."""
    return update_task_in_db(task_id=task_id, title=title, done=done)


def remove(task_id: int) -> bool:
    """Delete a task row by ID. Returns True if deleted, False if missing."""
    return delete_task_from_db(task_id)


def get_stats() -> dict[str, int]:
    """Return total, done, and open counts computed via SQL COUNT(*)."""
    return get_stats_from_db()


def reset() -> list[dict[str, Any]]:
    """Restore the SQLite table back to the 3 starter tasks."""
    return reset_tasks_in_db()
