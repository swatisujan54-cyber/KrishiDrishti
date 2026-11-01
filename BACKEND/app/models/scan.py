"""Scan model — a single crop-image analysis record owned by a user."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, Float, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class PredictionStatus(str, enum.Enum):
    """Outcome status of a scan's AI prediction."""
    pending = "pending"          # scan created, prediction not yet run
    completed = "completed"        # prediction returned with acceptable confidence
    uncertain = "uncertain"        # prediction returned but below confidence threshold
    unsupported = "unsupported"    # the selected crop is not supported by the model
    failed = "failed"              # prediction could not be completed (error)


class Scan(TimestampMixin, Base):
    """A crop image scan belonging to a specific user.

    Ownership is enforced at the API layer — users can only access their own
    scans.  Image data is stored on disk; only the path is stored here.
    ``client_id`` enables offline idempotent synchronisation.
    """

    __tablename__ = "scans"
    __table_args__ = (
        UniqueConstraint("client_id", name="uq_scan_client_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crops.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    disease_id: Mapped[int | None] = mapped_column(
        ForeignKey("diseases.id", ondelete="SET NULL"), index=True, nullable=True
    )

    # Client-generated UUID for offline synchronisation (nullable for online).
    client_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)

    # Image storage identifier (relative path inside UPLOAD_DIR).
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)

    # Optional metadata the farmer can attach.
    crop_variety: Mapped[str | None] = mapped_column(String(150), nullable=True)
    field_info: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Prediction results.
    prediction_status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus, name="prediction_status"),
        default=PredictionStatus.pending,
        nullable=False,
    )
    predicted_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    # List of {"label": str, "confidence": float} dicts.
    top_predictions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="scans")  # noqa: F821
    crop: Mapped["Crop"] = relationship()  # noqa: F821
    disease: Mapped["Disease | None"] = relationship()  # noqa: F821
    expert_requests: Mapped[list["ExpertRequest"]] = relationship(  # noqa: F821
        back_populates="scan", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(  # noqa: F821
        back_populates="scan", cascade="all, delete-orphan"
    )
