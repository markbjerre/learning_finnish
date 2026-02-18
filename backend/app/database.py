"""Database configuration and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Use separate schema for FastAPI tables to avoid conflict with homelab schema (public.words has integer id)
APP_SCHEMA = "app"

# Create async engine
if settings.database_url:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=0,
        connect_args={"server_settings": {"search_path": f'"{APP_SCHEMA}", public'}} if (settings.database_url or "").startswith("postgresql") else {},
    )
else:
    # Default to SQLite for development if no database_url is set
    engine = create_async_engine(
        "sqlite+aiosqlite:///./learning_finnish.db",
        echo=settings.debug,
        future=True,
        connect_args={"check_same_thread": False},
    )

# Create session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables in app schema (avoids conflict with homelab public.words)"""
    async with engine.begin() as conn:
        if "postgresql" in (settings.database_url or ""):
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{APP_SCHEMA}"'))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def close_db():
    """Close database engine"""
    await engine.dispose()
    logger.info("Database closed")
