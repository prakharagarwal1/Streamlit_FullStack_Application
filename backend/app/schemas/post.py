"""Blog post Pydantic schemas."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TagCreate(BaseModel):
    name: str
    slug: Optional[str] = None


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class PostCreate(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    slug: Optional[str] = None
    status: str = "draft"
    tag_ids: List[int] = []
    cover_image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in {"draft", "published", "archived"}:
            raise ValueError("status must be draft, published, or archived")
        return v


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    cover_image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    author_id: int
    status: str
    published_at: Optional[str] = None
    view_count: int
    is_pinned: bool
    cover_image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: List[TagResponse] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None