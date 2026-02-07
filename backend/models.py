"""SQLModel database models with strict user isolation.

This module defines the Task entity with mandatory user_id filtering for all queries.
Every task belongs to exactly one user, enforcing Constitution Principle II.
"""
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


class Task(SQLModel, table=True):
    """Task model with strict user isolation.

    Every task belongs to exactly one user (user_id).
    All queries MUST filter by user_id to prevent cross-user data leaks.

    Constitution Principle II compliance:
    - user_id is indexed for query performance
    - All queries must include .where(Task.user_id == authenticated_user_id)

    Example usage:
        # ✅ CORRECT - User isolation enforced
        tasks = session.exec(
            select(Task).where(Task.user_id == request.state.user_id)
        ).all()

        # ❌ WRONG - Security violation, exposes all users' data
        tasks = session.exec(select(Task)).all()
    """
    __tablename__ = "tasks"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the task"
    )

    # Foreign key to user (managed by Better Auth)
    # CRITICAL: indexed for efficient user-scoped queries
    # Note: Better Auth uses text-based IDs, not UUIDs
    user_id: str = Field(
        index=True,
        nullable=False,
        description="ID of the user who owns this task (Better Auth text format)"
    )

    # Task data
    title: str = Field(
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional detailed description of the task"
    )

    completed: bool = Field(
        default=False,
        description="Completion status (false = incomplete, true = complete)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when task was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when task was last modified (UTC)"
    )
