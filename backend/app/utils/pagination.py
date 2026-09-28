"""Pagination helper."""
from __future__ import annotations

from typing import List, TypeVar

T = TypeVar("T")


def paginate(items: List[T], page: int, page_size: int) -> tuple[List[T], int, int]:
    """Slice a list into a page and compute total pages."""
    total = len(items)
    pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total, pages