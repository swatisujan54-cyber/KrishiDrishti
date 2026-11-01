"""Disease endpoints — list and detail (with multilingual support)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.disease import DiseaseListItem, DiseaseResponse
from app.services.advisory_service import get_disease, list_diseases

router = APIRouter(prefix="/diseases", tags=["diseases"])


@router.get(
    "",
    response_model=PaginatedResponse[DiseaseListItem],
    summary="List crop diseases",
)
async def list_all_diseases(
    crop_id: int | None = Query(None, description="Filter diseases by crop ID."),
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    """Return a paginated list of diseases, optionally filtered by crop."""
    items, total, total_pages = list_diseases(
        db, crop_id=crop_id, page=page, page_size=page_size
    )
    return PaginatedResponse[DiseaseListItem](
        items=items,
        meta={"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    )


@router.get(
    "/{disease_id}",
    response_model=DiseaseResponse,
    summary="Get details of a specific disease",
)
async def get_disease_detail(
    disease_id: int,
    lang: str = Query(settings.DEFAULT_LANGUAGE, description="Language code, e.g. 'en' or 'hi'."),
    db: Session = Depends(get_db),
):
    """Return a single disease's full record.

    Translated content is returned when a translation exists for *lang*;
    otherwise the original content is used.
    """
    return get_disease(db, disease_id, lang=lang)
