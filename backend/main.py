"""Multi-User Task Management API - Main Application.

Production-grade FastAPI application with JWT authentication, user isolation,
and PostgreSQL async database operations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging

from routers import tasks
from models import Task
from db import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: startup and shutdown events."""
    # Startup: Create database tables
    from sqlmodel import SQLModel
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables created (if not exists)")

    yield

    # Shutdown: cleanup if needed
    logger.info("Application shutting down")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Multi-User Task Management API",
    description="Secure REST API for todo tasks with JWT authentication and user isolation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration (spec FR-016)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # Only allow frontend origin
    allow_credentials=True,  # Allow cookies for Better Auth
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"]
)

# Register routers
app.include_router(tasks.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and deployment verification.

    Returns:
        dict: Service health status

    Example:
        GET /health
        Response: {"status": "healthy", "service": "task-api"}
    """
    return {"status": "healthy", "service": "task-api"}


logger.info("Application initialized")
