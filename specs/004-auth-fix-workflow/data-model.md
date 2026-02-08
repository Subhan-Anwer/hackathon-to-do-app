# Data Model: JWT Bearer Token Authentication Flow

**Feature**: `004-auth-fix-workflow`
**Date**: 2026-02-08
**Purpose**: Document authentication data flow and JWT token structure

## Overview

This document describes the data structures and authentication flow for JWT Bearer token transmission between Next.js frontend and FastAPI backend. Unlike traditional data models (database entities), this focuses on **authentication artifacts** and **request/response flows**.

## Authentication Artifacts

### 1. JWT Token Structure

**Format**: Standard JWT (JSON Web Token) with three parts: `header.payload.signature`

**Example**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImlhdCI6MTcwNzM5NjAwMCwiZXhwIjoxNzA3NDgyNDAwfQ.signature_hash
```

**Decoded Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Decoded Payload** (Better Auth format):
```json
{
  "sub": "user_abc123",           // User ID (primary claim for backend)
  "email": "user@example.com",    // User email
  "iat": 1707396000,              // Issued at timestamp
  "exp": 1708000800               // Expiry timestamp (7 days from iat)
}
```

**Key Claims**:
- `sub` (Subject): User ID - **CRITICAL** for user isolation
- `email`: User email address
- `iat` (Issued At): Token creation timestamp
- `exp` (Expiry): Token expiration timestamp (7 days default)

**Signature**: HMAC SHA-256 hash using `BETTER_AUTH_SECRET`

**Validation**:
- Backend verifies signature using shared `BETTER_AUTH_SECRET`
- Checks `exp` claim to reject expired tokens
- Extracts `sub` claim for user_id (used in all database queries)

**Source**: Better Auth JWT plugin (configured in `frontend/lib/auth.ts`)

---

### 2. Better Auth Session Object

**Returned by**: `auth.api.getSession()` in Next.js Server Components/Actions

**Structure**:
```typescript
type BetterAuthSession = {
  user: {
    id: string;           // User ID (matches JWT "sub" claim)
    name: string | null;
    email: string;
    role: string | null;
    image: string | null;
  };
  session: {
    id: string;           // Session ID (not used for API auth)
    userId: string;       // Reference to user.id
    expiresAt: Date;      // Session expiration
  };
} | null;
```

**Usage in Server Actions**:
```typescript
const session = await auth.api.getSession({
  headers: await headers()
});

if (!session) {
  throw new Error("Unauthorized");
}

const userId = session.user.id;  // Use for API calls
```

**Null Case**: If user not authenticated, `getSession()` returns `null`

---

### 3. JWT Token Extraction (set-auth-jwt Header)

**Method**: Extract from `set-auth-jwt` response header when calling `getSession()`

**Implementation**:
```typescript
const session = await auth.api.getSession({
  headers: await headers(),
  fetchOptions: {
    onSuccess: (ctx) => {
      const jwt = ctx.response.headers.get("set-auth-jwt");
      return jwt;  // Use for Authorization: Bearer <token>
    }
  }
});
```

**Header Name**: `set-auth-jwt`

**Header Value**: Raw JWT token string (without "Bearer " prefix)

**Fallback**: If `set-auth-jwt` header missing, call `GET /api/auth/token` endpoint

---

### 4. Authorization Header

**Format**: `Authorization: Bearer <token>`

**Example**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Composition**:
- Prefix: `Bearer ` (with trailing space)
- Token: Raw JWT string from `set-auth-jwt` header

**Usage in fetch**:
```typescript
fetch(`${API_URL}/api/${userId}/tasks`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${jwtToken}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify(taskData)
});
```

**Backend Extraction** (in `dependencies.py`):
```python
auth_header = request.headers.get("Authorization")
if auth_header and auth_header.startswith("Bearer "):
    token = auth_header.split(" ")[1]
```

---

## Authentication Flow Diagrams

### Current Flow (Cookie-Based) - BROKEN in Development

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User signs in via Better Auth                               │
│    POST /api/auth/sign-in/email                                │
│    Better Auth generates JWT and stores in httpOnly cookie     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Browser stores session cookie                               │
│    Cookie: session=<jwt-token>; HttpOnly; SameSite=lax         │
│    Domain: localhost:3000                                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. User creates task via client component                      │
│    taskApi.create(userId, taskData)                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Client-side fetch to backend                                │
│    fetch("http://localhost:8000/api/{userId}/tasks", {         │
│      method: "POST",                                            │
│      credentials: "include",  // ❌ Attempts to send cookie    │
│      body: JSON.stringify(taskData)                            │
│    })                                                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Browser blocks cookie (cross-origin)                        │
│    ❌ Cookie NOT sent (localhost:3000 ≠ localhost:8000)        │
│    ❌ Request arrives without Authorization header             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Backend dependency: get_current_user                        │
│    auth_header = None (no Authorization header)                │
│    token = request.cookies.get("session")  # None (blocked)    │
│    ❌ HTTPException(401, "Not authenticated - missing token")  │
└─────────────────────────────────────────────────────────────────┘
```

**Problem**: Browsers block cookies on cross-origin requests (different ports = different origins in development).

---

### New Flow (Bearer Token) - FIXES Development + Production

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User signs in via Better Auth                               │
│    POST /api/auth/sign-in/email                                │
│    Better Auth generates JWT and stores in httpOnly cookie     │
│    (Cookie still used for Better Auth's own endpoints)         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. User creates task via client component                      │
│    createTask(userId, taskData)  // Server Action             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Server Action: createTask (frontend/app/actions/tasks.ts)  │
│    "use server";                                                │
│    const session = await auth.api.getSession({                 │
│      headers: await headers(),                                  │
│      fetchOptions: {                                            │
│        onSuccess: (ctx) => {                                    │
│          jwt = ctx.response.headers.get("set-auth-jwt")        │
│        }                                                         │
│      }                                                           │
│    })                                                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Server Action extracts JWT token                            │
│    ✅ jwt = "eyJhbGc..." (from set-auth-jwt header)            │
│    ✅ userId = session.user.id                                 │
│    ✅ Verify userId matches function parameter (security)      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Server Action calls backend with Bearer token              │
│    fetch("http://localhost:8000/api/{userId}/tasks", {         │
│      method: "POST",                                            │
│      headers: {                                                 │
│        "Authorization": `Bearer ${jwt}`,  // ✅ JWT included   │
│        "Content-Type": "application/json"                      │
│      },                                                          │
│      body: JSON.stringify(taskData)                            │
│    })                                                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Backend dependency: get_current_user                        │
│    auth_header = "Bearer eyJhbGc..."                           │
│    token = auth_header.split(" ")[1]  // ✅ JWT extracted     │
│    payload = jwt.decode(token, BETTER_AUTH_SECRET, HS256)     │
│    user_id = payload.get("sub")  // ✅ user_abc123            │
│    return user_id  // ✅ Request authenticated                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Backend task endpoint: create_task                         │
│    if user_id != current_user_id:                              │
│      raise HTTPException(403)  // User isolation check         │
│                                                                 │
│    task = Task(user_id=user_id, title=..., description=...)   │
│    db.add(task)                                                │
│    await db.commit()                                            │
│    ✅ return TaskRead.model_validate(task)                     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Server Action returns task to client                       │
│    return createdTask  // Serialized by Next.js               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. Client component receives task                             │
│    const newTask = await createTask(userId, taskData)         │
│    setTasks([...tasks, newTask])  // Optimistic UI update     │
│    ✅ toast.success("Task created successfully!")             │
└─────────────────────────────────────────────────────────────────┘
```

**Key Improvements**:
1. ✅ No reliance on cross-origin cookies
2. ✅ Explicit JWT transmission via Authorization header
3. ✅ Works in both development (different ports) and production (same origin)
4. ✅ Server Actions provide server-side security (JWT extraction not exposed to client)
5. ✅ Backend unchanged (already supports Bearer token authentication)

---

## Error Handling Flow

### Scenario 1: Missing JWT Token

```
Server Action: createTask
  ├─> auth.api.getSession() returns null
  ├─> throw new Error("Unauthorized")
  └─> Client catches error
       └─> toast.error("Session expired. Please log in again.")
       └─> redirect("/login")
```

### Scenario 2: set-auth-jwt Header Missing

```
Server Action: createTask
  ├─> auth.api.getSession() succeeds
  ├─> fetchOptions.onSuccess callback
  ├─> ctx.response.headers.get("set-auth-jwt") returns null
  └─> Fallback: call GET /api/auth/token endpoint
       ├─> Success: Use token from response
       └─> Failure: throw new Error("Failed to retrieve JWT token")
```

### Scenario 3: Invalid/Expired JWT Token

```
Backend: get_current_user dependency
  ├─> Extract token from Authorization header
  ├─> jwt.decode(token, BETTER_AUTH_SECRET)
  ├─> JWTError raised (signature invalid or token expired)
  └─> HTTPException(401, "Invalid token - verification failed")
       └─> Frontend receives 401 response
            └─> toast.error("Session expired. Please log in again.")
            └─> redirect("/login")
```

### Scenario 4: User ID Mismatch (Security Violation)

```
Server Action: createTask(userId, taskData)
  ├─> session = await auth.api.getSession()
  ├─> if (userId !== session.user.id)
  └─> throw new Error("User ID mismatch - security violation")
       └─> Client catches error
            └─> toast.error("Security error. Please refresh and try again.")
            └─> redirect("/tasks")
```

---

## Data Validation

### JWT Token Validation (Backend)

**Validation Steps** (in `dependencies.py:68-88`):

1. **Extract token** from Authorization header or cookie
   - Fail if neither present → 401 "Not authenticated - missing token"

2. **Decode JWT** with BETTER_AUTH_SECRET
   - Fail if signature invalid → 401 "Invalid token - verification failed"
   - Fail if token expired → 401 "Invalid token - verification failed"

3. **Extract user_id** from "sub" claim
   - Fail if "sub" claim missing → 401 "Invalid token - missing user_id"

4. **Return user_id** for use in endpoint dependencies

**Algorithm**: HS256 (HMAC SHA-256)

**Secret**: `BETTER_AUTH_SECRET` environment variable (must match frontend)

### Session Validation (Frontend)

**Validation Steps** (in Server Actions):

1. **Call getSession()** to verify active session
   - Fail if session null → throw Error("Unauthorized")

2. **Extract JWT** from set-auth-jwt header
   - Warn if header missing → fallback to /api/auth/token endpoint

3. **Verify userId** matches session.user.id
   - Fail if mismatch → throw Error("User ID mismatch")

4. **Use JWT** for Authorization header in backend requests

---

## Security Model

### Threat Model

**Threats Mitigated**:
1. ✅ **Cross-Origin Cookie Blocking**: Bearer token bypasses browser cookie policies
2. ✅ **XSS (Cross-Site Scripting)**: JWT extracted server-side, not exposed to client JavaScript
3. ✅ **CSRF (Cross-Site Request Forgery)**: No cookies sent cross-origin, explicit Authorization header
4. ✅ **User Data Leakage**: Backend enforces user_id filtering on all queries

**Threats NOT Mitigated** (out of scope):
- ⚠️ Token replay attacks (would require token expiry + refresh mechanism)
- ⚠️ Man-in-the-middle (MITM) in development HTTP (production HTTPS mitigates)

### Defense in Depth

**Layer 1: Frontend Validation** (Server Actions)
- Verify session exists before making backend call
- Verify userId matches authenticated user
- Fail early with user-friendly error messages

**Layer 2: Backend JWT Verification** (Middleware)
- Verify JWT signature with shared secret
- Check token expiration
- Extract user_id from "sub" claim

**Layer 3: Backend User Isolation** (Endpoint Logic)
- Verify path user_id matches authenticated user_id
- Filter all database queries by user_id
- Return 403 on user_id mismatch

**Constitution Alignment**: Implements Principle II (User Isolation and Security First)

---

## Environment Configuration

### Required Environment Variables

**Frontend** (`.env.local`):
```
BETTER_AUTH_SECRET="<32-char-secret>"  # MUST match backend
BETTER_AUTH_URL="http://localhost:3000"
DATABASE_URL="postgresql://..."
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

**Backend** (`.env`):
```
BETTER_AUTH_SECRET="<32-char-secret>"  # MUST match frontend
DATABASE_URL="postgresql://..."
FRONTEND_ORIGIN="http://localhost:3000"
```

**Secret Generation**:
```bash
openssl rand -base64 32
```

**Validation** (startup checks):
- Frontend: Throws error if BETTER_AUTH_SECRET < 32 chars
- Backend: Throws error if BETTER_AUTH_SECRET < 32 chars
- Both: Log warning if secrets don't match (detectable by JWT validation failures)

---

## Related Documents

- [Specification](./spec.md) - Feature requirements (FR-001 to FR-017)
- [Research](./research.md) - Better Auth JWT extraction methods
- [Plan](./plan.md) - Implementation strategy
- [Backend Dependencies](../../backend/dependencies.py) - JWT verification code
- [Frontend Auth Config](../../frontend/lib/auth.ts) - Better Auth configuration

---

**Status**: Phase 1 Complete - Data model documented, ready for quickstart guide and contracts.
