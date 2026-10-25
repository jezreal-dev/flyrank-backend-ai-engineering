"""
Public Unauthenticated Routes
"""

from fastapi import APIRouter

router = APIRouter(tags=["Public"])


@router.get("/public/info", summary="Public information")
def get_public_info():
    """Read public, unauthenticated data."""
    return {"message": "Welcome stranger! This info is public."}
