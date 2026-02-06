# Data Model: Multi-User Task Management API

**Feature**: 001-task-api
**Date**: 2026-02-06
**Status**: Complete

## Overview

This document defines the database schema for the multi-user task management system. The data model enforces strict user isolation through foreign key relationships and indexed queries. All entities follow SQLModel conventions for async PostgreSQL operations.

## Entity-Relationship Diagram

```
┌─────────────────────┐
│      User           │ (Managed by Better Auth - not in this database)
│                     │
│ - id: UUID (PK)     │
└──────────┬──────────┘
           │
           │ 1:N (one user has many tasks)
           │
           ▼
┌─────────────────────┐
│      Task           │
│                     │
│ - id: UUID (PK)     │
│ - user_id: UUID (FK)│───┐ (indexed)
│ - title: str        │   │
│ - description: str? │   │ CRITICAL: All queries MUST filter by user_id
│ - completed: bool   │   │ to enforce user isolation
│ - created_at: dt    │   │
│ - updated_at: dt    │   │
└─────────────────────┘   │
                          │
                          └──> Filters: .where(Task.user_id == authenticated_user_id)
```

## Entity Definitions

### Task Entity

**Purpose**: Represents a todo item belonging to exactly one user.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model with strict user isolation.

    Every task belongs to exactly one user (user_id).
    All queries MUST filter by user_id to prevent cross-user data leaks.

    Constitution Principle II compliance:
    - user_id is indexed for query performance
    - All queries must include .where(Task.user_id == authenticated_user_id)
    """
    __tablename__ = "tasks"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the task"
    )

    # Foreign key to user (managed by Better Auth)
    user_id: UUID = Field(
        index=True,  # CRITICAL: indexed for efficient user-scoped queries
        nullable=False,
        description="ID of the user who owns this task"
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
        default_factory=datetime.utcnow,
        description="Timestamp when task was created (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was last modified (UTC)"
    )
```

**Table Name**: `tasks`

**Columns**:

| Column | Type | Constraints | Description | Spec Reference |
|--------|------|-------------|-------------|----------------|
| id | UUID | PRIMARY KEY | Unique task identifier | FR-014 |
| user_id | UUID | NOT NULL, INDEXED | Owner of the task (foreign key concept) | FR-004, FR-014 |
| title | VARCHAR(200) | NOT NULL | Task title (required) | FR-008, FR-009 |
| description | TEXT | NULLABLE | Optional task description | FR-013 |
| completed | BOOLEAN | DEFAULT FALSE | Completion status | FR-012 |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp | FR-010 |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp | FR-011 |

**Indexes**:
1. **PRIMARY KEY** on `id`: Automatic, unique identifier
2. **INDEX** on `user_id`: **CRITICAL for performance and security**
   - Enables fast queries: `SELECT * FROM tasks WHERE user_id = ?`
   - All queries MUST filter by user_id (Constitution Principle II)
   - Without this index, queries would scan entire table

**Database Generation** (SQLModel auto-create):
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX ix_tasks_user_id ON tasks(user_id);
```

### User Entity (External)

**Note**: Users are managed by Better Auth and stored in a separate database. The backend only references user_id from JWT tokens. No user table exists in this backend database.

**Conceptual Relationship**:
- User (Better Auth) has many Tasks (this database)
- user_id extracted from JWT token's `sub` claim
- No foreign key constraint (cross-database reference)
- Backend treats user_id as opaque UUID identifier

## Data Validation Rules

### Field-Level Validation (SQLModel)

**title**:
- **Type**: string
- **Length**: 1-200 characters
- **Nullable**: NO (required)
- **Validation**: Enforced via Pydantic schema (TaskCreate, TaskUpdate)
- **Error**: 422 Unprocessable Entity if validation fails
- **Spec Reference**: FR-008, FR-009

**description**:
- **Type**: string
- **Length**: No limit
- **Nullable**: YES (optional)
- **Validation**: None (free-form text)
- **Spec Reference**: FR-013

**completed**:
- **Type**: boolean
- **Values**: true | false
- **Default**: false
- **Nullable**: NO
- **Spec Reference**: FR-012

**user_id**:
- **Type**: UUID
- **Nullable**: NO (required)
- **Validation**: Must match authenticated user from JWT token
- **Error**: 403 Forbidden if mismatch between path param and JWT
- **Spec Reference**: FR-003, FR-004

**Timestamps (created_at, updated_at)**:
- **Type**: datetime (UTC)
- **Nullable**: NO
- **Auto-set**: created_at on insert, updated_at on update
- **Format**: ISO 8601 in responses
- **Spec Reference**: FR-010, FR-011

### Entity-Level Validation

**User Isolation Check** (enforced in application layer):
```python
# CORRECT: Verify path user_id matches authenticated user
if str(user_id) != current_user_id:
    raise HTTPException(403, "Cannot access other users' tasks")

# CORRECT: Filter query by user_id
statement = select(Task).where(Task.user_id == user_id)
```

**Resource Ownership Check**:
```python
# CORRECT: Double filter for specific task
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # CRITICAL: prevent cross-user access
)
```

## State Transitions

### Task Lifecycle

```
┌─────────────┐
│   CREATE    │
└──────┬──────┘
       │ POST /api/{user_id}/tasks
       │ title (required), description (optional)
       │
       ▼
┌────────────────────────────┐
│  INCOMPLETE (default)      │
│  completed = false         │
└────────┬───────────────────┘
         │
         │ PATCH /api/{user_id}/tasks/{task_id}/complete
         │ PUT /api/{user_id}/tasks/{task_id} with completed=true
         │
         ▼
┌────────────────────────────┐
│  COMPLETED                 │
│  completed = true          │
└────────┬───────────────────┘
         │
         │ PATCH (toggle back)
         │ PUT with completed=false
         │
         ▼
┌────────────────────────────┐
│  INCOMPLETE (again)        │
│  completed = false         │
└────────┬───────────────────┘
         │
         │ DELETE /api/{user_id}/tasks/{task_id}
         │
         ▼
┌────────────────────────────┐
│  DELETED (permanently)     │
└────────────────────────────┘
```

**State Rules**:
1. **Creation**: Task always starts with `completed = false`
2. **Toggle**: PATCH endpoint flips completed status (true ↔ false)
3. **Update**: PUT endpoint can set any completed value
4. **Deletion**: Permanent (no soft delete, no archive state)
5. **Timestamps**: `updated_at` changes on any modification (spec FR-011)

## Query Patterns

### List All User Tasks (GET /api/{user_id}/tasks)

```python
statement = select(Task).where(Task.user_id == user_id)
results = await db.execute(statement)
tasks = results.scalars().all()
```

**Index Used**: `ix_tasks_user_id`
**Performance**: O(log n) index seek + O(k) scan (k = tasks for user)
**Expected**: <500ms for 1000 tasks (spec SC-001)

### Get Single Task (GET /api/{user_id}/tasks/{task_id})

```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id
)
result = await db.execute(statement)
task = result.scalar_one_or_none()
```

**Indexes Used**: Primary key (id) + user_id index
**Performance**: O(1) primary key lookup
**Security**: Returns None if task belongs to different user (404 response)

### Create Task (POST /api/{user_id}/tasks)

```python
task = Task(
    user_id=UUID(current_user_id),
    title=task_data.title,
    description=task_data.description
)
db.add(task)
await db.commit()
await db.refresh(task)
```

**Performance**: O(1) insert + index update
**Expected**: <300ms (spec SC-002)

### Update Task (PUT /api/{user_id}/tasks/{task_id})

```python
# Fetch with user_id filter
task = await get_task_by_id_and_user(task_id, user_id)

# Update fields
task.title = new_title
task.description = new_description
task.completed = new_completed
task.updated_at = datetime.utcnow()

db.add(task)
await db.commit()
await db.refresh(task)
```

**Performance**: O(1) primary key update + timestamp update
**Security**: Fetch verifies ownership before update

### Delete Task (DELETE /api/{user_id}/tasks/{task_id})

```python
# Fetch with user_id filter
task = await get_task_by_id_and_user(task_id, user_id)

await db.delete(task)
await db.commit()
```

**Performance**: O(1) primary key delete + index cleanup
**Security**: Fetch verifies ownership before deletion

## Security Considerations

### User Isolation Enforcement

**CRITICAL**: Every query MUST filter by `user_id`. This is enforced in code, not database constraints (since User table is external).

**Pattern** (from Constitution Principle II):
```python
# ✅ CORRECT
tasks = session.exec(
    select(Task).where(Task.user_id == request.state.user_id)
).all()

# ❌ WRONG - Security violation, exposes all users' data
tasks = session.exec(select(Task)).all()
```

**Test Verification**:
- User A creates task
- User B attempts to access User A's task
- System returns 404 (not 403, to avoid leaking existence)
- Integration test verifies isolation (spec SC-003)

### Index Performance

**Why user_id index is critical**:
- Without index: Full table scan for every query (O(n) where n = all tasks)
- With index: Fast seek to user's tasks (O(log n) + O(k) where k = user's tasks)
- Expected: 1000 tasks per user, 10,000 users = 10M total tasks
- Full scan: 10M rows scanned per query (unacceptable)
- Index scan: ~log(10M) + 1000 = ~13 + 1000 = 1013 operations (acceptable)

### Data Integrity

**No Foreign Key Constraint**: user_id does not have FK constraint to User table (external database)

**Orphaned Data**: If user deleted in Better Auth, tasks remain (design decision)
- **Pro**: Data preservation for auditing
- **Con**: Orphaned data accumulation
- **Mitigation**: Future ADR for cleanup strategy if needed

**UUID Primary Keys**: Prevents enumeration attacks (can't guess IDs)

## Database Connection

**Driver**: asyncpg (async PostgreSQL driver)
**Connection String Format**:
```
postgresql+asyncpg://user:password@host:port/database?ssl=require
```

**Connection Pool** (SQLAlchemy async engine):
- Pool size: 5 (default for Neon serverless)
- Pool pre-ping: Enabled (verify connections before use)
- Pool recycle: 3600 seconds (1 hour)

**Environment Variable**: `DATABASE_URL`

## Migration Strategy

**Phase 1 (MVP)**: Auto-create tables on startup
```python
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Phase 2 (Production)**: If schema changes needed, migrate to Alembic
- **Trigger**: Multiple tables, complex migrations, rollback requirements
- **ADR**: Create decision record if migration tool added

## Testing Considerations

**Unit Tests**: Validate model creation, field constraints
```python
def test_task_creation():
    task = Task(
        user_id=uuid4(),
        title="Test Task"
    )
    assert task.completed == False
    assert task.description is None
```

**Integration Tests**: Verify database operations, user isolation
```python
async def test_user_isolation(db, user_a_token, user_b_token):
    # User A creates task
    task = await create_task(user_a_id, "Task A", db)

    # User B cannot access it
    response = await get_task(user_b_id, task.id, db)
    assert response.status_code == 404
```

## References

- Spec FR-003, FR-004 (user isolation)
- Spec FR-008 to FR-014 (field requirements)
- Constitution Principle II (data isolation pattern)
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- PostgreSQL UUID Type: https://www.postgresql.org/docs/current/datatype-uuid.html

## Conclusion

Data model complete and aligned with spec requirements. Single-table design is intentionally simple (Constitution Principle VI). User isolation enforced via application-layer checks and indexed queries. Ready for implementation.

**Status**: ✅ DATA MODEL COMPLETE
