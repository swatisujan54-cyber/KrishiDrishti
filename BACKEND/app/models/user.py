"""User model — farmers and authorized experts."""

from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class UserRole(str, enum.Enum):
    """Application roles."""
    farmer = "farmer"
    expert = "expert"


class User(TimestampMixin, Base):
    """A registered user of the platform.

    Passwords are stored *only* as bcrypt hashes.  The ``hashed_password``
    column never appears in any API response (see schemas).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.farmer, nullable=False
    )
    preferred_language: Mapped[str] = mapped_column(
        String(10), default="en", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships — ``foreign_keys`` is needed for expert_requests because
    # ExpertRequest links to users twice (user_id + expert_id).
    scans: Mapped[list["Scan"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    expert_requests: Mapped[list["ExpertRequest"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[ExpertRequest.user_id]",
    )
    # Expert assignments (requests assigned to this expert).
    expert_assignments: Mapped[list["ExpertRequest"]] = relationship(  # noqa: F821
        back_populates="expert",
        foreign_keys="[ExpertRequest.expert_id]",
    )
    feedback: Mapped[list["Feedback"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
