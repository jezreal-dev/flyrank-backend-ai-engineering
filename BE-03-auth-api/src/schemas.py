"""
Pydantic Schemas for Request Validation and Response Serialization
"""

from typing import Any
from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password (min 6 characters)")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User's registered email address")
    password: str = Field(..., description="User's password")


class AuthResponse(BaseModel):
    message: str
    access_token: str | None = None
    refresh_token: str | None = None
    user_id: str | None = None
    email: str | None = None


class UserProfileResponse(BaseModel):
    id: str
    email: str | None = None
    created_at: str | None = None
    role: str | None = None
    app_metadata: dict[str, Any] = {}
    user_metadata: dict[str, Any] = {}


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
