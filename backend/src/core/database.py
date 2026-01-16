"""
Database configuration and session management.
"""
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from .config import settings

# Create async engine for SQLite
# Note: SQLite async support requires aiosqlite driver
DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # SQLite works best with StaticPool for local development
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        # Enable WAL mode for better concurrency
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA synchronous=NORMAL"))
        await conn.execute(text("PRAGMA cache_size=-64000"))  # 64MB cache
        await conn.execute(text("PRAGMA temp_store=MEMORY"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
