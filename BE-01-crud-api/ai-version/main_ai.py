from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import uvicorn

app = FastAPI(title="Task API (AI Single-Shot Version)", version="1.0")


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


INITIAL_TASKS = [
    {"id": 1, "title": "Read the FastAPI docs", "done": True},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Test every endpoint with curl", "done": False},
]

tasks = [dict(t) for t in INITIAL_TASKS]


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
    filtered = [
        t
        for t in tasks
        if (done is None or t["done"] == done)
        and (not search or search.lower() in t["title"].lower())
    ]
    return filtered[offset : offset + limit if limit is not None else None]


@app.get("/tasks/{id}")
def retrieve_task(id: int):
    task = next((t for t in tasks if t["id"] == id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return task


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": next_id, "title": body.title, "done": False}
    tasks.append(task)
    return task


@app.put("/tasks/{id}")
def update_task(id: int, body: TaskUpdate):
    task = next((t for t in tasks if t["id"] == id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    if body.title is None and body.done is None:
        raise HTTPException(
            status_code=400, detail="Request body must include 'title' and/or 'done'"
        )
    if body.title is not None:
        task["title"] = body.title
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    task = next((t for t in tasks if t["id"] == id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    tasks.remove(task)
    return Response(status_code=204)


@app.get("/stats")
def stats():
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": len(tasks), "done": done_count, "open": len(tasks) - done_count}


@app.post("/reset")
def reset():
    tasks[:] = [dict(t) for t in INITIAL_TASKS]
    return {"message": "Tasks reset to starter state", "tasks": tasks}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
