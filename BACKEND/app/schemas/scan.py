"""Scan schemas — request and response models for the scan endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.scan import PredictionStatus


class ScanResponse(BaseModel):
    """Full scan record returned by the API."""
    id: int
    user_id: int
    crop_id: int
    crop_name: str = ""
    disease_id: int | None = None
    disease_name: str | None = None
    client_id: str | None = None
    image_path: str
    crop_variety: str | None = None
    field_info: str | None = None
    prediction_status: PredictionStatus
    predicted_label: str | None = None
    confidence: float | None = None
    top_predictions: list[dict] | None = None
    model_version: str | None = None
    is_mock_prediction: bool = False
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScanListItem(BaseModel):
    """Brief scan info for list views."""
    id: int
    crop_id: int
    crop_name: str = ""
    disease_id: int | None = None
    disease_name: str | None = None
    prediction_status: PredictionStatus
    predicted_label: str | None = None
    confidence: float | None = None
    image_path: str
    created_at: datetime

    model_config = {"from_attributes": True}
