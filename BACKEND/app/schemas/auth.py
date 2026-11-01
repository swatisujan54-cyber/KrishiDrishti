"""Authentication schemas: signup, login, token responses."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserSignup(BaseModel):
    """Request body for farmer registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128,
                           description="At least 8 characters.")
    full_name: str = Field(..., min_length=1, max_length=150)
    preferred_language: str = Field(default="en", max_length=10,
                                   description="Language code, e.g. 'en' or 'hi'.")


class UserLogin(BaseModel):
    """Request body for login (JSON, not OAuth2 form)."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload (internal use)."""
    user_id: int | None = None
