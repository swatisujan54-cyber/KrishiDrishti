"""Scan endpoints — create, list, view, delete.

All endpoints require authentication.  Users can only access their own scans.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.exceptions import AppError, NotFoundError
from app.db.session import get_db
from app.models.crop import Crop
from app.models.disease import Disease
from app.models.scan import Scan, PredictionStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.scan import ScanListItem, ScanResponse
from app.services.advisory_service import find_disease_by_label
from app.services.image_service import delete_upload, save_upload, validate_image
from app.services.prediction_service import get_prediction_service

router = APIRouter(prefix="/scans", tags=["scans"])


def _enrich_scan(scan: Scan, db: Session) -> ScanResponse:
    """Build a ScanResponse with crop and disease names."""
    crop = db.get(Crop, scan.crop_id)
    disease = db.get(Disease, scan.disease_id) if scan.disease_id else None
    return ScanResponse(
        id=scan.id,
        user_id=scan.user_id,
        crop_id=scan.crop_id,
        crop_name=crop.name if crop else "",
        disease_id=scan.disease_id,
        disease_name=disease.name if disease else None,
        client_id=scan.client_id,
        image_path=scan.image_path,
        crop_variety=scan.crop_variety,
        field_info=scan.field_info,
        prediction_status=scan.prediction_status,
        predicted_label=scan.predicted_label,
        confidence=scan.confidence,
        top_predictions=scan.top_predictions,
        model_version=scan.model_version,
        is_mock_prediction="mock" in (scan.model_version or ""),
        notes=scan.notes,
        created_at=scan.created_at,
        updated_at=scan.updated_at,
    )


@router.post(
    "",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new scan (upload image + run prediction)",
)
async def create_scan(
    crop_id: int = Form(..., description="ID of the crop being scanned."),
    image: UploadFile = File(..., description="Crop leaf image (JPEG or PNG)."),
    crop_variety: str | None = Form(None, description="Optional crop variety."),
    field_info: str | None = Form(None, description="Optional field/location info."),
    notes: str | None = Form(None, description="Optional notes."),
    client_id: str | None = Form(None, description="Client-generated UUID for offline sync."),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload a crop image and run the disease prediction pipeline.

    The image is validated, saved, and analysed by the prediction service.
    The result (predicted label, confidence, status) is stored in the scan
    record along with the associated crop and optional metadata.
    """
    # Verify the crop exists
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise NotFoundError(f"Crop with id {crop_id} not found.", error_code="crop_not_found")

    # Read and validate the uploaded image
    file_bytes = await image.read()
    pil_img = validate_image(file_bytes)
    relative_path = save_upload(pil_img)

    # Check for idempotent re-submission (offline sync)
    existing = None
    if client_id:
        existing = db.execute(
            select(Scan).where(Scan.client_id == client_id)
        ).scalar_one_or_none()

    if existing is not None:
        # Return the existing scan (idempotent)
        return _enrich_scan(existing, db)

    # Run prediction
    pred_service = get_prediction_service()

    if not crop.is_supported:
        # Crop is not supported by the model
        scan = Scan(
            user_id=current_user.id,
            crop_id=crop_id,
            image_path=relative_path,
            crop_variety=crop_variety,
            field_info=field_info,
            notes=notes,
            client_id=client_id,
            prediction_status=PredictionStatus.unsupported,
            model_version=pred_service.model_version,
        )
    else:
        from app.services.image_service import load_image_for_prediction
        loaded_img = load_image_for_prediction(relative_path)
        result = pred_service.predict(loaded_img)

        # Map predicted label to a disease record in the knowledge base
        disease_id = None
        if result.label:
            disease = find_disease_by_label(db, result.label)
            if disease:
                disease_id = disease.id

        scan = Scan(
            user_id=current_user.id,
            crop_id=crop_id,
            disease_id=disease_id,
            image_path=relative_path,
            crop_variety=crop_variety,
            field_info=field_info,
            notes=notes,
            client_id=client_id,
            prediction_status=result.status,
            predicted_label=result.label,
            confidence=result.confidence,
            top_predictions=[c.model_dump() for c in result.top_predictions] if result.top_predictions else None,
            model_version=result.model_version,
        )

    db.add(scan)
    db.commit()
    db.refresh(scan)
    return _enrich_scan(scan, db)


@router.get(
    "",
    response_model=PaginatedResponse[ScanListItem],
    summary="List the current user's scans",
)
async def list_scans(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return a paginated list of the authenticated user's scans only."""
    stmt = (
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
    )
    total = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar() or 0
    total_pages = (total + page_size - 1) // page_size if total else 0
    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    items = []
    for s in rows:
        crop = db.get(Crop, s.crop_id)
        disease = db.get(Disease, s.disease_id) if s.disease_id else None
        items.append(ScanListItem(
            id=s.id,
            crop_id=s.crop_id,
            crop_name=crop.name if crop else "",
            disease_id=s.disease_id,
            disease_name=disease.name if disease else None,
            prediction_status=s.prediction_status,
            predicted_label=s.predicted_label,
            confidence=s.confidence,
            image_path=s.image_path,
            created_at=s.created_at,
        ))

    return PaginatedResponse[ScanListItem](
        items=items,
        meta={"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    )


@router.get(
    "/{scan_id}",
    response_model=ScanResponse,
    summary="Get details of a specific scan",
)
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return a scan by ID — only if it belongs to the current user."""
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise NotFoundError(f"Scan with id {scan_id} not found.", error_code="scan_not_found")
    if scan.user_id != current_user.id:
        raise NotFoundError(f"Scan with id {scan_id} not found.", error_code="scan_not_found")
    return _enrich_scan(scan, db)


@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a scan",
)
async def delete_scan(
    scan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a scan — only if it belongs to the current user.

    Also removes the stored image file.
    """
    from app.schemas.common import MessageResponse

    scan = db.get(Scan, scan_id)
    if scan is None:
        raise NotFoundError(f"Scan with id {scan_id} not found.", error_code="scan_not_found")
    if scan.user_id != current_user.id:
        raise NotFoundError(f"Scan with id {scan_id} not found.", error_code="scan_not_found")

    # Delete the image file
    delete_upload(scan.image_path)

    db.delete(scan)
    db.commit()
    return {"message": f"Scan {scan_id} deleted."}
