"""Authentication endpoints: signup, login, logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserSignup
from app.schemas.common import MessageResponse
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farmer account",
)
async def signup(body: UserSignup, db: Session = Depends(get_db)):
    """Create a new farmer account.

    Self-registration always creates a ``farmer`` role.  Expert accounts are
    managed separately to prevent privilege escalation.
    """
    user = register_user(
        db=db,
        email=str(body.email),
        password=body.password,
        full_name=body.full_name,
        preferred_language=body.preferred_language,
    )
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive a JWT access token",
)
async def login(body: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email + password and return a JWT.

    The token must be sent as ``Authorization: Bearer <token>`` for protected
    endpoints.
    """
    user = authenticate_user(db=db, email=str(body.email), password=body.password)
    if user is None:
        raise AppError(
            "Incorrect email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="invalid_credentials",
        )
    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (invalidate token client-side)",
)
async def logout():
    """Acknowledge logout.

    JWTs are stateless, so the server cannot revoke a token without a
    blacklist.  The client should discard the token.  See the README for
    notes on implementing a token revocation list if needed.
    """
    return MessageResponse(message="Logged out. Please discard the access token.")
