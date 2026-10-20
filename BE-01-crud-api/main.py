"""
API Layer — Week 1/2 (Assignment A1) & Week 3 (Assignment A2)

Defines the FastAPI HTTP routes, request validation, and status codes.
All persistence is delegated to `database.py` (Separation of Concerns).
"""

from typing import Any
from fastapi import Body, FastAPI, Query, Response
from fastapi.responses import JSONResponse
import uvicorn

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

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A clean SQLite-backed CRUD API for managing tasks (BE-01 / W3-A2).",
)

init_db()


@app.get("/", summary="API root metadata", tags=["System"])
def read_root():
    """Return the API name, version, and primary resource endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check", tags=["System"])
def health_check():
    """Return service health status."""
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", tags=["Tasks"])
def get_tasks(
    done: bool | None = Query(default=None, description="Filter by completion status (true/false)"),
    search: str | None = Query(default=None, description="Search keyword in task title (SQL LIKE)"),
    sort: str | None = Query(default=None, description="Pass 'title' to sort alphabetically"),
    limit: int | None = Query(default=None, ge=0, description="Maximum number of tasks to return"),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip for pagination"),
):
    """Retrieve tasks from SQLite with optional SQL filtering, sorting, and pagination."""
    return list_tasks_from_db(
        done=done,
        search=search,
        sort_by_title=(sort == "title"),
        limit=limit,
        offset=offset,
    )


@app.get("/tasks/{id}", summary="Get a single task by ID", tags=["Tasks"])
def get_task(id: int):
    """Retrieve a single task by ID, or return 404 if not found."""
    task = get_task_from_db(id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    return task


@app.post("/tasks", status_code=201, summary="Create a new task", tags=["Tasks"])
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
    """Validate `title` and insert a new task into SQLite."""
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
    return create_task_in_db(title.strip())


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
    """Validate update fields and update the matching task in SQLite."""
    if get_task_from_db(id) is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

    if not isinstance(payload, dict) or ("title" not in payload and "done" not in payload):
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must include 'title' and/or 'done'"},
        )

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

    if "done" in payload:
        if not isinstance(payload["done"], bool):
            return JSONResponse(status_code=400, content={"error": "'done' must be a boolean"})

    return update_task_in_db(
        task_id=id,
        title=payload["title"].strip() if "title" in payload else None,
        done=payload["done"] if "done" in payload else None,
    )


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task by ID", tags=["Tasks"])
def delete_task(id: int):
    """Delete a task by ID. Returns 204 No Content or 404 if not found."""
    if not delete_task_from_db(id):
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    return Response(status_code=204)


@app.get("/stats", summary="Get task statistics", tags=["Extras"])
def get_stats():
    """Return total, completed (`done`), and remaining (`open`) counts via SQL COUNT(*)."""
    return get_stats_from_db()


@app.post("/reset", summary="Reset tasks to starter data", tags=["Extras"])
def reset_tasks():
    """Restore the SQLite tasks table to the original 3 starter tasks."""
    tasks = reset_tasks_in_db()
    return {"message": "Tasks reset to starter state", "tasks": tasks}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
