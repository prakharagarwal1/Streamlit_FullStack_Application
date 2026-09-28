"""Products router: CRUD for products & categories."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.schemas.product import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.common import PageResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(payload: ProductCategoryCreate, db=Depends(get_db)):
    service = ProductService(db)
    return await service.create_category(payload)


@router.get("/categories", response_model=list[ProductCategoryResponse])
async def list_categories(db=Depends(get_db)):
    service = ProductService(db)
    return await service.list_categories()


@router.get("/categories/{category_id}", response_model=ProductCategoryResponse)
async def get_category(category_id: int, db=Depends(get_db)):
    service = ProductService(db)
    return await service.get_category(category_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db=Depends(get_db)):
    service = ProductService(db)
    return await service.create_product(payload)


@router.get("", response_model=PageResponse[ProductResponse])
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    db=Depends(get_db),
):
    service = ProductService(db)
    items, total = await service.list_products(
        page=page, page_size=page_size, category_id=category_id,
        is_active=is_active, search=search,
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return PageResponse[ProductResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db=Depends(get_db)):
    service = ProductService(db)
    return await service.get_product(product_id)


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(slug: str, db=Depends(get_db)):
    service = ProductService(db)
    return await service.get_by_slug(slug)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, payload: ProductUpdate, db=Depends(get_db)):
    service = ProductService(db)
    return await service.update_product(product_id, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db=Depends(get_db)):
    service = ProductService(db)
    await service.delete_product(product_id)