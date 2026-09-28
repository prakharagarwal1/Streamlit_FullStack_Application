"""Analytics service: aggregate stats for dashboards."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.product import Product
from app.models.user import User


class AnalyticsService:
    """Compute aggregate metrics for dashboards."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def overview(self) -> dict[str, Any]:
        users = await self.session.execute(select(func.count(User.id)))
        products = await self.session.execute(select(func.count(Product.id)))
        orders = await self.session.execute(select(func.count(Order.id)))
        revenue = await self.session.execute(select(func.coalesce(func.sum(Order.total_amount), 0)))
        return {
            "total_users": users.scalar() or 0,
            "total_products": products.scalar() or 0,
            "total_orders": orders.scalar() or 0,
            "total_revenue": float(revenue.scalar() or 0),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def sales_last_7_days(self) -> list[dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(days=7)
        result = await self.session.execute(
            select(Order.created_at, Order.total_amount).where(Order.created_at >= since)
        )
        rows = result.all()
        buckets: dict[str, float] = {}
        for i in range(7):
            day = (datetime.now(timezone.utc) - timedelta(days=6 - i)).date().isoformat()
            buckets[day] = 0.0
        for created_at, amount in rows:
            if created_at is None:
                continue
            day = created_at.date().isoformat()
            if day in buckets:
                buckets[day] += float(amount or 0)
        return [{"date": k, "revenue": round(v, 2)} for k, v in buckets.items()]

    async def top_products(self, limit: int = 10) -> list[dict[str, Any]]:
        result = await self.session.execute(
            select(Product).order_by(Product.price.desc()).limit(limit)
        )
        products = result.scalars().all()
        return [
            {"id": p.id, "name": p.name, "price": p.price, "stock": p.stock_quantity}
            for p in products
        ]