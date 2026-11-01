"""KrishiDrishti FastAPI application factory and entry point.

Run the development server with::

    uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.api.router import api_router

# Module-level logger used across the app.
logger = logging.getLogger("krishidrishti")


def _configure_logging() -> None:
    """Configure root logging. Adjust level via DEBUG setting."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _ensure_dirs() -> None:
    """Create runtime directories if they don't exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Keep the DB directory (sqlite) parent in place.
    if settings.DATABASE_URL.startswith("sqlite:///"):
        db_path = settings.DATABASE_URL.replace("sqlite:///", "", 1)
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)


def _create_tables() -> None:
    """Create all tables if they don't exist (development convenience).

    In production prefer Alembic migrations instead of auto-creating tables.
    We import the models package so every model is registered on the
    metadata before ``create_all`` runs.
    """
    # Importing the package registers all models on Base.metadata.
    from app import models  # noqa: F401  (import side-effect)
    from app.db.session import Base, engine

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    _configure_logging()
    _ensure_dirs()
    _create_tables()
    logger.info("KrishiDrishti backend started (prediction mode: %s)",
                "mock" if not settings.MODEL_PATH else "model")
    yield
    logger.info("KrishiDrishti backend shutting down.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "KrishiDrishti — AI-powered crop disease detection and advisory "
            "platform.  Decision-support tool for farmers; not a replacement "
            "for agricultural experts."
        ),
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS — restricted to configured frontend origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Consistent error responses.
    register_exception_handlers(app)

    # Mount all API routes under the configured prefix.
    app.include_router(api_router)

    return app


# The ASGI app instance imported by uvicorn.
app = create_app()
