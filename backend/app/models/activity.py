"""Activity log model for audit trail."""
from __future__ import annotations

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.enums import ActivityAction, TimestampMixin, utc_now
from app.models.base import BaseMixin


class ActivityLog(BaseMixin, TimestampMixin):
    """Audit trail entry for user actions."""

    __tablename__ = "activitylog"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    action = Column(String(20), default=ActivityAction.CREATE.value, index=True)
    resource_type = Column(String(40), nullable=True, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True)
    path = Column(String(500), nullable=True, index=True)
    status_code = Column(Integer, nullable=True, index=True)
    metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="activities")
    file = relationship("FileUpload", back_populates="activities")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ActivityLog(id={self.id}, action={self.action!r}, path={self.path!r})>"