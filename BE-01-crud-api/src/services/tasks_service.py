"""
Service Layer — Business Rules & Validation (HTTP-Agnostic and SQL-Agnostic)

Matches `src/services/tasks.service.js` from the FlyRank Layered Architecture example:
Enforces all validation and "not found" domain rules, calls the repository layer,
and raises `ValidationError` or `NotFoundError` when a rule is broken.
"""

from typing import Any

from src.errors import NotFoundError, ValidationError
from src.repositories import tasks_repository as repo


def list_tasks(
    done: bool | None = None,
    search: str | None = None,
    sort: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Validate optional query filters and return matching tasks from the repository."""
    if search is not None and not search.strip():
        raise ValidationError("search must not be empty")

    return repo.find_all(
        done=done,
        search=search,
        sort_by_title=(sort == "title"),
        limit=limit,
        offset=offset,
    )


def get_task(task_id: int) -> dict[str, Any]:
    """Return a single task by ID or raise NotFoundError."""
    task = repo.find_by_id(task_id)
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    return task


def create_task(body: Any) -> dict[str, Any]:
    """Validate task creation payload and delegate persistence to the repository."""
    if not isinstance(body, dict):
        raise ValidationError("Title is required and cannot be empty")

    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title is required and cannot be empty")

    return repo.create(title.strip())


def update_task(task_id: int, body: Any) -> dict[str, Any]:
    """Validate task update payload and update the task in the repository."""
    if repo.find_by_id(task_id) is None:
        raise NotFoundError(f"Task {task_id} not found")

    if not isinstance(body, dict) or ("title" not in body and "done" not in body):
        raise ValidationError("Request body must include 'title' and/or 'done'")

    title_val: str | None = None
    done_val: bool | None = None

    if "title" in body:
        if not isinstance(body["title"], str) or not body["title"].strip():
            raise ValidationError("Title cannot be empty")
        title_val = body["title"].strip()

    if "done" in body:
        if not isinstance(body["done"], bool):
            raise ValidationError("'done' must be a boolean")
        done_val = body["done"]

    updated = repo.update(task_id=task_id, title=title_val, done=done_val)
    if updated is None:
        raise NotFoundError(f"Task {task_id} not found")
    return updated


def delete_task(task_id: int) -> None:
    """Delete a task by ID or raise NotFoundError if it does not exist."""
    if not repo.remove(task_id):
        raise NotFoundError(f"Task {task_id} not found")


def get_stats() -> dict[str, int]:
    """Return computed task statistics (total, done, open)."""
    return repo.get_stats()


def reset_tasks() -> dict[str, Any]:
    """Reset the repository to starter tasks and return the reset confirmation."""
    tasks = repo.reset()
    return {"message": "Tasks reset to starter state", "tasks": tasks}
