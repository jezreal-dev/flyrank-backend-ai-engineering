from typing import Any
from fastapi import Body, FastAPI, Query, Response
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A clean in-memory CRUD API for managing tasks (Assignment BE-01).",
)

STARTER_TASKS = [
    {"id": 1, "title": "Read the FastAPI docs", "done": True},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Test every endpoint with curl", "done": False},
]

tasks: list[dict[str, Any]] = [dict(t) for t in STARTER_TASKS]


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
    search: str | None = Query(default=None, description="Case-insensitive keyword search in task title"),
    limit: int | None = Query(default=None, ge=0, description="Maximum number of tasks to return"),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip for pagination"),
):
    """Retrieve all tasks with optional filtering by `done` status, keyword `search`, and `limit`/`offset` pagination."""
    result = list(tasks)
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
    """Retrieve a single task by its integer `id`, or return 404 if not found."""
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


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
    """Create a new task with a required non-empty `title`. Assigns the next integer ID and sets `done` to `False`."""
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
    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": next_id, "title": title.strip(), "done": False}
    tasks.append(new_task)
    return new_task


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
    """Update a task's `title` and/or `done` status by ID. Returns 404 if not found or 400 if validation fails."""
    target = None
    for task in tasks:
        if task["id"] == id:
            target = task
            break
    if target is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

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

    if "title" in payload:
        target["title"] = payload["title"].strip()
    if "done" in payload:
        target["done"] = payload["done"]

    return target


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task by ID", tags=["Tasks"])
def delete_task(id: int):
    """Delete a task by its integer `id`. Returns 204 No Content on success or 404 if not found."""
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.get("/stats", summary="Get task statistics", tags=["Extras"])
def get_stats():
    """Return counts of total, completed (`done`), and remaining (`open`) tasks."""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    open_count = total - done_count
    return {"total": total, "done": done_count, "open": open_count}


@app.post("/reset", summary="Reset tasks to starter data", tags=["Extras"])
def reset_tasks():
    """Restore the in-memory task list to the original 3 starter tasks."""
    tasks.clear()
    tasks.extend(dict(t) for t in STARTER_TASKS)
    return {"message": "Tasks reset to starter state", "tasks": tasks}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
