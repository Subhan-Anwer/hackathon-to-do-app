---
name: fastapi-backend-builder
description: Generate production-ready FastAPI backend applications with SQLModel ORM, JWT authentication, proper project structure, RESTful API patterns, and user isolation security. Use when building Python backends, implementing API specifications, creating REST endpoints, or setting up FastAPI projects with authentication.
---

# FastAPI Backend Builder

Generate production-ready FastAPI backend applications with best practices, SQLModel ORM integration, JWT authentication, and comprehensive security.

## Purpose

Build FastAPI backends that implement API specifications with:
- Proper project structure and organization
- SQLModel for type-safe database operations
- JWT authentication middleware with user isolation
- RESTful API patterns and error handling
- CORS configuration for frontend integration
- Dependency injection for sessions and authentication

## When to Use

Invoke when user requests:
- "Build a FastAPI backend"
- "Create REST API endpoints"
- "Implement the API specification"
- "Set up Python backend with authentication"
- "Add database models and CRUD operations"
- Creating backends from spec-writer specifications

## Workflow

### 1. Initialize Project Structure

Create standard FastAPI project layout with uv package manager:

```bash
mkdir backend && cd backend
uv init
echo "3.11" > .python-version
uv add fastapi uvicorn sqlmodel python-jose[cryptography]
```

Create directories:
```bash
mkdir -p app/routes app/middleware app/utils
touch app/{__init__.py,main.py,models.py,schemas.py,db.py}
touch app/routes/__init__.py app/middleware/__init__.py app/utils/__init__.py
```

### 2. Set Up Configuration Files

Copy templates from `assets/`:
- `.env.example` → Project root (customize as needed)
- `README.template.md` → `README.md` (update with project specifics)
- `CLAUDE.template.md` → `CLAUDE.md` (backend-specific AI instructions)

Create `.env` from template and populate with actual values (never commit).

### 3. Implement Core Components

**Database Connection (`app/db.py`):**
- Create SQLModel engine with proper connection args
- Implement `get_session()` dependency
- Add `create_db_and_tables()` function
- See `references/code_patterns.md` section 2 for complete pattern

**Models (`app/models.py`):**
- Define SQLModel tables with proper types
- CRITICAL: Add `user_id: str = Field(index=True)` to all user-specific tables
- Include timestamps: `created_at`, `updated_at`
- See `references/code_patterns.md` section 3 for pattern

**Schemas (`app/schemas.py`):**
- Create Pydantic models for Create, Update, Response
- Separate API contract from database models
- Use `Optional` fields for PATCH operations
- See `references/code_patterns.md` section 4

**JWT Middleware (`app/middleware/jwt.py`):**
- Implement `verify_jwt()` dependency
- Extract and validate Bearer token
- Return `{"user_id": str}` payload
- Handle JWTError with 401 status
- See `references/code_patterns.md` section 5

**Main App (`app/main.py`):**
- Configure CORS with `allow_credentials=True`
- Register routers with `/api` prefix
- Add startup event to create tables
- Include health check endpoint
- See `references/code_patterns.md` section 1

### 4. Implement Protected Endpoints

For each resource, create routes file in `app/routes/` following this pattern:

```python
@router.get("/{user_id}/resource", response_model=List[ResourceResponse])
async def list_resources(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # CRITICAL: Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # CRITICAL: Filter by user_id
    statement = select(Resource).where(Resource.user_id == user_id)
    return session.exec(statement).all()
```

**MANDATORY User Isolation Checklist:**
- ✅ Path parameter: `user_id: str`
- ✅ JWT dependency: `current_user: dict = Depends(verify_jwt)`
- ✅ User verification: `if current_user["user_id"] != user_id: raise 403`
- ✅ Query filter: `.where(Model.user_id == user_id)`

See `references/code_patterns.md` section 6 for all CRUD patterns.

### 5. Implement Standard CRUD Operations

For each resource, implement:
- `GET /{user_id}/resources` - List all (status: 200)
- `POST /{user_id}/resources` - Create (status: 201)
- `GET /{user_id}/resources/{id}` - Get one (status: 200)
- `PUT /{user_id}/resources/{id}` - Update (status: 200)
- `DELETE /{user_id}/resources/{id}` - Delete (status: 204)
- `PATCH /{user_id}/resources/{id}/*` - Partial update (status: 200)

Use proper response models, status codes, and error handling.

### 6. Testing and Validation

Verify implementation:
```bash
# Start server
uv run uvicorn app.main:app --reload

# Test health
curl http://localhost:8000/health

# Test protected endpoint (should fail without auth)
curl http://localhost:8000/api/user123/tasks

# Check interactive docs
open http://localhost:8000/docs
```

## Critical Security Patterns

### User Isolation (Non-Negotiable)

Every protected endpoint MUST implement all five checks:

1. Accept `user_id` in path
2. Require `Depends(verify_jwt)`
3. Compare `current_user["user_id"]` with path `user_id`
4. Return 403 if mismatch
5. Filter queries: `.where(Model.user_id == user_id, ...)`

**Never** use `session.get(Model, id)` - always filter by user_id.

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS").split(","),
    allow_credentials=True,  # REQUIRED for JWT cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables

All secrets and configuration from environment:
```python
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET must be set")
```

## Reference Documentation

Load as needed using Read tool:

- **`references/project_structure.md`** - Directory layout and file responsibilities
- **`references/code_patterns.md`** - Complete implementations for all components
- **`references/setup_guide.md`** - Installation, configuration, development workflow
- **`references/common_pitfalls.md`** - Security issues and mistakes to avoid

Search patterns for specific topics:
```
grep "Pattern Name" references/code_patterns.md
grep "Issue Name" references/common_pitfalls.md
grep "Setup Step" references/setup_guide.md
```

## Common Pitfalls to Avoid

Critical mistakes - check `references/common_pitfalls.md` for details:

1. Missing user verification (no 403 check)
2. Not filtering queries by user_id
3. CORS without `allow_credentials=True`
4. Hardcoded secrets
5. Using `session.get()` without user filter
6. Missing indexes on user_id
7. Not using `exclude_unset=True` for updates
8. Wrong HTTP status codes
9. Generic error messages
10. Not handling JWT errors

## Output Style

When generating code:
- Include complete, working implementations
- Add inline comments for critical security checks
- Use proper type hints throughout
- Follow FastAPI dependency injection patterns
- Include docstrings for endpoints
- Provide clear error messages
- Reference line numbers when discussing existing code

When explaining:
- Start with security implications
- Explain the "why" behind patterns
- Reference common pitfalls
- Provide testing commands
- Link to relevant reference sections
