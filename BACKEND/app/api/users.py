"""User profile endpoints: view and update the current user."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user's profile",
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Return the authenticated user's profile (no sensitive fields)."""
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the current user's profile",
)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update full name, preferred language, or password.

    Only the provided fields are changed; omitted fields keep their current
    values.
    """
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.preferred_language is not None:
        current_user.preferred_language = body.preferred_language
    if body.password is not None:
        current_user.hashed_password = hash_password(body.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
