"""File upload model."""
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.enums import FileCategory, TimestampMixin, utc_now
from app.models.base import BaseMixin


class FileUpload(BaseMixin, TimestampMixin):
    """Metadata for an uploaded file."""

    __tablename__ = "fileupload"

    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(120), nullable=False, index=True)
    extension = Column(String(16), nullable=True, index=True)
    size_bytes = Column(Integer, nullable=False, default=0)
    category = Column(String(20), default=FileCategory.OTHER.value, index=True)
    storage_path = Column(String(500), nullable=False)
    storage_backend = Column(String(20), default="local", index=True)
    checksum = Column(String(64), nullable=True, index=True)
    is_public = Column(Boolean, default=False, index=True)
    download_count = Column(Integer, default=0, index=True)
    uploaded_by_id = Column(
        Integer, ForeignKey("user.id"), nullable=True, index=True
    )
    expires_at = Column(DateTime, nullable=True, index=True)

    uploader = relationship("User", back_populates="files")
    activities = relationship(
        "ActivityLog", back_populates="file", cascade="all, delete-orphan"
    )

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at < utc_now()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FileUpload(id={self.id}, filename={self.filename!r}, size={self.size_bytes})>"