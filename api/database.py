from contextlib import contextmanager
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings


# --- Async (for FastAPI) ---

# asyncpg requires postgresql+asyncpg:// scheme
_async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(_async_url, echo=False)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes."""
    async with async_session_factory() as session:
        yield session


# --- Sync (for Celery workers) ---

# psycopg2 uses plain postgresql:// scheme
sync_engine = create_engine(settings.DATABASE_URL, echo=False)
sync_session_factory = sessionmaker(sync_engine, expire_on_commit=False)


@contextmanager
def get_sync_session() -> Session:
    """Context manager for Celery tasks."""
    session = sync_session_factory()
    try:
        yield session
    finally:
        session.close()
