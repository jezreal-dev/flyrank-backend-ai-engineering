"""
Authentication Routes: Signup, Login, and Logout
"""

from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from src.auth import get_current_user
from src.schemas import SignupRequest, LoginRequest
from src.supabase_client import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, summary="Register a new user")
def sign_up(payload: dict[str, Any] = Body(...)):
    """
    Register a new user account via Supabase Auth.
    Returns 201 Created on success, or 400 Bad Request on invalid input.
    """
    email = payload.get("email")
    password = payload.get("password")

    if not email or not isinstance(email, str) or not email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email is required"},
        )

    if not password or not isinstance(password, str) or len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Password is required and must be at least 6 characters"},
        )

    supabase = get_supabase_client()
    try:
        res = supabase.auth.sign_up({"email": email.strip(), "password": password})
        if not res or not res.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Signup failed. User could not be created."},
            )

        return {
            "message": "User registered successfully",
            "user": {
                "id": res.user.id,
                "email": res.user.email,
                "created_at": str(res.user.created_at) if res.user.created_at else None,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(exc)},
        ) from exc


@router.post("/login", status_code=status.HTTP_200_OK, summary="Authenticate user & obtain JWT")
def log_in(payload: dict[str, Any] = Body(...)):
    """
    Authenticate credentials with Supabase Auth and return an Access Token (JWT).
    Returns 200 OK with access_token and refresh_token, or 401 on invalid credentials.
    """
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password or not str(email).strip() or not str(password).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password are required"},
        )

    supabase = get_supabase_client()
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": str(email).strip(), "password": str(password)}
        )

        if not res or not res.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid login credentials"},
            )

        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer",
            "expires_in": res.session.expires_in,
            "user": {
                "id": res.user.id,
                "email": res.user.email,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"},
        ) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Terminate user session")
def log_out(current_user: dict[str, Any] = Depends(get_current_user)):
    """
    Sign out user and invalidate session.
    Protected route: requires valid Bearer token.
    """
    supabase = get_supabase_client()
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # Stateless token cleanup
    return Response(status_code=status.HTTP_204_NO_CONTENT)
