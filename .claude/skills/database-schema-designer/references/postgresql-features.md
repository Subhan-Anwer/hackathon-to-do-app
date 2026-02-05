# PostgreSQL-Specific Features with SQLModel

Advanced PostgreSQL features that can be used with SQLModel for enhanced functionality.

## JSONB Fields

Store flexible, semi-structured data that can be queried efficiently.

### Definition

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from typing import Optional, Any

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)

    # JSONB field for flexible metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
```

### Usage Examples

```python
# Create with metadata
task = Task(
    user_id="user123",
    title="Design mockups",
    metadata={
        "priority": "high",
        "tags": ["design", "ui"],
        "estimated_hours": 8,
        "client": "Acme Corp"
    }
)

# Query JSONB fields
from sqlalchemy import func

# PostgreSQL JSONB operators
statement = select(Task).where(
    Task.user_id == user_id,
    func.jsonb_extract_path_text(Task.metadata, "priority") == "high"
)
```

### Use Cases

- Custom fields per user/organization
- Flexible tag systems
- Configuration storage
- Activity logs
- Form responses with varying structure

## Array Fields

Store arrays of values natively in PostgreSQL.

### Definition

```python
from sqlalchemy import ARRAY, String

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)

    # Array of strings
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String))
    )
```

### Usage Examples

```python
# Create with array
task = Task(
    user_id="user123",
    title="Complete documentation",
    tags=["docs", "high-priority", "review-needed"]
)

# Query arrays
# Check if array contains value
statement = select(Task).where(
    Task.user_id == user_id,
    Task.tags.contains(["high-priority"])
)

# Check if array overlaps with values
statement = select(Task).where(
    Task.user_id == user_id,
    Task.tags.overlap(["urgent", "high-priority"])
)
```

### Use Cases

- Simple tagging systems (without join tables)
- Multi-select options
- Role assignments
- Feature flags

## Full-Text Search

PostgreSQL's built-in full-text search capabilities.

### Setup with GIN Index

```python
from sqlalchemy import Index, func

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)

    # Define GIN index for full-text search
    __table_args__ = (
        Index(
            'idx_task_fts',
            func.to_tsvector('english', 'title || \' \' || description'),
            postgresql_using='gin'
        ),
    )
```

### Query Examples

```python
# Full-text search
statement = select(Task).where(
    Task.user_id == user_id,
    func.to_tsvector('english', Task.title + ' ' + Task.description).match(
        'urgent & meeting'
    )
)

# With ranking
from sqlalchemy import desc

statement = (
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(
        desc(
            func.ts_rank(
                func.to_tsvector('english', Task.title),
                func.to_query('english', 'meeting')
            )
        )
    )
)
```

### Use Cases

- Search across multiple text fields
- Relevance ranking
- Stemming and language support
- Phrase search

## Enum Types

PostgreSQL native enums for better type safety.

### Definition

```python
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)

    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        sa_column=Column(SQLAlchemyEnum(TaskStatus))
    )
```

### Usage

```python
# Create with enum
task = Task(
    user_id="user123",
    title="Review PR",
    status=TaskStatus.REVIEW
)

# Query by enum
statement = select(Task).where(
    Task.user_id == user_id,
    Task.status == TaskStatus.IN_PROGRESS
)
```

## Triggers for Auto-Update Timestamp

Automatically update `updated_at` using PostgreSQL triggers.

### Migration SQL

```sql
-- Create function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for tasks table
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Benefit

No need to manually set `updated_at` in Python code - PostgreSQL handles it automatically on every UPDATE.

## Partial Indexes

Create indexes only for subset of rows to save space and improve performance.

### Example

```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False)

    # Partial index for incomplete tasks only
    __table_args__ = (
        Index(
            'idx_incomplete_tasks',
            'user_id',
            postgresql_where=(completed == False)
        ),
    )
```

### Use Cases

- Index only active/incomplete records
- Index only recent records (created_at > threshold)
- Exclude soft-deleted records from index

## Composite Indexes

Multi-column indexes for common query patterns.

### Example

```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Composite index for common query: user + status + date
    __table_args__ = (
        Index('idx_user_status_date', 'user_id', 'completed', 'created_at'),
    )
```

### Query Optimized

```python
# This query benefits from composite index
statement = select(Task).where(
    Task.user_id == user_id,
    Task.completed == False
).order_by(Task.created_at.desc())
```

### Index Column Order

Order matters! Put most selective columns first:
1. Equality conditions (`user_id == 'x'`)
2. Inequality conditions (`created_at > date`)
3. Sort columns (`ORDER BY created_at`)

## UUID Primary Keys

Use UUIDs instead of auto-incrementing integers.

### Definition

```python
import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True)
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
```

### Benefits

- Non-sequential IDs (security)
- No ID conflicts in distributed systems
- Can generate IDs client-side

### Drawbacks

- Larger storage (16 bytes vs 4 bytes)
- Slightly slower indexing
- Less human-readable

## Check Constraints

Database-level validation for data integrity.

### Example

```python
from sqlalchemy import CheckConstraint

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    priority: int = Field(default=1)

    __table_args__ = (
        CheckConstraint('priority >= 1 AND priority <= 5', name='valid_priority'),
        CheckConstraint("title != ''", name='title_not_empty'),
    )
```

## Generated Columns

Computed columns that PostgreSQL maintains automatically.

### Example (PostgreSQL 12+)

```python
from sqlalchemy import Computed

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)

    # Computed search field (STORED means value is saved)
    search_text: str = Field(
        sa_column=Column(
            String,
            Computed("title || ' ' || COALESCE(description, '')", persisted=True)
        )
    )
```

## Performance Best Practices

1. **Use appropriate data types**
   - `VARCHAR(n)` for bounded strings
   - `TEXT` for unbounded text
   - `INTEGER` instead of `BIGINT` when possible

2. **Index strategy**
   - Index foreign keys (always)
   - Index WHERE clause columns
   - Use partial indexes for filtered queries
   - Use composite indexes for multi-column queries

3. **JSONB vs separate tables**
   - Use JSONB for flexible, low-query metadata
   - Use separate tables for structured, frequently queried data

4. **Full-text search**
   - Create GIN indexes
   - Use materialized views for complex searches
   - Consider dedicated search (Elasticsearch) for large datasets

5. **Array fields**
   - Good for simple lists (tags)
   - Use many-to-many tables for complex relationships
   - Index arrays with GIN when querying them
