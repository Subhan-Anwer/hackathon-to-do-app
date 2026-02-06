# Feature Specification: Multi-User Task Management API

**Feature Branch**: `001-task-api`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Multi-User Todo App Backend - Production-grade REST API using FastAPI + SQLModel + Neon PostgreSQL with JWT authentication and user isolation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Personal Task List (Priority: P1)

As an authenticated user, I need to view all my tasks so I can see what work needs to be done.

**Why this priority**: Core read operation - foundational to all other features. Without being able to view tasks, no other functionality matters.

**Independent Test**: Can be fully tested by authenticating as a user, creating several tasks via the API, and verifying that GET request returns only that user's tasks (not other users' tasks).

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with 5 tasks, **When** I request my task list, **Then** I receive exactly 5 tasks in the response
2. **Given** I am an authenticated user, **When** I request my task list, **Then** I receive only my tasks, not tasks belonging to other users
3. **Given** I am an authenticated user with no tasks, **When** I request my task list, **Then** I receive an empty list

---

### User Story 2 - Create New Tasks (Priority: P1)

As an authenticated user, I need to create new tasks with a title and optional description so I can track work items.

**Why this priority**: Core write operation - equally critical as viewing tasks. Together with P1 viewing, forms the minimum viable product.

**Independent Test**: Can be fully tested by authenticating as a user, submitting a POST request with task data, and verifying the task is created and associated with the authenticated user.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I create a task with title "Buy groceries", **Then** a new task is created with that title and assigned to me
2. **Given** I am an authenticated user, **When** I create a task with title and description, **Then** both fields are saved correctly
3. **Given** I am an authenticated user, **When** I create a task, **Then** the task is marked as incomplete by default
4. **Given** I am an authenticated user, **When** I create a task, **Then** timestamps for creation and last update are automatically set

---

### User Story 3 - Mark Tasks Complete (Priority: P2)

As an authenticated user, I need to mark tasks as complete so I can track my progress.

**Why this priority**: Primary workflow completion action - critical for task lifecycle but depends on viewing/creating tasks first.

**Independent Test**: Can be fully tested by creating a task, then sending a PATCH request to toggle completion status, and verifying the status changes.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task, **When** I mark it as complete, **Then** its completed status becomes true
2. **Given** I have a completed task, **When** I toggle completion, **Then** its completed status becomes false
3. **Given** I attempt to mark another user's task as complete, **When** I send the request, **Then** I receive a 403 Forbidden error

---

### User Story 4 - Update Task Details (Priority: P2)

As an authenticated user, I need to update task titles, descriptions, and completion status so I can modify existing tasks.

**Why this priority**: Important for task maintenance but not as critical as core create/read/complete operations.

**Independent Test**: Can be fully tested by creating a task, then sending a PUT request with updated fields, and verifying the changes are saved.

**Acceptance Scenarios**:

1. **Given** I have a task, **When** I update its title, **Then** the new title is saved
2. **Given** I have a task, **When** I update its description, **Then** the new description is saved
3. **Given** I have a task, **When** I update its completion status, **Then** the status is updated
4. **Given** I attempt to update another user's task, **When** I send the request, **Then** I receive a 403 Forbidden error

---

### User Story 5 - View Single Task Details (Priority: P3)

As an authenticated user, I need to retrieve details of a specific task so I can view full information.

**Why this priority**: Nice-to-have for detailed views but list view typically shows all necessary information.

**Independent Test**: Can be fully tested by creating a task, then requesting it by ID, and verifying the full task details are returned.

**Acceptance Scenarios**:

1. **Given** I have a task with ID X, **When** I request task X, **Then** I receive its full details
2. **Given** another user has a task with ID Y, **When** I request task Y, **Then** I receive a 404 Not Found error
3. **Given** I request a task ID that doesn't exist, **When** I send the request, **Then** I receive a 404 Not Found error

---

### User Story 6 - Delete Tasks (Priority: P3)

As an authenticated user, I need to delete tasks I no longer need so I can maintain a clean task list.

**Why this priority**: Cleanup operation - useful but not critical for core workflow.

**Independent Test**: Can be fully tested by creating a task, deleting it, and verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** I have a task with ID X, **When** I delete task X, **Then** it is permanently removed
2. **Given** I delete a task, **When** I subsequently request my task list, **Then** the deleted task does not appear
3. **Given** I attempt to delete another user's task, **When** I send the request, **Then** I receive a 403 Forbidden error

---

### Edge Cases

- What happens when a user attempts to create a task with an empty title?
- What happens when a user attempts to create a task with a title exceeding 200 characters?
- How does the system handle concurrent updates to the same task by the same user?
- What happens when a user's JWT token expires during a request?
- How does the system handle invalid user_id in the URL path that doesn't match the authenticated user?
- What happens when database connection is lost during a request?
- How does the system handle malformed JSON in request bodies?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate all API requests using JWT tokens from Better Auth
- **FR-002**: System MUST extract user_id from validated JWT tokens
- **FR-003**: System MUST verify that the user_id in the URL path matches the authenticated user_id from the JWT
- **FR-004**: System MUST filter all database queries by the authenticated user_id
- **FR-005**: System MUST return 401 Unauthorized for requests with missing or invalid JWT tokens
- **FR-006**: System MUST return 403 Forbidden when URL user_id does not match authenticated user_id
- **FR-007**: System MUST return 404 Not Found when a task doesn't exist or belongs to a different user
- **FR-008**: System MUST validate task title length (1-200 characters)
- **FR-009**: System MUST reject task creation requests with empty or missing titles
- **FR-010**: System MUST automatically set created_at timestamp when creating tasks
- **FR-011**: System MUST automatically update updated_at timestamp when modifying tasks
- **FR-012**: System MUST default new tasks to incomplete status (completed=false)
- **FR-013**: System MUST allow optional description field for tasks
- **FR-014**: System MUST use UUID for task IDs and user IDs
- **FR-015**: System MUST connect to Neon PostgreSQL database using async engine
- **FR-016**: System MUST enable CORS for frontend origin
- **FR-017**: System MUST log all authentication failures
- **FR-018**: System MUST log all authorization failures (user_id mismatches)
- **FR-019**: System MUST use dependency injection for database sessions
- **FR-020**: System MUST use dependency injection for authenticated user verification
- **FR-021**: System MUST handle database errors gracefully with appropriate HTTP status codes
- **FR-022**: System MUST validate JWT using BETTER_AUTH_SECRET environment variable
- **FR-023**: System MUST read database connection string from DATABASE_URL environment variable

### Key Entities

- **Task**: Represents a todo item belonging to a user
  - Primary identifier (UUID)
  - Owner identifier (UUID, references user)
  - Title (required, max 200 characters)
  - Description (optional)
  - Completion status (boolean)
  - Creation timestamp
  - Last update timestamp
  - Indexed by owner identifier for efficient querying

- **User**: Represents an authenticated user (managed by Better Auth, not backend)
  - User identifier (UUID) extracted from JWT token
  - No user data stored in backend database
  - Backend only references user_id for task ownership

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can retrieve their task list in under 500ms for up to 1000 tasks
- **SC-002**: Users can create a new task in under 300ms
- **SC-003**: System successfully blocks 100% of attempts to access other users' tasks (zero cross-user data leaks)
- **SC-004**: System handles 100 concurrent authenticated requests without errors
- **SC-005**: All API endpoints return responses within 1 second under normal load
- **SC-006**: Invalid authentication attempts receive clear error messages within 200ms
- **SC-007**: System maintains 99.9% uptime for API availability
- **SC-008**: All database queries execute with proper user_id filtering (verified via audit)

## Scope *(mandatory)*

### In Scope

- JWT token validation and user extraction
- User_id verification against URL path parameters
- CRUD operations for tasks (Create, Read, Update, Delete)
- Task completion toggle endpoint
- User isolation enforcement on all operations
- Async database operations with SQLModel
- Error handling and appropriate HTTP status codes
- CORS middleware configuration
- Logging for authentication and authorization events
- Environment variable configuration for secrets

### Out of Scope

- User signup and signin endpoints (handled by Better Auth on frontend)
- User profile management
- Task sharing or collaboration between users
- Task categories or tags
- Task due dates or reminders
- Task priority levels
- File attachments to tasks
- Task comments or notes
- Search or filtering of tasks (beyond basic list)
- Pagination of task lists
- Sorting of tasks
- Email notifications
- Rate limiting (handled at infrastructure level)
- API versioning (v1 assumed)

## Assumptions *(include if making assumptions)*

- Frontend handles all user authentication via Better Auth
- JWT tokens issued by Better Auth include user_id claim
- BETTER_AUTH_SECRET is securely shared between frontend and backend
- Neon PostgreSQL database is already provisioned
- DATABASE_URL connection string is available as environment variable
- Frontend runs on a known origin for CORS configuration
- User accounts are managed entirely by Better Auth (no user table in backend)
- Task lists will not exceed 10,000 items per user in near term
- All clients use JSON for request/response bodies
- Timestamp precision to seconds is sufficient
- UTF-8 encoding for all text fields
- System time zone is UTC for all timestamps
- Backend runs on port 8000 (standard FastAPI default)
- Frontend runs on port 3000 (standard Next.js default)

## Dependencies *(include if feature depends on external systems/features)*

### External Dependencies

- **Better Auth**: Provides JWT tokens with user_id claims
- **Neon PostgreSQL**: Serverless PostgreSQL database hosting
- **Frontend Application**: Consumes this API and manages user authentication

### Environment Variables Required

- `DATABASE_URL`: PostgreSQL connection string for Neon database
- `BETTER_AUTH_SECRET`: Shared secret for JWT validation (must match frontend)
- `FRONTEND_ORIGIN`: Frontend URL for CORS configuration (assumed: http://localhost:3000)

### Technical Dependencies

- FastAPI framework
- SQLModel ORM
- asyncpg database driver
- python-jose or PyJWT for JWT validation
- pydantic for request/response validation
- uv package manager

## Non-Functional Requirements *(include if relevant)*

### Performance

- API response time under 1 second for all endpoints under normal load
- Database queries optimized with proper indexes on user_id
- Connection pooling for database efficiency
- Async operations throughout to handle concurrent requests

### Security

- All endpoints require valid JWT authentication
- Zero tolerance for cross-user data access
- SQL injection prevention via SQLModel parameterization
- No sensitive data in logs (tokens, passwords)
- HTTPS enforced in production (infrastructure level)
- Environment variables for all secrets (no hardcoding)

### Reliability

- Graceful error handling for database failures
- Clear error messages for client debugging
- Proper HTTP status codes for all responses
- Transaction rollback on errors
- Automatic reconnection to database on connection loss

### Maintainability

- Clean separation of concerns (routers, models, schemas, dependencies)
- Type hints throughout codebase
- Clear function and variable names
- Dependency injection for testability
- Follows FastAPI and SQLModel best practices

### Observability

- Structured logging for authentication failures
- Structured logging for authorization failures
- Structured logging for database errors
- Request/response logging (excluding sensitive data)
- Health check endpoint for monitoring

## References *(optional)*

- Better Auth JWT Integration Skill: `@.claude/skills/better-auth-integration/SKILL.md`
- API Security Skill: `@.claude/skills/api-security/SKILL.md`
- FastAPI Backend Builder Agent: `@.claude/agents/fastapi-backend-builder.md`
- Database Schema Designer Skill: `@.claude/skills/database-schema-designer/SKILL.md`
- Project Constitution: `@.specify/memory/constitution.md`
