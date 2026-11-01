"""System endpoints (health check)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns service status, version, and whether the AI model is loaded.",
)
async def health(db: Session = Depends(get_db)):
    """Lightweight liveness/readiness probe.

    Checks that the database is reachable.  Reports the prediction mode
    (``mock`` when no trained model is configured).
    """
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    prediction_mode = "mock" if not settings.MODEL_PATH else "model"

    return {
        "status": "healthy" if db_ok else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "ok" if db_ok else "error",
        "prediction_mode": prediction_mode,
        "model_loaded": bool(settings.MODEL_PATH),
    }
