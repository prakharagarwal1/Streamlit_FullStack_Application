"""Order service: cart → order flow with stock validation."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import (
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    OrderUpdate,
)


class OrderService:
    """Order creation and management business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_order(self, user_id: int, payload: OrderCreate) -> OrderResponse:
        """Create an order from items, validating stock."""
        order_number = "ORD-" + uuid.uuid4().hex[:12].upper()
        order = Order(
            order_number=order_number,
            user_id=user_id,
            shipping_address=payload.shipping_address,
            billing_address=payload.billing_address,
            notes=payload.notes,
            currency=payload.currency,
        )
        self.session.add(order)
        await self.session.flush()

        subtotal = 0.0
        items_response: list[OrderItemResponse] = []
        for item in payload.items:
            product = await self._get_product(item.product_id)
            if product.stock_quantity < item.quantity:
                raise ConflictError(
                    f"Insufficient stock for product {product.name}"
                )
            product.stock_quantity -= item.quantity
            unit_price = product.price
            line_total = round(unit_price * item.quantity, 2)
            subtotal += line_total
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
            self.session.add(order_item)
            await self.session.flush()
            await self.session.refresh(order_item)
            items_response.append(OrderItemResponse.model_validate(order_item))

        order.subtotal = round(subtotal, 2)
        order.tax_amount = round(subtotal * 0.08, 2)  # demo 8% tax
        order.shipping_amount = 0.0 if subtotal >= 100 else 5.99
        order.total_amount = round(
            order.subtotal + order.tax_amount + order.shipping_amount, 2
        )
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return OrderResponse.model_validate(
            {**order.__dict__, "items": items_response}
        )

    async def get_order(self, order_id: int, user_id: Optional[int] = None) -> OrderResponse:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("Order not found")
        if user_id is not None and order.user_id != user_id:
            raise NotFoundError("Order not found")
        items = await self._get_items(order.id)
        return OrderResponse.model_validate({**order.__dict__, "items": items})

    async def list_orders(
        self, user_id: int, page: int = 1, page_size: int = 20
    ) -> Tuple[list[OrderResponse], int]:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        total_result = await self.session.execute(
            select(Order).where(Order.user_id == user_id)
        )
        total = len(total_result.scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        responses = []
        for order in orders:
            items = await self._get_items(order.id)
            responses.append(OrderResponse.model_validate({**order.__dict__, "items": items}))
        return responses, total

    async def update_order(self, order_id: int, payload: OrderUpdate) -> OrderResponse:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("Order not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, field, value)
        self.session.add(order)
        await self.session.flush()
        items = await self._get_items(order.id)
        return OrderResponse.model_validate({**order.__dict__, "items": items})

    async def cancel_order(self, order_id: int, user_id: int) -> OrderResponse:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("Order not found")
        if order.status in ("shipped", "delivered"):
            raise ConflictError("Cannot cancel a shipped/delivered order")
        order.status = "cancelled"
        # restore stock
        items = await self._get_items(order.id)
        for item in items:
            product = await self._get_product(item.product_id)
            product.stock_quantity += item.quantity
            self.session.add(product)
        self.session.add(order)
        await self.session.flush()
        return OrderResponse.model_validate({**order.__dict__, "items": items})

    async def _get_product(self, product_id: int) -> Product:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")
        return product

    async def _get_items(self, order_id: int) -> list[OrderItemResponse]:
        result = await self.session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return [OrderItemResponse.model_validate(item) for item in result.scalars().all()]