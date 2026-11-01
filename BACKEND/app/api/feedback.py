"""Feedback endpoint — user feedback on prediction accuracy."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.feedback import Feedback
from app.models.scan import Scan
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback on a prediction",
)
async def create_feedback(
    body: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit user feedback on whether a prediction was correct.

    Feedback is collected for quality monitoring.  It is NOT used to
    automatically retrain the model without expert verification.
    """
    scan = db.get(Scan, body.scan_id)
    if scan is None or scan.user_id != current_user.id:
        raise NotFoundError("Scan not found.", error_code="scan_not_found")

    # Prevent duplicate feedback for the same scan
    existing = db.execute(
        select(Feedback).where(Feedback.scan_id == body.scan_id, Feedback.user_id == current_user.id)
    ).scalar_one_or_none()
    if existing is not None:
        # Update existing feedback
        existing.is_correct = body.is_correct
        existing.correct_label = body.correct_label
        existing.comments = body.comments
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    fb = Feedback(
        scan_id=body.scan_id,
        user_id=current_user.id,
        is_correct=body.is_correct,
        correct_label=body.correct_label,
        comments=body.comments,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
