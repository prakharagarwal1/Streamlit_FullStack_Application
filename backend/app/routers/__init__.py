"""API routers."""
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.orders import router as orders_router
from app.routers.posts import router as posts_router
from app.routers.files import router as files_router
from app.routers.tasks import router as tasks_router
from app.routers.admin import router as admin_router
from app.routers.analytics import router as analytics_router

__all__ = [
    "auth_router",
    "products_router",
    "orders_router",
    "posts_router",
    "files_router",
    "tasks_router",
    "admin_router",
    "analytics_router",
]