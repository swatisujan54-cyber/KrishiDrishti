"""FastAPI dependencies for authentication and authorization.

Usage in route functions::

    @router.get("/me")
    async def get_me(current_user: User = Depends(get_current_active_user)):
        ...
"""

from __future__ import annotations

import jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError, ForbiddenError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

# The tokenUrl is only used for the OpenAPI "Authorize" button; our login
# endpoint actually accepts JSON (see app/api/auth.py).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode the JWT and return the matching user, or raise 401."""
    credentials_error = AppError(
        "Could not validate credentials. Please log in again.",
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code="invalid_credentials",
    )
    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_error
        user_id = int(user_id_str)
    except jwt.PyJWTError:
        raise credentials_error
    except (ValueError, TypeError):
        raise credentials_error

    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user account is still active."""
    if not current_user.is_active:
        raise AppError(
            "This account has been deactivated.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="account_inactive",
        )
    return current_user


def get_current_expert(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require the authenticated user to have the 'expert' role."""
    if current_user.role != UserRole.expert:
        raise ForbiddenError(
            "This action requires an expert account.",
            error_code="expert_required",
        )
    return current_user
