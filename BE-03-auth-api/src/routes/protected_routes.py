"""
Protected Routes Guarded by Bearer Token Verification
"""

from typing import Any
from fastapi import APIRouter, Depends
from src.auth import get_current_user

router = APIRouter(prefix="/protected", tags=["Protected"])


@router.get("/profile", summary="Get current user profile")
def get_user_profile(current_user: dict[str, Any] = Depends(get_current_user)):
    """
    Read private user profile data.
    Requires Authorization: Bearer <valid_jwt>.
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
        "role": current_user["role"],
        "app_metadata": current_user["app_metadata"],
        "user_metadata": current_user["user_metadata"],
    }


@router.get("/dashboard", summary="User dashboard")
def get_user_dashboard(current_user: dict[str, Any] = Depends(get_current_user)):
    """
    A second protected route demonstrating reusable auth middleware.
    """
    return {
        "message": f"Welcome to your private dashboard, {current_user['email']}!",
        "user_id": current_user["id"],
        "status": "active",
    }
