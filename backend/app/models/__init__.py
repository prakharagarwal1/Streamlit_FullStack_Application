"""Models package — registers all SQLAlchemy models on Base.metadata."""
from app.enums import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.product import Product, ProductCategory, ProductImage  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.post import Post, PostTag, Tag  # noqa: F401
from app.models.file import FileUpload  # noqa: F401
from app.models.api_key import ApiKey  # noqa: F401
from app.models.activity import ActivityLog  # noqa: F401
from app.models.task import Task  # noqa: F401