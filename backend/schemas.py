"""Pydantic schemas for request/response validation.

This module defines schemas for task creation, updates, and API responses.
Enforces validation rules from spec (title length, optional fields).
"""
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for creating a new task.

    Validates:
    - title: required, 1-200 characters (FR-008, FR-009)
    - description: optional, no length limit (FR-013)
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating an existing task.

    All fields optional - only provided fields are updated (partial update).

    Validates:
    - title: optional, 1-200 characters if provided
    - description: optional
    - completed: optional boolean
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskRead(BaseModel):
    """Schema for reading task data in API responses.

    IMPORTANT: Does not include user_id in response (privacy).
    User isolation is enforced at query level, not response level.

    Configuration:
    - from_attributes=True: Enables conversion from SQLModel to Pydantic
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
