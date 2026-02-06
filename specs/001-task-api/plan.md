# Implementation Plan: Multi-User Task Management API

**Branch**: `001-task-api` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-task-api/spec.md`

## Summary

Build a production-grade FastAPI backend for a multi-user todo application with strict user isolation enforced at every layer. The API provides CRUD operations for tasks with JWT authentication via Better Auth, async PostgreSQL database operations using SQLModel ORM, and comprehensive error handling. Every endpoint validates JWT tokens, extracts user_id, verifies path parameters match the authenticated user, and filters all database queries by user_id to ensure zero cross-user data leaks.

**Technical Approach**: Follow strict layered architecture with dependency injection for database sessions and authentication. Implement JWT middleware first to establish security foundation, then build data layer with SQLModel, followed by router endpoints with user isolation enforcement. Use FastAPI's dependency system for reusable auth and database dependencies.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI 0.128.1+, SQLModel (latest), python-jose[cryptography], asyncpg, uvicorn[standard]
**Storage**: Neon Serverless PostgreSQL (async connection via asyncpg driver)
**Testing**: pytest with pytest-asyncio for async tests, httpx for API testing
**Target Platform**: Linux server (Docker-compatible)
**Project Type**: Web backend API
**Performance Goals**: <500ms task list retrieval (1000 tasks), <300ms task creation, 100 concurrent requests
**Constraints**: Zero cross-user data leaks (enforced via tests), all queries filtered by user_id, JWT validation required on all endpoints
**Scale/Scope**: 6 REST endpoints, 1 SQLModel entity, single-user microservice architecture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- Implementation follows spec at `specs/001-task-api/spec.md`
- All 23 functional requirements traced to implementation steps
- No manual coding - all work via `/sp.implement` or specialized agents

### Principle II: User Isolation and Security First ✅ PASS
- **FR-001 to FR-007**: JWT authentication and user_id filtering enforced
- Middleware extracts user_id before request processing
- All queries include `.where(Task.user_id == current_user_id)`
- Constitution example code pattern followed exactly (lines 136-144)

### Principle III: Reusability Through Skills and Agents ✅ PASS
- `better-auth-integration` skill: JWT validation setup
- `api-security` skill: Middleware and isolation patterns
- `database-schema-designer` skill: SQLModel Task model design
- `fastapi-backend-builder` agent: Router and endpoint implementation

### Principle IV: Clarity and Consistency ✅ PASS
- Follows `backend/CLAUDE.md` structure (uv, pyproject.toml)
- Uses monorepo paths (`backend/`, `specs/001-task-api/`)
- References constitution data isolation pattern (Principle II, lines 133-148)

### Principle V: Test-First for Security-Critical Paths ✅ PASS
- Tests for auth failures (401), user_id mismatch (403), cross-user access (404)
- Test user isolation: User A cannot access User B's tasks
- Verify middleware rejects invalid tokens before implementation

### Principle VI: Simplicity and Smallest Viable Change ✅ PASS
- No premature abstraction: direct FastAPI patterns, no custom base classes
- Implements only specified endpoints (6 from spec, no extras)
- Single concern per file: models.py, schemas.py, dependencies.py, routers/tasks.py

## Project Structure

### Documentation (this feature)

```text
specs/001-task-api/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (SQLModel schema)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (OpenAPI spec)
│   └── openapi.yaml     # Generated API contract
├── checklists/          # Quality validation (already exists)
│   └── requirements.md  # Spec quality checklist (PASSED)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── .venv/                    # Virtual environment (managed by uv)
├── .python-version           # Python version (3.12)
├── pyproject.toml            # Project configuration (already exists)
├── uv.lock                   # Dependency lock file
├── main.py                   # FastAPI app initialization & router registration
├── db.py                     # Database engine, async session, get_db dependency
├── models.py                 # SQLModel Task model (with user_id foreign key)
├── schemas.py                # Pydantic TaskCreate, TaskUpdate, TaskRead schemas
├── dependencies.py           # current_user dependency (JWT validation)
├── routers/
│   └── tasks.py              # All 6 task endpoints with user isolation
├── tests/
│   ├── conftest.py           # Pytest fixtures (test client, database, auth)
│   ├── test_auth.py          # JWT middleware tests (401/403)
│   ├── test_isolation.py     # Cross-user access tests (User A vs User B)
│   └── test_tasks.py         # CRUD endpoint integration tests
└── .env.example              # Environment variable template
```

**Structure Decision**: Standard FastAPI web application structure selected. Follows `backend/CLAUDE.md` conventions with uv package management. Single `backend/` directory contains all API code (no separate services or monorepo complexity). Testing structure mirrors source with contract, integration, and unit test separation. This aligns with Constitution Principle VI (simplicity) - no unnecessary abstraction layers.

## Complexity Tracking

> **No violations - table intentionally empty per Constitution Principle VI**

All design choices align with constitution principles. No additional complexity introduced beyond FastAPI standard practices and SQLModel ORM patterns. Architecture is intentionally simple: single router, single model, dependency injection for auth and database.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **JWT Validation with Better Auth**
   - **Question**: How to validate Better Auth JWT tokens in FastAPI?
   - **Dependencies**: python-jose or PyJWT, BETTER_AUTH_SECRET env variable
   - **Patterns**: Extract user_id from token claims, attach to request.state
   - **References**: `@.claude/skills/better-auth-integration/SKILL.md`

2. **SQLModel Async Operations**
   - **Question**: How to configure async SQLModel sessions with Neon PostgreSQL?
   - **Dependencies**: sqlmodel, asyncpg driver, SQLAlchemy async engine
   - **Patterns**: create_async_engine, AsyncSession, async context managers
   - **References**: SQLModel docs, `@.claude/skills/database-schema-designer/SKILL.md`

3. **User Isolation Patterns**
   - **Question**: How to enforce user_id filtering on all queries without duplication?
   - **Dependencies**: FastAPI dependencies system, request.state
   - **Patterns**: Dependency injection for current_user, query filters
   - **References**: Constitution Principle II (lines 133-148), `@.claude/skills/api-security/SKILL.md`

4. **Error Handling Strategy**
   - **Question**: How to structure 401/403/404 error responses consistently?
   - **Dependencies**: FastAPI HTTPException, custom exception handlers
   - **Patterns**: Centralized error models, exception middleware
   - **References**: FastAPI error handling docs

### Technology Decisions (to be documented in research.md)

**Decision Matrix**:

| **Decision** | **Options** | **Selected** | **Rationale** |
|--------------|-------------|--------------|---------------|
| JWT Library | PyJWT vs python-jose | python-jose[cryptography] | Better Auth compatibility, includes cryptography for RS256 |
| Database Driver | psycopg2 vs asyncpg | asyncpg | Async support, Neon serverless compatibility, better performance |
| Session Management | sync vs async | async sessions | Aligns with FastAPI async patterns, Neon requirement |
| Auth Dependency | Middleware vs Dependency | Dependency injection | More flexible, testable, follows FastAPI best practices |
| Error Structure | Custom classes vs HTTPException | HTTPException with detail dict | Simple, FastAPI-native, JSON-serializable |

**Output**: `research.md` documenting all decisions with alternatives considered and rationale.

## Phase 1: Design Artifacts

### 1. Data Model Design (`data-model.md`)

**Task Entity** (SQLModel):
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to user (managed by Better Auth)
    user_id: UUID = Field(index=True, nullable=False)

    # Task data
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
- `user_id` (single-column index) for efficient querying by owner
- Primary key `id` (automatic)

**Validation Rules**:
- `title`: 1-200 characters (enforced via Pydantic schema)
- `description`: optional, no length limit (spec FR-013)
- `completed`: boolean default false (spec FR-012)
- `user_id`: required, must match authenticated user (spec FR-003, FR-004)

**State Transitions**:
- `completed`: false → true (mark complete), true → false (toggle)
- `updated_at`: automatically updated on any modification (spec FR-011)

### 2. API Contracts (`contracts/openapi.yaml`)

**Endpoints**:

```yaml
paths:
  /api/{user_id}/tasks:
    get:
      summary: List all tasks for authenticated user
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: string, format: uuid}
      responses:
        200: {description: Task list, content: {application/json: {schema: {type: array, items: {$ref: '#/components/schemas/TaskRead'}}}}}
        401: {description: Unauthorized}
        403: {description: Forbidden - user_id mismatch}

    post:
      summary: Create new task
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: string, format: uuid}
      requestBody:
        content:
          application/json:
            schema: {$ref: '#/components/schemas/TaskCreate'}
      responses:
        201: {description: Task created, content: {application/json: {schema: {$ref: '#/components/schemas/TaskRead'}}}}
        401: {description: Unauthorized}
        403: {description: Forbidden}
        422: {description: Validation error}

  /api/{user_id}/tasks/{task_id}:
    get:
      summary: Get single task
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: string, format: uuid}
        - name: task_id
          in: path
          required: true
          schema: {type: string, format: uuid}
      responses:
        200: {description: Task details, content: {application/json: {schema: {$ref: '#/components/schemas/TaskRead'}}}}
        401: {description: Unauthorized}
        403: {description: Forbidden}
        404: {description: Not found or not owned by user}

    put:
      summary: Update task
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: string, format: uuid}
        - name: task_id
          in: path
          required: true
          schema: {type: string, format: uuid}
      requestBody:
        content:
          application/json:
            schema: {$ref: '#/components/schemas/TaskUpdate'}
      responses:
        200: {description: Task updated, content: {application/json: {schema: {$ref: '#/components/schemas/TaskRead'}}}}
        401: {description: Unauthorized}
        403: {description: Forbidden}
        404: {description: Not found}
        422: {description: Validation error}

    delete:
      summary: Delete task
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: string, format: uuid}
        - name: task_id
          in: path
          required: true
          schema: {type: string, format: uuid}
      responses:
        200: {description: Task deleted, content: {application/json: {schema: {type: object, properties: {success: {type: boolean}}}}}}
        401: {description: Unauthorized}
        403: {description: Forbidden}
        404: {description: Not found}

  /api/{user_id}/tasks/{task_id}/complete:
    patch:
      summary: Toggle task completion status
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: string, format: uuid}
        - name: task_id
          in: path
          required: true
          schema: {type: string, format: uuid}
      responses:
        200: {description: Task completion toggled, content: {application/json: {schema: {$ref: '#/components/schemas/TaskRead'}}}}
        401: {description: Unauthorized}
        403: {description: Forbidden}
        404: {description: Not found}

components:
  schemas:
    TaskCreate:
      type: object
      required: [title]
      properties:
        title: {type: string, minLength: 1, maxLength: 200}
        description: {type: string, nullable: true}

    TaskUpdate:
      type: object
      properties:
        title: {type: string, minLength: 1, maxLength: 200}
        description: {type: string, nullable: true}
        completed: {type: boolean}

    TaskRead:
      type: object
      properties:
        id: {type: string, format: uuid}
        title: {type: string}
        description: {type: string, nullable: true}
        completed: {type: boolean}
        created_at: {type: string, format: date-time}
        updated_at: {type: string, format: date-time}

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

### 3. Implementation Phases (Step-by-Step Plan)

#### **Step 1: Project Setup & Dependencies**

**Objective**: Install all required packages and configure environment

**Files to Create/Modify**:
- `backend/.env.example` (create)
- `backend/pyproject.toml` (modify - add dependencies)

**Actions**:
```bash
cd backend
uv add fastapi uvicorn[standard] sqlmodel asyncpg python-jose[cryptography] python-multipart
uv add --dev pytest pytest-asyncio httpx
```

**Environment Variables** (`.env.example`):
```bash
DATABASE_URL=postgresql+asyncpg://user:password@host/database
BETTER_AUTH_SECRET=your-secret-key-here
FRONTEND_ORIGIN=http://localhost:3000
```

**Key Patterns**:
- Use `uv add` not `pip install` (per `backend/CLAUDE.md`)
- Separate dev dependencies with `--dev` flag
- Document all env vars in `.env.example`

**References**:
- `backend/CLAUDE.md` lines 15-66 (uv commands)
- Spec FR-022, FR-023 (environment variables)

**Skills/Templates**: N/A (standard setup)

**Testing**: After this step, verify `uv sync` runs without errors and `uv run python -c "import fastapi, sqlmodel, jose"` succeeds.

---

#### **Step 2: Database Connection & Engine**

**Objective**: Configure async PostgreSQL connection with SQLModel

**Files to Create/Modify**:
- `backend/db.py` (create)

**Code Structure** (`db.py`):
```python
from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# Read from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create async engine for Neon PostgreSQL
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    future=True
)

# Async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI routes
async def get_db():
    async with async_session() as session:
        yield session
```

**Key Patterns**:
- Use `create_async_engine` for Neon compatibility
- Set `echo=True` for development SQL logging
- Dependency yields session, FastAPI handles cleanup
- Environment variable validation on import

**References**:
- Spec FR-015 (async engine requirement)
- Spec FR-019 (dependency injection)
- Spec FR-023 (DATABASE_URL env var)
- SQLModel async docs

**Skills/Templates**: `database-schema-designer` skill patterns

**Testing**: After this step, verify `DATABASE_URL` is read and engine created without errors. Test with: `uv run python -c "from db import engine; print(engine)"`.

---

#### **Step 3: SQLModel Task Model**

**Objective**: Define Task entity with user_id foreign key and indexes

**Files to Create/Modify**:
- `backend/models.py` (create)

**Code Structure** (`models.py`):
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model with strict user isolation.

    Every task belongs to exactly one user (user_id).
    All queries MUST filter by user_id to prevent cross-user data leaks.
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)  # CRITICAL: indexed for query performance

    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Key Patterns**:
- `user_id` indexed (spec FR-004 performance)
- UUID primary key (spec FR-014)
- Title max 200 chars (spec FR-008)
- Description optional (spec FR-013)
- Completed defaults false (spec FR-012)
- Timestamps auto-set (spec FR-010, FR-011)

**References**:
- Spec Key Entities (lines 146-161)
- Spec FR-008 to FR-014
- Constitution Principle II (user_id requirement)

**Skills/Templates**: `database-schema-designer` skill (SQLModel patterns)

**Testing**: After this step, verify model imports without errors. Test with: `uv run python -c "from models import Task; print(Task.__table__)"`.

---

#### **Step 4: Pydantic Schemas**

**Objective**: Define request/response schemas with validation

**Files to Create/Modify**:
- `backend/schemas.py` (create)

**Code Structure** (`schemas.py`):
```python
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    """Schema for updating an existing task.

    All fields optional - only provided fields are updated.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskRead(BaseModel):
    """Schema for reading task data.

    IMPORTANT: Does not include user_id in response (privacy).
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

**Key Patterns**:
- `TaskCreate` requires title (spec FR-009)
- `TaskUpdate` all fields optional (partial update)
- `TaskRead` excludes user_id (not exposed to client)
- Validation: title 1-200 chars (spec FR-008)
- `from_attributes=True` for SQLModel → Pydantic conversion

**References**:
- Spec FR-008, FR-009 (validation)
- Spec FR-013 (optional description)
- User input from command (Pydantic models section)

**Skills/Templates**: FastAPI schema patterns

**Testing**: After this step, verify schemas validate correctly. Test with: `uv run python -c "from schemas import TaskCreate; TaskCreate(title='Test')"`.

---

#### **Step 5: JWT Authentication Dependency**

**Objective**: Implement current_user dependency with JWT validation

**Files to Create/Modify**:
- `backend/dependencies.py` (create)

**Code Structure** (`dependencies.py`):
```python
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
import os
import logging

logger = logging.getLogger(__name__)

# JWT configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

ALGORITHM = "HS256"  # Better Auth default

async def get_current_user(request: Request) -> str:
    """Extract and validate user_id from JWT token.

    Checks Authorization header or cookie for JWT token.
    Decodes token and extracts user_id claim.

    Returns:
        str: user_id from token

    Raises:
        HTTPException 401: Missing or invalid token
    """
    # Try Authorization header first
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to cookie (Better Auth httpOnly cookie)
        token = request.cookies.get("session")

    if not token:
        logger.warning("Authentication failed: No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - missing token"
        )

    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # Better Auth uses 'sub' claim

        if user_id is None:
            logger.warning("Authentication failed: Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing user_id"
            )

        logger.info(f"User authenticated: {user_id}")
        return user_id

    except JWTError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - verification failed"
        )
```

**Key Patterns**:
- Dependency injection pattern (spec FR-020)
- Checks Authorization header + cookie (Better Auth compatibility)
- Decodes JWT with BETTER_AUTH_SECRET (spec FR-022)
- Returns user_id string (spec FR-002)
- Logs auth failures (spec FR-017)
- Raises 401 on failure (spec FR-005)

**References**:
- Spec FR-001, FR-002, FR-005, FR-017, FR-022
- `@.claude/skills/better-auth-integration/SKILL.md`
- Constitution Principle II (JWT requirement)

**Skills/Templates**: `better-auth-integration` skill, `api-security` skill

**Testing**: After this step, test with mock JWT tokens. Verify 401 on missing/invalid tokens.

---

#### **Step 6: Task Router - List Tasks Endpoint**

**Objective**: Implement GET /api/{user_id}/tasks with user isolation

**Files to Create/Modify**:
- `backend/routers/` (create directory)
- `backend/routers/__init__.py` (create empty file)
- `backend/routers/tasks.py` (create)

**Code Structure** (`routers/tasks.py` - first endpoint):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import List
import logging

from db import get_db
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskRead
from dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["tasks"])
logger = logging.getLogger(__name__)

@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def list_tasks(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all tasks for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Filters all tasks by user_id to prevent data leaks.
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if str(user_id) != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Query with user_id filter (spec FR-004)
    statement = select(Task).where(Task.user_id == user_id)
    results = await db.execute(statement)
    tasks = results.scalars().all()

    logger.info(f"Listed {len(tasks)} tasks for user {user_id}")
    return tasks
```

**Key Patterns**:
- Path parameter `user_id` (spec API design)
- Dependency injection for auth + database (spec FR-019, FR-020)
- Verify path user_id matches token user_id (spec FR-003)
- 403 Forbidden on mismatch (spec FR-006)
- Query filter `.where(Task.user_id == user_id)` (spec FR-004, Constitution Principle II)
- Log authorization failures (spec FR-018)

**References**:
- Spec FR-003, FR-004, FR-006, FR-018
- Constitution Principle II lines 136-144 (exact pattern)
- User input (GET /api/{user_id}/tasks endpoint)

**Skills/Templates**: `fastapi-backend-builder` agent patterns, `api-security` skill

**Testing**: After this step, test with multiple user tokens. Verify User A cannot access User B's tasks (403). Verify empty list for new users.

---

#### **Step 7: Task Router - Create Task Endpoint**

**Objective**: Implement POST /api/{user_id}/tasks

**Files to Modify**:
- `backend/routers/tasks.py` (add endpoint)

**Code to Add**:
```python
@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Sets user_id on task to authenticated user (not from request).
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if str(user_id) != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users"
        )

    # Create task with authenticated user_id (spec FR-004)
    task = Task(
        user_id=UUID(current_user_id),  # CRITICAL: use authenticated user, not path param
        title=task_data.title,
        description=task_data.description
        # completed defaults to False (spec FR-012)
        # timestamps auto-set (spec FR-010)
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"Created task {task.id} for user {current_user_id}")
    return task
```

**Key Patterns**:
- Validates title length via TaskCreate schema (spec FR-008, FR-009)
- Sets user_id from authenticated token, NOT path param (security)
- Defaults: completed=False (spec FR-012), timestamps auto (spec FR-010)
- Returns 201 Created status code
- Commit + refresh pattern for async session

**References**:
- Spec FR-003, FR-004, FR-008, FR-009, FR-010, FR-012
- User input (POST /api/{user_id}/tasks endpoint)

**Skills/Templates**: `fastapi-backend-builder` agent

**Testing**: After this step, verify task creation. Test empty title rejection (422). Verify user_id mismatch returns 403.

---

#### **Step 8: Task Router - Get Single Task Endpoint**

**Objective**: Implement GET /api/{user_id}/tasks/{task_id}

**Files to Modify**:
- `backend/routers/tasks.py` (add endpoint)

**Code to Add**:
```python
@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single task by ID for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if str(user_id) != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # CRITICAL: prevent cross-user access
    )
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if task is None:
        # Spec FR-007: 404 for nonexistent OR foreign tasks (don't reveal existence)
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Retrieved task {task_id} for user {user_id}")
    return task
```

**Key Patterns**:
- Double filter: task_id AND user_id (spec FR-004, FR-007)
- 404 on not found OR wrong owner (don't leak existence) (spec FR-007)
- Uses `scalar_one_or_none()` for single result

**References**:
- Spec FR-003, FR-004, FR-007
- User input (GET /api/{user_id}/tasks/{task_id} endpoint)

**Skills/Templates**: `fastapi-backend-builder` agent

**Testing**: After this step, verify 404 when User A requests User B's task. Verify 404 for nonexistent task_id.

---

#### **Step 9: Task Router - Update Task Endpoint**

**Objective**: Implement PUT /api/{user_id}/tasks/{task_id}

**Files to Modify**:
- `backend/routers/tasks.py` (add endpoint)

**Code to Add**:
```python
from datetime import datetime

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing task for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.
    Updates only provided fields (partial update).
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if str(user_id) != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if task is None:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update provided fields only (partial update)
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Update timestamp (spec FR-011)
    task.updated_at = datetime.utcnow()

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"Updated task {task_id} for user {user_id}")
    return task
```

**Key Patterns**:
- Partial update (only provided fields) via TaskUpdate schema
- Manually update `updated_at` timestamp (spec FR-011)
- Same auth and isolation checks as get_task

**References**:
- Spec FR-003, FR-004, FR-007, FR-011
- User input (PUT /api/{user_id}/tasks/{task_id} endpoint)

**Skills/Templates**: `fastapi-backend-builder` agent

**Testing**: After this step, verify partial updates work (only title, only description, etc.). Verify 404 for cross-user update attempts. Verify updated_at changes.

---

#### **Step 10: Task Router - Delete Task Endpoint**

**Objective**: Implement DELETE /api/{user_id}/tasks/{task_id}

**Files to Modify**:
- `backend/routers/tasks.py` (add endpoint)

**Code to Add**:
```python
@router.delete("/{user_id}/tasks/{task_id}", response_model=dict)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task for the authenticated user.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if str(user_id) != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if task is None:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await db.delete(task)
    await db.commit()

    logger.info(f"Deleted task {task_id} for user {user_id}")
    return {"success": True}
```

**Key Patterns**:
- Returns `{"success": true}` per spec
- Permanent deletion (no soft delete)
- Same auth and isolation checks

**References**:
- Spec FR-003, FR-004, FR-007
- User input (DELETE /api/{user_id}/tasks/{task_id} endpoint)

**Skills/Templates**: `fastapi-backend-builder` agent

**Testing**: After this step, verify task deletion. Verify 404 for cross-user delete attempts. Verify deleted tasks don't appear in list.

---

#### **Step 11: Task Router - Toggle Completion Endpoint**

**Objective**: Implement PATCH /api/{user_id}/tasks/{task_id}/complete

**Files to Modify**:
- `backend/routers/tasks.py` (add endpoint)

**Code to Add**:
```python
@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle the completion status of a task.

    SECURITY: Verifies user_id path param matches authenticated user.
    SECURITY: Returns 404 if task doesn't exist OR belongs to different user.
    Toggles: false → true, true → false.
    """
    # Verify user_id in path matches authenticated user (spec FR-003)
    if str(user_id) != current_user_id:
        logger.warning(f"Authorization failed: user_id mismatch {user_id} != {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' tasks"
        )

    # Query with user_id AND task_id filter (spec FR-004, FR-007)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    result = await db.execute(statement)
    task = result.scalar_one_or_none()

    if task is None:
        logger.warning(f"Task {task_id} not found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update timestamp (spec FR-011)
    task.updated_at = datetime.utcnow()

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"Toggled completion for task {task_id} (now {task.completed}) for user {user_id}")
    return task
```

**Key Patterns**:
- Toggle: `not task.completed`
- No request body (PATCH with path params only)
- Updates timestamp on modification

**References**:
- Spec FR-003, FR-004, FR-007, FR-011
- User input (PATCH /api/{user_id}/tasks/{task_id}/complete endpoint)

**Skills/Templates**: `fastapi-backend-builder` agent

**Testing**: After this step, verify toggle works (false→true→false). Verify 404 for cross-user toggle attempts.

---

#### **Step 12: Main Application - CORS & Router Integration**

**Objective**: Configure CORS middleware and register task router

**Files to Modify**:
- `backend/main.py` (modify existing)

**Code Structure** (`main.py`):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from routers import tasks
from models import Task
from db import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Multi-User Task Management API",
    description="Secure REST API for todo tasks with JWT authentication and user isolation",
    version="1.0.0"
)

# CORS configuration (spec FR-016)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # Only allow frontend origin
    allow_credentials=True,  # Allow cookies for Better Auth
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"]
)

# Register routers
app.include_router(tasks.router)

# Startup event: Create tables
@app.on_event("startup")
async def on_startup():
    from sqlmodel import SQLModel
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables created (if not exists)")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-api"}

logger.info("Application initialized")
```

**Key Patterns**:
- CORS allows frontend origin only (spec FR-016)
- `allow_credentials=True` for httpOnly cookies (Better Auth)
- Startup event creates tables (auto-migration)
- Health check for monitoring
- Logging configuration

**References**:
- Spec FR-016 (CORS requirement)
- Spec Dependencies section (FRONTEND_ORIGIN env var)
- User input (final integration in main.py)

**Skills/Templates**: `fastapi-backend-builder` agent

**Testing**: After this step, verify app starts with `uv run uvicorn main:app --reload`. Test health check at `http://localhost:8000/health`. Verify CORS headers in browser dev tools.

---

#### **Step 13: Error Handling & Database Exception Handling**

**Objective**: Add graceful database error handling

**Files to Modify**:
- `backend/routers/tasks.py` (wrap database operations)

**Pattern to Add** (wrap each route):
```python
from sqlalchemy.exc import SQLAlchemyError

# Example for list_tasks:
try:
    statement = select(Task).where(Task.user_id == user_id)
    results = await db.execute(statement)
    tasks = results.scalars().all()
    logger.info(f"Listed {len(tasks)} tasks for user {user_id}")
    return tasks
except SQLAlchemyError as e:
    logger.error(f"Database error listing tasks: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database operation failed"
    )
```

**Key Patterns**:
- Catch `SQLAlchemyError` for database failures
- Log error details for debugging
- Return 500 Internal Server Error to client
- Don't expose internal error details (spec FR-021)

**References**:
- Spec FR-021 (graceful error handling)

**Skills/Templates**: `api-security` skill (error handling patterns)

**Testing**: After this step, verify app doesn't crash on database errors. Test by temporarily breaking DATABASE_URL.

---

### 4. Quickstart Guide (`quickstart.md`)

**Setup Instructions**:
```markdown
# Multi-User Task API - Quickstart

## Prerequisites
- Python 3.12+
- uv package manager
- Neon PostgreSQL database (or local PostgreSQL)
- Better Auth JWT secret (shared with frontend)

## Setup

1. **Install dependencies**:
   ```bash
   cd backend
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your values:
   # DATABASE_URL=postgresql+asyncpg://...
   # BETTER_AUTH_SECRET=your-secret
   # FRONTEND_ORIGIN=http://localhost:3000
   ```

3. **Run database migrations**:
   Tables are auto-created on startup via SQLModel.

4. **Start the server**:
   ```bash
   uv run uvicorn main:app --reload --port 8000
   ```

5. **Verify health**:
   ```bash
   curl http://localhost:8000/health
   ```

## Testing

Run tests:
```bash
pytest tests/
```

Test user isolation:
```bash
pytest tests/test_isolation.py -v
```

## API Endpoints

- GET /api/{user_id}/tasks - List tasks
- POST /api/{user_id}/tasks - Create task
- GET /api/{user_id}/tasks/{task_id} - Get task
- PUT /api/{user_id}/tasks/{task_id} - Update task
- DELETE /api/{user_id}/tasks/{task_id} - Delete task
- PATCH /api/{user_id}/tasks/{task_id}/complete - Toggle completion

## Authentication

All endpoints require JWT in:
- Authorization header: `Bearer <token>`
- OR httpOnly cookie: `session=<token>`

## Security Notes

- Every endpoint verifies user_id path param matches authenticated user
- All queries filtered by user_id to prevent data leaks
- Test with multiple user accounts to verify isolation
```

### 5. Agent Context Update

**Action**: Run agent context update script:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

**Updates**:
- Add FastAPI, SQLModel, python-jose to technology list
- Add Neon PostgreSQL async patterns
- Add Better Auth JWT validation patterns
- Preserve manual additions between markers

## Post-Design Constitution Check

### Re-Evaluation After Phase 1

#### Principle II: User Isolation and Security First ✅ VERIFIED
- **Design Decision**: Every endpoint includes user_id verification before database access
- **Implementation**: `if str(user_id) != current_user_id: raise 403 Forbidden`
- **Database Queries**: All include `.where(Task.user_id == user_id)` filter
- **Evidence**: See Steps 6-11 code examples (identical pattern in all 6 endpoints)

#### Principle V: Test-First for Security-Critical Paths ✅ VERIFIED
- **Test Plan**: Created test structure (`tests/test_auth.py`, `tests/test_isolation.py`)
- **Critical Tests**:
  - User A cannot list User B's tasks (403)
  - User A cannot get/update/delete User B's tasks (404)
  - Invalid JWT returns 401
  - Missing JWT returns 401
- **TDD Approach**: Tests will be written before endpoint implementation in `/sp.tasks` phase

#### Principle VI: Simplicity ✅ VERIFIED
- **No Complexity Violations**: Table is empty (no abstractions, repositories, or future-proofing)
- **Evidence**: Direct FastAPI patterns, no custom middleware, no service layer, dependency injection only for auth and database

## Next Steps

1. **Generate Tasks** (`/sp.tasks`):
   - Break this plan into atomic, testable tasks
   - Group by user story priority (P1, P2, P3)
   - Include test-writing tasks before implementation

2. **Implement** (`/sp.implement` or `fastapi-backend-builder` agent):
   - Execute tasks sequentially following this plan
   - Run tests after each step to verify progress
   - Use `api-security` skill to validate isolation

3. **Integration Testing**:
   - Create multiple test user accounts (User A, User B)
   - Verify isolation: User A cannot access User B's data
   - Verify all success criteria (SC-001 to SC-008)

4. **Create PR** (`/sp.git.commit_pr`):
   - Commit with reference to spec and tasks
   - PR description includes constitution compliance statement
   - Link to this plan and spec for reviewers

## Architectural Decision Suggestions

📋 **Architectural decision detected**: JWT validation strategy (middleware vs dependency injection)
**Decision**: Use FastAPI dependency injection (`Depends(get_current_user)`) instead of global middleware
**Rationale**: More testable (can mock dependencies), more flexible (some routes can be public), follows FastAPI best practices
**Alternatives Considered**: Global JWT middleware (less flexible, harder to test)
**Impact**: Low (standard FastAPI pattern)
**Recommendation**: No ADR needed (standard practice, not architecturally significant)

---

📋 **Architectural decision detected**: Database schema auto-migration vs explicit migrations
**Decision**: Use SQLModel auto-create on startup (`SQLModel.metadata.create_all`)
**Rationale**: Simple for single-table schema, no migration history needed initially, aligns with Principle VI (simplicity)
**Alternatives Considered**: Alembic migrations (overkill for MVP), manual CREATE TABLE (not idempotent)
**Impact**: Medium (affects database deployment)
**Recommendation**: No ADR needed for MVP. Create ADR if multi-table schemas or production migrations become complex.

## Implementation Readiness

**Status**: ✅ READY FOR TASK GENERATION

All design decisions documented. No unresolved NEEDS CLARIFICATION markers. Constitution gates passed. Research complete. Data model defined. API contracts specified. Implementation steps sequenced with testing strategy.

**Next Command**: `/sp.tasks` to break this plan into executable, testable tasks.
