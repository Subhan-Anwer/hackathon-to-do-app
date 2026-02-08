# Research: JWT Bearer Token Authentication Fix

**Feature**: `004-auth-fix-workflow`
**Date**: 2026-02-08
**Researchers**: Claude Code (Context7 MCP + Code Analysis)

## Executive Summary

**Problem**: Frontend task operations fail with 401 Unauthorized because JWT tokens are sent via httpOnly cookies, which browsers block on cross-origin requests (localhost:3000 → localhost:8000 in development).

**Solution**: Extract JWT token from Better Auth session server-side and include it in `Authorization: Bearer <token>` header for all backend API requests. Backend already supports Bearer token authentication (fallback implemented).

**Key Finding**: Better Auth provides JWT tokens in two ways:
1. **Response header** (`set-auth-jwt`) when calling `getSession()` - **RECOMMENDED**
2. **Endpoint** (`GET /api/auth/token`) for explicit token retrieval

## Research Tasks Completed

### 1. Better Auth JWT Token Extraction Methods

**Research Question**: How do we extract the JWT token from Better Auth session in Next.js Server Components or Server Actions?

**Finding**: Better Auth JWT plugin provides multiple extraction methods:

#### Method 1: From `set-auth-jwt` Response Header (RECOMMENDED)

```typescript
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

const session = await auth.api.getSession({
  headers: await headers(),
  fetchOptions: {
    onSuccess: (ctx) => {
      const jwt = ctx.response.headers.get("set-auth-jwt");
      // Use jwt for Authorization: Bearer <token>
    }
  }
});
```

**Advantages**:
- Single call gets both session AND token
- No additional API roundtrip
- Built-in to Better Auth JWT plugin
- Works in Server Components and Server Actions

**Source**: [Better Auth JWT Plugin Documentation](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx)

#### Method 2: From `/api/auth/token` Endpoint

```typescript
// GET /api/auth/token
// Returns: { "token": "ey..." }
```

**Advantages**:
- Explicit token retrieval
- Can be called independently

**Disadvantages**:
- Extra API call required
- Need existing session first
- More network overhead

### 2. Better Auth Session Object Structure

**Research Question**: What properties are available in the session object returned by `getSession()`?

**Finding**: Session object contains two main properties:

```typescript
type Session = {
  user: {
    id: string;           // User ID (same as JWT "sub" claim)
    name: string | null;
    email: string;
    role: string | null;
    image: string | null;
    // Additional custom fields from plugins
  };
  session: {
    id: string;           // Session ID
    userId: string;       // Reference to user.id
    expiresAt: Date;      // Session expiration
    // Additional custom fields
  };
}
```

**Usage in Server Component**:

```typescript
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export default async function Page() {
  const session = await auth.api.getSession({
    headers: await headers()
  });

  if (!session) {
    redirect("/login");
  }

  // Access user data
  const userId = session.user.id;  // Use for API calls
  const email = session.user.email;

  return <div>Welcome, {session.user.name}!</div>;
}
```

**Source**: [Better Auth Session Management](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/concepts/session-management.mdx)

### 3. Backend JWT Verification Support

**Research Question**: Does the FastAPI backend already support Authorization Bearer header authentication?

**Finding**: **YES** - Backend already implements dual authentication support:

```python
# backend/dependencies.py (lines 51-59)
async def get_current_user(request: Request) -> str:
    # Try Authorization header first (Bearer token)
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to cookie (Better Auth httpOnly cookie)
        token = request.cookies.get("session")

    # ... JWT validation with BETTER_AUTH_SECRET
```

**Key Points**:
- ✅ Already reads `Authorization` header
- ✅ Falls back to `session` cookie if no header
- ✅ Uses same `BETTER_AUTH_SECRET` for validation
- ✅ Extracts `user_id` from JWT "sub" claim
- ✅ No backend changes required

**Source**: `backend/dependencies.py:25-89`

### 4. Next.js Server-Side API Proxy Patterns

**Research Question**: What's the best pattern for adding Authorization headers to frontend API requests?

**Finding**: Three viable patterns for Next.js 16+ App Router:

#### Pattern A: Server Actions (RECOMMENDED)

```typescript
// app/actions/tasks.ts
"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function createTask(userId: string, data: TaskCreateInput) {
  const session = await auth.api.getSession({
    headers: await headers(),
    fetchOptions: {
      onSuccess: (ctx) => {
        const jwt = ctx.response.headers.get("set-auth-jwt");
        // Make backend call with Authorization header
        fetch(`${API_URL}/api/${userId}/tasks`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${jwt}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        });
      }
    }
  });
}
```

**Advantages**:
- Built-in to Next.js 16
- Type-safe with TypeScript
- Automatic serialization
- Works with React 19 useTransition/useOptimistic

#### Pattern B: API Routes

```typescript
// app/api/tasks/route.ts
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function POST(request: Request) {
  const session = await auth.api.getSession({
    headers: await headers()
  });

  if (!session) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Extract JWT and forward to backend
  // ...
}
```

**Advantages**:
- RESTful pattern
- Can be called from client components
- Familiar to developers

**Disadvantages**:
- More boilerplate
- Extra server roundtrip

#### Pattern C: Route Handlers (Combined with Server Actions)

Hybrid approach using Server Actions for mutations and Route Handlers for queries.

### 5. Current Frontend Implementation Analysis

**Research Question**: What's the current frontend authentication implementation?

**Finding**: Frontend currently uses cookie-based authentication:

```typescript
// frontend/lib/api.ts (lines 61-74)
async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const response = await fetch(url, {
    ...options,
    credentials: "include", // Sends httpOnly session cookie
    headers: {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    },
  });

  // Handles 401 with redirect to /login
  // ...
}
```

**Current Setup**:
- ✅ Better Auth configured with JWT plugin (`frontend/lib/auth.ts`)
- ✅ Session cookie named "session" (matches backend expectation)
- ✅ 401 error handling with toast + redirect
- ❌ No Authorization header included
- ❌ Relies on cross-origin cookie transmission (fails in development)

**Files to Modify**:
- `frontend/lib/api.ts` - Replace cookie-based auth with Bearer token
- `frontend/app/actions/tasks.ts` - Create Server Actions for task operations (NEW FILE)
- `frontend/components/tasks/*` - Update to call Server Actions instead of direct API calls

## Technology Decisions

### Decision 1: Use Server Actions for Task Operations

**Selected Option**: Next.js Server Actions (Pattern A)

**Rationale**:
- Built-in to Next.js 16 (no additional dependencies)
- Type-safe with TypeScript
- Works seamlessly with React 19 features (useTransition, useOptimistic)
- Simpler than API Routes (less boilerplate)
- Better developer experience
- Matches modern Next.js best practices

**Alternatives Considered**:
- ❌ API Routes: More boilerplate, extra roundtrip
- ❌ Client-side fetch with token in localStorage: Security risk (XSS vulnerability)

**References**:
- [Next.js 16 Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
- Constitution Principle VI: Simplicity and Smallest Viable Change

### Decision 2: Extract JWT from `set-auth-jwt` Header

**Selected Option**: Use `set-auth-jwt` response header from `getSession()`

**Rationale**:
- Single API call gets both session validation AND JWT token
- No extra network roundtrip
- Built-in to Better Auth JWT plugin
- Recommended by Better Auth documentation
- Reduces latency compared to separate `/api/auth/token` call

**Alternatives Considered**:
- ❌ Separate `/api/auth/token` call: Extra network roundtrip
- ❌ Access session.token property: Not exposed in session object structure

**References**:
- [Better Auth JWT Plugin - set-auth-jwt Header](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx)

### Decision 3: Keep Cookie-Based Auth as Fallback (Backend)

**Selected Option**: Maintain dual authentication support in backend (Bearer header + cookie)

**Rationale**:
- Backend already implements this pattern
- Provides backward compatibility
- No breaking changes required
- Follows defense-in-depth security principle
- Spec requirement FR-015: Keep httpOnly cookies enabled

**Alternatives Considered**:
- ❌ Remove cookie support: Breaking change, violates spec requirement
- ❌ Bearer token only: Loses httpOnly cookie security benefits

## Best Practices Identified

### Next.js 16 Server Actions

**Pattern**: Progressive enhancement with Server Actions

```typescript
// app/actions/tasks.ts
"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function createTask(formData: FormData) {
  // Validate session
  const session = await auth.api.getSession({
    headers: await headers()
  });

  if (!session) {
    throw new Error("Unauthorized");
  }

  // Extract form data
  const title = formData.get("title") as string;
  const description = formData.get("description") as string;

  // Validate inputs
  if (!title || title.length > 200) {
    throw new Error("Invalid title");
  }

  // Make backend API call with Bearer token
  // ...
}
```

**Benefits**:
- Works without JavaScript (progressive enhancement)
- Automatic request deduplication
- Built-in error handling
- Type-safe with zod validation

**Source**: [Next.js Server Actions Documentation](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)

### Error Handling for JWT Extraction

**Pattern**: Graceful fallback when JWT header is missing

```typescript
const session = await auth.api.getSession({
  headers: await headers(),
  fetchOptions: {
    onSuccess: (ctx) => {
      const jwt = ctx.response.headers.get("set-auth-jwt");

      if (!jwt) {
        // Fallback: Try explicit token endpoint
        // OR redirect to login
        throw new Error("Failed to retrieve JWT token");
      }

      return jwt;
    }
  }
});
```

**Rationale**:
- Handles edge cases (token generation failure)
- Provides clear error messages
- Prevents silent failures
- Aligns with spec FR-014: Clear authentication error feedback

### User Isolation Verification

**Pattern**: Verify user_id consistency between session and API call

```typescript
export async function createTask(userId: string, data: TaskCreateInput) {
  const session = await auth.api.getSession({
    headers: await headers()
  });

  if (!session) {
    throw new Error("Unauthorized");
  }

  // Verify userId matches authenticated user
  if (userId !== session.user.id) {
    throw new Error("User ID mismatch - security violation");
  }

  // Proceed with API call
  // ...
}
```

**Rationale**:
- Defense in depth (client-side + backend verification)
- Prevents user ID manipulation
- Aligns with Constitution Principle II: User Isolation and Security First

## Implementation Risks and Mitigations

### Risk 1: Better Auth Session Structure Changes

**Risk**: Better Auth may change session object structure in future versions, breaking JWT extraction.

**Mitigation**:
- Pin Better Auth version in `package.json`
- Add error handling for missing `set-auth-jwt` header
- Implement fallback to `/api/auth/token` endpoint
- Add TypeScript type checking for session properties

**Likelihood**: Low (Better Auth maintains backward compatibility)

### Risk 2: JWT Token Not Available in Response Header

**Risk**: Some Better Auth configurations may not include JWT in response headers.

**Mitigation**:
- Verify JWT plugin is enabled in `lib/auth.ts` (already done)
- Add explicit check for `set-auth-jwt` header presence
- Implement fallback to `/api/auth/token` endpoint
- Log warning if JWT extraction fails for debugging

**Likelihood**: Very Low (JWT plugin explicitly enabled in current config)

### Risk 3: Performance Impact of Server Actions

**Risk**: Server Actions may add latency compared to direct client-side fetch.

**Mitigation**:
- Measure baseline performance with browser DevTools
- Compare latency before/after implementation
- Use React 19 useTransition for UI responsiveness
- Implement optimistic updates for immediate feedback

**Likelihood**: Low (Server Actions are optimized by Next.js)

### Risk 4: CORS Issues with Authorization Header

**Risk**: Backend CORS configuration may block Authorization header.

**Mitigation**:
- Backend already allows `allow_headers=["*"]` (main.py:78)
- Authorization header is standard HTTP header (should not be blocked)
- Test in development environment before production

**Likelihood**: Very Low (backend CORS already permissive)

## Open Questions (RESOLVED)

All research questions from Technical Context have been resolved:

1. ✅ **How to extract JWT token from Better Auth session?**
   - Answer: Use `set-auth-jwt` response header from `getSession()`

2. ✅ **What Server Actions pattern works best for Next.js 16?**
   - Answer: Server Actions with `"use server"` directive + type-safe form handling

3. ✅ **Does backend support Authorization Bearer header?**
   - Answer: Yes, already implemented in `dependencies.py:51-59`

4. ✅ **Which session properties contain user_id?**
   - Answer: `session.user.id` contains the user ID

5. ✅ **What error handling is needed for JWT extraction?**
   - Answer: Check for `set-auth-jwt` header, fallback to `/api/auth/token`, log failures

## References

### Primary Sources

1. **Better Auth Documentation**
   - JWT Plugin: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx
   - Session Management: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/concepts/session-management.mdx
   - API Concepts: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/concepts/api.mdx

2. **Next.js 16 Documentation**
   - Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
   - App Router: https://nextjs.org/docs/app

3. **Codebase Analysis**
   - `frontend/lib/auth.ts`: Better Auth server configuration with JWT plugin
   - `frontend/lib/api.ts`: Current API client implementation
   - `backend/dependencies.py`: JWT verification middleware
   - `backend/routers/tasks.py`: Task endpoints with user isolation

### Secondary Sources

- Constitution Principle II: User Isolation and Security First
- Constitution Principle VI: Simplicity and Smallest Viable Change
- Spec FR-001 to FR-017: Functional requirements for JWT authentication
- Hackathon II PDF: JWT token transmission requirements

## Conclusion

All research tasks completed successfully. The solution path is clear:

1. **Frontend**: Create Server Actions that extract JWT from `set-auth-jwt` header
2. **API Client**: Add Authorization Bearer header to all backend requests
3. **Components**: Update to call Server Actions instead of direct fetch
4. **Backend**: No changes required (already supports Bearer tokens)

Implementation can proceed to Phase 1 (Design & Contracts).
