"""Pytest configuration and fixtures for backend tests.

Provides test client, database setup, and mock JWT token generation.
"""
import pytest
import os
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import uuid4
from jose import jwt

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-min-32-characters-long"
os.environ["FRONTEND_ORIGIN"] = "http://localhost:3000"

from main import app
from db import get_db


# Test database engine (in-memory SQLite for fast tests)
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    future=True,
)

test_session_factory = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture
async def test_db():
    """Provide test database session with clean schema."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client(test_db: AsyncSession):
    """Provide async HTTP client with test database."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def user_a_id():
    """Generate consistent user ID for User A."""
    return str(uuid4())


@pytest.fixture
def user_b_id():
    """Generate consistent user ID for User B."""
    return str(uuid4())


@pytest.fixture
def user_a_token(user_a_id):
    """Generate valid JWT token for User A."""
    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {"sub": user_a_id}
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def user_b_token(user_b_id):
    """Generate valid JWT token for User B."""
    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {"sub": user_b_id}
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def invalid_token():
    """Generate invalid JWT token (wrong secret)."""
    payload = {"sub": str(uuid4())}
    return jwt.encode(payload, "wrong-secret", algorithm="HS256")
