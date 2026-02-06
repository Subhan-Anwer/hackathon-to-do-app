# Backend Quickstart Guide

## Installation & Setup

```bash
cd backend

# Install dependencies (production + dev)
uv sync

# Create environment file
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - BETTER_AUTH_SECRET: Same secret as frontend (min 32 chars)
# - FRONTEND_ORIGIN: Frontend URL for CORS
```

## Running the Server

### Development

```bash
# With auto-reload (recommended for development)
uv run uvicorn main:app --reload --port 8000

# Server will be available at: http://localhost:8000
# API docs (Swagger): http://localhost:8000/docs
# Alternative docs (ReDoc): http://localhost:8000/redoc
```

### Production

```bash
# Single worker
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Multiple workers (for production)
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_isolation.py -v

# Run specific test
uv run pytest tests/test_auth.py::test_list_tasks_returns_401_when_no_token -v

# Run with short traceback
uv run pytest tests/ --tb=short
```

## API Endpoints

### Health Check (Public)

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "task-api"}
```

### List Tasks (Requires JWT)

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/USER_ID/tasks
```

### Create Task (Requires JWT)

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}' \
  http://localhost:8000/api/USER_ID/tasks
```

### Get Single Task (Requires JWT)

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/USER_ID/tasks/TASK_ID
```

### Update Task (Requires JWT)

```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "completed": true}' \
  http://localhost:8000/api/USER_ID/tasks/TASK_ID
```

### Toggle Task Completion (Requires JWT)

```bash
curl -X PATCH \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/USER_ID/tasks/TASK_ID/complete
```

### Delete Task (Requires JWT)

```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/USER_ID/tasks/TASK_ID
```

## Security Notes

**All protected endpoints require JWT authentication:**
- Header: `Authorization: Bearer <token>`
- OR Cookie: `session=<token>` (httpOnly)

**User isolation enforced:**
- Each user can ONLY access their own tasks
- Path `user_id` must match authenticated user from JWT
- Returns 403 Forbidden if user_id mismatch detected
- Returns 404 Not Found for nonexistent tasks OR tasks belonging to other users

## Error Responses

| Status | Meaning | Example |
|--------|---------|---------|
| 401 | Missing or invalid JWT token | `{"detail": "Not authenticated - missing token"}` |
| 403 | Valid token but user_id mismatch | `{"detail": "Cannot access other users' tasks"}` |
| 404 | Task not found or wrong owner | `{"detail": "Task not found"}` |
| 422 | Validation error | `{"detail": [{"loc": ["body", "title"], "msg": "..."}]}` |
| 500 | Database error | `{"detail": "Database operation failed"}` |

## Troubleshooting

### Server won't start

**Check environment variables:**
```bash
# Verify .env file exists
cat .env

# Test DATABASE_URL format
# Should be: postgresql+asyncpg://user:pass@host/db?ssl=require
```

### JWT authentication fails

**Ensure BETTER_AUTH_SECRET matches frontend:**
```bash
# Backend .env
BETTER_AUTH_SECRET=your-secret-key-here

# Frontend .env.local
BETTER_AUTH_SECRET=your-secret-key-here
```

### Tests fail

**Re-sync dependencies:**
```bash
uv sync
```

**Check Python version:**
```bash
python --version
# Should be 3.12+
```

## Project Structure

```
backend/
├── main.py              # FastAPI app initialization
├── db.py                # Database connection
├── models.py            # SQLModel Task model
├── schemas.py           # Pydantic schemas
├── dependencies.py      # JWT authentication
├── routers/
│   └── tasks.py         # Task endpoints (6 routes)
├── tests/
│   ├── conftest.py      # Test fixtures
│   ├── test_auth.py     # Auth tests (401)
│   ├── test_isolation.py # User isolation (403)
│   └── test_tasks.py    # Functional tests
├── .env.example         # Environment template
└── pyproject.toml       # Project config
```

## Development Workflow

1. **Write tests first** (TDD approach)
2. **Verify tests FAIL** before implementation
3. **Implement endpoint** with user isolation
4. **Verify tests PASS** after implementation
5. **Test manually** with curl or API client

## Next Steps

See `DEVELOPMENT.md` for detailed development guide including:
- Architecture deep-dive
- Security patterns
- Adding new endpoints
- Database migrations
- Production deployment

## API Documentation

Interactive API documentation available when server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide:
- All endpoint definitions
- Request/response schemas
- Try-it-out functionality
- Authentication setup

---

**Status**: ✅ All 6 endpoints implemented and tested (34/34 tests passing)
