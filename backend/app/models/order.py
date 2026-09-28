"""Order & order-item models."""
from __future__ import annotations

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.enums import OrderStatus, TimestampMixin
from app.models.base import BaseMixin


class Order(BaseMixin, TimestampMixin):
    """A customer order."""

    __tablename__ = "order"

    order_number = Column(String(40), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    status = Column(String(20), default=OrderStatus.PENDING.value, index=True)
    shipping_address = Column(Text, nullable=True)
    billing_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")

    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def computed_total(self) -> float:
        return round(
            self.subtotal
            + self.tax_amount
            + self.shipping_amount
            - self.discount_amount,
            2,
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order(id={self.id}, order_number={self.order_number!r}, status={self.status!r})>"


class OrderItem(BaseMixin, TimestampMixin):
    """Single line item inside an order."""

    __tablename__ = "orderitem"

    order_id = Column(Integer, ForeignKey("order.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)
    line_total = Column(Float, nullable=False, default=0.0)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"