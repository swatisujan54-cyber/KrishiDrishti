"""Advisory service — retrieves disease advisory content with language support.

Keeps the AI prediction separate from the disease knowledge base.  The
prediction service returns a label; the advisory service uses the disease ID
to fetch the appropriate reviewed advisory.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.disease import Disease, DiseaseTranslation, ReviewStatus
from app.models.crop import Crop
from app.schemas.disease import AdvisoryResponse, DiseaseListItem, DiseaseResponse


# Disclaimer shown alongside advisory content.
_DEMO_DISCLAIMER = (
    "This advisory is demonstration data and has not been reviewed by a "
    "qualified agricultural expert.  Confirm the diagnosis and treatment "
    "with your local agricultural extension officer before acting."
)
_UNREVIEWED_DISCLAIMER = (
    "This advisory has not yet been fully reviewed.  Please confirm the "
    "diagnosis with a qualified agricultural expert before acting."
)
_REVIEWED_DISCLAIMER = (
    "This advisory has been reviewed.  However, always confirm the diagnosis "
    "with your local agricultural extension officer, especially before "
    "applying any pesticides."
)


def _get_disclaimer(review_status: ReviewStatus) -> str:
    """Return the appropriate safety disclaimer for a review status."""
    if review_status == ReviewStatus.demonstration:
        return _DEMO_DISCLAIMER
    if review_status == ReviewStatus.draft:
        return _UNREVIEWED_DISCLAIMER
    return _REVIEWED_DISCLAIMER


def get_disease(db: Session, disease_id: int, *, lang: str = "en") -> DiseaseResponse:
    """Return a full disease record, using translated content if available.

    Falls back to the original English content when no translation exists
    for the requested language.
    """
    disease = db.get(Disease, disease_id)
    if disease is None or not disease.is_active:
        raise NotFoundError(f"Disease with id {disease_id} not found.", error_code="disease_not_found")

    crop = db.get(Crop, disease.crop_id)

    # Find available translation languages
    translations = db.execute(
        select(DiseaseTranslation).where(DiseaseTranslation.disease_id == disease.id)
    ).scalars().all()
    available_languages = [t.language for t in translations]

    # Use translated fields if available for the requested language
    tr = next((t for t in translations if t.language == lang), None)

    return DiseaseResponse(
        id=disease.id,
        crop_id=disease.crop_id,
        crop_name=crop.name if crop else "",
        name=tr.name if tr and tr.name else disease.name,
        label_key=disease.label_key,
        symptoms=tr.symptoms if tr and tr.symptoms else disease.symptoms,
        possible_causes=tr.possible_causes if tr and tr.possible_causes else disease.possible_causes,
        preventive_measures=tr.preventive_measures if tr and tr.preventive_measures else disease.preventive_measures,
        recommended_next_steps=tr.recommended_next_steps if tr and tr.recommended_next_steps else disease.recommended_next_steps,
        expert_consultation_guidance=tr.expert_consultation_guidance if tr and tr.expert_consultation_guidance else disease.expert_consultation_guidance,
        advisory_source=tr.advisory_source if tr and tr.advisory_source else disease.advisory_source,
        review_status=tr.review_status if tr else disease.review_status,
        last_reviewed_date=tr.last_reviewed_date if tr else disease.last_reviewed_date,
        is_active=disease.is_active,
        available_languages=available_languages,
        created_at=disease.created_at,
    )


def get_advisory(db: Session, disease_id: int, *, lang: str = "en") -> AdvisoryResponse:
    """Return the advisory content for a disease in the requested language.

    If a reviewed translation exists for *lang*, its content is used.
    Otherwise the original English content is returned and ``is_translated``
    is set to ``False``.
    """
    disease = db.get(Disease, disease_id)
    if disease is None or not disease.is_active:
        raise NotFoundError(f"Disease with id {disease_id} not found.", error_code="disease_not_found")

    crop = db.get(Crop, disease.crop_id)

    # Look for a translation in the requested language
    translation = db.execute(
        select(DiseaseTranslation).where(
            DiseaseTranslation.disease_id == disease.id,
            DiseaseTranslation.language == lang,
        )
    ).scalar_one_or_none()

    # Determine which content to use
    if translation:
        source = translation
        is_translated = True
        review_status = translation.review_status
        last_reviewed = translation.last_reviewed_date
    else:
        source = disease
        is_translated = False
        review_status = disease.review_status
        last_reviewed = disease.last_reviewed_date

    return AdvisoryResponse(
        disease_id=disease.id,
        disease_name=getattr(source, "name", None) or disease.name,
        crop_name=crop.name if crop else "",
        language=lang if translation else settings.DEFAULT_LANGUAGE,
        is_translated=is_translated,
        review_status=review_status,
        last_reviewed_date=last_reviewed,
        symptoms=getattr(source, "symptoms", None),
        possible_causes=getattr(source, "possible_causes", None),
        preventive_measures=getattr(source, "preventive_measures", None),
        recommended_next_steps=getattr(source, "recommended_next_steps", None),
        expert_consultation_guidance=getattr(source, "expert_consultation_guidance", None),
        advisory_source=getattr(source, "advisory_source", None),
        disclaimer=_get_disclaimer(review_status),
    )


def find_disease_by_label(db: Session, label: str) -> Disease | None:
    """Find a disease by its model label_key (case-insensitive).

    Used by the scan flow to connect a prediction to the knowledge base.
    """
    if not label:
        return None
    return db.execute(
        select(Disease).where(Disease.label_key.ilike(label))
    ).scalar_one_or_none()


def list_diseases(
    db: Session,
    *,
    crop_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DiseaseListItem], int, int]:
    """Return a paginated list of diseases, optionally filtered by crop."""
    stmt = select(Disease).where(Disease.is_active.is_(True))
    if crop_id is not None:
        stmt = stmt.where(Disease.crop_id == crop_id)
    stmt = stmt.order_by(Disease.name)

    from sqlalchemy import func

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    total_pages = (total + page_size - 1) // page_size if total else 0
    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    items: list[DiseaseListItem] = []
    for d in rows:
        crop = db.get(Crop, d.crop_id)
        items.append(DiseaseListItem(
            id=d.id,
            name=d.name,
            crop_id=d.crop_id,
            crop_name=crop.name if crop else "",
            label_key=d.label_key,
            review_status=d.review_status,
        ))

    return items, total, total_pages
