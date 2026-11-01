"""Expert request schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.expert_request import ExpertRequestStatus


class ExpertRequestCreate(BaseModel):
    """Request body for creating an expert consultation request."""
    scan_id: int
    question: str | None = None
    consent_shared: bool = False


class ExpertRequestResponse(BaseModel):
    """Expert request data returned by the API."""
    id: int
    scan_id: int
    user_id: int
    expert_id: int | None = None
    status: ExpertRequestStatus
    question: str | None = None
    expert_notes: str | None = None
    consent_shared: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpertRequestUpdate(BaseModel):
    """Body for an expert to update a request (status, notes)."""
    status: ExpertRequestStatus | None = None
    expert_notes: str | None = None
