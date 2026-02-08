# API Contracts: JWT Bearer Token Authentication

**Feature**: `004-auth-fix-workflow`
**Date**: 2026-02-08

## Overview

This feature does **NOT** introduce new API contracts or modify existing backend endpoints. The backend API surface remains unchanged - only the **authentication method** changes from cookie-based to Bearer token.

## Existing API Contracts (UNCHANGED)

All task endpoints remain identical:

### Authentication Endpoint (Better Auth)

**Note**: Better Auth endpoints are managed by the Better Auth library, not by this feature.

```
POST /api/auth/sign-in/email
POST /api/auth/sign-up/email
POST /api/auth/sign-out
GET  /api/auth/session
GET  /api/auth/token  # NEW: Explicitly retrieve JWT token (fallback)
```

### Task Endpoints (FastAPI Backend)

```
GET    /api/{user_id}/tasks
POST   /api/{user_id}/tasks
GET    /api/{user_id}/tasks/{task_id}
PUT    /api/{user_id}/tasks/{task_id}
DELETE /api/{user_id}/tasks/{task_id}
PATCH  /api/{user_id}/tasks/{task_id}/complete
```

## Authentication Header Change

### Before (Cookie-Based)

**Request**:
```http
POST /api/user_abc123/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "title": "New task",
  "description": "Task description"
}
```

**Problem**: Cookie NOT sent on cross-origin requests (localhost:3000 → localhost:8000)

---

### After (Bearer Token)

**Request**:
```http
POST /api/user_abc123/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "title": "New task",
  "description": "Task description"
}
```

**Solution**: Authorization header works in all scenarios (development cross-origin + production same-origin)

---

## Backend API Contract Validation

### Request Headers (NEW Requirement)

**All task endpoints now expect**:

```http
Authorization: Bearer <jwt-token>
```

**OR** (fallback for backward compatibility):

```http
Cookie: session=<jwt-token>
```

**Backend Logic** (in `dependencies.py:get_current_user`):

```python
# Try Authorization header first (Bearer token)
auth_header = request.headers.get("Authorization")
token = None

if auth_header and auth_header.startswith("Bearer "):
    token = auth_header.split(" ")[1]
else:
    # Fallback to cookie (Better Auth httpOnly cookie)
    token = request.cookies.get("session")

if not token:
    raise HTTPException(401, "Not authenticated - missing token")
```

**Key Point**: Backend already implements this dual authentication support (no changes required).

---

## Response Contracts (UNCHANGED)

All response formats remain identical:

### Success Response: Create Task

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_abc123",
  "title": "New task",
  "description": "Task description",
  "is_completed": false,
  "created_at": "2026-02-08T10:30:00Z",
  "updated_at": "2026-02-08T10:30:00Z"
}
```

### Error Response: 401 Unauthorized

```json
{
  "detail": "Not authenticated - missing token"
}
```

### Error Response: 403 Forbidden

```json
{
  "detail": "Cannot access other users' tasks"
}
```

---

## Frontend API Contract (Server Actions)

**New Contract**: Server Actions replace direct fetch calls

### Before (Direct Fetch)

```typescript
// frontend/lib/api.ts
export const taskApi = {
  async create(userId: string, data: TaskCreateInput): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
      method: "POST",
      credentials: "include",  // Relies on cookie
      body: JSON.stringify(data),
    });
    return await response.json();
  }
};
```

**Called from client component**:
```typescript
const newTask = await taskApi.create(userId, taskData);
```

---

### After (Server Action)

```typescript
// frontend/app/actions/tasks.ts
"use server";

export async function createTask(userId: string, data: TaskCreateInput): Promise<Task> {
  const session = await auth.api.getSession({
    headers: await headers(),
    fetchOptions: {
      onSuccess: (ctx) => {
        jwtToken = ctx.response.headers.get("set-auth-jwt");
      }
    }
  });

  if (!session || !jwtToken) {
    throw new Error("Unauthorized");
  }

  const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${jwtToken}`,  // Bearer token
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data),
  });

  return await response.json();
}
```

**Called from client component**:
```typescript
const newTask = await createTask(userId, taskData);
```

**Key Difference**: Same function signature from component perspective, but Server Action adds Authorization header server-side.

---

## Contract Compatibility Matrix

| Scenario | Cookie Auth | Bearer Token | Backend Response |
|----------|-------------|--------------|------------------|
| Development (localhost:3000 → localhost:8000) | ❌ Cookie blocked | ✅ Header sent | 200/201 OK |
| Production (same origin) | ✅ Cookie sent | ✅ Header sent | 200/201 OK |
| Missing both cookie and header | ❌ 401 | ❌ 401 | 401 Unauthorized |
| Invalid/expired token | ❌ 401 | ❌ 401 | 401 Unauthorized |
| Valid token | ✅ 200/201 | ✅ 200/201 | 200/201 OK |

**Backward Compatibility**: ✅ Backend accepts both cookie and Bearer token (no breaking changes)

---

## OpenAPI Schema (UNCHANGED)

The backend OpenAPI schema (accessible at `http://localhost:8000/docs`) remains unchanged. Only the **authentication mechanism** changes:

**Before**:
```yaml
security:
  - cookieAuth: []
```

**After** (conceptually, not reflected in OpenAPI schema):
```yaml
security:
  - bearerAuth: []
  - cookieAuth: []  # Fallback
```

**Note**: FastAPI Swagger UI may require manual Bearer token entry in "Authorize" dialog.

---

## Testing Contract Compliance

### Manual Testing

1. **Sign in** at http://localhost:3000/login
2. **Open DevTools** → Network tab
3. **Create a task** via frontend UI
4. **Verify request** to `http://localhost:8000/api/{userId}/tasks`
5. **Check Request Headers**:
   ```
   Authorization: Bearer eyJhbGc...
   Content-Type: application/json
   ```
6. **Check Response**:
   ```
   Status: 201 Created
   Body: { "id": "...", "title": "...", ... }
   ```

### Automated Testing (Backend)

**Existing tests remain valid** (`backend/tests/test_auth.py`):

```python
def test_jwt_authentication_with_bearer_token():
    """Test that backend accepts Authorization: Bearer <token> header."""
    token = generate_jwt_token(user_id="user_123")
    response = client.get(
        "/api/user_123/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

**Key Point**: No new tests required - existing tests already validate Bearer token authentication.

---

## Contract Migration Path

### Phase 1: Add Bearer Token Support (THIS FEATURE)

- ✅ Frontend sends Authorization header via Server Actions
- ✅ Backend validates Bearer token (already implemented)
- ✅ Cookie authentication remains as fallback

### Phase 2: Deprecate Cookie Auth (FUTURE - OUT OF SCOPE)

- ⚠️ Remove cookie fallback from backend
- ⚠️ Update OpenAPI schema to require Bearer token only
- ⚠️ Breaking change notification to API consumers

**Note**: Phase 2 is intentionally out of scope. This feature maintains backward compatibility.

---

## Related Documents

- [Specification](../spec.md) - Feature requirements (FR-004 to FR-007: Authorization Header Implementation)
- [Data Model](../data-model.md) - Authentication flow diagrams
- [Quickstart](../quickstart.md) - Testing guide for Bearer token authentication
- [Backend API Docs](http://localhost:8000/docs) - Live OpenAPI documentation (when backend running)

---

**Summary**: No new API contracts introduced. Existing contracts unchanged. Only authentication method enhanced from cookie-only to Bearer token + cookie fallback.
