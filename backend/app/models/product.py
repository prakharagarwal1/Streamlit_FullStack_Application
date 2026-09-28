"""Product & category models."""
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.enums import TimestampMixin
from app.models.base import BaseMixin


class ProductCategory(BaseMixin, TimestampMixin):
    """Product category (e.g. Electronics, Books)."""

    __tablename__ = "productcategory"

    name = Column(String(80), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(
        Integer, ForeignKey("productcategory.id"), nullable=True, index=True
    )

    products = relationship("Product", back_populates="category")
    parent = relationship(
        "ProductCategory",
        back_populates="children",
        remote_side="ProductCategory.id",
    )
    children = relationship("ProductCategory", back_populates="parent")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductCategory(id={self.id}, name={self.name!r})>"


class Product(BaseMixin, TimestampMixin):
    """A sellable product."""

    __tablename__ = "product"

    name = Column(String(160), index=True, nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(60), unique=True, index=True, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    compare_at_price = Column(Float, nullable=True)  # MSRP / list price
    cost_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, default=0, index=True)
    low_stock_threshold = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, index=True)
    is_digital = Column(Boolean, default=False)
    weight_grams = Column(Float, nullable=True)
    category_id = Column(
        Integer, ForeignKey("productcategory.id"), nullable=True, index=True
    )

    category = relationship("ProductCategory", back_populates="products")
    images = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product(id={self.id}, name={self.name!r}, price={self.price})>"


class ProductImage(BaseMixin, TimestampMixin):
    """Product image URL + metadata."""

    __tablename__ = "productimage"

    url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False, index=True)
    product_id = Column(
        Integer, ForeignKey("product.id"), nullable=False, index=True
    )

    product = relationship("Product", back_populates="images")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductImage(id={self.id}, url={self.url!r})>"