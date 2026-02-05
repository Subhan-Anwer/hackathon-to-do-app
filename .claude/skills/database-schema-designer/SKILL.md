---
name: database-schema-designer
description: Design production-ready database schemas using SQLModel ORM for PostgreSQL. Use when designing database structures, creating SQLModel models, defining table relationships, setting up indexes, or when users ask to "design database", "create schema", "set up models", or "design data structure".
---

# Database Schema Designer

Generate well-designed database schemas using SQLModel that are optimized for performance, maintain data integrity, and follow PostgreSQL best practices.

## Schema Design Workflow

### 1. Analyze Requirements
- Identify entities and their attributes from specifications
- Determine relationships (one-to-many, many-to-many)
- Identify fields requiring indexes
- Plan user ownership and data isolation

### 2. Define SQLModel Tables
- Create table classes with proper field types and constraints
- Add indexes for foreign keys and frequently queried fields
- Include created_at/updated_at timestamps
- Set up validation rules

### 3. Configure Relationships
- Define relationship objects for navigation
- Choose appropriate cascade rules
- Create link tables for many-to-many

### 4. Document Query Patterns
- Provide examples for common operations
- Show proper user isolation in queries
- Include pagination and filtering patterns

## SQLModel Table Definition Pattern

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Primary key with auto-increment
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key with index (always index FKs)
    user_id: str = Field(foreign_key="users.id", index=True)

    # Required fields with validation
    title: str = Field(max_length=200, min_length=1)

    # Optional fields
    description: Optional[str] = Field(default=None, max_length=1000)

    # Boolean with default and index
    completed: bool = Field(default=False, index=True)

    # Timestamps (always include)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (optional, for navigation)
    # user: Optional["User"] = Relationship(back_populates="tasks")
```

## Field Types and Constraints

| Field Type | SQLModel Definition | Use Case |
|------------|---------------------|----------|
| String (required) | `title: str = Field(max_length=200)` | Names, titles, short text |
| String (optional) | `description: Optional[str] = Field(default=None, max_length=1000)` | Optional text |
| Integer | `priority: int = Field(ge=1, le=5)` | Numbers with min/max |
| Boolean | `completed: bool = Field(default=False)` | True/false flags |
| DateTime | `created_at: datetime = Field(default_factory=datetime.utcnow)` | Timestamps |
| Foreign Key | `user_id: str = Field(foreign_key="users.id", index=True)` | References |
| Unique | `email: str = Field(unique=True, max_length=255)` | Unique values |

## Indexing Strategy

**Always index:**
- Foreign keys (for join performance)
- Fields used in WHERE clauses frequently
- Boolean status fields queried often
- Fields used for sorting

**Example:**
```python
user_id: str = Field(foreign_key="users.id", index=True)
completed: bool = Field(default=False, index=True)
```

**Avoid:**
- Over-indexing (impacts write performance)
- Indexing low-cardinality fields (except status flags)
- Indexing fields never used in queries

## Relationship Patterns

**One-to-Many:**
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    user_id: str = Field(foreign_key="users.id", index=True)
    user: Optional[User] = Relationship(back_populates="tasks")
```

**Many-to-Many (with link table):**
```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
```

## Common Query Patterns

Refer to `references/query-patterns.md` for detailed examples of:
- Get all records for user
- Get single record with user verification
- Create with auto-timestamps
- Update with timestamp refresh
- Delete operations
- Filter by status
- Pagination and sorting

## Naming Conventions

- **Tables**: lowercase, plural (`tasks`, `users`)
- **Columns**: lowercase with underscores (`user_id`, `created_at`)
- **Foreign keys**: `{table_singular}_id` (`user_id`, `task_id`)
- **Indexes**: `idx_{table}_{column}` (if manually created)

## Required Patterns

**Timestamps (always include):**
```python
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**User Association (for user-owned data):**
```python
user_id: str = Field(foreign_key="users.id", index=True)
```

## Data Validation

```python
from pydantic import validator

class Task(SQLModel, table=True):
    title: str = Field(max_length=200)

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

## Database Setup Pattern

```python
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## Common Pitfalls

1. **Forgetting to index foreign keys** - Always add `index=True`
2. **Not setting max_length on strings** - Required for string fields
3. **Using nullable for required fields** - Use `Optional[]` only when truly optional
4. **Missing timestamps** - Always include created_at/updated_at
5. **Wrong relationship definitions** - Check back_populates matches
6. **Not using Optional[]** - Required for nullable fields in SQLModel

## Resources

### references/
- `query-patterns.md` - Comprehensive query examples for CRUD operations, filtering, pagination
- `postgresql-features.md` - PostgreSQL-specific features (JSONB, arrays, full-text search)
- `migration-guide.md` - Database migration strategies (create_all vs Alembic)

### assets/
- `table-template.py` - Blank SQLModel table template
