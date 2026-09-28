"""API key model for service-to-service auth."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.enums import TimestampMixin
from app.models.base import BaseMixin


class ApiKey(BaseMixin, TimestampMixin):
    """A hashed API key issued to a user."""

    __tablename__ = "apikey"

    name = Column(String(80), nullable=False)
    key_prefix = Column(String(12), nullable=False, index=True)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    last_used_at = Column(DateTime, nullable=True, index=True)
    permissions = Column(String(200), default="read,write")

    user = relationship("User", back_populates="api_keys")

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at < datetime.now(
            timezone.utc
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ApiKey(id={self.id}, name={self.name!r}, prefix={self.key_prefix!r})>"