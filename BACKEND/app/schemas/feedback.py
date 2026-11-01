"""Feedback schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    """Request body for submitting feedback on a prediction."""
    scan_id: int
    is_correct: bool | None = None
    correct_label: str | None = None
    comments: str | None = None


class FeedbackResponse(BaseModel):
    """Feedback data returned by the API."""
    id: int
    scan_id: int
    user_id: int
    is_correct: bool | None = None
    correct_label: str | None = None
    comments: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
