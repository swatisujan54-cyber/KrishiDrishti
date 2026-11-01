"""SQLAlchemy 2.0 engine, session factory, and declarative base.

A synchronous engine is used for simplicity and broad driver support (SQLite
works out of the box).  To switch to PostgreSQL just change ``DATABASE_URL`` to
a ``postgresql+psycopg2://`` URL and install ``psycopg2-binary``; the rest of
the code stays the same.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# SQLite needs check_same_thread=False so the session can be shared across
# the event-loop threads that FastAPI uses.
_connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
