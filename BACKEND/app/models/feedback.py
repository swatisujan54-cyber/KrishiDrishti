"""Feedback model — user feedback on a prediction's accuracy."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class Feedback(TimestampMixin, Base):
    """User-submitted feedback on whether a prediction was correct.

    Feedback is used to collect ground-truth signal; it is **not** used to
    automatically retrain the model without verification.
    """

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        ForeignKey("scans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    correct_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    scan: Mapped["Scan"] = relationship(back_populates="feedback")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="feedback")  # noqa: F821
