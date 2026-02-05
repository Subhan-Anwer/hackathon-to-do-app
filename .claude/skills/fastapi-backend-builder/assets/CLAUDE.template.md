# Claude Code Instructions - FastAPI Backend

## Project Context

This is a FastAPI backend application with SQLModel ORM and JWT authentication. The backend implements user isolation, RESTful API patterns, and proper error handling.

## Critical Security Rules

### User Isolation (MANDATORY)

Every protected endpoint MUST:
1. Accept `user_id` in the path parameter
2. Require JWT authentication: `current_user: dict = Depends(verify_jwt)`
3. Verify `current_user["user_id"] == user_id` (return 403 if mismatch)
4. Filter ALL database queries by the authenticated `user_id`

**Never skip these checks.** This prevents users from accessing other users' data.

### Database Query Pattern

Always use:
```python
statement = select(Model).where(Model.user_id == user_id, Model.id == item_id)
```

Never use:
```python
session.get(Model, item_id)  # Missing user_id filter!
```

## Code Standards

### 1. Import Organization
```python
# Standard library
import os
from typing import Optional, List
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

# Local
from app.db import get_session
from app.middleware.jwt import verify_jwt
from app.models import ModelName
from app.schemas import SchemaName
```

### 2. Route Structure

```python
@router.http_method("/{user_id}/resource", response_model=ResponseModel, status_code=status.HTTP_XXX)
async def function_name(
    user_id: str,
    # ... other path/query params
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Docstring explaining endpoint purpose."""
    # 1. Verify user
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2. Business logic with user_id filter
    # 3. Return response
```

### 3. Error Handling

Use appropriate HTTP status codes:
- 200: Success (GET, PUT, PATCH)
- 201: Created (POST)
- 204: No Content (DELETE)
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (user_id mismatch)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error (unexpected errors)

Always include descriptive error messages:
```python
raise HTTPException(status_code=404, detail="Task not found")
```

### 4. Database Operations

**Create:**
```python
item = Model(**data.model_dump(), user_id=user_id)
session.add(item)
session.commit()
session.refresh(item)
return item
```

**Read:**
```python
statement = select(Model).where(Model.user_id == user_id, Model.id == item_id)
item = session.exec(statement).first()
if not item:
    raise HTTPException(status_code=404, detail="Not found")
```

**Update:**
```python
update_data = data.model_dump(exclude_unset=True)
for key, value in update_data.items():
    setattr(item, key, value)
item.updated_at = datetime.utcnow()
session.add(item)
session.commit()
session.refresh(item)
```

**Delete:**
```python
session.delete(item)
session.commit()
```

## Project Structure

- `app/main.py` - FastAPI app, CORS, routers
- `app/models.py` - SQLModel tables
- `app/schemas.py` - Pydantic request/response models
- `app/db.py` - Database connection and session
- `app/routes/*.py` - API endpoints
- `app/middleware/jwt.py` - JWT verification
- `app/utils/*.py` - Helper functions

## When Adding New Features

1. **Model** - Add SQLModel table in `models.py` with `user_id` field and index
2. **Schemas** - Add Pydantic models in `schemas.py` (Create, Update, Response)
3. **Routes** - Create endpoint file in `routes/` with user isolation
4. **Router** - Register router in `main.py`

## Testing Commands

```bash
# Run tests
uv run pytest

# Start server
uv run uvicorn app.main:app --reload

# Test endpoint
curl -X GET http://localhost:8000/api/{user_id}/resource \
  -H "Authorization: Bearer {token}"
```

## Environment Variables

Required in `.env`:
- `DATABASE_URL` - Database connection string
- `BETTER_AUTH_SECRET` - JWT secret (must match frontend)
- `CORS_ORIGINS` - Allowed frontend origins
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)

## Common Mistakes to Avoid

1. ❌ Not verifying `user_id` matches authenticated user
2. ❌ Using `session.get(Model, id)` without user_id filter
3. ❌ Missing `allow_credentials=True` in CORS
4. ❌ Hardcoding secrets instead of using environment variables
5. ❌ Not using `exclude_unset=True` for updates
6. ❌ Missing error handling for 404/403/401
7. ❌ Not committing database changes
8. ❌ Wrong HTTP status codes

## Git Commit Practices

When creating commits:
- Focus on what changed, not implementation details
- Keep commits small and focused
- Use conventional commit format
- Always include co-author: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

## Questions?

If unclear about requirements:
1. Check existing code patterns
2. Review API specification
3. Ask for clarification rather than guessing
