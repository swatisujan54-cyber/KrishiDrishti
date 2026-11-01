"""Disease and advisory schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.models.disease import ReviewStatus


class DiseaseListItem(BaseModel):
    """Brief disease info for list views."""
    id: int
    name: str
    crop_id: int
    crop_name: str
    label_key: str | None = None
    review_status: ReviewStatus

    model_config = {"from_attributes": True}


class DiseaseResponse(BaseModel):
    """Full disease record including advisory content."""
    id: int
    crop_id: int
    crop_name: str
    name: str
    label_key: str | None = None
    symptoms: str | None = None
    possible_causes: str | None = None
    preventive_measures: str | None = None
    recommended_next_steps: str | None = None
    expert_consultation_guidance: str | None = None
    advisory_source: str | None = None
    review_status: ReviewStatus
    last_reviewed_date: date | None = None
    is_active: bool
    available_languages: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class AdvisoryResponse(BaseModel):
    """Advisory content for a disease, in the requested or fallback language."""
    disease_id: int
    disease_name: str
    crop_name: str
    language: str
    is_translated: bool
    review_status: ReviewStatus
    last_reviewed_date: date | None = None
    symptoms: str | None = None
    possible_causes: str | None = None
    preventive_measures: str | None = None
    recommended_next_steps: str | None = None
    expert_consultation_guidance: str | None = None
    advisory_source: str | None = None
    disclaimer: str
