"""Posts router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.schemas.post import PostCreate, PostResponse, PostUpdate, TagCreate, TagResponse
from app.schemas.common import PageResponse
from app.services.post_service import PostService
from app.security import get_current_user_id

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    author_id: int = Depends(get_current_user_id),
    db=Depends(get_db),
):
    service = PostService(db)
    return await service.create_post(author_id, payload)


@router.get("", response_model=PageResponse[PostResponse])
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    author_id: int | None = Query(None),
    tag_id: int | None = Query(None),
    db=Depends(get_db),
):
    service = PostService(db)
    items, total = await service.list_posts(
        page=page, page_size=page_size, status=status, author_id=author_id, tag_id=tag_id
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return PageResponse[PostResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db=Depends(get_db)):
    service = PostService(db)
    return await service.get_post(post_id)


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(slug: str, db=Depends(get_db)):
    service = PostService(db)
    return await service.get_by_slug(slug)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    db=Depends(get_db),
):
    service = PostService(db)
    return await service.update_post(post_id, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db=Depends(get_db)):
    service = PostService(db)
    await service.delete_post(post_id)


@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(payload: TagCreate, db=Depends(get_db)):
    service = PostService(db)
    return await service.create_tag(payload)


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(db=Depends(get_db)):
    service = PostService(db)
    return await service.list_tags()