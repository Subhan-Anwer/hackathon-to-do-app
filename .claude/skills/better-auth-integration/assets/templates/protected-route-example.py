# Example protected route with JWT authentication
from fastapi import APIRouter, Depends, HTTPException
from middleware.jwt import verify_jwt, verify_user_access
from typing import List

router = APIRouter()


@router.get("/api/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
):
    """
    Get tasks for a specific user.
    Requires authentication and user isolation.
    """
    # Verify the authenticated user can access this user's data
    verify_user_access(user_id, current_user)

    # Fetch user's tasks from database
    # tasks = db.query(Task).filter(Task.user_id == user_id).all()

    return {
        "user_id": user_id,
        "tasks": []  # Replace with actual database query
    }


@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: dict,
    current_user: dict = Depends(verify_jwt),
):
    """
    Create a new task for a specific user.
    Requires authentication and user isolation.
    """
    # Verify the authenticated user can access this user's data
    verify_user_access(user_id, current_user)

    # Create task in database
    # new_task = Task(**task_data, user_id=user_id)
    # db.add(new_task)
    # db.commit()

    return {
        "message": "Task created",
        "user_id": user_id,
        "task": task_data
    }


@router.get("/api/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
):
    """
    Get user profile.
    Requires authentication and user isolation.
    """
    verify_user_access(user_id, current_user)

    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
    }
