"""Crop model — database-backed list of supported crops."""

from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin


class Crop(TimestampMixin, Base):
    """A crop type (e.g. Tomato, Rice).

    ``is_supported`` indicates whether the AI model can currently detect
    diseases on this crop.  Unsupported crops can still be stored and
    associated with scans, but predictions will be flagged accordingly.
    """

    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_supported: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    diseases: Mapped[list["Disease"]] = relationship(  # noqa: F821
        back_populates="crop", cascade="all, delete-orphan"
    )
