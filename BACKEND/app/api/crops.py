"""Crop endpoints — list and detail.

These endpoints are public (no auth required) because the crop list is
reference data that the frontend needs for the crop-selection step.  They do
not expose any private user information.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.pagination import pagination_params
from app.db.session import get_db
from app.models.crop import Crop
from app.models.disease import Disease
from app.schemas.common import PaginatedResponse
from app.schemas.crop import CropResponse

router = APIRouter(prefix="/crops", tags=["crops"])


def _crop_to_response(crop: Crop, db: Session) -> CropResponse:
    """Build a CropResponse, including the disease count."""
    disease_count = db.execute(
        select(func.count()).select_from(Disease).where(Disease.crop_id == crop.id)
    ).scalar() or 0
    return CropResponse(
        id=crop.id,
        name=crop.name,
        scientific_name=crop.scientific_name,
        description=crop.description,
        is_supported=crop.is_supported,
        disease_count=disease_count,
        created_at=crop.created_at,
    )


@router.get(
    "",
    response_model=PaginatedResponse[CropResponse],
    summary="List supported crops",
)
async def list_crops(
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    """Return a paginated list of crops.

    Use ``?supported=true`` to filter to only AI-supported crops, or
    ``?supported=false`` for unsupported ones.  Omit the param for all crops.
    """
    page, page_size = pagination["page"], pagination["page_size"]

    stmt = select(Crop).order_by(Crop.name)
    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    total = db.execute(select(func.count()).select_from(Crop)).scalar() or 0
    total_pages = (total + page_size - 1) // page_size if total else 0

    items = [_crop_to_response(c, db) for c in rows]
    return PaginatedResponse[CropResponse](
        items=items,
        meta={"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    )


@router.get(
    "/{crop_id}",
    response_model=CropResponse,
    summary="Get details of a specific crop",
)
async def get_crop(crop_id: int, db: Session = Depends(get_db)):
    """Return a single crop by ID, or 404 if it doesn't exist."""
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise NotFoundError(f"Crop with id {crop_id} not found.", error_code="crop_not_found")
    return _crop_to_response(crop, db)
