"""User schemas: response and update profiles.

These schemas never expose ``hashed_password`` or other sensitive fields.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import settings
from app.models.user import UserRole


class UserResponse(BaseModel):
    """User data returned by the API (safe — no password hash)."""

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    preferred_language: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Fields a user can update on their own profile."""
    full_name: str | None = Field(None, min_length=1, max_length=150)
    preferred_language: str | None = Field(None, max_length=10)
    password: str | None = Field(None, min_length=8, max_length=128,
                                 description="New password (at least 8 chars).")

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in settings.supported_languages_list:
            raise ValueError(
                f"Unsupported language '{v}'. "
                f"Supported: {', '.join(settings.supported_languages_list)}"
            )
        return v
