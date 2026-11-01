"""Sync schemas — offline-to-online synchronization."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.sync_event import SyncStatus


class SyncEventItem(BaseModel):
    """A single event to synchronise."""
    client_id: str
    event_type: str
    payload: dict


class SyncRequest(BaseModel):
    """Batch sync request body."""
    events: list[SyncEventItem]


class SyncResultItem(BaseModel):
    """Result of applying a single event."""
    client_id: str
    status: SyncStatus
    conflict_detail: str | None = None


class SyncResponse(BaseModel):
    """Overall sync response."""
    results: list[SyncResultItem]
    server_time: datetime
