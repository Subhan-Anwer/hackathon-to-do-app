# Database Migration Strategies

Guide for managing database schema changes with SQLModel.

## Approach Overview

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| `create_all()` | Hackathons, prototypes | Fast, simple | No version control, destructive |
| Alembic | Production apps | Version control, safe migrations | More setup, learning curve |
| Raw SQL | Complex migrations | Full control | Manual, error-prone |

## Method 1: create_all() - Quick Setup

**Use for:** Hackathons, demos, rapid prototyping, development environments.

### Setup

```python
# models.py
from sqlmodel import SQLModel, create_engine

DATABASE_URL = "postgresql://user:pass@localhost/dbname"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create all tables. WARNING: Does not handle schema changes."""
    SQLModel.metadata.create_all(engine)

def drop_all_tables():
    """Drop all tables. WARNING: Destroys all data."""
    SQLModel.metadata.drop_all(engine)
```

### Usage in FastAPI

```python
# main.py
from fastapi import FastAPI
from models import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
```

### Workflow

1. Define models in Python
2. Run application
3. Tables created automatically on startup
4. Change models → restart app → tables updated (may lose data)

### Limitations

- **No migration history**: Can't track what changed when
- **Destructive updates**: Changing column types may require drop/recreate
- **Data loss risk**: Schema changes can delete data
- **No rollback**: Can't undo changes
- **Limited alterations**: Can't handle complex schema changes

### When to Use

✅ Initial development
✅ Throwaway prototypes
✅ Testing environments
✅ Hackathons (time-limited projects)

❌ Production
❌ Projects with real user data
❌ Team collaboration requiring schema versioning

## Method 2: Alembic - Production Migrations

**Use for:** Production applications, team projects, projects with real data.

### Installation

```bash
pip install alembic
```

### Initial Setup

```bash
# Initialize Alembic
alembic init alembic

# Creates:
# alembic/
#   ├── env.py          # Migration environment config
#   ├── script.py.mako  # Migration template
#   └── versions/       # Migration files
# alembic.ini           # Alembic configuration
```

### Configuration

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Import your SQLModel base
from models import SQLModel

# Get database URL from environment
config = context.config
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

# Set target metadata
target_metadata = SQLModel.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

### Workflow

#### 1. Create Initial Migration

```bash
# Auto-generate migration from current models
alembic revision --autogenerate -m "Initial schema"

# Creates: alembic/versions/xxxxx_initial_schema.py
```

#### 2. Review Migration

```python
# alembic/versions/xxxxx_initial_schema.py
def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])

def downgrade():
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
```

#### 3. Apply Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade +1

# Revert last migration
alembic downgrade -1

# Revert all migrations
alembic downgrade base
```

### Common Migration Scenarios

#### Add Column

```python
# 1. Update model
class Task(SQLModel, table=True):
    priority: int = Field(default=1)  # New field

# 2. Generate migration
alembic revision --autogenerate -m "Add priority to tasks"

# 3. Review and apply
alembic upgrade head
```

#### Rename Column

```python
# Manual migration required
def upgrade():
    op.alter_column('tasks', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('tasks', 'new_name', new_column_name='old_name')
```

#### Add Index

```python
def upgrade():
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])

def downgrade():
    op.drop_index('idx_tasks_completed', table_name='tasks')
```

#### Data Migration

```python
from alembic import op
from sqlalchemy import table, column

def upgrade():
    # Get reference to table
    tasks = table('tasks',
        column('id', Integer),
        column('status', String),
        column('completed', Boolean)
    )

    # Update data
    op.execute(
        tasks.update()
        .where(tasks.c.status == 'done')
        .values(completed=True)
    )

def downgrade():
    # Reverse data migration
    pass
```

### Alembic Commands Reference

```bash
# Create new migration manually
alembic revision -m "Description"

# Auto-generate from model changes
alembic revision --autogenerate -m "Description"

# Show current revision
alembic current

# Show migration history
alembic history

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade to specific revision
alembic downgrade abc123

# Show SQL without executing
alembic upgrade head --sql

# Stamp database to specific revision (without running migrations)
alembic stamp head
```

### Best Practices

1. **Always review auto-generated migrations**
   - Alembic may miss complex changes
   - Verify data safety before applying

2. **Test migrations on copy of production data**
   - Clone database
   - Run migration
   - Verify data integrity

3. **Write reversible migrations**
   - Implement both `upgrade()` and `downgrade()`
   - Handle data transformations carefully

4. **Use meaningful migration messages**
   - ❌ "Update schema"
   - ✅ "Add priority field to tasks table"

5. **One logical change per migration**
   - Easier to review and revert
   - Better version history

6. **Backup before production migrations**
   - Always have restore option
   - Test rollback procedure

## Method 3: Raw SQL Migrations

**Use for:** Complex migrations Alembic can't handle automatically.

### Example: Complex Data Transformation

```python
# alembic/versions/xxxxx_complex_migration.py
from alembic import op

def upgrade():
    # Raw SQL for complex operations
    op.execute("""
        -- Create temporary column
        ALTER TABLE tasks ADD COLUMN tags_array TEXT[];

        -- Migrate data from JSONB to array
        UPDATE tasks
        SET tags_array = ARRAY(
            SELECT jsonb_array_elements_text(metadata->'tags')
        )
        WHERE metadata ? 'tags';

        -- Remove old JSONB tags
        UPDATE tasks
        SET metadata = metadata - 'tags';
    """)

def downgrade():
    op.execute("""
        -- Reverse migration
        UPDATE tasks
        SET metadata = jsonb_set(
            metadata,
            '{tags}',
            to_jsonb(tags_array)
        )
        WHERE tags_array IS NOT NULL;

        ALTER TABLE tasks DROP COLUMN tags_array;
    """)
```

## Deployment Strategies

### Strategy 1: Automated on Startup

```python
# main.py - Run migrations automatically
from alembic import command
from alembic.config import Config

@app.on_event("startup")
async def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

**Pros:** Simple, automatic
**Cons:** Risky, blocks startup, hard to rollback

### Strategy 2: Separate Migration Step

```bash
# 1. Run migrations first
alembic upgrade head

# 2. Then start application
uvicorn main:app
```

**Pros:** Safe, controlled, can verify before deployment
**Cons:** Requires manual step or CI/CD integration

### Strategy 3: Blue-Green Deployment

```bash
# 1. Deploy new version (blue) alongside old (green)
# 2. Run forward-compatible migration
alembic upgrade head

# 3. Switch traffic to blue
# 4. Shutdown green

# If issues:
# 5. Switch traffic back to green
# 6. Rollback migration
alembic downgrade -1
```

## Handling Schema Changes in Production

### Safe Changes (No Downtime)

✅ Add nullable column
✅ Add table
✅ Add index
✅ Add relationship (foreign key with existing data)

### Risky Changes (Potential Downtime)

⚠️ Rename column → Use multi-step migration
⚠️ Change column type → May require data transformation
⚠️ Add NOT NULL column → Requires default value or data population
⚠️ Drop column/table → Ensure not in use first

### Multi-Step Migration Example: Rename Column

```python
# Step 1: Add new column
def upgrade():
    op.add_column('tasks', sa.Column('new_name', sa.String()))
    # Copy data
    op.execute('UPDATE tasks SET new_name = old_name')

# Deploy application that writes to both columns

# Step 2: Remove old column
def upgrade():
    op.drop_column('tasks', 'old_name')
```

## Development Workflow

```bash
# 1. Update models
# Edit models.py

# 2. Generate migration
alembic revision --autogenerate -m "Add priority field"

# 3. Review generated migration
# Check alembic/versions/xxxxx_add_priority_field.py

# 4. Test migration locally
alembic upgrade head

# 5. Test application with new schema
uvicorn main:app

# 6. If issues, rollback
alembic downgrade -1

# 7. Commit migration file
git add alembic/versions/xxxxx_add_priority_field.py
git commit -m "Add priority field migration"

# 8. Deploy to production
# Run migration first, then deploy code
```

## Summary

- **Hackathons/Prototypes**: Use `create_all()` for speed
- **Production/Team Projects**: Use Alembic for safety and version control
- **Complex Transformations**: Use raw SQL within Alembic migrations
- **Always**: Test migrations on copy of production data before applying
