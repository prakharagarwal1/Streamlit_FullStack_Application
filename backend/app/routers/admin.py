"""Admin router: user management + stats."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.schemas.user import UserResponse
from app.schemas.common import PageResponse
from app.services.user_service import UserService
from app.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = Query(None),
    db=Depends(get_db),
):
    service = UserService(db)
    items, total = await service.list_users(page=page, page_size=page_size, role=role)
    pages = max(1, (total + page_size - 1) // page_size)
    return PageResponse[UserResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )