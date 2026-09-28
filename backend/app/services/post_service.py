"""Blog post service."""
from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.post import Post, PostTag, Tag
from app.schemas.post import (
    PostCreate,
    PostResponse,
    PostUpdate,
    TagCreate,
    TagResponse,
)
from app.security import generate_slug


class PostService:
    """Blog post + tag business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_post(self, author_id: int, payload: PostCreate) -> PostResponse:
        slug = payload.slug or generate_slug(payload.title)
        post = Post(
            title=payload.title,
            slug=slug,
            excerpt=payload.excerpt,
            content=payload.content,
            author_id=author_id,
            status=payload.status,
            cover_image_url=payload.cover_image_url,
            meta_title=payload.meta_title,
            meta_description=payload.meta_description,
        )
        if payload.status == "published":
            from app.enums import utc_now

            post.published_at = utc_now()
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        await self._sync_tags(post.id, payload.tag_ids)
        return await self._to_response(post)

    async def get_post(self, post_id: int) -> PostResponse:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")
        return await self._to_response(post)

    async def get_by_slug(self, slug: str) -> PostResponse:
        result = await self.session.execute(select(Post).where(Post.slug == slug))
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")
        return await self._to_response(post)

    async def update_post(
        self, post_id: int, payload: PostUpdate
    ) -> PostResponse:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")
        data = payload.model_dump(exclude_unset=True)
        if "slug" in data and not data["slug"]:
            data["slug"] = generate_slug(post.title)
        if "title" in data and "slug" not in data:
            data["slug"] = generate_slug(data["title"])
        for field, value in data.items():
            if field == "tag_ids":
                continue
            setattr(post, field, value)
        if data.get("status") == "published" and post.published_at is None:
            from app.enums import utc_now

            post.published_at = utc_now()
        self.session.add(post)
        await self.session.flush()
        if "tag_ids" in data and data["tag_ids"] is not None:
            await self._sync_tags(post.id, data["tag_ids"])
        return await self._to_response(post)

    async def delete_post(self, post_id: int) -> None:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundError("Post not found")
        await self.session.delete(post)

    async def list_posts(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        author_id: Optional[int] = None,
        tag_id: Optional[int] = None,
    ) -> Tuple[list[PostResponse], int]:
        stmt = select(Post)
        if status:
            stmt = stmt.where(Post.status == status)
        if author_id:
            stmt = stmt.where(Post.author_id == author_id)
        if tag_id:
            stmt = stmt.join(PostTag, PostTag.post_id == Post.id).where(
                PostTag.tag_id == tag_id
            )
        stmt = stmt.order_by(Post.created_at.desc())
        total_result = await self.session.execute(select(Post).select_from(stmt.subquery()))
        total = len(total_result.scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        posts = result.scalars().unique().all()
        return [await self._to_response(p) for p in posts], total

    async def create_tag(self, payload: TagCreate) -> TagResponse:
        slug = payload.slug or generate_slug(payload.name)
        tag = Tag(name=payload.name, slug=slug)
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return TagResponse.model_validate(tag)

    async def list_tags(self) -> list[TagResponse]:
        result = await self.session.execute(select(Tag))
        return [TagResponse.model_validate(t) for t in result.scalars().all()]

    async def increment_view(self, post_id: int) -> None:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post:
            post.view_count += 1
            self.session.add(post)

    async def _sync_tags(self, post_id: int, tag_ids: list[int]) -> None:
        # Remove existing
        result = await self.session.execute(
            select(PostTag).where(PostTag.post_id == post_id)
        )
        for existing in result.scalars().all():
            await self.session.delete(existing)
        for tag_id in tag_ids:
            tag = await self.session.get(Tag, tag_id)
            if tag:
                self.session.add(PostTag(post_id=post_id, tag_id=tag_id))

    async def _to_response(self, post: Post) -> PostResponse:
        result = await self.session.execute(
            select(PostTag).where(PostTag.post_id == post.id)
        )
        tag_ids = [pt.tag_id for pt in result.scalars().all()]
        tags: list[TagResponse] = []
        if tag_ids:
            tag_result = await self.session.execute(
                select(Tag).where(Tag.id.in_(tag_ids))
            )
            tags = [TagResponse.model_validate(t) for t in tag_result.scalars().all()]
        return PostResponse.model_validate({**post.__dict__, "tags": tags})