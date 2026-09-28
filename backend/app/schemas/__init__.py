"""Common response schemas."""
from __future__ import annotations

from app.schemas.common import BulkResponse, MessageResponse, PageResponse


from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    TokenRefresh,
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductCategoryCreate,
    ProductCategoryResponse,
)
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderItemCreate,
    OrderResponse,
    OrderItemResponse,
)
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    TagCreate,
    TagResponse,
)
from app.schemas.file import FileUploadResponse
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse
from app.schemas.activity import ActivityLogResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "TokenResponse",
    "TokenRefresh",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductCategoryCreate",
    "ProductCategoryResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderItemCreate",
    "OrderResponse",
    "OrderItemResponse",
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "TagCreate",
    "TagResponse",
    "FileUploadResponse",
    "ApiKeyCreate",
    "ApiKeyResponse",
    "ActivityLogResponse",
    "TaskCreate",
    "TaskResponse",
    "TaskUpdate",
    "PageResponse",
    "MessageResponse",
    "BulkResponse",
]