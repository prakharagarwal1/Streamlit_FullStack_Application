"""User model with authentication fields."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.enums import TimestampMixin, UserRole, utc_now
from app.models.base import BaseMixin


class User(BaseMixin, TimestampMixin):
    """A registered platform user."""

    __tablename__ = "user"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    is_staff = Column(Boolean, default=False, index=True)
    role = Column(String(20), default=UserRole.USER.value, index=True)

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )
    activities = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User(id={self.id}, username={self.username!r}, role={self.role!r})>"


# Avoid circular import at module load time
from app.models.base import BaseMixin  # noqa: E402