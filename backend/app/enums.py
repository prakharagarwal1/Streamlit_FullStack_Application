"""SQLAlchemy enum types and shared column mixins."""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Shared declarative base for all models.

    Automatically lowercases the class name as the table name.
    """

    @declared_attr
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()


def utc_now() -> datetime:
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at / updated_at columns to any model."""

    created_at: Column[DateTime] = Column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at: Column[DateTime] = Column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(str, enum.Enum):
    JSON = "application/json"
    CSV = "text/csv"
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"


class BaseMixin:
    """Common integer primary key."""

    id: Column[Integer] = Column(Integer, primary_key=True, index=True)


def soft_delete_filter(model):
    return model.is_deleted == False  # noqa: E712


def _optional_import(name: str) -> Optional[type]:
    """Lazy import helper for optional dependencies."""
    try:
        import importlib

        return importlib.import_module(name)
    except Exception:
        return None


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FileCategory(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"


class ActivityAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    EXPORT = "export"