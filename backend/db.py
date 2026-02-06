"""Database connection and session management for async PostgreSQL operations.

This module configures the async database engine for Neon PostgreSQL using
asyncpg driver and provides dependency injection for FastAPI routes.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create async engine for Neon PostgreSQL
# echo=True logs SQL queries (useful for development and debugging)
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production for performance)
    future=True,
    pool_pre_ping=True,  # Verify connections before use (Neon serverless compatibility)
)

# Async session factory
# expire_on_commit=False prevents SQLAlchemy from expiring objects after commit
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI routes
# Usage: db: AsyncSession = Depends(get_db)
async def get_db():
    """Provide async database session for FastAPI dependency injection.

    Yields:
        AsyncSession: Database session for query execution

    Example:
        @router.get("/tasks")
        async def list_tasks(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Task))
            return result.scalars().all()
    """
    async with async_session() as session:
        yield session
