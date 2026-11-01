"""Prediction result schemas (used internally by the scan flow)."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.scan import PredictionStatus


class PredictionCandidate(BaseModel):
    """A single candidate prediction from the model."""
    label: str
    confidence: float


class PredictionResult(BaseModel):
    """The full result of running a prediction on an image.

    This is an internal transfer object, not a direct API response.
    """
    label: str | None = None
    confidence: float | None = None
    top_predictions: list[PredictionCandidate] = []
    status: PredictionStatus = PredictionStatus.pending
    model_version: str = ""
    is_mock: bool = True
    error_message: str | None = None
