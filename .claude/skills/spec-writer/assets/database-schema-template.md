---
title: {{PROJECT_NAME}} - Database Schema
status: draft
version: 1.0.0
last-updated: {{CURRENT_DATE}}
owner: {{TEAM_NAME}}
---

# {{PROJECT_NAME}} - Database Schema

## Database Overview

**Database:** {{DATABASE_TYPE}} (e.g., PostgreSQL 16+)
**ORM:** {{ORM}} (e.g., SQLModel, Prisma)
**Hosting:** {{DB_HOSTING}} (e.g., Neon, Supabase)
**Migrations:** {{MIGRATION_TOOL}} (e.g., Alembic, Prisma Migrate)

## Schema Diagram

```
{{ENTITY_1}} (1) ──── (N) {{ENTITY_2}}
    │
    │ (1)
    │
    └──── (N) {{ENTITY_3}}
```

## Tables

### {{TABLE_NAME_1}} Table

**Purpose:** {{Description of what this table stores}}

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | Unique identifier |
| {{COLUMN_1}} | {{TYPE}} | {{CONSTRAINTS}} | {{DEFAULT}} | {{DESCRIPTION}} |
| {{COLUMN_2}} | {{TYPE}} | {{CONSTRAINTS}} | {{DEFAULT}} | {{DESCRIPTION}} |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |

**Indexes:**
- `PRIMARY KEY (id)`
- `CREATE INDEX idx_{{table}}_{{column}} ON {{table}}({{column}})`

**Foreign Keys:**
- `{{FK_COLUMN}}` → `{{REFERENCED_TABLE}}(id)` ON DELETE {{CASCADE/SET NULL/RESTRICT}}

**Example Row:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "{{COLUMN_1}}": "{{SAMPLE_VALUE_1}}",
  "{{COLUMN_2}}": "{{SAMPLE_VALUE_2}}",
  "created_at": "2025-02-02T10:30:00Z",
  "updated_at": "2025-02-02T10:30:00Z"
}
```

### {{TABLE_NAME_2}} Table

**Purpose:** {{Description}}

| Column | Type | Constraints | Default | Description |
|--------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY | uuid_generate_v4() | Unique identifier |
| {{FK_COLUMN}} | UUID | FOREIGN KEY, NOT NULL | - | Reference to {{table}} |
| {{COLUMN_1}} | {{TYPE}} | {{CONSTRAINTS}} | {{DEFAULT}} | {{DESCRIPTION}} |
| created_at | TIMESTAMP | NOT NULL | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp |

**Indexes:**
- `PRIMARY KEY (id)`
- `CREATE INDEX idx_{{table}}_{{fk}} ON {{table}}({{fk_column}})`

**Foreign Keys:**
- `{{FK_COLUMN}}` → `{{REFERENCED_TABLE}}(id)` ON DELETE CASCADE

## Relationships

### One-to-Many
- One `{{TABLE_1}}` has many `{{TABLE_2}}`
- Foreign key: `{{TABLE_2}}.{{FK_COLUMN}}` → `{{TABLE_1}}.id`

### Many-to-Many (via junction table)
- `{{TABLE_1}}` ↔ `{{JUNCTION_TABLE}}` ↔ `{{TABLE_2}}`

**{{JUNCTION_TABLE}} Table:**
| Column | Type | Constraints |
|--------|------|-------------|
| {{TABLE_1}}_id | UUID | FOREIGN KEY, NOT NULL |
| {{TABLE_2}}_id | UUID | FOREIGN KEY, NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

**Composite Primary Key:** `({{TABLE_1}}_id, {{TABLE_2}}_id)`

## Data Types Reference

| Type | PostgreSQL | SQLModel/Python | Description |
|------|-----------|-----------------|-------------|
| UUID | UUID | str (with UUID validation) | Universally unique identifier |
| String | VARCHAR(n) | str (max_length=n) | Variable-length string |
| Integer | INTEGER | int | 32-bit integer |
| Boolean | BOOLEAN | bool | True/false value |
| Timestamp | TIMESTAMP | datetime | Date and time |
| JSON | JSONB | dict | JSON data |
| Enum | VARCHAR + CHECK | Enum | Predefined values |

## Enums

### {{ENUM_NAME}} Enum
```python
class {{EnumName}}(str, Enum):
    {{VALUE_1}} = "{{value_1}}"
    {{VALUE_2}} = "{{value_2}}"
    {{VALUE_3}} = "{{value_3}}"
```

**Database:** Stored as VARCHAR with CHECK constraint

## Constraints and Validation

### Unique Constraints
```sql
ALTER TABLE {{table}} ADD CONSTRAINT unique_{{column}} UNIQUE ({{column}});
```

### Check Constraints
```sql
ALTER TABLE {{table}} ADD CONSTRAINT check_{{name}}
  CHECK ({{CONDITION}});
```

**Examples:**
- `CHECK (price > 0)` - Price must be positive
- `CHECK (status IN ('active', 'inactive', 'pending'))` - Valid status values
- `CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}$')` - Email format

### Not Null Constraints
```sql
ALTER TABLE {{table}} ALTER COLUMN {{column}} SET NOT NULL;
```

## Default Values

```sql
ALTER TABLE {{table}} ALTER COLUMN {{column}} SET DEFAULT {{value}};
```

**Common Defaults:**
- `id DEFAULT uuid_generate_v4()`
- `created_at DEFAULT NOW()`
- `status DEFAULT 'pending'`
- `is_active DEFAULT true`

## Triggers

### Auto-update `updated_at`
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_{{table}}_updated_at
  BEFORE UPDATE ON {{table}}
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

## Migrations

### Initial Schema
```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create {{TABLE_NAME_1}} table
CREATE TABLE {{table_name_1}} (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    {{column_1}} {{TYPE}} {{CONSTRAINTS}},
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_{{table}}_{{column}} ON {{table}}({{column}});

-- Create triggers
CREATE TRIGGER update_{{table}}_updated_at
  BEFORE UPDATE ON {{table}}
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

### Migration Workflow
1. Create migration file: `migrations/{{timestamp}}_{{description}}.sql`
2. Apply up migration: `{{MIGRATION_COMMAND_UP}}`
3. Rollback (if needed): `{{MIGRATION_COMMAND_DOWN}}`

### Example Alembic Migration
```python
"""{{description}}

Revision ID: {{revision_id}}
Revises: {{previous_revision}}
Create Date: {{timestamp}}
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        '{{table_name}}',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('{{column}}', sa.{{Type}}(), nullable={{True/False}}),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    )

def downgrade():
    op.drop_table('{{table_name}}')
```

## Sample Data (Development)

### Seed Script
```sql
-- Seed {{TABLE_1}}
INSERT INTO {{table_1}} (id, {{column}}) VALUES
  ('{{UUID_1}}', '{{VALUE_1}}'),
  ('{{UUID_2}}', '{{VALUE_2}}');

-- Seed {{TABLE_2}}
INSERT INTO {{table_2}} (id, {{fk_column}}, {{column}}) VALUES
  ('{{UUID_3}}', '{{UUID_1}}', '{{VALUE_3}}'),
  ('{{UUID_4}}', '{{UUID_1}}', '{{VALUE_4}}');
```

## Performance Considerations

### Indexes
- Add indexes on foreign keys for faster joins
- Add indexes on frequently queried columns
- Avoid over-indexing (impacts write performance)

### Query Optimization
- Use `EXPLAIN ANALYZE` to profile queries
- Avoid `SELECT *`, specify needed columns
- Use pagination for large result sets

### Connection Pooling
```python
# SQLModel/SQLAlchemy example
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## Security

### Row-Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE {{table}} ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY user_{{table}}_policy ON {{table}}
  FOR ALL
  USING (user_id = current_user_id());
```

### Sensitive Data
- **Passwords:** Hash with bcrypt/argon2 before storing
- **Tokens:** Store hashed, never plain text
- **PII:** Encrypt at application level if required

## Backup and Recovery

**Backup Strategy:** {{BACKUP_STRATEGY}}
- Automated daily backups
- Point-in-time recovery enabled
- Retention: {{RETENTION_PERIOD}}

**Restore Command:**
```bash
pg_restore -d {{database}} {{backup_file}}
```

## References

- [API Specification](./api-spec.md) - API endpoints using this schema
- [Architecture Documentation](./architecture.md) - Data flow diagrams
- PostgreSQL Documentation: https://www.postgresql.org/docs/

## Model Definitions (SQLModel)

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class {{ModelName}}(SQLModel, table=True):
    __tablename__ = "{{table_name}}"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    {{field_1}}: {{Type}} = Field({{constraints}})
    {{field_2}}: Optional[{{Type}}] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    {{related_items}}: list["{{RelatedModel}}"] = Relationship(back_populates="{{back_ref}}")
```

## Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | {{CURRENT_DATE}} | Initial schema design | {{AUTHOR}} |
