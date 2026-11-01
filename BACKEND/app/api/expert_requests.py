"""Expert request endpoints — farmers request expert review of scans."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user, get_current_expert
from app.core.exceptions import AppError, NotFoundError
from app.db.session import get_db
from app.models.expert_request import ExpertRequest, ExpertRequestStatus
from app.models.scan import Scan
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.expert_request import (
    ExpertRequestCreate,
    ExpertRequestResponse,
    ExpertRequestUpdate,
)

router = APIRouter(prefix="/expert-requests", tags=["expert-requests"])


@router.post(
    "",
    response_model=ExpertRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an expert consultation request",
)
async def create_expert_request(
    body: ExpertRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a request for an expert to review a scan.

    The scan must belong to the current user.  Set ``consent_shared`` to True
    to allow the expert to see the image and details.
    """
    scan = db.get(Scan, body.scan_id)
    if scan is None or scan.user_id != current_user.id:
        raise NotFoundError("Scan not found.", error_code="scan_not_found")

    req = ExpertRequest(
        scan_id=body.scan_id,
        user_id=current_user.id,
        question=body.question,
        consent_shared=body.consent_shared,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get(
    "",
    response_model=PaginatedResponse[ExpertRequestResponse],
    summary="List expert requests",
)
async def list_expert_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Farmers see their own requests; experts see all pending requests."""
    if current_user.role.value == "expert":
        stmt = select(ExpertRequest).order_by(ExpertRequest.created_at.desc())
    else:
        stmt = (
            select(ExpertRequest)
            .where(ExpertRequest.user_id == current_user.id)
            .order_by(ExpertRequest.created_at.desc())
        )

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    total_pages = (total + page_size - 1) // page_size if total else 0
    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    return PaginatedResponse[ExpertRequestResponse](
        items=list(rows),
        meta={"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    )


@router.patch(
    "/{request_id}",
    response_model=ExpertRequestResponse,
    summary="Update an expert request (expert only)",
)
async def update_expert_request(
    request_id: int,
    body: ExpertRequestUpdate,
    expert: User = Depends(get_current_expert),
    db: Session = Depends(get_db),
):
    """Allow an expert to update the status or add notes to a request."""
    req = db.get(ExpertRequest, request_id)
    if req is None:
        raise NotFoundError("Expert request not found.", error_code="expert_request_not_found")

    if body.status is not None:
        req.status = body.status
    if body.expert_notes is not None:
        req.expert_notes = body.expert_notes
    if req.expert_id is None:
        req.expert_id = expert.id

    db.add(req)
    db.commit()
    db.refresh(req)
    return req
