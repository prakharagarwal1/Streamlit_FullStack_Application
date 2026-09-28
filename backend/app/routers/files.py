"""Files router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.database import get_db
from app.schemas.file import FileUploadResponse
from app.schemas.common import PageResponse
from app.services.file_service import FileService
from app.security import get_current_user_id

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    is_public: bool = Form(False),
    expires_in_days: int | None = Form(None),
    user_id: int | None = Depends(get_current_user_id),
    db=Depends(get_db),
):
    service = FileService(db)
    content = await file.read()
    return await service.upload_file(
        file_bytes=content,
        filename=file.filename or "upload.bin",
        mime_type=file.content_type or "application/octet-stream",
        uploaded_by_id=user_id,
        is_public=is_public,
        expires_in_days=expires_in_days,
    )


@router.get("", response_model=PageResponse[FileUploadResponse])
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    uploaded_by_id: int | None = Query(None),
    category: str | None = Query(None),
    db=Depends(get_db),
):
    service = FileService(db)
    items, total = await service.list_files(
        page=page, page_size=page_size, uploaded_by_id=uploaded_by_id, category=category
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return PageResponse[FileUploadResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file(file_id: int, db=Depends(get_db)):
    service = FileService(db)
    return await service.get_file(file_id)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, db=Depends(get_db)):
    service = FileService(db)
    await service.delete_file(file_id)


@router.post("/upload-image")
async def upload_image(
    prompt: str,
    user_id: int | None = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Generate an image from a text prompt (DALL·E / OpenAI)."""
    from app.config import get_settings

    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured")
    try:
        from openai import OpenAI
        import httpx

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
        image_url = resp.data[0].url
        image_bytes = httpx.get(image_url, timeout=60).content
        service = FileService(db)
        record = await service.upload_file(
            file_bytes=image_bytes,
            filename=f"ai-{prompt[:30]}.png",
            mime_type="image/png",
            uploaded_by_id=user_id,
            is_public=False,
        )
        return {"image_url": image_url, "file": record.model_dump()}
    except Exception as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=str(exc))