"""
Application Wiring & Entry Point — Week 1/2 (A1) & Week 3 (A2: Layered + SQLite)

Mirrors `src/app.js` + `index.js` from the FlyRank Layered Architecture example:
Wires together the three horizontal layers:
  1. `src/routes/`       — HTTP Layer (request parsing & status codes)
  2. `src/services/`     — Business Rules Layer (validation & domain errors)
  3. `src/repositories/` — Data Access Layer (`database.py` SQLite persistence)
"""

from fastapi import FastAPI
import uvicorn

from src.middleware.error_handler import register_error_handlers
from src.repositories.tasks_repository import initialize_storage
from src.routes.meta_routes import router as meta_router
from src.routes.tasks_routes import router as tasks_router


def create_app() -> FastAPI:
    """Build the FastAPI application, initialize SQLite storage, and wire all layers."""
    initialize_storage()

    application = FastAPI(
        title="Task API",
        version="1.0",
        description=(
            "A layered, SQLite-backed CRUD API for managing tasks "
            "(Routes -> Service -> SQLite Repository)."
        ),
    )

    register_error_handlers(application)
    application.include_router(meta_router)
    application.include_router(tasks_router)
    return application


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
