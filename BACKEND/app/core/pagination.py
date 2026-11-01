"""Pagination helpers shared across list endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.common import PageMeta


def pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)."),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page.",
    ),
):
    """FastAPI dependency that validates pagination query params."""
    return {"page": page, "page_size": page_size}


def paginate(
    db: Session,
    stmt: select,
    *,
    page: int,
    page_size: int,
    transform: Any | None = None,
):
    """Execute *stmt* with limit/offset and return (items, PageMeta).

    ``transform`` (if given) is applied to each row before returning.
    """
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    total_pages = (total + page_size - 1) // page_size if total else 0
    rows = db.execute(
        stmt.offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()

    items = [transform(r) for r in rows] if transform else list(rows)
    meta = PageMeta(page=page, page_size=page_size, total=total, total_pages=total_pages)
    return items, meta
