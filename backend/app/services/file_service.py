"""File upload service with local storage + categorization."""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.enums import FileCategory
from app.exceptions import NotFoundError
from app.models.file import FileUpload
from app.schemas.file import FileUploadResponse


class FileService:
    """Upload, store, and track files."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()

    def _categorize(self, mime_type: str, extension: str) -> str:
        ext = (extension or "").lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"} or mime_type.startswith("image/"):
            return FileCategory.IMAGE.value
        if ext in {".pdf", ".docx", ".txt", ".csv", ".xlsx", ".doc"} or mime_type.startswith("text/") or "spreadsheet" in mime_type or "wordprocessing" in mime_type:
            return FileCategory.DOCUMENT.value
        if ext in {".mp4", ".mov", ".avi", ".mkv"} or mime_type.startswith("video/"):
            return FileCategory.VIDEO.value
        if ext in {".mp3", ".wav", ".flac", ".aac"} or mime_type.startswith("audio/"):
            return FileCategory.AUDIO.value
        if ext in {".zip", ".rar", ".tar", ".gz", ".7z"} or "zip" in mime_type or "compressed" in mime_type:
            return FileCategory.ARCHIVE.value
        return FileCategory.OTHER.value

    def _storage_path(self, filename: str) -> str:
        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique = uuid.uuid4().hex
        sub = upload_dir / unique[:2]
        sub.mkdir(parents=True, exist_ok=True)
        return str(sub / f"{unique}_{filename}")

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        uploaded_by_id: Optional[int] = None,
        is_public: bool = False,
        expires_in_days: Optional[int] = None,
    ) -> FileUploadResponse:
        if len(file_bytes) > self.settings.MAX_UPLOAD_BYTES:
            from app.exceptions import ValidationError

            raise ValidationError("File exceeds maximum upload size")

        extension = Path(filename).suffix
        category = self._categorize(mime_type, extension)
        storage_path = self._storage_path(filename)
        with open(storage_path, "wb") as f:
            f.write(file_bytes)
        checksum = hashlib.sha256(file_bytes).hexdigest()
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        record = FileUpload(
            filename=Path(storage_path).name,
            original_filename=filename,
            mime_type=mime_type,
            extension=extension,
            size_bytes=len(file_bytes),
            category=category,
            storage_path=storage_path,
            storage_backend="local",
            checksum=checksum,
            is_public=is_public,
            uploaded_by_id=uploaded_by_id,
            expires_at=expires_at,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return FileUploadResponse.model_validate(record)

    async def get_file(self, file_id: int) -> FileUploadResponse:
        result = await self.session.execute(
            select(FileUpload).where(FileUpload.id == file_id)
        )
        file = result.scalar_one_or_none()
        if not file:
            raise NotFoundError("File not found")
        return FileUploadResponse.model_validate(file)

    async def list_files(
        self,
        page: int = 1,
        page_size: int = 20,
        uploaded_by_id: Optional[int] = None,
        category: Optional[str] = None,
    ) -> Tuple[List[FileUploadResponse], int]:
        stmt = select(FileUpload)
        if uploaded_by_id is not None:
            stmt = stmt.where(FileUpload.uploaded_by_id == uploaded_by_id)
        if category:
            stmt = stmt.where(FileUpload.category == category)
        stmt = stmt.order_by(FileUpload.created_at.desc())
        total_result = await self.session.execute(select(FileUpload).select_from(stmt.subquery()))
        total = len(total_result.scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        files = result.scalars().all()
        return [FileUploadResponse.model_validate(f) for f in files], total

    async def delete_file(self, file_id: int) -> None:
        result = await self.session.execute(
            select(FileUpload).where(FileUpload.id == file_id)
        )
        file = result.scalar_one_or_none()
        if not file:
            raise NotFoundError("File not found")
        try:
            if os.path.exists(file.storage_path):
                os.remove(file.storage_path)
        except OSError:
            pass
        await self.session.delete(file)

    async def increment_download(self, file_id: int) -> None:
        result = await self.session.execute(
            select(FileUpload).where(FileUpload.id == file_id)
        )
        file = result.scalar_one_or_none()
        if file:
            file.download_count += 1
            self.session.add(file)