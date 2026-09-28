"""Common response schemas."""
from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic success message."""

    message: str
    success: bool = True


class BulkResponse(BaseModel):
    """Generic bulk operation response."""

    success: int = 0
    failed: int = 0
    errors: List[str] = []


class PageResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool = False
    has_prev: bool = False