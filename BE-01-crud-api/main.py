from typing import Any
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

tasks = [
    {"id": 1, "title": "Read the FastAPI docs", "done": True},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Test every endpoint with curl", "done": False},
]


@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.post("/tasks", status_code=201)
def create_task(payload: dict[str, Any] | None = Body(default=None)):
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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
