# API Security Skill

Comprehensive security implementation for FastAPI applications with JWT authentication, user isolation, and OWASP protection.

## Quick Start

Use this skill when:
- Securing FastAPI endpoints
- Implementing JWT verification middleware
- Ensuring user data isolation
- Protecting against common vulnerabilities
- User asks to "secure API", "add JWT auth", "implement authentication"

## What This Skill Provides

### 1. JWT Authentication Middleware
Complete JWT verification with:
- Token signature validation
- Expiration checking
- User data extraction
- Comprehensive error handling

### 2. User Isolation Patterns
Three-layer defense:
- Layer 1: JWT Authentication
- Layer 2: Endpoint Ownership Verification
- Layer 3: Resource Ownership Verification

### 3. Protected Route Templates
Ready-to-use patterns for:
- GET (list and single resource)
- POST (create)
- PUT/PATCH (update)
- DELETE (remove)
- Search and bulk operations

### 4. Security Best Practices
Protection against:
- IDOR (Insecure Direct Object Reference)
- Mass Assignment
- SQL Injection
- Information Disclosure
- All OWASP Top 10 vulnerabilities

### 5. Testing Framework
Comprehensive test suite covering:
- Authentication tests
- Authorization tests
- IDOR tests
- Input validation tests
- Rate limiting tests

## File Structure

```
.claude/skills/api-security/
├── SKILL.md                          # Main skill documentation
├── README.md                         # This file
├── assets/
│   └── templates/
│       ├── jwt-middleware.py         # JWT verification middleware
│       ├── protected-routes.py       # Example protected routes
│       ├── security-tests.py         # Automated test suite
│       ├── cors-config.py            # CORS configuration
│       └── env-validation.py         # Environment validation
└── references/
    ├── jwt-verification.md           # JWT deep dive
    ├── user-isolation-patterns.md    # User isolation guide
    ├── owasp-top10.md                # OWASP protection
    └── security-testing.md           # Testing guide
```

## Usage Examples

### Example 1: Implement JWT Middleware

```bash
# Copy template to your project
cp .claude/skills/api-security/assets/templates/jwt-middleware.py backend/middleware/jwt.py
```

**Result:**
- JWT verification dependency
- Helper functions for user/resource verification
- Comprehensive error handling

### Example 2: Secure a Route

```python
from fastapi import APIRouter, Depends, HTTPException
from middleware.jwt import verify_jwt, verify_user_access, verify_resource_ownership
from database import get_session

@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # Layer 2: Verify endpoint ownership
    verify_user_access(user_id, current_user)

    # Fetch resource
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # Layer 3: Verify resource ownership
    verify_resource_ownership(task.user_id, current_user, "task")

    return task
```

### Example 3: Add Security Tests

```bash
# Copy test templates
cp .claude/skills/api-security/assets/templates/security-tests.py backend/tests/test_security.py

# Run tests
pytest tests/test_security.py -v
```

### Example 4: Configure CORS

```python
from cors_config import configure_cors, configure_security_headers

app = FastAPI()

# Add CORS and security headers
configure_cors(app)
configure_security_headers(app)
```

## Key Security Principles

### 1. User Isolation is MANDATORY

Every protected endpoint MUST:
```python
# ✅ Verify token
current_user: dict = Depends(verify_jwt)

# ✅ Verify endpoint ownership
if current_user["user_id"] != user_id:
    raise HTTPException(403)

# ✅ Filter queries by user
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

### 2. Never Trust Client Input

```python
# ❌ WRONG - Client controls user_id
task = Task(**task_data.dict())

# ✅ CORRECT - Force from token
task = Task(
    **task_data.dict(),
    user_id=current_user["user_id"]
)
```

### 3. Always Verify Resource Ownership

```python
# Fetch resource
resource = session.get(Resource, resource_id)

# Verify ownership
if resource.user_id != current_user["user_id"]:
    raise HTTPException(403)
```

## Common Patterns

### Pattern: Protected List Endpoint

```python
@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    verify_user_access(user_id, current_user)

    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return tasks
```

### Pattern: Protected Create Endpoint

```python
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    verify_user_access(user_id, current_user)

    task = Task(
        **task_data.dict(),
        user_id=current_user["user_id"]  # Force from token
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

### Pattern: Protected Update Endpoint

```python
@router.put("/api/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    verify_user_access(user_id, current_user)

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404)

    verify_resource_ownership(task.user_id, current_user, "task")

    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

## Security Checklist

Before deploying, verify:

- [ ] JWT verification on all protected endpoints
- [ ] User ID comparison (token vs URL)
- [ ] Resource ownership verification
- [ ] Database queries filtered by user_id
- [ ] CORS properly configured with allow_credentials=True
- [ ] Strong BETTER_AUTH_SECRET (32+ characters)
- [ ] Proper HTTP status codes (401 for auth, 403 for authorization)
- [ ] Error messages don't leak sensitive information
- [ ] HTTPS enabled in production
- [ ] Input validation with Pydantic models
- [ ] Rate limiting configured
- [ ] Security tests passing
- [ ] Dependencies scanned for vulnerabilities

## Testing

### Run Security Tests

```bash
# Run all security tests
pytest tests/test_security.py -v

# Run specific test class
pytest tests/test_security.py::TestAuthentication -v

# Check test coverage
pytest --cov=middleware --cov-report=html
```

### Manual Testing

```bash
# Test without token
curl http://localhost:8000/api/user123/tasks
# Expected: 401

# Test with invalid token
curl -H "Authorization: Bearer invalid" \
  http://localhost:8000/api/user123/tasks
# Expected: 401

# Test cross-user access
curl -H "Authorization: Bearer <userA_token>" \
  http://localhost:8000/api/userB/tasks
# Expected: 403
```

## Common Pitfalls

### ❌ Forgetting User ID Verification
```python
# Missing verification against token
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str):
    return get_user_tasks(user_id)  # Anyone can access any user's tasks!
```

### ❌ Not Filtering Queries
```python
# Returns ALL tasks from ALL users
tasks = session.exec(select(Task)).all()
```

### ❌ Trusting Client Input
```python
# Client could set any user_id
task = Task(**task_data.dict())
```

### ❌ Missing Resource Ownership Check
```python
# Only checks endpoint, not resource ownership
verify_user_access(user_id, current_user)
task = session.get(Task, task_id)
session.delete(task)  # What if task belongs to different user?
```

## Resources

### Templates (Complete, Production-Ready Code)
- `jwt-middleware.py` - JWT verification middleware
- `protected-routes.py` - All CRUD route patterns
- `security-tests.py` - Automated test suite
- `cors-config.py` - CORS configuration
- `env-validation.py` - Environment validation

### References (In-Depth Guides)
- `jwt-verification.md` - JWT structure and verification
- `user-isolation-patterns.md` - User isolation strategies
- `owasp-top10.md` - OWASP vulnerability prevention
- `security-testing.md` - Security testing guide

## Related Skills

- **better-auth-integration** - Frontend JWT token generation and proxy setup
- **fastapi-backend-builder** - FastAPI project structure with security built-in
- **database-schema-designer** - Schema design with user_id foreign keys

## Quick Reference

### HTTP Status Codes
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Valid token but no permission
- **404 Not Found**: Resource doesn't exist
- **422 Validation Error**: Invalid input data

### JWT Token Structure
```json
{
  "sub": "user_id",     // User ID (CRITICAL - use this!)
  "email": "user@example.com",
  "exp": 1706890000     // Expiration timestamp
}
```

### Helper Functions
```python
verify_jwt               # Dependency: Verify JWT token
verify_user_access()     # Verify endpoint ownership (token vs URL)
verify_resource_ownership()  # Verify resource belongs to user
```

## Support

For detailed documentation on specific topics:
1. Read `SKILL.md` for comprehensive implementation guide
2. Check `references/` for deep dives on specific topics
3. Copy `assets/templates/` for ready-to-use code

## Version

Current version: 1.0.0

## License

This skill is part of the Claude Code skills library.
