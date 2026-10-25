"""
Authentication Guard & Bearer Token Verification Dependency
"""

from typing import Any
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.supabase_client import get_supabase_client

# HTTPBearer automatically generates the Swagger "Authorize" padlock at /docs
security = HTTPBearer(auto_error=False)


async def get_token_from_header(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """
    Extract the Bearer token from the HTTP Authorization header.
    Rejects missing or malformed headers with 401 Unauthorized.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"},
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"},
        )

    return parts[1].strip()


async def get_current_user(token: str = Depends(get_token_from_header)) -> dict[str, Any]:
    """
    Verify the token with Supabase Auth and return authenticated user metadata.
    Rejects expired, forged, or invalid tokens with 401 Unauthorized.
    """
    supabase = get_supabase_client()
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"},
            )

        user = user_response.user
        return {
            "id": user.id,
            "email": user.email,
            "created_at": str(user.created_at) if user.created_at else None,
            "role": user.role,
            "app_metadata": user.app_metadata or {},
            "user_metadata": user.user_metadata or {},
            "raw_token": token,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"},
        ) from exc
