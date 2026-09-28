"""Analytics router."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(db=Depends(get_db)):
    service = AnalyticsService(db)
    return await service.overview()


@router.get("/sales-last-7-days")
async def sales_last_7_days(db=Depends(get_db)):
    service = AnalyticsService(db)
    return await service.sales_last_7_days()


@router.get("/top-products")
async def top_products(limit: int = 10, db=Depends(get_db)):
    service = AnalyticsService(db)
    return await service.top_products(limit=limit)