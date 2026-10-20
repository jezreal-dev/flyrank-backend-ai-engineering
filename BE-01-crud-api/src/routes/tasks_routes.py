"""
Route (HTTP) Layer — Thin Translator Between HTTP and `tasks_service`

Matches `src/routes/tasks.routes.js` from the FlyRank Layered Architecture example:
Each route handler does only three things:
1. Read query/path/body parameters from the HTTP request
2. Call `tasks_service`
3. Return the HTTP status code and JSON response
Domain errors (`ValidationError` -> 400, `NotFoundError` -> 404) are handled
centrally by `src/middleware/error_handler.py`.
"""

from typing import Any
from fastapi import APIRouter, Body, Query, Response

from src.services import tasks_service as service

router = APIRouter()


@router.get("/tasks", summary="List all tasks", tags=["Tasks"])
def get_tasks(
    done: bool | None = Query(default=None, description="Filter by completion status (true/false)"),
    search: str | None = Query(default=None, description="Search keyword in task title (SQL LIKE)"),
    sort: str | None = Query(default=None, description="Pass 'title' to sort alphabetically"),
    limit: int | None = Query(default=None, ge=0, description="Maximum number of tasks to return"),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip for pagination"),
):
    """Retrieve tasks with optional filtering, sorting, and pagination."""
    return service.list_tasks(done=done, search=search, sort=sort, limit=limit, offset=offset)


@router.get("/stats", summary="Get task statistics", tags=["Extras"])
def get_stats():
    """Return total, completed (`done`), and remaining (`open`) counts."""
    return service.get_stats()


@router.post("/reset", summary="Reset tasks to starter data", tags=["Extras"])
def reset_tasks():
    """Restore the SQLite tasks table to the original 3 starter tasks."""
    return service.reset_tasks()


@router.post("/tasks", status_code=201, summary="Create a new task", tags=["Tasks"])
def create_task(
    payload: dict[str, Any] | None = Body(
        default=None,
        openapi_examples={
            "normal": {
                "summary": "A valid new task",
                "value": {"title": "Ship W3-A2 SQLite migration"},
            }
        },
    ),
):
    """Create a new task and return HTTP 201."""
    return service.create_task(payload)


@router.get("/tasks/{id}", summary="Get a single task by ID", tags=["Tasks"])
def get_task(id: int):
    """Retrieve a single task by ID."""
    return service.get_task(id)


@router.put("/tasks/{id}", summary="Update an existing task", tags=["Tasks"])
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
    """Update an existing task's title and/or done status."""
    return service.update_task(id, payload)


@router.delete("/tasks/{id}", status_code=204, summary="Delete a task by ID", tags=["Tasks"])
def delete_task(id: int):
    """Delete a task by ID and return HTTP 204 No Content."""
    service.delete_task(id)
    return Response(status_code=204)
