# Spec-Kit Plus Conventions

## Directory Structure

```
/specs/
  ├── <feature-name>/
  │   ├── spec.md              # Feature requirements
  │   ├── plan.md              # Architecture decisions
  │   └── tasks.md             # Implementation tasks
  ├── overview.md              # Project overview
  ├── architecture.md          # System architecture
  ├── database-schema.md       # Database design
  ├── api-spec.md              # API endpoints
  └── ui-components.md         # Frontend components
```

## File Naming Conventions

- **Use lowercase with hyphens**: `database-schema.md`, `api-spec.md`, `user-authentication.md`
- **Avoid underscores or camelCase**: ❌ `database_schema.md`, ❌ `databaseSchema.md`
- **Be descriptive**: `auth-endpoints.md` > `auth.md`
- **Feature folders**: Use singular noun (e.g., `todo-management/` not `todos-management/`)

## Document Structure Standards

### Required Frontmatter
All spec files should start with metadata:

```yaml
---
title: [Document Title]
status: draft | in-progress | completed
version: 1.0.0
last-updated: YYYY-MM-DD
owner: [Team/Person]
---
```

### Standard Section Headers

**For spec.md:**
1. Overview
2. User Stories / Requirements
3. Acceptance Criteria
4. Dependencies
5. Out of Scope
6. Open Questions

**For plan.md:**
1. Architecture Overview
2. Design Decisions
3. Data Flow
4. Implementation Approach
5. Risk Analysis
6. Testing Strategy

**For tasks.md:**
1. Task List (with checkboxes)
2. Dependencies (task ordering)
3. Acceptance Tests
4. Definition of Done

## Cross-Referencing Patterns

### Linking Between Specs
Use relative paths with descriptive text:
```markdown
See [API Authentication](./api-spec.md#authentication) for endpoint details.
Referenced in [Database Schema](./database-schema.md#users-table).
Implements requirements from [Todo Feature Spec](./todo-management/spec.md).
```

### Referencing Code
Use file:line notation:
```markdown
Implementation at `backend/api/todos.py:45-67`
Component defined in `frontend/components/TodoList.tsx:12`
```

### Linking External Resources
```markdown
[FastAPI Documentation](https://fastapi.tiangolo.com/)
[Next.js App Router Guide](https://nextjs.org/docs/app)
```

## Code Example Formatting

### API Endpoint Examples
```markdown
### POST /api/todos

**Request:**
\`\`\`json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high"
}
\`\`\`

**Response (201 Created):**
\`\`\`json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "completed": false,
  "created_at": "2025-02-02T10:30:00Z"
}
\`\`\`
```

### Database Schema Examples
```markdown
### todos Table

| Column       | Type         | Constraints           | Description              |
|--------------|--------------|----------------------|--------------------------|
| id           | UUID         | PRIMARY KEY          | Unique identifier        |
| user_id      | UUID         | FOREIGN KEY, NOT NULL| Owner reference          |
| title        | VARCHAR(255) | NOT NULL             | Todo title               |
| completed    | BOOLEAN      | DEFAULT false        | Completion status        |
| created_at   | TIMESTAMP    | DEFAULT NOW()        | Creation timestamp       |
```

### Component Props Examples
```markdown
### TodoItem Component

\`\`\`typescript
interface TodoItemProps {
  id: string;
  title: string;
  completed: boolean;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}
\`\`\`
```

## Table Formatting for Structured Data

### API Endpoints Table
```markdown
| Method | Endpoint           | Auth Required | Description           |
|--------|-------------------|---------------|-----------------------|
| GET    | /api/todos        | Yes           | List all todos        |
| POST   | /api/todos        | Yes           | Create new todo       |
| PATCH  | /api/todos/:id    | Yes           | Update todo           |
| DELETE | /api/todos/:id    | Yes           | Delete todo           |
```

### Error Codes Table
```markdown
| Code | Status               | Description                    | Example                  |
|------|---------------------|--------------------------------|--------------------------|
| 400  | Bad Request          | Invalid request body           | Missing required field   |
| 401  | Unauthorized         | Invalid or missing auth token  | Token expired            |
| 404  | Not Found            | Resource does not exist        | Todo not found           |
| 500  | Internal Server Error| Server-side error              | Database connection fail |
```

### Validation Rules Table
```markdown
| Field       | Type   | Required | Min | Max | Pattern            |
|-------------|--------|----------|-----|-----|--------------------|
| title       | string | Yes      | 1   | 255 | -                  |
| description | string | No       | 0   | 2000| -                  |
| priority    | enum   | No       | -   | -   | low\|medium\|high  |
```

## Status Tracking Patterns

### Checkbox Lists for Tasks
```markdown
## Implementation Tasks

- [x] Set up database schema
- [x] Create API endpoints
- [ ] Implement frontend components
- [ ] Add unit tests
- [ ] Integration testing
- [ ] Documentation
```

### Status Indicators
Use emojis or badges consistently:
```markdown
- ✅ Completed
- 🚧 In Progress
- 📋 Planned
- ❌ Blocked
- 🔍 Under Review
```

### Version Status
```markdown
**Status:** Draft v0.1
**Status:** Review v0.9
**Status:** Released v1.0
```

## Anti-Patterns to Avoid

### ❌ Vague Requirements
```markdown
<!-- Bad -->
The system should be fast and handle users efficiently.

<!-- Good -->
The system must handle 100 concurrent users with p95 latency < 200ms.
```

### ❌ Inconsistent Terminology
```markdown
<!-- Bad - mixing terms -->
User creates a task... The todo item is stored... Items are displayed...

<!-- Good - consistent -->
User creates a todo... The todo is stored... Todos are displayed...
```

### ❌ Missing Error Scenarios
```markdown
<!-- Bad -->
POST /api/todos - Creates a new todo

<!-- Good -->
POST /api/todos - Creates a new todo
Returns 201 on success, 400 if validation fails, 401 if unauthorized
```

### ❌ Ambiguous Acceptance Criteria
```markdown
<!-- Bad -->
- Todo list should work well
- User can manage todos

<!-- Good -->
- User can view all their todos in descending order by creation date
- User can mark a todo as complete with a single click
- Completed todos show with strikethrough styling
```

### ❌ Copying Specs Without Customization
```markdown
<!-- Bad - generic template text left in -->
This component handles [COMPONENT_NAME] and provides [FEATURES].

<!-- Good - specific content -->
The TodoList component renders a scrollable list of todo items with
real-time updates via WebSocket connection.
```

### ❌ Overspecifying Implementation Details in Spec
```markdown
<!-- Bad - spec.md shouldn't dictate implementation -->
Use React useState hook with useEffect for side effects and implement
a custom useTodos hook that memoizes with useMemo.

<!-- Good - spec focuses on what, not how -->
Todo list updates in real-time when todos are added, updated, or deleted.
```

### ❌ Specs That Don't Match Each Other
```markdown
<!-- Bad - API spec says one thing -->
GET /api/todos - Returns array of todos

<!-- Database schema says another -->
Todos table stores user_id, but API doesn't filter by user

<!-- Good - consistency across specs -->
GET /api/todos - Returns todos for authenticated user
Todos table has user_id foreign key; API filters by JWT user claim
```

## Quality Checklist

Before finalizing specs, verify:

- [ ] All file names use lowercase-with-hyphens convention
- [ ] Frontmatter metadata is complete and accurate
- [ ] Cross-references between specs are correct and valid
- [ ] Code examples include language tags for syntax highlighting
- [ ] Tables are properly formatted with aligned columns
- [ ] No template placeholders remain (e.g., `[TODO]`, `{{PLACEHOLDER}}`)
- [ ] Terminology is consistent across all documents
- [ ] Error scenarios are documented
- [ ] Acceptance criteria are specific and testable
- [ ] API endpoints match database schema
- [ ] No contradictions between different spec files
