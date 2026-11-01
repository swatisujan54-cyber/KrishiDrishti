"""Sync event model — tracks offline-to-online synchronisation of records."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin


class SyncStatus(str, enum.Enum):
    """Result of applying a synchronised event."""
    applied = "applied"      # successfully applied
    conflict = "conflict"    # server-side record conflicts with client data
    rejected = "rejected"    # could not be applied (invalid data etc.)


class SyncEvent(TimestampMixin, Base):
    """A single synchronisation event received from an offline client.

    Each event carries a client-generated ``client_id`` (UUID) so duplicate
    deliveries are idempotent — receiving the same event twice does not
    create duplicate records.
    """

    __tablename__ = "sync_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Type of record being synced (e.g. "scan_created", "feedback_submitted").
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # The full event payload (JSON).
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus, name="sync_status"),
        default=SyncStatus.applied,
        nullable=False,
    )
    conflict_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
