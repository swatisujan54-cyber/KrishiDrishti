"""Disease knowledge base model and multilingual translations.

The disease record holds the canonical advisory information.  Translations are
kept in a separate table so original content is never overwritten by
unverified translations.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class ReviewStatus(str, enum.Enum):
    """Editorial review state of advisory content."""
    draft = "draft"               # not yet reviewed
    reviewed = "reviewed"          # reviewed and approved
    demonstration = "demonstration"  # sample/demo data, not for production use


class Disease(TimestampMixin, Base):
    """A crop disease and its advisory information (knowledge base).

    ``label_key`` optionally links this record to a model output label (as
    found in ``ml/labels.json``).  This is the connection point between the
    prediction service and the knowledge base — the prediction returns a
    label, and we look up the matching Disease by ``label_key``.
    """

    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crops.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    # Maps to a model output label (e.g. "Tomato___Early_blight").
    label_key: Mapped[str | None] = mapped_column(String(200), index=True, nullable=True)

    # Advisory content (English by default; translations in DiseaseTranslation)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    possible_causes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preventive_measures: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    expert_consultation_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    advisory_source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status"),
        default=ReviewStatus.draft,
        nullable=False,
    )
    last_reviewed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    crop: Mapped["Crop"] = relationship(back_populates="diseases")  # noqa: F821
    translations: Mapped[list["DiseaseTranslation"]] = relationship(
        back_populates="disease", cascade="all, delete-orphan"
    )


class DiseaseTranslation(TimestampMixin, Base):
    """A language-specific translation of a disease's advisory content.

    One row per (disease, language).  Keeps its own review status so
    unverified translations can be distinguished from reviewed ones.
    """

    __tablename__ = "disease_translations"
    __table_args__ = (
        UniqueConstraint("disease_id", "language", name="uq_disease_translation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    disease_id: Mapped[int] = mapped_column(
        ForeignKey("diseases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False)

    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    possible_causes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preventive_measures: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    expert_consultation_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    advisory_source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status"),
        default=ReviewStatus.draft,
        nullable=False,
    )
    last_reviewed_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    disease: Mapped["Disease"] = relationship(back_populates="translations")
