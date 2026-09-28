"""API key schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = None
    permissions: str = "read,write"


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key_prefix: str
    user_id: int
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    permissions: str
    created_at: Optional[datetime] = None


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned only once when the key is created — contains the raw key."""

    key: str