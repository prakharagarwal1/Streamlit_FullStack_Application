"""File upload schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_filename: str
    mime_type: str
    extension: Optional[str] = None
    size_bytes: int
    category: str
    storage_path: str
    is_public: bool
    download_count: int
    uploaded_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None