"""Shared schemas used across endpoints: error responses, pagination."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Consistent error body returned by all error responses."""
    detail: str = Field(..., description="Human-readable error message")
    error_code: str | None = Field(
        None, description="Optional machine-readable error code"
    )


class MessageResponse(BaseModel):
    """A simple message response (e.g. for logout / delete)."""
    message: str


class PageMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response."""
    items: list[T]
    meta: PageMeta
