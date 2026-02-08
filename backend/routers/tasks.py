"""Task management API endpoints with strict user isolation.

All endpoints enforce:
1. JWT authentication (get_current_user dependency)
2. User ID verification (path param matches authenticated user)
3. Database query filtering (all queries filter by user_id)

Security patterns per Constitution Principle II.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from uuid import UUID as TaskId  # Only for task IDs, not user IDs
import logging

from db import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskRead
from dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["tasks"])
logger = logging.getLogger(__name__)


@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def list_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all tasks for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Filters all tasks by user_id to prevent data leaks.

    Args:
        user_id: User ID from URL path (Better Auth text format)
        current_user_id: Authenticated user ID from JWT token
        db: Database session

    Returns:
        List[TaskRead]: All tasks belonging to the authenticated user

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if user_id != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Query with user_id filter (spec FR-004, Constitution Principle II)
    try:
        statement = select(Task).where(Task.user_id == user_id)
        results = await db.exec(statement)
        tasks = results.all()

        logger.info(f"Listed {len(tasks)} tasks for user {user_id}")
        return tasks
    except SQLAlchemyError as e:
        logger.error(f"Database error listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Sets user_id on task to authenticated user (not from request).

    Args:
        user_id: User ID from URL path (Better Auth text format)
        task_data: Task creation data (title, description)
        current_user_id: Authenticated user ID from JWT token
        db: Database session

    Returns:
        TaskRead: Created task with default values set

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 422: If validation fails (title empty or > 200 chars)
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if user_id != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users"
        )

    # Create task with authenticated user_id (spec FR-004)
    # CRITICAL: use authenticated user (str type), not path param
    try:
        task = Task(
            user_id=current_user_id,
            title=task_data.title,
            description=task_data.description
            # completed defaults to False (spec FR-012)
            # timestamps auto-set (spec FR-010)
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Created task {task.id} for user {current_user_id}")
        return task
    except SQLAlchemyError as e:
        logger.error(f"Database error creating task: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: TaskId,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single task by ID for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.

    Args:
        user_id: User ID from URL path (Better Auth text format)
        task_id: Task ID from URL path (UUID format)
        current_user_id: Authenticated user ID from JWT token
        db: Database session

    Returns:
        TaskRead: Task details

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If task not found or belongs to different user
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if user_id != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    try:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id  # CRITICAL: prevent cross-user access
        )
        result = await db.exec(statement)
        task = result.first()

        if task is None:
            # Spec FR-007: 404 for nonexistent OR foreign tasks (don't reveal existence)
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Retrieved task {task_id} for user {user_id}")
        return task
    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error getting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: TaskId,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing task for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.
    Updates only provided fields (partial update).

    Args:
        user_id: User ID from URL path (Better Auth text format)
        task_id: Task ID from URL path (UUID format)
        task_data: Task update data (title, description, completed)
        current_user_id: Authenticated user ID from JWT token
        db: Database session

    Returns:
        TaskRead: Updated task

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If task not found or belongs to different user
        HTTPException 422: If validation fails
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if user_id != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    try:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await db.exec(statement)
        task = result.first()

        if task is None:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update provided fields only (partial update)
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed

        # Update timestamp (spec FR-011)
        task.updated_at = datetime.utcnow()

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Updated task {task_id} for user {user_id}")
        return task
    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error updating task: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )


@router.delete("/{user_id}/tasks/{task_id}", response_model=dict)
async def delete_task(
    user_id: str,
    task_id: TaskId,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.

    Args:
        user_id: User ID from URL path (Better Auth text format)
        task_id: Task ID from URL path (UUID format)
        current_user_id: Authenticated user ID from JWT token
        db: Database session

    Returns:
        dict: {"success": True}

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If task not found or belongs to different user
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if user_id != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    try:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await db.exec(statement)
        task = result.first()

        if task is None:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        await db.delete(task)
        await db.commit()

        logger.info(f"Deleted task {task_id} for user {user_id}")
        return {"success": True}
    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting task: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: str,
    task_id: TaskId,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle the completion status of a task.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.
    Toggles: false → true, true → false.

    Args:
        user_id: User ID from URL path (Better Auth text format)
        task_id: Task ID from URL path (UUID format)
        current_user_id: Authenticated user ID from JWT token
        db: Database session

    Returns:
        TaskRead: Updated task

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If task not found or belongs to different user
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if user_id != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    try:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await db.exec(statement)
        task = result.first()

        if task is None:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Toggle completion status
        task.completed = not task.completed

        # Update timestamp (spec FR-011)
        task.updated_at = datetime.utcnow()

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Toggled completion for task {task_id} (now {task.completed}) for user {user_id}")
        return task
    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error toggling completion: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
