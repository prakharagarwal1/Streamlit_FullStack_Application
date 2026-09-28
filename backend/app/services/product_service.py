"""Product & category service."""
from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.product import Product, ProductCategory
from app.schemas.product import (
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.security import generate_slug


class ProductService:
    """Product & category business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_category(
        self, payload: ProductCategoryCreate
    ) -> ProductCategoryResponse:
        slug = payload.slug or generate_slug(payload.name)
        category = ProductCategory(
            name=payload.name,
            slug=slug,
            description=payload.description,
            parent_id=payload.parent_id,
        )
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return ProductCategoryResponse.model_validate(category)

    async def get_category(self, category_id: int) -> ProductCategoryResponse:
        result = await self.session.execute(
            select(ProductCategory).where(ProductCategory.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise NotFoundError("Category not found")
        return ProductCategoryResponse.model_validate(category)

    async def list_categories(self) -> list[ProductCategoryResponse]:
        result = await self.session.execute(select(ProductCategory))
        return [ProductCategoryResponse.model_validate(c) for c in result.scalars().all()]

    async def create_product(self, payload: ProductCreate) -> ProductResponse:
        slug = payload.slug or generate_slug(payload.name)
        product = Product(
            name=payload.name,
            slug=slug,
            description=payload.description,
            sku=payload.sku,
            price=payload.price,
            compare_at_price=payload.compare_at_price,
            cost_price=payload.cost_price,
            stock_quantity=payload.stock_quantity,
            low_stock_threshold=payload.low_stock_threshold,
            is_active=payload.is_active,
            is_digital=payload.is_digital,
            weight_grams=payload.weight_grams,
            category_id=payload.category_id,
        )
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return self._to_response(product)

    async def get_product(self, product_id: int) -> ProductResponse:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")
        return self._to_response(product)

    async def get_by_slug(self, slug: str) -> ProductResponse:
        result = await self.session.execute(
            select(Product).where(Product.slug == slug)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")
        return self._to_response(product)

    async def update_product(
        self, product_id: int, payload: ProductUpdate
    ) -> ProductResponse:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        self.session.add(product)
        await self.session.flush()
        return self._to_response(product)

    async def delete_product(self, product_id: int) -> None:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product not found")
        await self.session.delete(product)

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[list[ProductResponse], int]:
        stmt = select(Product)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)
        if search:
            stmt = stmt.where(Product.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(Product.created_at.desc())
        total_result = await self.session.execute(select(Product).select_from(stmt.subquery()))
        total = len(total_result.scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        products = result.scalars().all()
        return [self._to_response(p) for p in products], total

    @staticmethod
    def _to_response(product: Product) -> ProductResponse:
        return ProductResponse.model_validate(
            {
                **product.__dict__,
                "is_low_stock": product.stock_quantity <= product.low_stock_threshold,
            }
        )