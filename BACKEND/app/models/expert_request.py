"""Expert request model — farmer asks an expert to review a scan."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class ExpertRequestStatus(str, enum.Enum):
    """Lifecycle of an expert consultation request."""
    pending = "pending"        # submitted, waiting for an expert
    in_review = "in_review"    # an expert is reviewing
    resolved = "resolved"      # expert has provided their assessment
    closed = "closed"          # request closed (resolved or withdrawn)


class ExpertRequest(TimestampMixin, Base):
    """A request from a farmer for expert review of a scan.

    Images and personal data are shared with experts only when
    ``consent_shared`` is True (user consent).
    """

    __tablename__ = "expert_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        ForeignKey("scans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # The expert assigned to review (nullable until assigned).
    expert_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[ExpertRequestStatus] = mapped_column(
        Enum(ExpertRequestStatus, name="expert_request_status"),
        default=ExpertRequestStatus.pending,
        nullable=False,
    )
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    expert_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User must explicitly consent to share their data with an expert.
    consent_shared: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships — specify foreign_keys for both user links.
    scan: Mapped["Scan"] = relationship(back_populates="expert_requests")  # noqa: F821
    user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="expert_requests", foreign_keys=[user_id]
    )
    expert: Mapped["User | None"] = relationship(  # noqa: F821
        back_populates="expert_assignments", foreign_keys=[expert_id]
    )
