# Quickstart: Multi-User Task Management API

**Feature**: 001-task-api
**Date**: 2026-02-06

## Overview

This guide walks through setting up and running the FastAPI backend for the multi-user task management system. Follow these steps to get the API running locally in under 5 minutes.

## Prerequisites

- **Python**: 3.12 or higher
- **uv**: Python package manager ([Install](https://github.com/astral-sh/uv))
- **PostgreSQL**: Neon Serverless PostgreSQL database (or local PostgreSQL)
- **Better Auth**: JWT secret shared with frontend

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd backend
uv sync
```

This installs all production and development dependencies from `pyproject.toml`.

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# PostgreSQL connection (Neon serverless or local)
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# JWT secret (MUST match frontend Better Auth secret)
BETTER_AUTH_SECRET=your-secret-key-here

# Frontend origin for CORS
FRONTEND_ORIGIN=http://localhost:3000
```

**Important**: `BETTER_AUTH_SECRET` must be the same value used in your Next.js frontend.

### 3. Run Database Migrations

Tables are auto-created on first startup (SQLModel auto-migration). No manual migration needed for MVP.

### 4. Start the Server

```bash
uv run uvicorn main:app --reload --port 8000
```

**Development mode flags**:
- `--reload`: Auto-restart on code changes
- `--port 8000`: Run on port 8000

### 5. Verify Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "task-api"
}
```

## API Endpoints

Base URL: `http://localhost:8000`

### Authentication

All endpoints require JWT token in **one of**:
- **Authorization header**: `Authorization: Bearer <token>`
- **httpOnly cookie**: `session=<token>` (Better Auth default)

### Endpoints

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/api/{user_id}/tasks` | List all user's tasks | - |
| POST | `/api/{user_id}/tasks` | Create new task | `{"title": "...", "description": "..."}` |
| GET | `/api/{user_id}/tasks/{task_id}` | Get single task | - |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update task | `{"title": "...", "description": "...", "completed": true}` |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete task | - |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle completion | - |

### Example Requests

**Create Task**:
```bash
curl -X POST http://localhost:8000/api/YOUR_USER_ID/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

**List Tasks**:
```bash
curl http://localhost:8000/api/YOUR_USER_ID/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Toggle Completion**:
```bash
curl -X PATCH http://localhost:8000/api/YOUR_USER_ID/tasks/TASK_ID/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Interactive API Documentation

FastAPI provides automatic interactive docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these to explore endpoints, test requests, and view schemas.

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run User Isolation Tests

```bash
pytest tests/test_isolation.py -v
```

### Run Specific Test

```bash
pytest tests/test_tasks.py::test_create_task -v
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Development Workflow

### 1. Activate Virtual Environment (Optional)

```bash
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

Or use `uv run` prefix for all commands (auto-activates).

### 2. Add New Dependencies

```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name

# Example: Add rate limiting
uv add slowapi
```

### 3. Update Dependencies

```bash
uv sync --upgrade
```

### 4. Run with Debug Logging

```bash
# Enable SQL query logging
export LOG_LEVEL=DEBUG
uv run uvicorn main:app --reload
```

### 5. Format Code (if linter configured)

```bash
uv run black .
uv run isort .
```

## Troubleshooting

### Issue: "DATABASE_URL environment variable not set"

**Solution**: Copy `.env.example` to `.env` and fill in your database URL.

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### Issue: "BETTER_AUTH_SECRET environment variable not set"

**Solution**: Add `BETTER_AUTH_SECRET` to `.env`. Must match frontend secret.

```bash
echo "BETTER_AUTH_SECRET=your-secret-here" >> .env
```

### Issue: "401 Unauthorized" on all requests

**Causes**:
1. Missing JWT token in request
2. Invalid token (wrong secret)
3. Expired token

**Solution**:
- Verify token is sent in Authorization header or cookie
- Check `BETTER_AUTH_SECRET` matches frontend
- Generate new token from frontend login

### Issue: "403 Forbidden - Cannot access other users' tasks"

**Cause**: URL `user_id` parameter doesn't match authenticated user in JWT token.

**Solution**: Use your own `user_id` from JWT `sub` claim in the URL.

### Issue: Database connection errors

**Solution**:
- Verify DATABASE_URL format: `postgresql+asyncpg://...`
- Check network access to Neon (firewall, VPN)
- Test connection: `uv run python -c "from db import engine; print(engine)"`

### Issue: CORS errors in browser

**Cause**: Frontend origin not allowed.

**Solution**:
- Set `FRONTEND_ORIGIN=http://localhost:3000` in `.env`
- Restart server after env change
- Verify origin in browser DevTools Network tab

## Security Notes

### Local Development

- JWT tokens are logged at INFO level (user_id only, not full token)
- SQL queries are logged (contains user data - disable in production)
- CORS allows only `FRONTEND_ORIGIN` (not wildcard)

### Production Checklist

Before deploying to production:

- [ ] Disable SQL logging (`echo=False` in db.py)
- [ ] Set `LOG_LEVEL=INFO` (not DEBUG)
- [ ] Use strong `BETTER_AUTH_SECRET` (min 32 characters)
- [ ] Configure `DATABASE_URL` with SSL: `?ssl=require`
- [ ] Set `FRONTEND_ORIGIN` to production domain
- [ ] Enable rate limiting (add middleware)
- [ ] Review all logged data (no tokens, no passwords)

## Performance Notes

**Expected Performance** (per spec):
- List tasks: <500ms for 1000 tasks
- Create task: <300ms
- Concurrent users: 100 simultaneous requests

**Optimization Tips**:
- Database indexes are auto-created (user_id indexed)
- Async operations throughout (FastAPI + asyncpg)
- Neon serverless auto-scales with load
- Connection pooling enabled by default

## Project Structure

```
backend/
├── .venv/                 # Virtual environment
├── main.py                # FastAPI app entry point
├── db.py                  # Database connection
├── models.py              # SQLModel Task model
├── schemas.py             # Pydantic request/response schemas
├── dependencies.py        # JWT auth dependency
├── routers/
│   └── tasks.py           # Task endpoints
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── test_auth.py       # Auth tests
│   ├── test_isolation.py  # User isolation tests
│   └── test_tasks.py      # Endpoint tests
├── .env                   # Environment variables (NOT in git)
├── .env.example           # Template (in git)
├── pyproject.toml         # Dependencies and config
└── uv.lock                # Locked dependencies
```

## Next Steps

1. **Frontend Integration**: Configure Next.js frontend to call this API
2. **User Accounts**: Set up Better Auth for user signup/login
3. **Testing**: Run `pytest tests/test_isolation.py` with multiple user accounts
4. **Production**: Deploy to cloud provider (Vercel, Railway, etc.)

## Resources

- **Spec**: `specs/001-task-api/spec.md`
- **Plan**: `specs/001-task-api/plan.md`
- **Data Model**: `specs/001-task-api/data-model.md`
- **API Contract**: `specs/001-task-api/contracts/openapi.yaml`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/

## Support

- **Issues**: Check `specs/001-task-api/` documentation first
- **Bugs**: Verify constitution compliance (user isolation, JWT validation)
- **Performance**: Check spec success criteria (SC-001 to SC-008)

---

**Status**: ✅ QUICKSTART COMPLETE

Server should be running at http://localhost:8000. Test with health check, then authenticate and try creating a task!
