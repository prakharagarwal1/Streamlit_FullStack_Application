"""Background task model."""
from __future__ import annotations

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.enums import TaskPriority, TaskStatus, TimestampMixin, utc_now
from app.models.base import BaseMixin


class Task(BaseMixin, TimestampMixin):
    """A tracked background task (Celery-style)."""

    __tablename__ = "task"

    name = Column(String(120), index=True, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    status = Column(String(20), default=TaskStatus.PENDING.value, index=True)
    priority = Column(String(10), default=TaskPriority.MEDIUM.value, index=True)
    queue = Column(String(40), default="default", index=True)
    args = Column(JSON, nullable=True)
    kwargs = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0, index=True)
    progress_message = Column(String(255), nullable=True)
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    max_retries = Column(Integer, default=3)
    retry_count = Column(Integer, default=0)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)

    user = relationship("User", back_populates="tasks")

    @property
    def is_running(self) -> bool:
        return self.status == TaskStatus.RUNNING.value

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.SUCCESS.value

    @property
    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED.value

    def mark_running(self) -> None:
        self.status = TaskStatus.RUNNING.value
        self.started_at = utc_now()

    def mark_success(self, result=None) -> None:
        self.status = TaskStatus.SUCCESS.value
        self.result = result
        self.completed_at = utc_now()
        self.progress = 100

    def mark_failed(self, error_message: str) -> None:
        self.status = TaskStatus.FAILED.value
        self.error_message = error_message
        self.completed_at = utc_now()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Task(id={self.id}, name={self.name!r}, status={self.status!r})>"