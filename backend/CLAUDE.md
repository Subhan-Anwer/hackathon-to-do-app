# Backend - FastAPI Application

## Current Structure

```
backend/
├── .venv/              # Virtual environment (managed by uv)
├── .python-version     # Python version (3.12)
├── main.py             # FastAPI application with lifespan events (130 lines)
├── db.py               # Async database engine and session (48 lines)
├── models.py           # SQLModel Task entity (76 lines)
├── schemas.py          # Pydantic request/response schemas (54 lines)
├── dependencies.py     # JWT authentication dependency (82 lines)
├── routers/
│   └── tasks.py        # All 6 task endpoints (338 lines)
├── tests/
│   ├── conftest.py     # Test fixtures and utilities (102 lines)
│   ├── test_auth.py    # Authentication tests (75 lines)
│   ├── test_isolation.py  # User isolation tests (189 lines)
│   └── test_tasks.py   # CRUD functionality tests (420 lines)
├── pyproject.toml      # Project configuration with all dependencies
├── uv.lock             # Dependency lock file
├── .env.example        # Environment variable template
├── docs/               # Documentation files
│   ├── DEVELOPMENT.md  # Comprehensive development guide (640 lines)
│   ├── QUICKSTART.md   # Quick reference guide (245 lines)
│   └── README.md       # Backend overview and setup instructions
└── CLAUDE.md           # This file - backend structure guide
```

**Total: 12 Python files, 1,588 lines of code, 34 passing tests**

## Package Manager: uv

This project uses **uv** - a fast Python package manager and resolver written in Rust.

### Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Basic uv Commands

**Install Dependencies:**
```bash
# Install all dependencies from pyproject.toml
uv sync

# Install project in editable mode
uv pip install -e .
```

**Add New Packages:**
```bash
# Add a package and update pyproject.toml
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Examples:
uv add sqlmodel          # Add SQLModel for ORM
uv add pyjwt             # Add JWT support
uv add pytest --dev      # Add pytest as dev dependency
```

**Remove Packages:**
```bash
uv remove <package-name>
```

**Update Dependencies:**
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add <package-name> --upgrade
```

**Run Python Scripts:**
```bash
# Run with uv (auto-activates venv)
uv run python main.py

# Or activate venv first, then run normally
source .venv/bin/activate
python main.py
```

## Working with requirements.txt

**Generate requirements.txt from pyproject.toml:**
```bash
uv pip freeze > requirements.txt
```

**Install from requirements.txt (if needed):**
```bash
uv pip install -r requirements.txt
```

**Note:** With uv, `pyproject.toml` and `uv.lock` are the source of truth. Only generate `requirements.txt` if needed for deployment or legacy compatibility.

## Current Dependencies

**Production:**
- `fastapi>=0.128.1` - Modern async web framework
- `uvicorn[standard]>=0.40.0` - ASGI server with async workers
- `sqlmodel>=0.0.32` - Async PostgreSQL ORM (SQLAlchemy + Pydantic)
- `asyncpg>=0.31.0` - Async PostgreSQL driver for Neon
- `python-jose[cryptography]>=3.5.0` - JWT token validation
- `python-multipart>=0.0.22` - Form data support

**Development:**
- `pytest>=9.0.2` - Testing framework
- `pytest-asyncio>=1.3.0` - Async test support
- `httpx>=0.28.1` - Async HTTP client for testing
- `aiosqlite>=0.22.1` - In-memory SQLite for tests

**Python Version:**
- Requires Python `>=3.12`

## Common Workflow

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Add a new dependency
uv add sqlmodel uvicorn

# 3. Run the application
python main.py
# or
uv run python main.py

# 4. Deactivate when done
deactivate
```

## Development Setup

```bash
# Initial setup (if .venv doesn't exist)
uv venv
source .venv/bin/activate
uv sync

# Start development
uv run uvicorn main:app --reload
```

## Implementation Status

✅ **COMPLETE** - Production-ready FastAPI backend with full user isolation

**Implemented Features:**
- ✅ JWT authentication with Better Auth integration (Bearer token + cookie)
- ✅ Async database with Neon PostgreSQL (asyncpg driver)
- ✅ SQLModel Task entity with user_id indexing
- ✅ All 6 task endpoints (list, create, get, update, delete, toggle complete)
- ✅ Strict user isolation (Constitution Principle II compliant)
- ✅ Comprehensive error handling with database exception wrapping
- ✅ CORS middleware configured for Next.js frontend
- ✅ 34 passing tests (auth, isolation, CRUD functionality)
- ✅ Complete documentation (docs/DEVELOPMENT.md, docs/QUICKSTART.md)

**Architecture Highlights:**
- Triple-layer security: JWT validation → user_id verification → DB filtering
- Test-first development (TDD) - all tests written before implementation
- Async all the way - true async operations with asyncpg
- Modern FastAPI patterns - lifespan events, dependency injection
- Privacy-focused - returns 404 (not 403) for unauthorized task access

**API Endpoints:**
```
GET    /health                                  - Health check (public)
GET    /api/{user_id}/tasks                     - List user's tasks
POST   /api/{user_id}/tasks                     - Create new task
GET    /api/{user_id}/tasks/{task_id}           - Get single task
PUT    /api/{user_id}/tasks/{task_id}           - Update task
DELETE /api/{user_id}/tasks/{task_id}           - Delete task
PATCH  /api/{user_id}/tasks/{task_id}/complete  - Toggle completion
```

**Quick Start:**
```bash
cd backend
uv sync
cp .env.example .env
# Edit .env with DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_ORIGIN
uv run uvicorn main:app --reload --port 8000
```

**Run Tests:**
```bash
uv run pytest tests/ -v  # All 34 tests should pass
```

**Documentation:**
- See `docs/DEVELOPMENT.md` for comprehensive development guide
- See `docs/QUICKSTART.md` for quick reference and curl examples
- See `docs/README.md` for backend overview and setup instructions
- See `specs/001-task-api/` for complete specification and design documents
