# FastAPI Backend Setup Guide

## Quick Start

### 1. Project Initialization

```bash
# Create backend directory
mkdir backend && cd backend

# Initialize uv project
uv init

# Set Python version
echo "3.11" > .python-version

# Add FastAPI dependencies
uv add fastapi uvicorn sqlmodel python-jose[cryptography] python-multipart
```

### 2. Install Dependencies

```bash
# Core dependencies
uv add fastapi         # Web framework
uv add uvicorn         # ASGI server
uv add sqlmodel        # ORM (combines SQLAlchemy + Pydantic)
uv add python-jose[cryptography]  # JWT handling
uv add python-multipart  # Form data support

# Database drivers (choose one)
uv add psycopg2-binary  # PostgreSQL
# OR
uv add pymysql         # MySQL
# OR - SQLite included in Python

# Optional but recommended
uv add python-dotenv   # Environment variables
```

### 3. Environment Configuration

Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
BETTER_AUTH_SECRET=your-super-secret-key-minimum-32-characters
CORS_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
```

Create `.env.example` (commit to git):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
BETTER_AUTH_SECRET=change-this-secret-key
CORS_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Run Development Server

```bash
# Using uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or activate venv first
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
uvicorn app.main:app --reload
```

## Project Structure Setup

Create the directory structure:

```bash
mkdir -p app/routes app/middleware app/utils
touch app/__init__.py
touch app/main.py
touch app/models.py
touch app/schemas.py
touch app/db.py
touch app/routes/__init__.py
touch app/middleware/__init__.py
touch app/utils/__init__.py
```

## Database Setup

### PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL driver
uv add psycopg2-binary

# Connection string format
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### SQLite (Good for Development)

```python
# No installation needed - included in Python
DATABASE_URL=sqlite:///./database.db
```

### MySQL

```bash
# Install MySQL driver
uv add pymysql

# Connection string format
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
```

## Development Workflow

### 1. Start Development Server

```bash
uv run uvicorn app.main:app --reload
```

### 2. Test Endpoints

Using curl:
```bash
# Health check
curl http://localhost:8000/health

# Create task (requires auth)
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Test"}'

# List tasks
curl http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer <token>"
```

Using httpie:
```bash
# Health check
http GET localhost:8000/health

# Create task
http POST localhost:8000/api/user123/tasks \
  Authorization:"Bearer <token>" \
  title="Test task" description="Test"
```

### 3. Interactive API Docs

FastAPI automatically generates interactive docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing Setup

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio httpx

# Create test file
mkdir tests
touch tests/test_api.py
```

Example test:
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

Run tests:
```bash
uv run pytest
```

## Migration Checklist

- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Initialize project: `uv init`
- [ ] Set Python version: `echo "3.11" > .python-version`
- [ ] Install dependencies: `uv add fastapi uvicorn sqlmodel python-jose`
- [ ] Create `.env` file with required variables
- [ ] Create directory structure (app/, routes/, middleware/, utils/)
- [ ] Implement app/main.py with CORS configuration
- [ ] Implement app/db.py with database connection
- [ ] Implement app/models.py with SQLModel tables
- [ ] Implement app/schemas.py with Pydantic models
- [ ] Implement app/middleware/jwt.py for authentication
- [ ] Implement app/routes/*.py for endpoints
- [ ] Test user isolation (verify 403 for wrong user_id)
- [ ] Test all CRUD operations
- [ ] Test error handling (404, 401, 403, 400, 500)
- [ ] Verify CORS allows credentials
- [ ] Test JWT secret matches frontend

## Common Commands

```bash
# Start server
uv run uvicorn app.main:app --reload

# Install new package
uv add package-name

# Install dev dependency
uv add --dev package-name

# Export requirements
uv pip compile pyproject.toml -o requirements.txt

# Run tests
uv run pytest

# Check types (if using mypy)
uv run mypy app/

# Format code (if using black)
uv run black app/

# Lint code (if using ruff)
uv run ruff check app/
```

## Production Considerations

### 1. Environment Variables

Never commit `.env` to git. Use environment-specific configurations:
- `.env.development`
- `.env.production`

### 2. Database Migrations

Consider using Alembic for schema migrations:
```bash
uv add alembic
alembic init migrations
```

### 3. Logging

Add structured logging:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 4. Security Headers

Add security middleware:
```bash
uv add fastapi-security
```

### 5. Rate Limiting

Protect endpoints from abuse:
```bash
uv add slowapi
```

## Troubleshooting

### CORS Errors
- Ensure `allow_credentials=True` in CORS middleware
- Verify `CORS_ORIGINS` includes frontend URL
- Check browser console for specific error

### JWT Authentication Fails
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check token format: "Bearer <token>"
- Ensure token not expired
- Verify user_id exists in token payload

### Database Connection Errors
- Check `DATABASE_URL` format
- Verify database server is running
- Test connection with database client
- Check firewall/network settings

### Import Errors
- Ensure all `__init__.py` files exist
- Check relative import paths
- Verify package installed in venv
- Use absolute imports from `app.`
