"""Database initialization script — creates tables and seeds reference data.

Run with::

    python -m app.db.init_db
"""

from __future__ import annotations

import logging

from app.db.seed import run_seed
from app.db.session import Base, engine

# Import all models so they register on Base.metadata.
from app import models  # noqa: F401

logger = logging.getLogger("krishidrishti.init_db")


def init_db() -> None:
    """Create all tables and insert seed data."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created. Running seed...")
    run_seed()
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
