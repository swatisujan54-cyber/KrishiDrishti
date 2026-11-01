"""Crop schemas — list/detail responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CropResponse(BaseModel):
    """Crop data returned by the API."""
    id: int
    name: str
    scientific_name: str | None = None
    description: str | None = None
    is_supported: bool
    disease_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
