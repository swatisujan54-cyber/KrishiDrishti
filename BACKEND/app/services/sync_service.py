"""Sync service — idempotent offline-to-online synchronisation.

Each event carries a client-generated ``client_id`` (UUID).  If an event with
the same ``client_id`` has already been received, the server returns the
previous result instead of re-applying it.  This makes sync idempotent: a
flaky connection that resends the same batch does not create duplicates.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.sync_event import SyncEvent, SyncStatus
from app.models.user import User
from app.schemas.sync import SyncResultItem


def apply_sync(
    db: Session,
    *,
    user_id: int,
    events: list[dict],
) -> list[SyncResultItem]:
    """Apply a batch of sync events for a user.

    Each event dict should have: client_id, event_type, payload.
    Returns a list of results — one per event.
    """
    results: list[SyncResultItem] = []

    for ev in events:
        client_id = ev.get("client_id", "")
        event_type = ev.get("event_type", "")
        payload = ev.get("payload", {})

        if not client_id:
            results.append(SyncResultItem(
                client_id="", status=SyncStatus.rejected,
                conflict_detail="Missing client_id.",
            ))
            continue

        # Check if already received (idempotency)
        existing = db.execute(
            select(SyncEvent).where(SyncEvent.client_id == client_id)
        ).scalar_one_or_none()

        if existing is not None:
            results.append(SyncResultItem(
                client_id=client_id,
                status=existing.status,
                conflict_detail=existing.conflict_detail,
            ))
            continue

        # Apply the event based on its type
        status_, detail = _apply_event(db, user_id=user_id, event_type=event_type, payload=payload)

        # Record the sync event
        sync_event = SyncEvent(
            client_id=client_id,
            user_id=user_id,
            event_type=event_type,
            payload=payload,
            status=status_,
            conflict_detail=detail,
            received_at=datetime.now(timezone.utc),
            applied_at=datetime.now(timezone.utc) if status_ == SyncStatus.applied else None,
        )
        db.add(sync_event)
        results.append(SyncResultItem(client_id=client_id, status=status_, conflict_detail=detail))

    db.commit()
    return results


def _apply_event(
    db: Session,
    *,
    user_id: int,
    event_type: str,
    payload: dict,
) -> tuple[SyncStatus, str | None]:
    """Apply a single event.  Returns (status, conflict_detail)."""
    if event_type == "scan_created":
        # Check if a scan with this client_id already exists
        scan_client_id = payload.get("client_id")
        if scan_client_id:
            existing = db.execute(
                select(Scan).where(Scan.client_id == scan_client_id)
            ).scalar_one_or_none()
            if existing is not None:
                return SyncStatus.applied, None
        # We don't re-run prediction on sync; we just acknowledge the event.
        # The actual scan should be created via POST /api/scans when online.
        return SyncStatus.applied, None

    elif event_type == "feedback_submitted":
        return SyncStatus.applied, None

    elif event_type == "scan_deleted":
        return SyncStatus.applied, None

    else:
        return SyncStatus.rejected, f"Unknown event_type: {event_type}"
