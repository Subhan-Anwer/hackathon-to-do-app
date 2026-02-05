# User Isolation Patterns

Comprehensive guide to implementing secure user data isolation in multi-tenant applications.

## Table of Contents

- [Overview](#overview)
- [The Three-Layer Defense](#the-three-layer-defense)
- [Database Schema Design](#database-schema-design)
- [Query Patterns](#query-patterns)
- [Route Protection Layers](#route-protection-layers)
- [Common Anti-Patterns](#common-anti-patterns)
- [Testing User Isolation](#testing-user-isolation)

## Overview

**User Isolation** ensures that users can only access their own data, never other users' data. This is critical for:
- Privacy compliance (GDPR, CCPA)
- Security (preventing data breaches)
- Trust (users expect their data is private)

**Threat Model:**
- Malicious user tries to access another user's data
- Attacker manipulates request parameters (IDOR attack)
- Token theft or session hijacking
- Privilege escalation attempts

## The Three-Layer Defense

Implement defense-in-depth with three validation layers:

### Layer 1: JWT Authentication
```python
current_user: dict = Depends(verify_jwt)
# Validates: Token is valid, not expired, signed with correct secret
```

### Layer 2: Endpoint Ownership
```python
if current_user["user_id"] != url_user_id:
    raise HTTPException(status_code=403)
# Validates: User in token matches user in URL
```

### Layer 3: Resource Ownership
```python
if resource.user_id != current_user["user_id"]:
    raise HTTPException(status_code=403)
# Validates: Resource belongs to authenticated user
```

**Why Three Layers?**
- Layer 1 fails: Unauthenticated user blocked
- Layer 2 fails: User trying to access another user's endpoint blocked
- Layer 3 fails: User trying to modify another user's resource blocked

## Database Schema Design

### Add user_id to All User-Owned Tables

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    """User account table"""
    id: str = Field(primary_key=True)  # UUID from Better Auth
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="owner")


class Task(SQLModel, table=True):
    """User's task (user-owned resource)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)

    # CRITICAL: user_id foreign key for isolation
    user_id: str = Field(foreign_key="user.id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    owner: User = Relationship(back_populates="tasks")
```

**Key Design Principles:**
1. **user_id is indexed** - Enables fast filtering by user
2. **Foreign key constraint** - Ensures referential integrity
3. **Required field** - Cannot create resource without user_id
4. **Consistent naming** - Always use `user_id` (not `userId`, `owner_id`, etc.)

### Multi-Level Hierarchies

For nested resources (e.g., Project → Task → Comment):

```python
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: str = Field(foreign_key="user.id", index=True)  # Owner


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    project_id: int = Field(foreign_key="project.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)  # Denormalized for fast filtering


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    task_id: int = Field(foreign_key="task.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)  # Denormalized
```

**Why Denormalize user_id?**
- Enables single-query filtering: `WHERE user_id = ?`
- Avoids expensive joins to check ownership
- Simplifies query logic
- Improves performance

## Query Patterns

### Pattern 1: List Resources (Always Filter by user_id)

```python
from sqlmodel import select, Session

@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Verify endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # CRITICAL: Always filter by user_id
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return tasks
```

**Anti-Pattern:**
```python
# ❌ WRONG - Returns ALL tasks from ALL users
tasks = session.exec(select(Task)).all()
```

### Pattern 2: Get Single Resource (Verify Ownership)

```python
@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Layer 2: Endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # Fetch resource
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # Layer 3: Resource ownership
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403)

    return task
```

**Optimization (Single Query):**
```python
# Combine fetch and ownership check in one query
task = session.exec(
    select(Task)
    .where(Task.id == task_id)
    .where(Task.user_id == user_id)
).first()

if not task:
    raise HTTPException(status_code=404)

return task
```

### Pattern 3: Create Resource (Force user_id from Token)

```python
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Verify endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # CRITICAL: Force user_id from token, NEVER from client
    task = Task(
        **task_data.dict(),
        user_id=current_user["user_id"]  # From authenticated token
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

**Anti-Pattern:**
```python
# ❌ WRONG - Client controls user_id
task = Task(**task_data.dict())  # task_data might include user_id!

# ❌ WRONG - Using user_id from URL (not verified)
task = Task(**task_data.dict(), user_id=user_id)
```

### Pattern 4: Update Resource (Double Verification)

```python
@router.put("/api/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Layer 2: Endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # Fetch resource
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # Layer 3: Resource ownership
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403)

    # Update (user_id cannot be changed)
    for key, value in task_data.dict(exclude_unset=True).items():
        if key != "user_id":  # Never allow changing user_id
            setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

### Pattern 5: Delete Resource (Same as Update)

```python
@router.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Layer 2: Endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # Fetch resource
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # Layer 3: Resource ownership
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403)

    # Delete
    session.delete(task)
    session.commit()

    return {"message": "Task deleted", "id": task_id}
```

### Pattern 6: Search and Filtering

```python
@router.get("/api/{user_id}/tasks/search")
async def search_tasks(
    user_id: str,
    q: Optional[str] = None,
    completed: Optional[bool] = None,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Verify endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # Start with user filter (ALWAYS required)
    query = select(Task).where(Task.user_id == user_id)

    # Add optional filters
    if q:
        query = query.where(Task.title.contains(q))
    if completed is not None:
        query = query.where(Task.completed == completed)

    tasks = session.exec(query).all()
    return tasks
```

**Critical: User filter is first and always applied**

### Pattern 7: Bulk Operations

```python
@router.post("/api/{user_id}/tasks/bulk-update")
async def bulk_update(
    user_id: str,
    task_ids: list[int],
    updates: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Verify endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    updated_count = 0

    for task_id in task_ids:
        # Fetch and verify ownership for each
        task = session.get(Task, task_id)

        if not task or task.user_id != current_user["user_id"]:
            continue  # Skip tasks that don't exist or don't belong to user

        # Update
        for key, value in updates.dict(exclude_unset=True).items():
            setattr(task, key, value)

        session.add(task)
        updated_count += 1

    session.commit()

    return {
        "updated": updated_count,
        "requested": len(task_ids)
    }
```

## Route Protection Layers

### Helper Functions for Reusability

```python
# middleware/jwt.py

def verify_user_access(url_user_id: str, current_user: dict) -> None:
    """Verify endpoint ownership (Layer 2)"""
    if current_user["user_id"] != url_user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own resources"
        )


def verify_resource_ownership(
    resource_user_id: str,
    current_user: dict,
    resource_name: str = "resource"
) -> None:
    """Verify resource ownership (Layer 3)"""
    if resource_user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to access this {resource_name}"
        )
```

### Using Helper Functions

```python
@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Layer 2
    verify_user_access(user_id, current_user)

    # Fetch
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # Layer 3
    verify_resource_ownership(task.user_id, current_user, "task")

    return task
```

## Common Anti-Patterns

### Anti-Pattern 1: Trusting Client Input

```python
# ❌ WRONG
@router.post("/api/tasks")
async def create_task(task_data: TaskCreate):
    # Client could set any user_id!
    task = Task(**task_data.dict())
```

**Fix:**
```python
# ✅ CORRECT
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
):
    verify_user_access(user_id, current_user)
    task = Task(**task_data.dict(), user_id=current_user["user_id"])
```

### Anti-Pattern 2: No Query Filtering

```python
# ❌ WRONG - Returns all users' data
tasks = session.exec(select(Task)).all()

# ❌ WRONG - Filters after fetching (inefficient, memory leak)
all_tasks = session.exec(select(Task)).all()
user_tasks = [t for t in all_tasks if t.user_id == user_id]
```

**Fix:**
```python
# ✅ CORRECT - Filter in database
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

### Anti-Pattern 3: Missing Resource Ownership Check

```python
# ❌ WRONG - Only checks endpoint ownership, not resource
@router.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(user_id: str, task_id: int, current_user: dict):
    verify_user_access(user_id, current_user)
    task = session.get(Task, task_id)
    session.delete(task)  # What if task belongs to different user?
```

**Fix:**
```python
# ✅ CORRECT - Check both endpoint and resource
verify_user_access(user_id, current_user)
task = session.get(Task, task_id)
if not task:
    raise HTTPException(404)
verify_resource_ownership(task.user_id, current_user, "task")
session.delete(task)
```

### Anti-Pattern 4: Using user_id from URL Without Verification

```python
# ❌ WRONG - user_id not verified against token
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str):
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
```

**Fix:**
```python
# ✅ CORRECT - Verify user_id matches token
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
):
    verify_user_access(user_id, current_user)
    # Now safe to use user_id
```

### Anti-Pattern 5: Returning 404 for Forbidden Resources

```python
# ⚠️ INFORMATION LEAK - Reveals resource existence
task = session.get(Task, task_id)
if not task:
    raise HTTPException(404)
if task.user_id != current_user["user_id"]:
    raise HTTPException(404)  # Should be 403!
```

**Better (but still debatable):**
```python
# Option 1: Return 403 (honest but reveals existence)
if task.user_id != current_user["user_id"]:
    raise HTTPException(403, "Forbidden")

# Option 2: Return 404 (hides existence, better for security)
if task.user_id != current_user["user_id"]:
    raise HTTPException(404, "Not found")
```

## Testing User Isolation

### Test Cases

```python
import pytest

class TestUserIsolation:
    """Comprehensive user isolation tests"""

    def test_user_cannot_list_other_users_resources(
        self, client, user_a_token, user_b_id
    ):
        """User A cannot list User B's resources"""
        response = client.get(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 403

    def test_user_cannot_read_other_users_resource(
        self, client, user_a_token, user_b_task_id
    ):
        """User A cannot read User B's specific resource"""
        response = client.get(
            f"/api/user_a_id/tasks/{user_b_task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 403

    def test_user_cannot_create_for_other_user(
        self, client, user_a_token, user_b_id
    ):
        """User A cannot create resources for User B"""
        response = client.post(
            f"/api/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "Test"}
        )
        assert response.status_code == 403

    def test_user_cannot_update_other_users_resource(
        self, client, user_a_token, user_b_task_id
    ):
        """User A cannot update User B's resource"""
        response = client.put(
            f"/api/user_a_id/tasks/{user_b_task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "Hacked"}
        )
        assert response.status_code == 403

    def test_user_cannot_delete_other_users_resource(
        self, client, user_a_token, user_b_task_id
    ):
        """User A cannot delete User B's resource"""
        response = client.delete(
            f"/api/user_a_id/tasks/{user_b_task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert response.status_code == 403

    def test_list_only_returns_user_resources(
        self, client, user_a_token, seed_data
    ):
        """List returns only authenticated user's resources"""
        response = client.get(
            "/api/user_a_id/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        assert response.status_code == 200
        tasks = response.json()

        # All tasks should belong to user_a
        for task in tasks:
            assert task["user_id"] == "user_a_id"

    def test_search_filters_by_user(
        self, client, user_a_token, seed_data
    ):
        """Search only returns authenticated user's results"""
        response = client.get(
            "/api/user_a_id/tasks/search?q=test",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        tasks = response.json()
        for task in tasks:
            assert task["user_id"] == "user_a_id"
```

### Manual Testing Checklist

- [ ] User A cannot access User B's endpoint (`/api/user_b/...`)
- [ ] User A cannot access User B's resources by ID
- [ ] List endpoints only return authenticated user's data
- [ ] Create forces user_id from token
- [ ] Update verifies resource ownership
- [ ] Delete verifies resource ownership
- [ ] Search filters by authenticated user
- [ ] Bulk operations verify ownership for each item
- [ ] No data leakage in error messages
- [ ] 403 returned for authorization failures (not 404)

## Summary Checklist

For every protected endpoint:

- [ ] JWT verification (`current_user: dict = Depends(verify_jwt)`)
- [ ] Endpoint ownership verification (`verify_user_access(user_id, current_user)`)
- [ ] Database queries filtered by user_id
- [ ] Resource ownership verification for get/update/delete
- [ ] Force user_id from token for create operations
- [ ] Never trust client-provided user_id
- [ ] Test cross-user access attempts
- [ ] Proper HTTP status codes (401 auth, 403 authorization)
