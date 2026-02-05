"""
Protected Route Examples with JWT Authentication and User Isolation

Complete examples of CRUD operations with proper security:
- JWT verification on all routes
- User ID verification (token vs URL)
- Resource ownership verification
- Database query filtering by user
- Proper error handling

Copy these patterns to your route files and adapt to your models.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from typing import List

# Import your dependencies
from middleware.jwt import verify_jwt, verify_user_access, verify_resource_ownership
from database import get_session
from models import Task, TaskCreate, TaskUpdate

router = APIRouter()


# ==============================================================================
# GET - List all resources for user
# ==============================================================================

@router.get("/api/{user_id}/tasks", response_model=List[Task])
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Get all tasks for authenticated user.

    Security:
    - Requires valid JWT token
    - Verifies user_id in URL matches token
    - Filters database query by authenticated user_id

    Returns:
        List[Task]: All tasks belonging to authenticated user
    """
    # Step 1: Verify user owns this endpoint
    verify_user_access(user_id, current_user)

    # Step 2: Query filtered by authenticated user
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return tasks


# ==============================================================================
# GET - Retrieve single resource
# ==============================================================================

@router.get("/api/{user_id}/tasks/{task_id}", response_model=Task)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Get specific task by ID.

    Security:
    - Requires valid JWT token
    - Verifies user_id in URL matches token
    - Verifies task belongs to authenticated user

    Returns:
        Task: Task details if found and owned by user

    Raises:
        404: Task not found
        403: Task belongs to different user
    """
    # Step 1: Verify endpoint ownership
    verify_user_access(user_id, current_user)

    # Step 2: Fetch resource
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found"
        )

    # Step 3: Verify resource ownership
    verify_resource_ownership(task.user_id, current_user, "task")

    return task


# ==============================================================================
# POST - Create new resource
# ==============================================================================

@router.post("/api/{user_id}/tasks", response_model=Task, status_code=201)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Create new task for authenticated user.

    Security:
    - Requires valid JWT token
    - Verifies user_id in URL matches token
    - Forces user_id from token (never trust client input)

    Args:
        user_id: User ID from URL path
        task_data: Validated task data (title, description, etc.)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        Task: Created task with generated ID

    Raises:
        403: user_id mismatch
        400: Invalid task data
    """
    # Step 1: Verify endpoint ownership
    verify_user_access(user_id, current_user)

    # Step 2: Create task with user_id from token (NEVER from client)
    task = Task(
        **task_data.dict(),
        user_id=current_user["user_id"]  # Force from authenticated user
    )

    # Step 3: Save to database
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# ==============================================================================
# PUT - Update existing resource
# ==============================================================================

@router.put("/api/{user_id}/tasks/{task_id}", response_model=Task)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Update existing task.

    Security:
    - Requires valid JWT token
    - Verifies user_id in URL matches token
    - Verifies task belongs to authenticated user
    - Only updates provided fields (partial update)

    Args:
        user_id: User ID from URL path
        task_id: Task ID to update
        task_data: Fields to update (only provided fields)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        Task: Updated task

    Raises:
        403: user_id mismatch or task belongs to different user
        404: Task not found
    """
    # Step 1: Verify endpoint ownership
    verify_user_access(user_id, current_user)

    # Step 2: Fetch resource
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found"
        )

    # Step 3: Verify resource ownership
    verify_resource_ownership(task.user_id, current_user, "task")

    # Step 4: Update only provided fields
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    # Step 5: Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# ==============================================================================
# PATCH - Partial update (alternative to PUT)
# ==============================================================================

@router.patch("/api/{user_id}/tasks/{task_id}", response_model=Task)
async def patch_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Partially update task (same as PUT in this case).

    Use PATCH for partial updates, PUT for full replacement.
    This example treats them the same for simplicity.

    Security: Same as PUT endpoint
    """
    # Reuse update logic
    return await update_task(user_id, task_id, task_data, current_user, session)


# ==============================================================================
# DELETE - Remove resource
# ==============================================================================

@router.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Delete task.

    Security:
    - Requires valid JWT token
    - Verifies user_id in URL matches token
    - Verifies task belongs to authenticated user

    Args:
        user_id: User ID from URL path
        task_id: Task ID to delete
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        dict: Confirmation message with deleted task ID

    Raises:
        403: user_id mismatch or task belongs to different user
        404: Task not found
    """
    # Step 1: Verify endpoint ownership
    verify_user_access(user_id, current_user)

    # Step 2: Fetch resource
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found"
        )

    # Step 3: Verify resource ownership
    verify_resource_ownership(task.user_id, current_user, "task")

    # Step 4: Delete resource
    session.delete(task)
    session.commit()

    return {
        "message": "Task deleted successfully",
        "id": task_id,
        "user_id": user_id
    }


# ==============================================================================
# Advanced: Bulk operations with user isolation
# ==============================================================================

@router.delete("/api/{user_id}/tasks")
async def delete_all_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Delete all tasks for user.

    Security:
    - Verifies user_id matches token
    - Only deletes tasks belonging to authenticated user

    USE WITH CAUTION: This deletes ALL user's tasks
    """
    verify_user_access(user_id, current_user)

    # Query filtered by user
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    count = len(tasks)

    for task in tasks:
        session.delete(task)

    session.commit()

    return {
        "message": f"Deleted {count} tasks",
        "count": count
    }


@router.patch("/api/{user_id}/tasks/bulk-complete")
async def bulk_complete_tasks(
    user_id: str,
    task_ids: List[int],
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Mark multiple tasks as completed.

    Security:
    - Verifies each task belongs to authenticated user
    - Skips tasks that don't exist or belong to other users
    """
    verify_user_access(user_id, current_user)

    updated_count = 0

    for task_id in task_ids:
        task = session.get(Task, task_id)

        # Skip if not found or doesn't belong to user
        if not task or task.user_id != current_user["user_id"]:
            continue

        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        updated_count += 1

    session.commit()

    return {
        "message": f"Updated {updated_count} tasks",
        "updated": updated_count,
        "requested": len(task_ids)
    }


# ==============================================================================
# Query parameters with user isolation
# ==============================================================================

@router.get("/api/{user_id}/tasks/search")
async def search_tasks(
    user_id: str,
    q: str | None = None,
    completed: bool | None = None,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """
    Search tasks with filters.

    Security:
    - Always filters by authenticated user_id
    - Query parameters only affect results within user's data

    Args:
        q: Search query for title/description
        completed: Filter by completion status
    """
    verify_user_access(user_id, current_user)

    # Start with user filter (ALWAYS required)
    query = select(Task).where(Task.user_id == user_id)

    # Add optional filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    if q:
        query = query.where(
            (Task.title.contains(q)) | (Task.description.contains(q))
        )

    tasks = session.exec(query).all()

    return tasks
