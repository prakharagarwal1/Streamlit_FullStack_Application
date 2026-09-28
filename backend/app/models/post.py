"""Blog post + tags models."""
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.enums import PostStatus, TimestampMixin, utc_now
from app.models.base import BaseMixin


class Tag(BaseMixin, TimestampMixin):
    """Reusable blog tag."""

    __tablename__ = "tag"

    name = Column(String(60), unique=True, index=True, nullable=False)
    slug = Column(String(80), unique=True, index=True, nullable=False)

    posts = relationship("PostTag", back_populates="tag")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Tag(id={self.id}, name={self.name!r})>"


class Post(BaseMixin, TimestampMixin):
    """Blog post authored by a user."""

    __tablename__ = "post"

    title = Column(String(200), index=True, nullable=False)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    status = Column(String(20), default=PostStatus.DRAFT.value, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    view_count = Column(Integer, default=0, index=True)
    is_pinned = Column(Boolean, default=False, index=True)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)

    author = relationship("User", back_populates="posts")
    tags = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")

    @property
    def is_published(self) -> bool:
        return self.status == PostStatus.PUBLISHED.value

    def publish(self) -> None:
        self.status = PostStatus.PUBLISHED.value
        if self.published_at is None:
            self.published_at = utc_now()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Post(id={self.id}, title={self.title!r}, status={self.status!r})>"


class PostTag(BaseMixin, TimestampMixin):
    """Association table between posts and tags."""

    __tablename__ = "posttag"

    post_id = Column(Integer, ForeignKey("post.id"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False, index=True)

    post = relationship("Post", back_populates="tags")
    tag = relationship("Tag", back_populates="posts")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PostTag(post_id={self.post_id}, tag_id={self.tag_id})>"