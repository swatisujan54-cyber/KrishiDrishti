"""Security helpers: password hashing and JWT access tokens.

We use ``bcrypt`` directly (no passlib) to avoid version-compatibility issues
and ``PyJWT`` for signed JSON Web Tokens.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


# --------------------------------------------------------------------------- #
# Password hashing                                                            #
# --------------------------------------------------------------------------- #

def hash_password(password: str) -> str:
    """Return a bcrypt hash for *password* (UTF-8 safe)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if *plain_password* matches *hashed_password*.

    Never raises on mismatch; returns ``False`` for any verification failure so
    callers can treat all invalid-credential cases uniformly.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError, AttributeError):
        return False


# --------------------------------------------------------------------------- #
# JWT access tokens                                                           #
# --------------------------------------------------------------------------- #

def create_access_token(
    *,
    subject: str,
    extra_claims: dict | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT for *subject* (the user id as a string).

    The token expires after ``ACCESS_TOKEN_EXPIRE_MINUTES`` unless
    *expires_delta* is provided.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": uuid.uuid4().hex,  # unique token id (for future revocation)
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT, returning its claims.

    Raises ``jwt.PyJWTError`` (or subclass) for expired / invalid tokens so the
    caller can translate that into an HTTP 401.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
