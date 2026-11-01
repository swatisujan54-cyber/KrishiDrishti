"""Sync endpoint — offline-to-online synchronization."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.sync import SyncRequest, SyncResponse
from app.services.sync_service import apply_sync

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post(
    "",
    response_model=SyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Synchronise offline records",
)
async def sync(
    body: SyncRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Receive a batch of client-generated sync events.

    Each event is processed idempotently — if an event with the same
    ``client_id`` has already been received, the previous result is returned
    without re-applying it.
    """
    results = apply_sync(db, user_id=current_user.id, events=[e.model_dump() for e in body.events])
    return SyncResponse(results=results, server_time=datetime.now(timezone.utc))
