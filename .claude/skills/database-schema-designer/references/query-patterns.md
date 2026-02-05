# SQLModel Query Patterns

Comprehensive examples for common database operations with proper user isolation.

## Basic CRUD Operations

### Get All Records for User

```python
from sqlmodel import select

def get_user_tasks(user_id: str, session: Session) -> list[Task]:
    """Retrieve all tasks belonging to a user."""
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()
```

### Get Single Record with User Verification

```python
def get_task_by_id(task_id: int, user_id: str, session: Session) -> Task | None:
    """Get a single task, ensuring it belongs to the user."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return session.exec(statement).first()
```

### Create Record with Auto-Timestamps

```python
def create_task(
    user_id: str,
    title: str,
    description: str | None,
    session: Session
) -> Task:
    """Create a new task with automatic timestamp."""
    task = Task(
        user_id=user_id,
        title=title,
        description=description
        # created_at and updated_at set automatically
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Update Record with Timestamp Refresh

```python
from datetime import datetime

def update_task(
    task_id: int,
    user_id: str,
    updates: dict,
    session: Session
) -> Task | None:
    """Update task fields and refresh timestamp."""
    task = get_task_by_id(task_id, user_id, session)
    if not task:
        return None

    for key, value in updates.items():
        if hasattr(task, key):
            setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### Delete Record

```python
def delete_task(task_id: int, user_id: str, session: Session) -> bool:
    """Delete a task after verifying ownership."""
    task = get_task_by_id(task_id, user_id, session)
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True
```

## Filtering and Searching

### Filter by Status

```python
def get_completed_tasks(user_id: str, session: Session) -> list[Task]:
    """Get all completed tasks for a user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == True
    )
    return session.exec(statement).all()

def get_incomplete_tasks(user_id: str, session: Session) -> list[Task]:
    """Get all incomplete tasks for a user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False
    )
    return session.exec(statement).all()
```

### Text Search (Partial Match)

```python
def search_tasks_by_title(
    user_id: str,
    search_term: str,
    session: Session
) -> list[Task]:
    """Search tasks by title using partial match."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title.contains(search_term)
    )
    return session.exec(statement).all()
```

### Multiple Conditions (AND)

```python
def get_tasks_by_status_and_search(
    user_id: str,
    completed: bool,
    search_term: str | None,
    session: Session
) -> list[Task]:
    """Filter tasks by completion status and optional search term."""
    statement = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    if search_term:
        statement = statement.where(Task.title.contains(search_term))

    return session.exec(statement).all()
```

## Sorting

### Sort by Single Field

```python
def get_tasks_sorted_by_date(
    user_id: str,
    ascending: bool = True,
    session: Session
) -> list[Task]:
    """Get tasks sorted by creation date."""
    statement = select(Task).where(Task.user_id == user_id)

    if ascending:
        statement = statement.order_by(Task.created_at)
    else:
        statement = statement.order_by(Task.created_at.desc())

    return session.exec(statement).all()
```

### Sort by Multiple Fields

```python
def get_tasks_sorted_by_status_and_date(
    user_id: str,
    session: Session
) -> list[Task]:
    """Get tasks sorted by completion status (incomplete first), then by date."""
    statement = select(Task).where(Task.user_id == user_id).order_by(
        Task.completed,  # False (0) comes before True (1)
        Task.created_at.desc()
    )
    return session.exec(statement).all()
```

## Pagination

### Offset-Based Pagination

```python
def get_tasks_paginated(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    session: Session
) -> list[Task]:
    """Get paginated list of tasks."""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()
```

### Count for Pagination

```python
from sqlmodel import func

def get_task_count(user_id: str, session: Session) -> int:
    """Get total count of tasks for pagination metadata."""
    statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    return session.exec(statement).one()
```

### Complete Pagination Response

```python
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    items: list[Task]
    total: int
    skip: int
    limit: int
    has_more: bool

def get_tasks_with_pagination(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    session: Session
) -> PaginatedResponse:
    """Get tasks with complete pagination metadata."""
    total = get_task_count(user_id, session)
    items = get_tasks_paginated(user_id, skip, limit, session)

    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )
```

## Aggregations

### Count by Status

```python
def get_task_statistics(user_id: str, session: Session) -> dict:
    """Get task count statistics for a user."""
    total_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    total = session.exec(total_statement).one()

    completed_statement = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed == True
    )
    completed = session.exec(completed_statement).one()

    return {
        "total": total,
        "completed": completed,
        "incomplete": total - completed
    }
```

## Batch Operations

### Bulk Create

```python
def create_tasks_bulk(user_id: str, task_data_list: list[dict], session: Session) -> list[Task]:
    """Create multiple tasks at once."""
    tasks = [
        Task(user_id=user_id, **task_data)
        for task_data in task_data_list
    ]
    session.add_all(tasks)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks
```

### Bulk Update

```python
def mark_all_complete(user_id: str, session: Session) -> int:
    """Mark all tasks as completed for a user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False
    )
    tasks = session.exec(statement).all()

    for task in tasks:
        task.completed = True
        task.updated_at = datetime.utcnow()

    session.add_all(tasks)
    session.commit()
    return len(tasks)
```

### Bulk Delete

```python
def delete_completed_tasks(user_id: str, session: Session) -> int:
    """Delete all completed tasks for a user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == True
    )
    tasks = session.exec(statement).all()

    for task in tasks:
        session.delete(task)

    session.commit()
    return len(tasks)
```

## Relationships and Joins

### Query with Relationship Loading

```python
def get_task_with_user(task_id: int, session: Session) -> Task | None:
    """Get task with user relationship loaded."""
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    if task:
        # Relationship is loaded automatically if configured
        # Access: task.user.email
        pass

    return task
```

### Many-to-Many Query

```python
def get_tasks_by_tag(user_id: str, tag_name: str, session: Session) -> list[Task]:
    """Get tasks that have a specific tag."""
    statement = (
        select(Task)
        .join(TaskTag, Task.id == TaskTag.task_id)
        .join(Tag, TaskTag.tag_id == Tag.id)
        .where(
            Task.user_id == user_id,
            Tag.name == tag_name
        )
    )
    return session.exec(statement).all()
```

## Error Handling Patterns

### Safe Get or Create

```python
def get_or_create_task(
    user_id: str,
    title: str,
    session: Session
) -> tuple[Task, bool]:
    """Get existing task or create new one. Returns (task, created)."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title == title
    )
    task = session.exec(statement).first()

    if task:
        return task, False

    task = Task(user_id=user_id, title=title)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task, True
```

### Transaction Rollback

```python
def update_task_safely(
    task_id: int,
    user_id: str,
    updates: dict,
    session: Session
) -> Task | None:
    """Update task with automatic rollback on error."""
    try:
        task = get_task_by_id(task_id, user_id, session)
        if not task:
            return None

        for key, value in updates.items():
            setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception as e:
        session.rollback()
        raise e
```

## Performance Tips

1. **Use indexes on filtered fields**: Foreign keys, status flags, search fields
2. **Limit result sets**: Always use pagination for lists
3. **Avoid N+1 queries**: Use relationship loading or joins
4. **Batch operations**: Use bulk create/update when processing multiple records
5. **Select specific columns**: When you don't need full objects:
   ```python
   statement = select(Task.id, Task.title).where(Task.user_id == user_id)
   ```
