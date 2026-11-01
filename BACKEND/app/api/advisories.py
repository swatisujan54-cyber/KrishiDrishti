"""Advisory endpoints — retrieve disease advisory content."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.disease import AdvisoryResponse
from app.services.advisory_service import get_advisory

router = APIRouter(prefix="/advisories", tags=["advisories"])


@router.get(
    "/{disease_id}",
    response_model=AdvisoryResponse,
    summary="Get advisory content for a disease",
)
async def get_disease_advisory(
    disease_id: int,
    lang: str = Query(settings.DEFAULT_LANGUAGE, description="Language code, e.g. 'en' or 'hi'."),
    db: Session = Depends(get_db),
):
    """Return the advisory (symptoms, causes, prevention, next steps) for a
    disease in the requested language.

    Falls back to the original language when no translation exists.  A
    ``disclaimer`` field is always present and reflects the review status of
    the advisory content.
    """
    return get_advisory(db, disease_id, lang=lang)
