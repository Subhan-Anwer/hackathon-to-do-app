# Server Actions Authentication Pattern

**Last Updated**: 2026-02-08
**Feature**: JWT Bearer Token Authentication Fix (`004-auth-fix-workflow`)

## Overview

This document describes the Server Actions authentication pattern implemented to fix 401 Unauthorized errors when making API requests to the FastAPI backend.

## Problem Statement

The original implementation used cookie-based authentication, which failed on cross-origin requests (localhost:3000 → localhost:8000) due to browser security policies blocking httpOnly cookies on different ports.

## Solution: JWT Bearer Token Authentication

We implemented Next.js Server Actions that:

1. Extract JWT tokens from Better Auth session server-side
2. Include `Authorization: Bearer <token>` header in all backend requests
3. Work consistently in both development and production environments
4. Maintain httpOnly cookie security while solving cross-origin issues

## Architecture

```
┌─────────────────────┐
│  Client Component   │
│  (task-form.tsx)    │
└──────────┬──────────┘
           │ Calls
           ▼
┌─────────────────────┐
│   Server Action     │
│  (createTask)       │
│  app/actions/       │
│  tasks.ts           │
└──────────┬──────────┘
           │ 1. Extract JWT from Better Auth
           │ 2. Add Authorization header
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  localhost:8000     │
│  /api/{userId}/tasks│
└─────────────────────┘
```

## Implementation Details

### 1. Combined Authentication & JWT Token Generation

Server Actions use a single helper function that performs authentication and **generates JWT tokens manually**:

```typescript
// app/actions/tasks.ts
import { SignJWT } from "jose";

async function authenticateAndGetToken(userId: string): Promise<string> {
  // Step 1: Get session (single database call)
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    throw new Error("Unauthorized - please log in");
  }

  // Step 2: Verify userId matches authenticated user (security check)
  if (userId !== session.user.id) {
    throw new Error("User ID mismatch - security violation");
  }

  // Step 3: Generate JWT token manually (matches backend expectations)
  const secret = process.env.BETTER_AUTH_SECRET;

  const jwtToken = await new SignJWT({ sub: session.user.id })
    .setProtectedHeader({ alg: "HS256" }) // Algorithm matches backend
    .setIssuedAt()
    .setExpirationTime("7d") // 7-day expiry
    .sign(new TextEncoder().encode(secret));

  return jwtToken;
}
```

**Key Points:**
- **Manual JWT generation** - uses `jose` library (same as backend for validation)
- **HS256 algorithm** - matches backend `dependencies.py` JWT validation
- **BETTER_AUTH_SECRET** - shared secret for signing and verification
- **`sub` claim** - contains user_id for backend extraction
- **7-day expiry** - matches Better Auth session duration
- **Single database call** - combines authentication and token generation

**Why Manual Generation:**
- Better Auth JWT plugin doesn't expose JWT tokens server-side
- `session.session.token` is the session ID (32 chars), not a JWT (200+ chars)
- Manual generation ensures exact format match with backend expectations
- Full control over token claims and expiry

**Performance Benefits:**
- Single database call per Server Action (optimized for Neon serverless)
- Eliminates ETIMEDOUT errors (2-3s wake-up time)
- No additional HTTP requests or endpoints needed

### 2. API Request with Authorization Header

All Server Actions include the JWT token in the Authorization header:

```typescript
export async function createTask(
  userId: string,
  data: TaskCreateInput
): Promise<Task> {
  // Authenticate and get JWT token (single database call)
  const jwtToken = await authenticateAndGetToken(userId);

  // Call backend with Authorization header
  const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${jwtToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    await handleFetchError(response, "create task");
  }

  return await response.json();
}
```

**Key Points:**
- `Authorization: Bearer <token>` header format
- Server Action ensures token is always included
- Backend reads token from Authorization header (not cookie)
- Consolidated authentication and JWT extraction in single helper

### 3. Error Handling

Server Actions provide user-friendly error messages:

```typescript
async function handleFetchError(
  response: Response,
  operation: string
): Promise<never> {
  if (response.status === 401) {
    throw new Error("Unauthorized - please log in again");
  }

  try {
    const error = await response.json();
    throw new Error(error.detail || `Failed to ${operation}`);
  } catch {
    throw new Error(`Failed to ${operation} - ${response.statusText}`);
  }
}
```

**Error Flow:**
1. Server Action throws error with clear message
2. Component catches error and displays toast notification
3. User sees actionable feedback (e.g., "please log in again")

## Available Server Actions

All Server Actions are exported from `app/actions/tasks.ts`:

### Task Management

- `createTask(userId, data)` - Create new task
- `listTasks(userId)` - List all user's tasks
- `getTask(userId, taskId)` - Get single task by ID
- `updateTask(userId, taskId, data)` - Update existing task
- `deleteTask(userId, taskId)` - Delete task
- `toggleComplete(userId, taskId)` - Toggle task completion status

### Usage Example

```typescript
"use client";

import { createTask } from "@/app/actions/tasks";
import { useSession } from "@/lib/auth-client";
import { toast } from "sonner";

export function TaskForm() {
  const { data: session } = useSession();

  async function handleSubmit(formData: FormData) {
    try {
      const task = await createTask(session!.user.id, {
        title: formData.get("title") as string,
        description: formData.get("description") as string,
      });

      toast.success("Task created successfully!");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create task");
    }
  }

  return (
    <form action={handleSubmit}>
      <input name="title" required />
      <textarea name="description" />
      <button type="submit">Create Task</button>
    </form>
  );
}
```

## Migration from Old API Client

### Before (Cookie-Based - DEPRECATED)

```typescript
import { taskApi } from "@/lib/api";

// ❌ Old pattern - cookie-based authentication
const task = await taskApi.create(userId, { title, description });
```

### After (Server Actions - RECOMMENDED)

```typescript
import { createTask } from "@/app/actions/tasks";

// ✅ New pattern - JWT Bearer token authentication
const task = await createTask(userId, { title, description });
```

## Benefits of Server Actions Pattern

1. **Cross-Origin Support**: Works on localhost:3000 → localhost:8000 without cookie issues
2. **Security**: JWT tokens never exposed to client-side JavaScript
3. **Type Safety**: Full TypeScript support with type inference
4. **Simplicity**: No need for separate API client or middleware
5. **Production Ready**: Works in development and production without code changes
6. **Error Handling**: Built-in error handling with user-friendly messages
7. **User Isolation**: Triple verification (Server Action + Backend + Database)

## Environment Variables

Required environment variables in `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (MUST match backend .env)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# Better Auth URL
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Database URL (for Better Auth user management)
DATABASE_URL=postgresql://...
```

**Critical:**
- `BETTER_AUTH_SECRET` MUST be identical in frontend and backend
- Generate with: `openssl rand -base64 32`
- Minimum 32 characters required

## Testing

### Manual Test Checklist

1. **JWT Plugin Enabled**: Verify `jwt()` plugin in `lib/auth.ts`
2. **Environment Variables**: Confirm `BETTER_AUTH_SECRET` matches in frontend and backend
3. **Create Task**: Sign in, create a task, verify in DevTools Network tab:
   - Request includes `Authorization: Bearer <token>` header
   - Response status: `201 Created` (not `401 Unauthorized`)
4. **Backend Logs**: Check backend logs for "User authenticated: {user_id}" messages
5. **httpOnly Cookies**: Verify cookies still have `httpOnly: true` in DevTools → Application → Cookies
6. **Multi-User Isolation**: Create two accounts, verify User A cannot access User B's tasks

### Debugging

**Issue: "Failed to retrieve JWT token"**

1. Check `lib/auth.ts` has `jwt()` plugin enabled
2. Verify `BETTER_AUTH_SECRET` is set in `.env.local`
3. Try logging out and logging back in

**Issue: "401 Unauthorized" from backend**

1. Verify `BETTER_AUTH_SECRET` matches in frontend and backend
2. Check backend logs for specific JWT validation error
3. Decode JWT at https://jwt.io/ and verify `sub` claim contains user ID

**Issue: "User ID mismatch - security violation"**

1. Ensure you're passing the authenticated user's ID to Server Actions
2. Verify session is valid and contains correct `user.id`

## References

- **Specification**: `specs/004-auth-fix-workflow/spec.md`
- **Research**: `specs/004-auth-fix-workflow/research.md`
- **Quickstart Guide**: `specs/004-auth-fix-workflow/quickstart.md`
- **Better Auth JWT Plugin**: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/plugins/jwt.mdx
- **Next.js Server Actions**: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

## Future Considerations

1. **Token Refresh**: Implement automatic token refresh for long sessions
2. **Rate Limiting**: Add rate limiting to Server Actions to prevent abuse
3. **Caching**: Implement caching strategy for listTasks() to reduce API calls
4. **Optimistic Updates**: Enhance optimistic UI updates for all CRUD operations
5. **Error Recovery**: Add automatic retry logic for transient network failures

---

**Status**: ✅ Production Ready
**Migration**: All components migrated to Server Actions
**Old API Client**: Deprecated (see `lib/api.ts` for migration notes)
