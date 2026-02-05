---
name: spec-writer
description: Generate comprehensive Spec-Kit Plus compliant specifications for full-stack web applications. Use when the user asks to create specs, write specifications, generate project specs, document features, or start spec-driven development. Covers overview.md, architecture.md, database-schema.md, api-spec.md, ui-components.md, and feature-specific specs.
---

# Spec Writer

## Overview

Generate comprehensive, implementation-ready specifications following Spec-Kit Plus conventions for full-stack web applications. Produces specifications that backend builders, frontend builders, and database designers can directly implement from.

## When to Use

Trigger this skill when users:
- Ask to "create specs", "write specifications", "generate project specs"
- Start a new spec-driven development project
- Need to document features, APIs, database schemas, or UI components
- Request creation of overview.md, architecture.md, or any spec files
- Want to generate specs for a hackathon or rapid development project

## Core Workflow

### 1. Gather Requirements

Ask targeted questions to collect essential information:

**Project Context:**
- Project name and purpose
- Current phase (MVP, Phase II, production)
- Target completion timeline

**Technical Stack:**
- Frontend: Framework (Next.js 16+, React, etc.), UI library, state management
- Backend: Framework (FastAPI, Express, etc.), language
- Database: Type (PostgreSQL, MySQL, etc.), ORM, hosting
- Authentication: Provider (Better Auth, NextAuth, etc.), strategy (JWT, session)

**Core Features:**
- Must-have features (MVP scope)
- Nice-to-have features
- Explicitly out-of-scope items

**Constraints:**
- Budget limitations
- Timeline restrictions
- Technology requirements
- Team size and composition

### 2. Create Directory Structure

Generate the standard Spec-Kit Plus directory structure in `/specs/`:

```
specs/
├── overview.md
├── architecture.md
├── database-schema.md
├── api-spec.md
├── ui-components.md
└── <feature-name>/
    ├── spec.md
    ├── plan.md
    └── tasks.md
```

### 3. Generate Specification Files

Use templates from `assets/` to generate each spec file:

#### Project-Level Specs

**overview.md** - Use `assets/overview-template.md`
- Replace all `{{PLACEHOLDERS}}` with actual project details
- Fill in tech stack, features, user flows, constraints
- Include realistic timeline and success metrics

**api-spec.md** - Use `assets/api-spec-template.md`
- Define all REST endpoints with method, path, auth requirements
- Include complete request/response examples with actual JSON
- Document error codes, rate limiting, pagination
- Ensure consistency with database schema

**database-schema.md** - Use `assets/database-schema-template.md`
- Define all tables with columns, types, constraints
- Include foreign key relationships and indexes
- Add SQLModel/ORM model definitions
- Document migrations strategy

#### Feature-Level Specs

**spec.md** - Use `assets/feature-spec-template.md`
- Write specific user stories with clear acceptance criteria
- Define API requirements matching api-spec.md
- Specify data model changes
- Document error handling scenarios

### 4. Validation

Run automatic validation checks:

**Structure Validation:**
- [ ] All required sections present in each file
- [ ] Directory structure follows conventions (lowercase-with-hyphens)
- [ ] Files created in correct locations

**Content Validation:**
- [ ] No template placeholders remain ({{PLACEHOLDER}}, [TODO])
- [ ] All cross-references point to valid files
- [ ] Code examples have proper syntax highlighting

**Consistency Validation:**
- [ ] API endpoints reference valid database tables
- [ ] Database foreign keys match referenced tables
- [ ] Features align with architecture decisions
- [ ] Terminology consistent across all files (e.g., "todo" not mixed with "task" or "item")

**Completeness Validation:**
- [ ] All CRUD operations documented
- [ ] Error scenarios specified
- [ ] Validation rules explicit
- [ ] Success metrics defined

Use `scripts/validate-specs.py` to automate validation:
```bash
python3 scripts/validate-specs.py /path/to/specs
```

### 5. Present to User

Provide a clear summary:

```markdown
✅ Generated specifications in /specs/

**Project-Level Specs:**
- overview.md - Project summary, tech stack, timeline
- api-spec.md - 7 endpoints documented with examples
- database-schema.md - 3 tables with relationships
- ui-components.md - 5 reusable components

**Feature Specs:**
- todo-management/spec.md - CRUD requirements and acceptance criteria

**Next Steps:**
1. Review specifications for accuracy
2. Run validation: `python3 .claude/skills/spec-writer/scripts/validate-specs.py specs/`
3. Generate implementation plan with `/sp.plan`
4. Create tasks with `/sp.tasks`
```

### 6. Suggest Next Steps

Based on project phase:
- Review and validate specifications
- Generate implementation plan (`/sp.plan`)
- Create actionable tasks (`/sp.tasks`)
- Set up project structure (create directories, initialize repos)
- Begin implementation phase

## Best Practices

### Be Specific and Concrete

**❌ Vague:**
```markdown
The system should be fast and handle users efficiently.
```

**✅ Specific:**
```markdown
The system must handle 100 concurrent users with p95 latency < 200ms for API calls.
```

### Use Consistent Terminology

Choose one term per concept and use it everywhere:
- "todo" (not mixed with "task", "item", "entry")
- "user" (not mixed with "account", "profile")
- "completed" (not mixed with "done", "finished")

### Include Concrete Examples

Every API endpoint should have:
```json
// Request example
{
  "title": "Buy groceries",
  "priority": "high"
}

// Response example (201 Created)
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "priority": "high",
  "completed": false,
  "created_at": "2025-02-02T10:30:00Z"
}
```

### Document Error Scenarios

For every operation, specify:
- What can go wrong
- Error codes returned
- User-facing error messages
- Recovery steps

### Cross-Reference Related Specs

```markdown
See [API Authentication](./api-spec.md#authentication) for endpoint details.
Database schema defined in [Database Schema](./database-schema.md#todos-table).
Implements [Todo Feature Spec](./todo-management/spec.md) requirements.
```

### Use Tables for Structured Data

**API Endpoints:**
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/todos | Yes | List all todos |
| POST | /api/todos | Yes | Create todo |

**Validation Rules:**
| Field | Type | Required | Min | Max | Pattern |
|-------|------|----------|-----|-----|---------|
| title | string | Yes | 1 | 255 | - |
| priority | enum | No | - | - | low\|medium\|high |

## Common Pitfalls

### Missing Error Handling
Always document error scenarios:
```markdown
POST /api/todos
- Returns 201 on success
- Returns 400 if validation fails (e.g., title too long)
- Returns 401 if unauthorized (e.g., invalid token)
- Returns 500 on server error
```

### Inconsistent Specs
Ensure API spec matches database schema:
```markdown
✅ api-spec.md: GET /api/todos - Returns todos for authenticated user
✅ database-schema.md: todos table has user_id FK; API filters by JWT claim

❌ api-spec.md: GET /api/todos - Returns array of todos
❌ database-schema.md: todos table has user_id but API doesn't filter
```

### Template Placeholders Left In
Before finalizing, remove all:
- `{{PLACEHOLDERS}}`
- `[TODO]` markers
- Example/dummy data meant to be replaced

### Overspecifying Implementation
Specs define **what**, not **how**:

**❌ Too specific (belongs in plan.md):**
```markdown
Use React useState with useEffect for side effects and implement
a custom useTodos hook that memoizes with useMemo.
```

**✅ Appropriate for spec.md:**
```markdown
Todo list updates in real-time when todos are added, updated, or deleted.
```

## Hackathon Context: Todo Application

For the current hackathon Phase II todo app project:

**Tech Stack:**
- Frontend: Next.js 16+ (App Router), Tailwind CSS
- Backend: Python FastAPI
- Database: PostgreSQL (Neon), SQLModel ORM
- Auth: Better Auth with JWT

**Core Features:**
- User authentication (register, login)
- Todo CRUD: Create, Read, Update, Delete
- Mark todos as complete/incomplete
- Filter by status (all, active, completed)

**Key Specifications to Generate:**

1. **overview.md** - Todo app summary with tech stack
2. **api-spec.md** - Auth endpoints + 5 todo CRUD endpoints
3. **database-schema.md** - Users table + Todos table with FK relationship
4. **todo-management/spec.md** - Todo feature requirements

**Sample API Endpoints:**
```
POST /auth/register - Create user account
POST /auth/login - Authenticate user
GET /api/todos - List user's todos
POST /api/todos - Create new todo
PATCH /api/todos/:id - Update todo (including toggle complete)
DELETE /api/todos/:id - Delete todo
```

**Sample Database Schema:**
```sql
users:
  - id: UUID (PK)
  - email: VARCHAR(255) UNIQUE
  - password_hash: VARCHAR(255)
  - name: VARCHAR(255)
  - created_at: TIMESTAMP

todos:
  - id: UUID (PK)
  - user_id: UUID (FK → users.id)
  - title: VARCHAR(255)
  - description: TEXT
  - completed: BOOLEAN
  - priority: VARCHAR(20)
  - created_at: TIMESTAMP
  - updated_at: TIMESTAMP
```

## Resources

### Templates (assets/)
- `overview-template.md` - Project overview structure
- `api-spec-template.md` - API documentation template
- `database-schema-template.md` - Database design template
- `feature-spec-template.md` - Feature requirements template

### Conventions (references/)
- `spec-kit-conventions.md` - Complete style guide covering:
  - File naming (lowercase-with-hyphens)
  - Document structure standards
  - Cross-referencing patterns
  - Code example formatting
  - Anti-patterns to avoid

### Scripts (scripts/)
- `validate-specs.py` - Automated validation tool
  - Checks for placeholders
  - Validates cross-references
  - Ensures consistency
  - Reports errors and warnings

## Quick Reference

### File Naming
```
✅ overview.md, api-spec.md, database-schema.md
✅ todo-management/spec.md
❌ Overview.md, api_spec.md, todoManagement/spec.md
```

### Required Frontmatter
```yaml
---
title: Project Name - Document Title
status: draft | in-progress | completed
version: 1.0.0
last-updated: YYYY-MM-DD
owner: Team/Person
---
```

### Common Sections
- **spec.md**: Overview, User Stories, Requirements, Acceptance Criteria, Dependencies, Out of Scope
- **plan.md**: Architecture, Design Decisions, Data Flow, Implementation Approach, Risks, Testing
- **api-spec.md**: Authentication, Endpoints, Error Codes, Rate Limiting, Pagination
- **database-schema.md**: Tables, Relationships, Indexes, Migrations, Models

## Validation Checklist

Before completing, verify:
- [ ] All required spec files created
- [ ] Directory structure follows conventions
- [ ] No template placeholders remain
- [ ] Cross-references are valid and accurate
- [ ] Code examples have syntax highlighting
- [ ] Tables are properly formatted
- [ ] API endpoints match database schema
- [ ] Error scenarios documented
- [ ] Validation rules explicit
- [ ] Terminology consistent across all files
- [ ] Files saved in correct locations
- [ ] Frontmatter metadata complete
