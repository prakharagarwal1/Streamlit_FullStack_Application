"""Orders router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.schemas.common import PageResponse
from app.services.order_service import OrderService
from app.security import get_current_user_id

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db),
):
    service = OrderService(db)
    return await service.create_order(user_id, payload)


@router.get("", response_model=PageResponse[OrderResponse])
async def list_orders(
    user_id: int = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    service = OrderService(db)
    items, total = await service.list_orders(user_id, page=page, page_size=page_size)
    pages = max(1, (total + page_size - 1) // page_size)
    return PageResponse[OrderResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db),
):
    service = OrderService(db)
    return await service.get_order(order_id, user_id=user_id)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    payload: OrderUpdate,
    db=Depends(get_db),
):
    service = OrderService(db)
    return await service.update_order(order_id, payload)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db),
):
    service = OrderService(db)
    return await service.cancel_order(order_id, user_id)