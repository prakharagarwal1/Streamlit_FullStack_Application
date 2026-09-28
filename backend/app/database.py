"""Async SQLAlchemy database engine and session factory."""
from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

# --- Async engine -----------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
)

# --- Session factory --------------------------------------------------------
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a fresh AsyncSession per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables on startup (useful for SQLite + dev)."""
    from sqlalchemy.exc import OperationalError

    from app.models import Base  # noqa: F401  (import to register mappers)

    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except OperationalError as exc:  # pragma: no cover - defensive
            # Some SQLite issues on Windows with file locks — retry once.
            import asyncio

            await asyncio.sleep(0.5)
            await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    """Dispose of the async engine during application shutdown."""
    await engine.dispose()