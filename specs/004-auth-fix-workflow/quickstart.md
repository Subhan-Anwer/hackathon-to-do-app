# Quickstart: JWT Bearer Token Authentication Testing

**Feature**: `004-auth-fix-workflow`
**Date**: 2026-02-08
**Purpose**: Quick reference guide for developers to test JWT Bearer token authentication

## Prerequisites

✅ Frontend running on `localhost:3000`
✅ Backend running on `localhost:8000`
✅ `.env.local` (frontend) and `.env` (backend) configured with matching `BETTER_AUTH_SECRET`
✅ User account created (sign up at http://localhost:3000/signup)

## Quick Test Checklist

### 1. Verify JWT Plugin Enabled

**Check** `frontend/lib/auth.ts`:

```typescript
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  // ...
  plugins: [
    jwt(),  // ✅ Must be present
    nextCookies()
  ],
});
```

**Expected**: JWT plugin listed in plugins array.

---

### 2. Test JWT Token Extraction

**Run** in Next.js Server Component or Server Action:

```typescript
// frontend/app/test-jwt/page.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export default async function TestJWTPage() {
  let jwtToken: string | null = null;

  const session = await auth.api.getSession({
    headers: await headers(),
    fetchOptions: {
      onSuccess: (ctx) => {
        jwtToken = ctx.response.headers.get("set-auth-jwt");
      }
    }
  });

  if (!session) {
    return <div>Not authenticated. Please log in.</div>;
  }

  return (
    <div>
      <h1>JWT Token Test</h1>
      <p><strong>User ID:</strong> {session.user.id}</p>
      <p><strong>Email:</strong> {session.user.email}</p>
      <p><strong>JWT Token:</strong> {jwtToken ? "✅ Found" : "❌ Missing"}</p>
      {jwtToken && (
        <pre style={{ fontSize: "10px", overflow: "auto" }}>
          {jwtToken}
        </pre>
      )}
    </div>
  );
}
```

**Expected Output**:
- User ID: `user_abc123` (or similar)
- Email: Your registered email
- JWT Token: ✅ Found
- Token preview: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**If JWT Token shows "❌ Missing"**:
1. Check that `jwt()` plugin is enabled in `lib/auth.ts`
2. Verify `BETTER_AUTH_SECRET` is set in `.env.local`
3. Try logging out and logging back in

---

### 3. Test Server Action with Bearer Token

**Create** `frontend/app/actions/test-auth.ts`:

```typescript
"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function testBearerAuth() {
  let jwtToken: string | null = null;

  const session = await auth.api.getSession({
    headers: await headers(),
    fetchOptions: {
      onSuccess: (ctx) => {
        jwtToken = ctx.response.headers.get("set-auth-jwt");
      }
    }
  });

  if (!session) {
    throw new Error("Not authenticated");
  }

  if (!jwtToken) {
    throw new Error("Failed to extract JWT token");
  }

  // Test backend authentication with Bearer token
  const response = await fetch(`${API_BASE_URL}/api/${session.user.id}/tasks`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${jwtToken}`,
      "Content-Type": "application/json"
    }
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Backend returned ${response.status}: ${error}`);
  }

  const tasks = await response.json();
  return {
    status: "success",
    userId: session.user.id,
    taskCount: tasks.length,
    message: "✅ Bearer token authentication working!"
  };
}
```

**Call** from client component:

```typescript
"use client";

import { testBearerAuth } from "@/app/actions/test-auth";
import { useState } from "react";

export function TestAuthButton() {
  const [result, setResult] = useState<string | null>(null);

  async function handleTest() {
    try {
      const data = await testBearerAuth();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  return (
    <div>
      <button onClick={handleTest}>Test Bearer Auth</button>
      {result && <pre>{result}</pre>}
    </div>
  );
}
```

**Expected Output**:
```json
{
  "status": "success",
  "userId": "user_abc123",
  "taskCount": 5,
  "message": "✅ Bearer token authentication working!"
}
```

**If you get 401 Unauthorized**:
1. Check backend logs for JWT validation errors
2. Verify `BETTER_AUTH_SECRET` matches in both frontend and backend
3. Check that Authorization header is formatted correctly: `Bearer <token>` (with space)

---

### 4. Verify Backend Receives Bearer Token

**Check** backend logs when making a request:

```bash
cd backend
uv run uvicorn main:app --reload --log-level=info
```

**Expected Log Output**:
```
INFO:dependencies:User authenticated: user_abc123
INFO:routers.tasks:Listed 5 tasks for user user_abc123
```

**If you see**:
```
WARNING:dependencies:Authentication failed: No token provided
```

Then the Authorization header is not being sent. Check Server Action implementation.

---

### 5. Test Task Creation with Bearer Token

**Create** a task using Server Action:

```typescript
// frontend/app/actions/tasks.ts
"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import type { Task, TaskCreateInput } from "@/types/task";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createTask(userId: string, data: TaskCreateInput): Promise<Task> {
  let jwtToken: string | null = null;

  const session = await auth.api.getSession({
    headers: await headers(),
    fetchOptions: {
      onSuccess: (ctx) => {
        jwtToken = ctx.response.headers.get("set-auth-jwt");
      }
    }
  });

  if (!session) {
    throw new Error("Unauthorized - please log in");
  }

  if (userId !== session.user.id) {
    throw new Error("User ID mismatch - security violation");
  }

  if (!jwtToken) {
    throw new Error("Failed to retrieve JWT token");
  }

  const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${jwtToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create task");
  }

  return await response.json();
}
```

**Call** from component:

```typescript
"use client";

import { createTask } from "@/app/actions/tasks";
import { useSession } from "@/lib/auth-client";

export function TaskForm() {
  const { data: session } = useSession();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    try {
      const newTask = await createTask(session!.user.id, {
        title: formData.get("title") as string,
        description: formData.get("description") as string
      });

      console.log("✅ Task created:", newTask);
    } catch (error) {
      console.error("❌ Error:", error);
    }
  }

  if (!session) return null;

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" placeholder="Task title" required />
      <textarea name="description" placeholder="Description" />
      <button type="submit">Create Task</button>
    </form>
  );
}
```

**Expected Behavior**:
1. Fill out form and submit
2. Check browser DevTools → Network tab
3. Find request to `http://localhost:8000/api/{userId}/tasks`
4. Verify **Request Headers** include: `Authorization: Bearer eyJhbGc...`
5. Check **Response** status: `201 Created`
6. Console log: `✅ Task created: { id: "...", title: "...", ... }`

---

## Browser DevTools Verification

### Network Tab Inspection

**Steps**:
1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Filter by `Fetch/XHR`
4. Create a task or perform any task operation
5. Click on the request to `http://localhost:8000/api/{userId}/tasks`
6. Go to **Headers** sub-tab

**Verify Request Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**If Authorization header is missing**:
- Check that you're calling a Server Action, not direct fetch from client
- Verify JWT token extraction in Server Action
- Check console for errors

**Verify Response**:
- Status: `201 Created` (for POST) or `200 OK` (for GET/PUT/PATCH)
- Body: JSON task object

**If Status is 401 Unauthorized**:
- Backend couldn't validate JWT
- Check `BETTER_AUTH_SECRET` matches in both environments
- Check backend logs for specific error

---

### Console Logging for Debugging

**Add to Server Action**:

```typescript
export async function createTask(userId: string, data: TaskCreateInput) {
  console.log("🔍 [Server Action] Starting createTask");

  const session = await auth.api.getSession({
    headers: await headers(),
    fetchOptions: {
      onSuccess: (ctx) => {
        const jwt = ctx.response.headers.get("set-auth-jwt");
        console.log("🔑 [Server Action] JWT extracted:", jwt ? "✅ Found" : "❌ Missing");
        jwtToken = jwt;
      }
    }
  });

  console.log("👤 [Server Action] Session:", session ? "✅ Authenticated" : "❌ Not authenticated");
  console.log("🆔 [Server Action] User ID:", session?.user.id);

  // ... rest of code
}
```

**Expected Console Output**:
```
🔍 [Server Action] Starting createTask
🔑 [Server Action] JWT extracted: ✅ Found
👤 [Server Action] Session: ✅ Authenticated
🆔 [Server Action] User ID: user_abc123
```

---

## Common Issues & Solutions

### Issue 1: "Failed to extract JWT token"

**Symptoms**:
- Error message: `Failed to retrieve JWT token`
- `jwtToken` is `null` after `getSession()`

**Solutions**:
1. **Verify JWT plugin enabled** in `lib/auth.ts`:
   ```typescript
   import { jwt } from "better-auth/plugins";
   plugins: [jwt(), nextCookies()]
   ```

2. **Check Better Auth version** (must support `set-auth-jwt` header):
   ```bash
   npm list better-auth
   ```
   Upgrade if version < 1.0.0

3. **Fallback to token endpoint**:
   ```typescript
   if (!jwtToken) {
     const tokenResponse = await fetch("http://localhost:3000/api/auth/token", {
       headers: { Cookie: `session=${session_cookie}` }
     });
     jwtToken = (await tokenResponse.json()).token;
   }
   ```

---

### Issue 2: "401 Unauthorized" from Backend

**Symptoms**:
- Request reaches backend
- Backend returns `401 Unauthorized`
- Backend log: `WARNING:dependencies:Authentication failed`

**Solutions**:
1. **Check BETTER_AUTH_SECRET matches**:
   ```bash
   # Frontend
   cat frontend/.env.local | grep BETTER_AUTH_SECRET

   # Backend
   cat backend/.env | grep BETTER_AUTH_SECRET
   ```
   Values MUST be identical.

2. **Verify Authorization header format**:
   - Correct: `Authorization: Bearer eyJhbGc...`
   - Incorrect: `Authorization: eyJhbGc...` (missing "Bearer ")
   - Incorrect: `Authorization: Bearer  eyJhbGc...` (two spaces)

3. **Check JWT token validity**:
   Decode at https://jwt.io/ and verify:
   - `alg`: `HS256`
   - `sub`: Contains user ID
   - `exp`: Not expired

---

### Issue 3: "User ID mismatch - security violation"

**Symptoms**:
- Error thrown in Server Action
- `userId !== session.user.id`

**Solution**:
- Verify you're passing the correct `userId` to Server Action
- Should match authenticated user's ID from session
- Example:
  ```typescript
  // ✅ Correct
  const session = await auth.api.getSession(...);
  await createTask(session.user.id, taskData);

  // ❌ Incorrect
  await createTask("some-other-user-id", taskData);
  ```

---

### Issue 4: CORS Error in Browser Console

**Symptoms**:
- Error: `Access to fetch at 'http://localhost:8000/api/...' has been blocked by CORS policy`

**Solutions**:
1. **Check backend CORS configuration** (`main.py`):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],  # Must include frontend origin
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
       allow_headers=["*"]  # Must allow Authorization header
   )
   ```

2. **Verify FRONTEND_ORIGIN environment variable**:
   ```bash
   cat backend/.env | grep FRONTEND_ORIGIN
   # Should be: FRONTEND_ORIGIN=http://localhost:3000
   ```

---

## Testing Checklist

Before marking feature complete, verify:

- [ ] JWT plugin enabled in `frontend/lib/auth.ts`
- [ ] `BETTER_AUTH_SECRET` matches in frontend and backend `.env` files
- [ ] `auth.api.getSession()` returns non-null session after login
- [ ] `set-auth-jwt` header present in getSession response
- [ ] Server Actions successfully extract JWT token
- [ ] Backend receives `Authorization: Bearer <token>` header (verify in DevTools)
- [ ] Backend logs show successful authentication (`User authenticated: {user_id}`)
- [ ] Task creation returns `201 Created` (not `401 Unauthorized`)
- [ ] All task operations work (list, create, update, delete, toggleComplete)
- [ ] httpOnly cookies still enabled (verify in DevTools → Application → Cookies)
- [ ] Multi-user isolation: User A cannot access User B's tasks

---

## Quick curl Test (Backend Direct)

**Extract JWT from frontend first**, then test backend directly:

```bash
# 1. Get JWT token from frontend (copy from TestJWTPage or DevTools)
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USER_ID="user_abc123"

# 2. Test GET /api/{user_id}/tasks
curl -X GET \
  "http://localhost:8000/api/${USER_ID}/tasks" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json"

# Expected: JSON array of tasks

# 3. Test POST /api/{user_id}/tasks
curl -X POST \
  "http://localhost:8000/api/${USER_ID}/tasks" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task from curl","description":"Testing Bearer auth"}'

# Expected: 201 Created with task JSON

# 4. Test without Authorization header (should fail)
curl -X GET "http://localhost:8000/api/${USER_ID}/tasks"

# Expected: 401 Unauthorized {"detail":"Not authenticated - missing token"}
```

---

## Related Documents

- [Specification](./spec.md) - Feature requirements and success criteria
- [Data Model](./data-model.md) - Authentication flow diagrams
- [Research](./research.md) - Better Auth JWT extraction methods
- [Backend Tests](../../backend/tests/test_auth.py) - Existing JWT validation tests

---

**Next Steps**: After verifying all checks pass, proceed to `/sp.tasks` to generate implementation tasks.
