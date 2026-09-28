"""Background task schemas."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: str = "medium"
    queue: str = "default"
    args: Optional[list] = None
    kwargs: Optional[dict] = None
    scheduled_at: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def priority_valid(cls, v: str) -> str:
        if v not in {"low", "medium", "high", "critical"}:
            raise ValueError("priority must be low, medium, high, or critical")
        return v


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    progress_message: Optional[str] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    user_id: Optional[int] = None
    status: str
    priority: str
    queue: str
    args: Optional[Any] = None
    kwargs: Optional[Any] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    progress: int
    progress_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int
    max_retries: int
    scheduled_at: Optional[str] = None
    created_at: Optional[str] = None