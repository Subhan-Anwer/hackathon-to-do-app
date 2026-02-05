---
name: api-security
description: Implement JWT authentication middleware, user isolation, and security best practices for FastAPI applications. Use when securing endpoints, implementing JWT verification, ensuring user data isolation, or protecting against common vulnerabilities.
---

# API Security for FastAPI

## Overview

Implement secure FastAPI endpoints with JWT authentication, comprehensive user data isolation, proper error handling, and protection against common vulnerabilities. This skill focuses on the backend security layer that works with JWT tokens from Better Auth.

## When to Use This Skill

- Securing FastAPI endpoints with JWT authentication
- Implementing JWT verification middleware
- Ensuring user data isolation across all operations
- Adding authentication to API routes
- Protecting against IDOR, mass assignment, and other OWASP vulnerabilities
- User asks to "secure API", "add JWT auth", "implement authentication", "protect endpoints"

## Critical Security Principles

### 1. User Isolation is MANDATORY

Every protected endpoint MUST:
- ✅ Verify JWT token validity
- ✅ Extract user_id from token payload
- ✅ Compare token user_id with user_id in URL path
- ✅ Return 403 Forbidden if mismatch
- ✅ Filter ALL database queries by authenticated user_id
- ✅ Verify resource ownership before updates/deletes

### 2. Never Trust Client Input

- Force user_id from JWT token, not from request body
- Validate all input data with Pydantic models
- Filter queries by authenticated user
- Verify ownership before modifying resources

### 3. Proper Error Handling

- Use appropriate HTTP status codes
- Don't leak sensitive information in errors
- Include WWW-Authenticate header for 401 responses
- Log security events for monitoring

## Implementation Workflow

### Step 1: Create JWT Middleware

Copy `assets/templates/jwt-middleware.py` to `middleware/jwt.py`.

**Key Features:**
- Extracts and parses Bearer token from Authorization header
- Verifies JWT signature using BETTER_AUTH_SECRET
- Checks token expiration
- Extracts user data (user_id, email)
- Returns comprehensive error messages for debugging
- Implements proper exception handling

**Usage:**
```python
from middleware.jwt import verify_jwt

@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
):
    # current_user = {"user_id": "...", "email": "...", "exp": ...}
```

### Step 2: Implement Route Protection Patterns

#### Pattern 1: Protected GET Route (List Resources)

```python
from fastapi import APIRouter, Depends, HTTPException
from middleware.jwt import verify_jwt
from sqlmodel import select, Session

@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Get all tasks for authenticated user"""

    # CRITICAL: Verify user owns this resource
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: You can only access your own tasks"
        )

    # Query MUST be filtered by authenticated user
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return tasks
```

#### Pattern 2: Protected POST Route (Create Resource)

```python
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Create new task for authenticated user"""

    # Verify user ownership of endpoint
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only create tasks for yourself"
        )

    # CRITICAL: Force user_id from token (don't trust client)
    task = Task(
        **task_data.dict(),
        user_id=current_user["user_id"]  # Use authenticated user
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

#### Pattern 3: Protected PUT Route (Update Resource)

```python
@router.put("/api/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Update existing task"""

    # Step 1: Verify user ownership of endpoint
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )

    # Step 2: Fetch resource
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Step 3: CRITICAL - Verify task belongs to authenticated user
    if task.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own tasks"
        )

    # Step 4: Update fields (only provided fields)
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

#### Pattern 4: Protected DELETE Route

```python
@router.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    """Delete task"""

    # Verify endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Fetch resource
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify resource ownership
    if task.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own tasks"
        )

    # Delete
    session.delete(task)
    session.commit()

    return {"message": "Task deleted", "id": task_id}
```

### Step 3: Configure CORS (CRITICAL)

CORS configuration is essential for frontend-backend communication:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware - MUST be configured before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "https://your-app.com",   # Production frontend
    ],
    allow_credentials=True,  # CRITICAL: Allows cookies and auth headers
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers including Authorization
)
```

**Why `allow_credentials=True` is Critical:**
- Allows Authorization header to be sent
- Enables cookie-based authentication
- Required for JWT token forwarding from Next.js proxy

### Step 4: Environment Configuration

Create proper environment variable validation:

```python
import os
from typing import Optional

# Load secret with validation
BETTER_AUTH_SECRET: Optional[str] = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is required. "
        "Set it in .env file."
    )

if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be at least 32 characters for security. "
        f"Current length: {len(BETTER_AUTH_SECRET)}"
    )

ALGORITHM = "HS256"  # HMAC with SHA-256
```

## Security Best Practices

### 1. Never Trust Client Input

```python
# ❌ WRONG - Client could send any user_id in body
task = Task(**task_data.dict())

# ✅ CORRECT - Force user_id from authenticated token
task = Task(
    **task_data.dict(),
    user_id=current_user["user_id"]
)
```

### 2. Always Filter Queries by User

```python
# ❌ WRONG - Returns all tasks from all users
tasks = session.exec(select(Task)).all()

# ✅ CORRECT - Filter by authenticated user
tasks = session.exec(
    select(Task).where(Task.user_id == current_user["user_id"])
).all()
```

### 3. Verify Resource Ownership

```python
# ✅ Always check resource belongs to authenticated user
resource = session.get(Resource, resource_id)

if not resource:
    raise HTTPException(status_code=404, detail="Not found")

if resource.user_id != current_user["user_id"]:
    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access this resource"
    )
```

### 4. Use Proper HTTP Status Codes

- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Valid token but no permission for resource
- **404 Not Found**: Resource doesn't exist
- **400 Bad Request**: Invalid input data
- **500 Internal Server Error**: Server error (not auth-related)

### 5. Secure Error Responses

```python
# ✅ Authentication error
raise HTTPException(
    status_code=401,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)

# ✅ Authorization error
raise HTTPException(
    status_code=403,
    detail="You do not have permission to access this resource"
)

# ❌ DON'T leak implementation details
# raise HTTPException(status_code=500, detail=str(exception))

# ✅ Generic error message
raise HTTPException(
    status_code=500,
    detail="An error occurred processing your request"
)
```

## Common Vulnerabilities Prevention

### 1. Insecure Direct Object Reference (IDOR)

**VULNERABLE:**
```python
@router.get("/api/tasks/{task_id}")
async def get_task(task_id: int, session: Session = Depends(get_session)):
    return session.get(Task, task_id)  # ❌ Anyone can access any task!
```

**SECURE:**
```python
@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Verify endpoint ownership
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    # Fetch resource
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404)

    # ✅ Verify resource ownership
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403)

    return task
```

### 2. Mass Assignment

**VULNERABLE:**
```python
@router.post("/api/{user_id}/tasks")
async def create_task(task_data: dict):  # ❌ Unvalidated dict
    task = Task(**task_data)  # Client could set any field including user_id!
```

**SECURE:**
```python
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,  # ✅ Validated Pydantic model
    current_user: dict = Depends(verify_jwt),
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403)

    task = Task(
        **task_data.dict(),
        user_id=current_user["user_id"]  # ✅ Force from token
    )
```

### 3. SQL Injection

**VULNERABLE:**
```python
query = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"  # ❌ String interpolation
```

**SECURE:**
```python
# ✅ SQLModel/SQLAlchemy prevents SQL injection automatically
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

### 4. Information Disclosure

```python
# ❌ DON'T expose internal errors
try:
    result = process_data()
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Leaks stack trace!

# ✅ Generic error message to client, log details server-side
import logging
logger = logging.getLogger(__name__)

try:
    result = process_data()
except Exception as e:
    logger.error(f"Processing error: {str(e)}", exc_info=True)  # Log details
    raise HTTPException(
        status_code=500,
        detail="An error occurred processing your request"  # Generic message
    )
```

## Testing Security

### Manual Testing with curl

1. **Test without token:**
```bash
curl http://localhost:8000/api/user123/tasks
# Expected: 401 Unauthorized
```

2. **Test with invalid token:**
```bash
curl -H "Authorization: Bearer invalid_token" \
  http://localhost:8000/api/user123/tasks
# Expected: 401 Unauthorized - Invalid token
```

3. **Test with mismatched user_id:**
```bash
# Get token for userA, try to access userB's data
curl -H "Authorization: Bearer <userA_token>" \
  http://localhost:8000/api/userB/tasks
# Expected: 403 Forbidden
```

4. **Test with valid token:**
```bash
curl -H "Authorization: Bearer <valid_token>" \
  http://localhost:8000/api/user123/tasks
# Expected: 200 OK with user's tasks
```

### Automated Security Tests

Copy `assets/templates/security-tests.py` for pytest-based security tests:

```python
def test_unauthenticated_access_denied(client):
    response = client.get("/api/user123/tasks")
    assert response.status_code == 401

def test_cross_user_access_denied(client, user_a_token, user_b_id):
    response = client.get(
        f"/api/{user_b_id}/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert response.status_code == 403

def test_resource_ownership_verified(client, user_token, user_id, other_user_task_id):
    response = client.delete(
        f"/api/{user_id}/tasks/{other_user_task_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
```

## Security Checklist

Before deploying to production, verify:

- [ ] JWT verification on all protected endpoints
- [ ] User ID comparison (token user_id vs URL user_id)
- [ ] Resource ownership verification before updates/deletes
- [ ] All database queries filtered by authenticated user_id
- [ ] CORS properly configured with allow_credentials=True
- [ ] Strong BETTER_AUTH_SECRET (32+ characters, random)
- [ ] Proper HTTP status codes (401 for auth, 403 for authorization)
- [ ] Error messages don't leak sensitive information
- [ ] HTTPS enabled in production
- [ ] Input validation with Pydantic models
- [ ] No SQL injection vulnerabilities (use ORM properly)
- [ ] Rate limiting configured (recommended)
- [ ] Security logging for failed auth attempts
- [ ] Token expiration properly configured
- [ ] No hardcoded secrets or credentials

## Common Pitfalls

### 1. Forgetting User ID Verification in URL

```python
# ❌ Missing verification
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, current_user: dict = Depends(verify_jwt)):
    return fetch_tasks(user_id)  # user_id not verified against token!

# ✅ Always verify
if current_user["user_id"] != user_id:
    raise HTTPException(status_code=403)
```

### 2. Not Filtering Database Queries

```python
# ❌ Returns all tasks
tasks = session.exec(select(Task)).all()

# ✅ Filter by authenticated user
tasks = session.exec(
    select(Task).where(Task.user_id == current_user["user_id"])
).all()
```

### 3. Trusting Client-Provided user_id

```python
# ❌ Client controls user_id
task = Task(**task_data.dict())  # task_data includes user_id from client

# ✅ Force from token
task = Task(**task_data.dict(), user_id=current_user["user_id"])
```

### 4. Missing CORS Credentials Configuration

```python
# ❌ Missing allow_credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # allow_credentials=True missing!
)

# ✅ Include allow_credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # CRITICAL
)
```

### 5. Wrong JWT Payload Field

```python
# ❌ WRONG - user_id is not a standard JWT field
user_id = payload.get("user_id")

# ✅ CORRECT - JWT standard uses 'sub' for subject (user ID)
user_id = payload.get("sub")
```

### 6. Not Verifying Resource Ownership

```python
# ❌ Only checks endpoint ownership
if current_user["user_id"] != user_id:
    raise HTTPException(status_code=403)
task = session.get(Task, task_id)
session.delete(task)  # What if task belongs to different user?

# ✅ Verify both endpoint AND resource ownership
if current_user["user_id"] != user_id:
    raise HTTPException(status_code=403)
task = session.get(Task, task_id)
if task.user_id != current_user["user_id"]:  # Check resource ownership
    raise HTTPException(status_code=403)
session.delete(task)
```

### 7. Exposing Internal Errors

```python
# ❌ Leaks implementation details
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# ✅ Generic message, log internally
import logging
logger.error(f"Error: {str(e)}", exc_info=True)
raise HTTPException(status_code=500, detail="Internal server error")
```

## Advanced Security Features

### Rate Limiting (Recommended)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/api/{user_id}/tasks")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def create_task(request: Request, ...):
    ...
```

### Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Force HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Prevent host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "your-app.com"]
)
```

### Audit Logging

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    request: Request,
):
    # Log security-relevant actions
    logger.info(
        f"Task created by user {current_user['user_id']} "
        f"from IP {request.client.host} "
        f"at {datetime.utcnow()}"
    )
    ...
```

## Resources

### Templates (assets/templates/)

- `jwt-middleware.py` - Complete JWT verification middleware
- `protected-routes.py` - All CRUD route patterns with security
- `security-tests.py` - Automated security test suite
- `cors-config.py` - Production-ready CORS configuration
- `env-validation.py` - Environment variable validation

### References (references/)

- `jwt-verification.md` - JWT token structure and verification details
- `user-isolation-patterns.md` - Comprehensive user isolation strategies
- `owasp-top10.md` - OWASP vulnerabilities and prevention
- `security-testing.md` - Security testing strategies and tools

### Related Skills

- `better-auth-integration` - Frontend JWT token generation and proxy setup
- `fastapi-backend-builder` - FastAPI project structure with security built-in
- `database-schema-designer` - Schema design with user_id foreign keys

## Output Style

When using this skill, provide:
- Complete, production-ready code examples
- Clear security explanations for each pattern
- Vulnerability prevention strategies
- Testing approaches
- Common pitfalls with corrections
- Comprehensive error handling

Always prioritize security over convenience. Every endpoint must verify authentication and authorization.
