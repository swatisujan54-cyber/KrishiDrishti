"""Authentication business logic: registration and credential verification."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError, ConflictError
from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole


def register_user(
    *,
    db: Session,
    email: str,
    password: str,
    full_name: str,
    preferred_language: str = "en",
    role: UserRole = UserRole.farmer,
) -> User:
    """Create a new user after checking the email isn't already taken.

    The password is hashed with bcrypt before being stored.
    Raises ``ConflictError`` if the email is already registered.
    """
    existing = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(
            "A user with this email already exists.",
            error_code="email_taken",
        )

    # Validate preferred language against the supported list.
    lang = preferred_language.strip().lower() if preferred_language else "en"
    if lang not in settings.supported_languages_list:
        lang = settings.DEFAULT_LANGUAGE

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        preferred_language=lang,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(*, db: Session, email: str, password: str) -> User | None:
    """Return the user if credentials are valid, otherwise ``None``.

    We return ``None`` (rather than raising) for both unknown-email and
    wrong-password cases so callers can return a uniform 401 without leaking
    *which* part was wrong.
    """
    user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
