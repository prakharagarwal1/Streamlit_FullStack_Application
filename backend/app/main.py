"""FastAPI application entry point."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.database import dispose_db, init_db
from app.exceptions import register_exception_handlers
from app.routers import (
    admin_router,
    analytics_router,
    auth_router,
    files_router,
    orders_router,
    posts_router,
    products_router,
    tasks_router,
)
from app.tasks.worker import app as celery_app
from app.utils.charts import build_plotly_figure  # noqa: F401 - demo import
from app.utils.serialization import model_to_dict  # noqa: F401 - demo import

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await init_db()
    # Start Celery worker (optional, only if broker configured)
    if settings.CELERY_BROKER_URL and "redis" in settings.CELERY_BROKER_URL:
        try:
            celery_app.connect_default_queue()
        except Exception:
            pass
    yield
    await dispose_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --- CORS -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiting ----------------------------------------------------------
try:
    from app.security import limiter

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
except Exception:  # pragma: no cover - optional dependency
    pass

# --- Request logging middleware ---------------------------------------------
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response


app.add_middleware(RequestLoggingMiddleware)

# --- Exception handlers -----------------------------------------------------
register_exception_handlers(app)

# --- Rate limit exceeded handler -------------------------------------------
@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests", "error": "RateLimitExceeded"},
    )

# --- Routers ---------------------------------------------------------------
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(products_router, prefix=API_PREFIX)
app.include_router(orders_router, prefix=API_PREFIX)
app.include_router(posts_router, prefix=API_PREFIX)
app.include_router(files_router, prefix=API_PREFIX)
app.include_router(tasks_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)


@app.get("/", tags=["health"])
async def root():
    """Liveness probe."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/metrics", tags=["health"])
async def metrics():
    """Prometheus metrics (if prometheus-client is installed)."""
    try:
        from prometheus_client import generate_latest

        return generate_latest()
    except Exception:
        return {"detail": "metrics unavailable"}