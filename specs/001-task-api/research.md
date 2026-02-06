# Research: Multi-User Task Management API

**Feature**: 001-task-api
**Date**: 2026-02-06
**Status**: Complete

## Executive Summary

This research document consolidates technology decisions and best practices for implementing a secure, multi-user FastAPI backend with JWT authentication and strict user isolation. All research tasks from Phase 0 of plan.md have been addressed with concrete recommendations.

## Research Tasks & Findings

### 1. JWT Validation with Better Auth

**Question**: How to validate Better Auth JWT tokens in FastAPI?

**Research Findings**:

**Library Selection**: `python-jose[cryptography]`
- Better Auth uses standard JWT format (RFC 7519)
- python-jose provides complete JWT implementation with cryptographic signing
- Includes support for multiple algorithms (HS256, RS256, ES256)
- Better Auth compatibility confirmed (uses standard `sub` claim for user_id)

**Token Structure** (Better Auth):
```json
{
  "sub": "uuid-of-user",
  "iat": 1234567890,
  "exp": 1234567890,
  "aud": "your-app",
  "iss": "better-auth"
}
```

**Extraction Pattern**:
```python
# Check Authorization header
token = request.headers.get("Authorization", "").replace("Bearer ", "")

# Fallback to httpOnly cookie
if not token:
    token = request.cookies.get("session")

# Decode and validate
payload = jwt.decode(token, SECRET, algorithms=["HS256"])
user_id = payload.get("sub")
```

**Best Practices**:
- Store secret in environment variable (`BETTER_AUTH_SECRET`)
- Use same secret value in frontend and backend
- Validate token signature, expiration, and required claims
- Log authentication failures for security auditing
- Return 401 Unauthorized for any validation failure

**Decision**: Use `python-jose[cryptography]` with FastAPI dependency injection pattern.

**Rationale**: Standard library, Better Auth compatible, supports FastAPI's dependency system for testability.

**Alternatives Considered**:
- PyJWT: More minimal, but python-jose provides additional crypto features
- FastAPI-JWT-Auth: Too opinionated, adds unnecessary complexity

---

### 2. SQLModel Async Operations

**Question**: How to configure async SQLModel sessions with Neon PostgreSQL?

**Research Findings**:

**Database Driver**: `asyncpg`
- Native async PostgreSQL driver (not psycopg2)
- Required for Neon Serverless PostgreSQL
- Better performance than sync drivers (event loop integration)
- Compatible with SQLModel via SQLAlchemy async engine

**Async Engine Configuration**:
```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

# Connection URL format for asyncpg
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging (disable in production)
    future=True,  # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,  # Verify connections before use (important for serverless)
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Allow access to objects after commit
)
```

**Session Management Pattern**:
```python
async def get_db():
    async with async_session() as session:
        yield session
    # FastAPI handles cleanup automatically
```

**Query Patterns**:
```python
# SELECT with filter
statement = select(Task).where(Task.user_id == user_id)
results = await db.execute(statement)
tasks = results.scalars().all()

# INSERT
task = Task(...)
db.add(task)
await db.commit()
await db.refresh(task)

# UPDATE
task.title = "New Title"
db.add(task)
await db.commit()

# DELETE
await db.delete(task)
await db.commit()
```

**Best Practices**:
- Always use `await` for database operations
- Use `pool_pre_ping=True` for serverless databases
- Set `expire_on_commit=False` to access objects after commit
- Use context managers (`async with`) for session lifecycle
- Enable SQL logging in development, disable in production

**Decision**: Use `create_async_engine` with asyncpg driver, AsyncSession with dependency injection.

**Rationale**: Native async support, Neon compatibility, aligns with FastAPI async patterns.

**Alternatives Considered**:
- psycopg2 (sync): Not compatible with Neon, blocks event loop
- psycopg3 async: Newer but less mature than asyncpg for SQLAlchemy

---

### 3. User Isolation Patterns

**Question**: How to enforce user_id filtering on all queries without duplication?

**Research Findings**:

**Pattern 1: Dependency Injection for current_user**
```python
async def get_current_user(request: Request) -> str:
    # Extract user_id from JWT
    return user_id

# Use in routes
async def list_tasks(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify path user_id matches authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(403, "Forbidden")

    # Filter query by user_id
    statement = select(Task).where(Task.user_id == user_id)
    results = await db.execute(statement)
    return results.scalars().all()
```

**Pattern 2: Path Parameter Validation**
- Include `user_id` in URL path: `/api/{user_id}/tasks`
- Verify path `user_id` matches JWT `user_id` before database query
- Return 403 Forbidden if mismatch (don't process request)
- This prevents parameter tampering attacks

**Pattern 3: Database Query Filtering**
- ALWAYS include `.where(Entity.user_id == authenticated_user_id)`
- Never query without user_id filter (constitution violation)
- Use double filter for specific resources: `.where(Task.id == task_id, Task.user_id == user_id)`
- Return 404 (not 403) when resource doesn't exist OR belongs to different user (don't leak existence)

**Anti-Patterns** (DO NOT USE):
```python
# ❌ WRONG: No user_id filter (leaks all users' data)
tasks = session.exec(select(Task)).all()

# ❌ WRONG: Trusts client-provided user_id without JWT verification
tasks = session.exec(select(Task).where(Task.user_id == user_id_from_request_body)).all()

# ❌ WRONG: Queries first, then filters in Python (inefficient, still queries all data)
all_tasks = session.exec(select(Task)).all()
user_tasks = [t for t in all_tasks if t.user_id == user_id]
```

**Best Practices**:
- Combine all three patterns for defense in depth
- Dependency injection ensures JWT validation happens first
- Path validation prevents URL parameter tampering
- Database filtering ensures query-level isolation
- Log all authorization failures (FR-018)

**Decision**: Use all three patterns - dependency injection, path validation, database filtering.

**Rationale**: Defense in depth, aligns with Constitution Principle II, testable at each layer.

**Alternatives Considered**:
- Global middleware: Less flexible, can't exclude public endpoints
- Query builder wrapper: Premature abstraction (Principle VI violation)

---

### 4. Error Handling Strategy

**Question**: How to structure 401/403/404 error responses consistently?

**Research Findings**:

**HTTP Status Code Standards** (RESTful):
- **401 Unauthorized**: Missing or invalid JWT token (authentication failure)
- **403 Forbidden**: Valid token but insufficient permissions (authorization failure)
- **404 Not Found**: Resource doesn't exist OR belongs to different user (don't leak existence)
- **422 Unprocessable Entity**: Validation errors (Pydantic schema failures)
- **500 Internal Server Error**: Database or server errors

**FastAPI Error Pattern**:
```python
from fastapi import HTTPException, status

# 401: Authentication failure
if not token:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated - missing token"
    )

# 403: Authorization failure (user_id mismatch)
if str(user_id) != current_user_id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cannot access other users' tasks"
    )

# 404: Resource not found OR wrong owner
if task is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

# 500: Database error
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database operation failed"
    )
```

**Security Considerations**:
- Don't expose internal errors to client (spec FR-021)
- Don't reveal whether resources exist for other users (use 404, not 403)
- Log detailed errors server-side for debugging
- Return generic messages to client

**Error Response Structure** (FastAPI default):
```json
{
  "detail": "User-friendly error message"
}
```

**Best Practices**:
- Use FastAPI's HTTPException (native, well-documented)
- Log all auth/authorization failures (spec FR-017, FR-018)
- Return consistent error structure
- Don't leak internal state (stack traces, SQL queries)

**Decision**: Use FastAPI HTTPException with standard status codes, generic client messages, detailed server logs.

**Rationale**: Simple, FastAPI-native, security-conscious, aligns with spec FR-021.

**Alternatives Considered**:
- Custom exception classes: Premature abstraction (Principle VI violation)
- Problem Details (RFC 7807): Overkill for simple API
- Custom error middleware: Adds complexity without benefit

---

## Technology Decision Matrix

| **Decision** | **Options Evaluated** | **Selected** | **Rationale** | **Constitution Principle** |
|--------------|-----------------------|--------------|---------------|----------------------------|
| JWT Library | PyJWT vs python-jose | python-jose[cryptography] | Better Auth compatibility, includes cryptography for RS256, complete JWT implementation | III (Reusability - use standard libraries) |
| Database Driver | psycopg2 vs psycopg3 vs asyncpg | asyncpg | Async support, Neon serverless compatibility, better performance, mature SQLAlchemy integration | II (Security - async prevents blocking) |
| Session Management | sync vs async sessions | async sessions (AsyncSession) | Aligns with FastAPI async patterns, Neon requirement, non-blocking I/O | VI (Simplicity - use framework patterns) |
| Auth Approach | Middleware vs Dependency | Dependency injection (Depends) | More flexible, testable (can mock), follows FastAPI best practices, can have public routes | V (Test-First - dependencies are testable) |
| Error Structure | Custom classes vs HTTPException | HTTPException with standard codes | Simple, FastAPI-native, JSON-serializable, no custom types needed | VI (Simplicity - use framework tools) |

## Implementation Recommendations

### Phase 1: Foundation (Steps 1-2)
1. Install dependencies: `uv add fastapi uvicorn sqlmodel asyncpg python-jose[cryptography]`
2. Configure async engine with Neon DATABASE_URL
3. Create get_db dependency
4. Test connection before proceeding

### Phase 2: Data Layer (Steps 3-4)
1. Define SQLModel Task with user_id index
2. Create Pydantic schemas (TaskCreate, TaskUpdate, TaskRead)
3. Test model creation and schema validation

### Phase 3: Security Layer (Step 5)
1. Implement get_current_user dependency
2. Test JWT validation with mock tokens
3. Verify 401 responses for invalid tokens

### Phase 4: API Layer (Steps 6-11)
1. Implement endpoints one at a time
2. Test each endpoint immediately after creation
3. Verify user isolation with multiple test accounts
4. Confirm 403/404 responses for cross-user access

### Phase 5: Integration (Steps 12-13)
1. Wire everything together in main.py
2. Add CORS middleware
3. Add database error handling
4. Test end-to-end with real JWT tokens

## Performance Considerations

**Expected Performance** (per spec success criteria):
- Task list retrieval: <500ms for 1000 tasks
- Task creation: <300ms
- Concurrent requests: 100 simultaneous users

**Optimization Strategies**:
1. **Indexing**: user_id indexed for fast filtering
2. **Connection Pooling**: Async engine handles pool automatically
3. **Query Efficiency**: Use `.where()` filters, not Python filtering
4. **Async Operations**: All I/O async (database, auth)
5. **Neon Serverless**: Auto-scales with load

**No premature optimization needed**: Architecture supports performance requirements without additional complexity.

## Security Audit Checklist

Before deployment, verify:
- [ ] All endpoints verify JWT token
- [ ] All endpoints check user_id path param vs token user_id
- [ ] All database queries filter by user_id
- [ ] No hardcoded secrets (check .env.example)
- [ ] CORS configured to frontend origin only
- [ ] Logs don't expose tokens or passwords
- [ ] Error messages don't leak internal state
- [ ] Test accounts verified for isolation (User A cannot access User B's data)

## References

- FastAPI Async Documentation: https://fastapi.tiangolo.com/async/
- SQLModel Async Sessions: https://sqlmodel.tiangolo.com/tutorial/async/
- python-jose JWT: https://python-jose.readthedocs.io/
- Better Auth JWT Structure: Inferred from Better Auth documentation
- Neon Serverless PostgreSQL: Connection pooling and asyncpg compatibility
- Constitution Principle II: User Isolation Pattern (lines 133-148)

## Conclusion

All research tasks complete. No unresolved questions. Technology stack selected and justified. Ready to proceed to task generation (`/sp.tasks`).

**Status**: ✅ RESEARCH COMPLETE
