"""
Meta Route Layer — Root Metadata & Health Check Endpoints

Matches `src/routes/meta.routes.js` from the FlyRank Layered Architecture example.
"""

from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/", summary="API root metadata")
def read_root():
    """Return the API name, version, and primary resource endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/stats", "/reset"]}


@router.get("/health", summary="Health check")
def health_check():
    """Return service health status."""
    return {"status": "ok"}
