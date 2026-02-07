# Backend Development Guide - Multi-User Task API

## Overview

Production-grade FastAPI backend with JWT authentication, user isolation, and PostgreSQL async operations. Built following Constitution Principle II: **users can only access their own data, always and without exception.**

## Architecture

```
backend/
├── main.py              # FastAPI app, CORS, lifespan events
├── db.py                # Async database engine, session factory
├── models.py            # SQLModel Task model with user_id
├── schemas.py           # Pydantic request/response schemas
├── dependencies.py      # JWT authentication dependency
├── routers/
│   ├── __init__.py
│   └── tasks.py         # Task CRUD endpoints (list, create)
├── tests/
│   ├── conftest.py      # Pytest fixtures and configuration
│   ├── test_auth.py     # JWT authentication tests (401)
│   ├── test_isolation.py # User isolation tests (403)
│   └── test_tasks.py    # Task CRUD functional tests
├── .env.example         # Environment variable template
├── pyproject.toml       # Project configuration
└── uv.lock              # Dependency lock file
```

## Setup

### Prerequisites

- Python 3.12+
- uv package manager
- Neon PostgreSQL database (or local PostgreSQL)
- Better Auth JWT secret (shared with frontend)

### Installation

```bash
cd backend

# Install dependencies
uv sync

# Configure environment variables
cp .env.example .env
# Edit .env with your values:
# DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/db?ssl=require
# BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
# FRONTEND_ORIGIN=http://localhost:3000
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string (asyncpg driver) | `postgresql+asyncpg://user:pass@host/db?ssl=require` |
| BETTER_AUTH_SECRET | JWT signing secret (MUST match frontend) | Generate with `openssl rand -hex 32` |
| FRONTEND_ORIGIN | Frontend URL for CORS | `http://localhost:3000` |

## Running the Server

### Development Mode

```bash
# With auto-reload on code changes
uv run uvicorn main:app --reload --port 8000

# With specific host binding
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Single worker
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Multiple workers (for production)
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: http://localhost:8000

## Testing

### Run All Tests

```bash
# Run all tests with verbose output
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_isolation.py -v

# Run specific test
uv run pytest tests/test_auth.py::test_list_tasks_returns_401_when_no_token -v
```

### Test Categories

- **test_auth.py**: JWT validation (401 Unauthorized)
- **test_isolation.py**: User isolation (403 Forbidden, cross-user access)
- **test_tasks.py**: CRUD functionality, validation

### Test Results

Current test status: **✅ 12 passed** (100% pass rate)

```
tests/test_auth.py::test_list_tasks_returns_401_when_no_token PASSED
tests/test_auth.py::test_list_tasks_returns_401_with_invalid_token PASSED
tests/test_auth.py::test_create_task_returns_401_when_no_token PASSED
tests/test_isolation.py::test_list_tasks_returns_403_when_user_id_mismatch PASSED
tests/test_isolation.py::test_user_a_cannot_see_user_b_tasks PASSED
tests/test_isolation.py::test_create_task_returns_403_when_user_id_mismatch PASSED
tests/test_tasks.py::test_list_tasks_returns_empty_for_new_user PASSED
tests/test_tasks.py::test_list_tasks_returns_correct_count PASSED
tests/test_tasks.py::test_create_task_returns_422_when_title_empty PASSED
tests/test_tasks.py::test_create_task_returns_422_when_title_too_long PASSED
tests/test_tasks.py::test_create_task_with_defaults PASSED
tests/test_tasks.py::test_create_task_with_title_and_description PASSED
```

## API Endpoints

### Implemented (MVP)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| GET | `/api/{user_id}/tasks` | List user's tasks | JWT |
| POST | `/api/{user_id}/tasks` | Create new task | JWT |

### Authentication

All protected endpoints require JWT token in:
- **Header**: `Authorization: Bearer <token>`
- **OR Cookie**: `session=<token>` (httpOnly)

### Example Requests

**Health Check:**
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "task-api"}
```

**List Tasks (requires JWT):**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks
```

**Create Task (requires JWT):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}' \
  http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks
```

## Security Patterns

### User Isolation (CRITICAL)

Every endpoint MUST:

1. **Validate JWT token** (get_current_user dependency)
2. **Verify user_id match** (path param vs token)
3. **Filter database queries** by user_id

```python
# ✅ CORRECT - User isolation enforced
@router.get("/{user_id}/tasks")
async def list_tasks(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify user_id match
    if str(user_id) != current_user_id:
        raise HTTPException(403, "Cannot access other users' tasks")

    # 2. Filter by user_id
    statement = select(Task).where(Task.user_id == user_id)
    tasks = await db.exec(statement)
    return tasks.all()
```

### Error Responses

| Status Code | When | Example |
|-------------|------|---------|
| 401 | Missing or invalid JWT token | `{"detail": "Not authenticated - missing token"}` |
| 403 | Valid token but user_id mismatch | `{"detail": "Cannot access other users' tasks"}` |
| 404 | Resource not found OR belongs to other user | `{"detail": "Task not found"}` |
| 422 | Validation error (title length, etc) | `{"detail": [{"loc": ["body", "title"], "msg": "..."}]}` |

### Security Checklist

Before deploying any endpoint:

- [ ] JWT token verified via `Depends(get_current_user)`
- [ ] Path `user_id` compared with `current_user_id` from token
- [ ] Database query includes `.where(Task.user_id == user_id)`
- [ ] Returns 401 on missing/invalid token
- [ ] Returns 403 on user_id mismatch
- [ ] Returns 404 (not 403) for cross-user resource access
- [ ] No hardcoded secrets (use environment variables)
- [ ] Errors don't leak sensitive information

## Database

### Connection

- **Driver**: asyncpg (async PostgreSQL)
- **ORM**: SQLModel
- **Pool**: Managed by SQLAlchemy async engine

### Migrations

Currently using auto-create on startup:
```python
# In main.py lifespan
async with engine.begin() as conn:
    await conn.run_sync(SQLModel.metadata.create_all)
```

For production: Consider Alembic for versioned migrations.

### Task Model

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)  # Indexed for performance
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## Development Workflow

### Adding a New Endpoint

1. **Write tests first** (TDD approach)
   - Auth tests (401) in `tests/test_auth.py`
   - Isolation tests (403) in `tests/test_isolation.py`
   - Functional tests in `tests/test_tasks.py`

2. **Verify tests FAIL** before implementation
   ```bash
   uv run pytest tests/ -v
   ```

3. **Implement endpoint** in `routers/tasks.py`
   - Add JWT dependency: `current_user_id: str = Depends(get_current_user)`
   - Verify user_id match
   - Filter query by user_id

4. **Verify tests PASS** after implementation
   ```bash
   uv run pytest tests/ -v
   ```

5. **Test manually** with curl or API client

### Adding Dependencies

```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name

# Example: Add SQLAlchemy error handling
uv add sqlalchemy-utils
```

### Code Style

- **Type hints**: All function parameters and returns
- **Docstrings**: All endpoints with security notes
- **Logging**: INFO for success, WARNING for auth failures, ERROR for exceptions
- **Async**: All database operations use `async/await`

## Troubleshooting

### Database Connection Errors

**Error**: `ValueError: DATABASE_URL environment variable not set`

**Solution**: Create `.env` file with valid DATABASE_URL

```bash
cp .env.example .env
# Edit .env with your Neon PostgreSQL URL
```

### JWT Verification Fails

**Error**: `401 Unauthorized - Invalid token`

**Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend

**Solution**: Ensure both use the same secret:
```bash
# Backend .env
BETTER_AUTH_SECRET=your-secret-key-here

# Frontend .env.local
BETTER_AUTH_SECRET=your-secret-key-here
```

### User Isolation Tests Fail

**Error**: User A can see User B's tasks

**Cause**: Missing user_id filter in database query

**Solution**: Add `.where(Task.user_id == user_id)` to all queries:
```python
# ❌ WRONG
statement = select(Task)

# ✅ CORRECT
statement = select(Task).where(Task.user_id == user_id)
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'asyncpg'`

**Solution**: Sync dependencies
```bash
uv sync
```

## Performance

### Current Performance Goals

- Task list retrieval: < 500ms (1000 tasks)
- Task creation: < 300ms
- Concurrent requests: 100 simultaneous users

### Optimization Tips

1. **Database Indexes**: user_id is indexed (critical for performance)
2. **Connection Pooling**: Configured in db.py via SQLAlchemy
3. **Async Operations**: All database calls use async/await
4. **Query Optimization**: Filter by user_id early in query chain

## Production Deployment

### Environment Setup

1. **Set environment variables** in production environment
2. **Use production PostgreSQL** (Neon or self-hosted)
3. **Disable SQL logging** (set `echo=False` in db.py)
4. **Use multiple workers** for uvicorn
5. **Add HTTPS** (behind nginx or load balancer)

### Health Monitoring

Health check endpoint: `GET /health`

Expected response:
```json
{
  "status": "healthy",
  "service": "task-api"
}
```

Use for:
- Docker health checks
- Kubernetes liveness/readiness probes
- Load balancer health checks

## Next Steps (Post-MVP)

Remaining user stories to implement:

- **US3**: PATCH /api/{user_id}/tasks/{task_id}/complete (toggle completion)
- **US4**: PUT /api/{user_id}/tasks/{task_id} (update task)
- **US5**: GET /api/{user_id}/tasks/{task_id} (get single task)
- **US6**: DELETE /api/{user_id}/tasks/{task_id} (delete task)

See `specs/001-task-api/tasks.md` for complete task breakdown.

## References

- **Specification**: `/specs/001-task-api/spec.md`
- **Implementation Plan**: `/specs/001-task-api/plan.md`
- **Task Breakdown**: `/specs/001-task-api/tasks.md`
- **Data Model**: `/specs/001-task-api/data-model.md`
- **API Contract**: `/specs/001-task-api/contracts/openapi.yaml`
- **Constitution**: `/.specify/memory/constitution.md` (Principle II: User Isolation)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test failures for specific error messages
3. Verify environment variables are set correctly
4. Check logs with `--log-level debug`

---

**MVP Status**: ✅ Complete (User Stories 1 & 2)
**Test Coverage**: 12/12 passing (100%)
**Security Audit**: User isolation verified via tests
