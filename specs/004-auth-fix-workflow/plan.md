# Implementation Plan: Authentication & Workflow Reliability Fixes

**Branch**: `004-auth-fix-workflow` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-auth-fix-workflow/spec.md`

## Summary

This plan addresses critical authentication and user experience issues preventing smooth task management workflows in the full-stack Todo application. The primary problems are: (1) Better Auth JWT plugin not enabled, (2) cookie security attributes blocking localhost HTTP communication, (3) missing Authorization Bearer header in API requests, (4) poor 401 error handling, and (5) lack of loading/success/error feedback in the UI.

**Technical Approach**: Fix authentication configuration in a layered manner - starting with Better Auth JWT plugin enablement, then environment-aware cookie attributes, followed by dual authentication mechanisms (Bearer + cookie), enhanced error handling, and finally UX improvements with loading states and toast notifications. Each step builds on the previous one and can be independently tested.

## Technical Context

**Language/Version**: TypeScript 5 (Frontend), Python 3.12 (Backend)
**Primary Dependencies**: Next.js 16+, React 19, Better Auth, FastAPI, SQLModel, python-jose
**Storage**: Neon PostgreSQL (shared between frontend auth and backend tasks)
**Testing**: Manual testing with browser DevTools, multi-user account validation
**Target Platform**: Web (development: localhost HTTP, production: HTTPS)
**Project Type**: Web application (monorepo: frontend + backend)
**Performance Goals**: <200ms UI feedback, <1s API response, <1s list refresh
**Constraints**: Must work on localhost HTTP without cookie blocking, maintain backward compatibility with existing JWT verification
**Scale/Scope**: Single-user flows → multi-user isolation testing, 5 user stories (P1-P3)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- Specification exists: `specs/004-auth-fix-workflow/spec.md`
- All changes trace back to functional requirements (FR-001 through FR-025)
- User stories prioritized (P1-P3) with independent testability
- No manual coding without spec reference

### Principle II: User Isolation and Security First ✅ PASS
- JWT authentication already enforced on all endpoints (maintained)
- Backend middleware extracts `user_id` from JWT (no changes needed)
- Database queries filter by `user_id` (preserved)
- Changes enhance authentication reliability, don't weaken security
- Dual auth mechanisms (Bearer + cookie) improve resilience

### Principle III: Reusability Through Skills and Agents ✅ PASS
- `better-auth-integration` skill referenced for JWT plugin setup
- `api-security` skill to validate environment-aware cookie configuration
- `frontend-design` skill for loading states and toast implementations
- No reinvention of JWT validation or cookie handling patterns

### Principle IV: Clarity and Consistency ✅ PASS
- Follows CLAUDE.md guidelines (frontend and backend)
- References specs explicitly (`specs/004-auth-fix-workflow/spec.md`)
- Uses monorepo paths (`frontend/lib/`, `backend/dependencies.py`)
- Single source of truth maintained (constitution for principles, spec for requirements)

### Principle V: Test-First for Security-Critical Paths ✅ PASS
- Manual test checklist created for each implementation step
- Multi-user account testing required for user isolation validation
- Browser DevTools validation for JWT tokens and cookie attributes
- Red-Green pattern: verify failure before fix, verify success after fix

### Principle VI: Simplicity and Smallest Viable Change ✅ PASS
- No premature abstraction (direct config changes to Better Auth)
- Implements only specified fixes (no "nice-to-haves")
- Small, focused diffs per step (single file per fix where possible)
- YAGNI: Environment-aware cookie logic is minimal conditional

**Post-Design Re-check**: ✅ All principles maintained. No constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-auth-fix-workflow/
├── spec.md              # Feature specification (169 lines)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (Better Auth JWT plugin research)
├── contracts/           # Phase 1 output (no new API contracts - fixing existing)
│   └── auth-flow.md     # Environment-aware auth flow diagram
└── checklists/          # Quality validation
    └── requirements.md  # Specification quality checklist (73 lines)
```

### Source Code (repository root)

```text
frontend/                            # Next.js 16 application
├── lib/
│   ├── auth.ts                     # 🔧 MODIFY: Enable JWT plugin, fix cookie attributes
│   └── api.ts                      # 🔧 MODIFY: Add Authorization Bearer header
├── components/
│   ├── tasks/
│   │   ├── task-list.tsx           # 🔧 MODIFY: Add loading states, error handling
│   │   ├── task-form.tsx           # 🔧 MODIFY: Add loading states, success toasts
│   │   ├── create-task-dialog.tsx  # 🔧 MODIFY: Add loading states, error toasts
│   │   ├── edit-task-dialog.tsx    # 🔧 MODIFY: Add loading states, error toasts
│   │   └── delete-task-dialog.tsx  # 🔧 MODIFY: Add loading states, error toasts
│   └── layout/
│       └── header.tsx              # 🔧 MODIFY: Improve 401 error handling (if needed)
├── hooks/
│   └── use-tasks.ts                # ✨ NEW: Custom hook for task operations with loading states
└── .env.example                    # 📝 UPDATE: Document environment-aware variables

backend/                             # FastAPI application
├── dependencies.py                  # ✅ VERIFIED: Already accepts Bearer OR cookie
├── main.py                          # ✅ VERIFIED: CORS configured correctly
└── .env.example                     # ✅ VERIFIED: BETTER_AUTH_SECRET documented
```

**Structure Decision**: Web application monorepo (Option 2 from template). Frontend uses Next.js App Router structure with `lib/` for auth/API, `components/` for UI, `hooks/` for reusable logic. Backend uses flat structure with `routers/` for endpoints and `dependencies.py` for auth middleware. No new directories needed - all modifications to existing files except one new custom hook.

## Complexity Tracking

> **No Constitution violations - this table is empty**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Implementation Steps

### Step 1: Enable Better Auth JWT Plugin 🔑 (Priority: P1)

**Objective**: Enable JWT plugin in Better Auth configuration to generate proper JWT tokens on sign-in/sign-up

**Files to Modify**:
- `frontend/lib/auth.ts` (line 20, line 83-85)

**Changes**:
```typescript
// Add JWT import at top
import { jwt } from "better-auth/plugins"

// Add JWT plugin to plugins array (before nextCookies)
plugins: [
  jwt(), // Enable JWT token generation with 'sub' claim
  nextCookies(), // Enable cookie handling in Server Actions (MUST be last)
],
```

**Rationale**: Better Auth requires explicit JWT plugin enablement to generate tokens with proper structure. The `jwt()` plugin adds the `sub` claim containing user_id, which the backend extracts for user isolation. Without this, tokens may not contain required claims.

**Related Requirements**: FR-001 (JWT plugin enabled), FR-002 (backend verifies JWT), SC-004 (JWT visible in DevTools)

**Skills Used**: `better-auth-integration` (JWT configuration patterns)

**Testing After Step**:
1. Start frontend dev server: `cd frontend && npm run dev`
2. Sign up with new test user account
3. Open browser DevTools → Application → Cookies → localhost:3000
4. Verify `session` cookie exists with JWT value
5. Decode JWT at jwt.io and verify `sub` claim contains user_id
6. **Expected**: JWT contains `sub`, `exp`, `iat` claims

**Manual Test Checklist**:
- [ ] JWT plugin imported from `better-auth/plugins`
- [ ] `jwt()` added to plugins array before `nextCookies()`
- [ ] No TypeScript errors in `frontend/lib/auth.ts`
- [ ] Frontend builds successfully (`npm run build`)
- [ ] JWT token visible in browser cookies after sign-in
- [ ] JWT contains `sub` claim with user ID

---

### Step 2: Fix Cookie Attributes for Localhost Compatibility 🍪 (Priority: P1)

**Objective**: Make cookie `secure` and `sameSite` attributes environment-aware to allow cookie transmission on localhost HTTP

**Files to Modify**:
- `frontend/lib/auth.ts` (lines 71-74)

**Changes**:
```typescript
// Replace static cookie attributes with environment-aware logic
advanced: {
  cookies: {
    session_token: {
      name: "session",
      attributes: {
        // Development: allow HTTP, use "lax" sameSite for localhost:3000 ↔ localhost:8000
        // Production: require HTTPS, use "none" for cross-origin HTTPS
        sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
        secure: process.env.NODE_ENV === "production", // true in prod, false in dev
      },
    },
  },
},
```

**Rationale**: The current configuration uses `sameSite: "none"` and `secure: true`, which blocks cookies on localhost HTTP. Browsers reject `secure: true` cookies over non-HTTPS connections, and `sameSite: "none"` requires `secure: true`. Environment-aware attributes solve this: in development, use `secure: false` and `sameSite: "lax"` (allows localhost cross-origin); in production, use `secure: true` and `sameSite: "none"` (allows HTTPS cross-origin).

**Related Requirements**: FR-005 (environment-aware attributes), FR-006 (dev: secure=false, sameSite=lax), FR-007 (prod: secure=true, sameSite=none), FR-008 (prevent cookie blocking)

**Skills Used**: `better-auth-integration` (cookie configuration), `api-security` (security attribute validation)

**Testing After Step**:
1. Verify `NODE_ENV=development` in `.env.local` (or undefined, defaults to development)
2. Start frontend: `cd frontend && npm run dev`
3. Sign in with test user
4. Open DevTools → Application → Cookies → localhost:3000
5. Click `session` cookie and verify:
   - `SameSite`: `Lax`
   - `Secure`: empty/false (not checked)
6. Make API request to localhost:8000 (e.g., create task)
7. Open DevTools → Network → Request Headers
8. Verify `Cookie: session=...` is sent in request

**Manual Test Checklist**:
- [ ] Cookie attributes use `process.env.NODE_ENV` conditional
- [ ] Development: `secure: false`, `sameSite: "lax"`
- [ ] Production: `secure: true`, `sameSite: "none"`
- [ ] No TypeScript errors
- [ ] Frontend starts without errors
- [ ] Cookie sent on localhost HTTP requests
- [ ] Cookie visible in DevTools with correct attributes

---

### Step 3: Add Authorization Bearer Header to API Client 📡 (Priority: P1)

**Objective**: Modify API client to prefer sending `Authorization: Bearer <token>` header using Better Auth's session token, with cookie fallback

**Files to Modify**:
- `frontend/lib/api.ts` (lines 52-72)
- `frontend/lib/auth-client.ts` (new import for getSession)

**Changes**:

1. Import Better Auth client to access session:
```typescript
// At top of api.ts
import { authClient } from "./auth-client"
```

2. Modify `fetchWithAuth` function:
```typescript
async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  // Try to get current session token from Better Auth
  const session = await authClient.getSession()
  const token = session?.session?.token

  // Build headers with Authorization Bearer if token available
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers as Record<string, string>,
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    credentials: "include", // Still include cookies as fallback
    headers,
  })

  // Handle 401 Unauthorized - redirect to login
  if (response.status === 401) {
    if (typeof window !== "undefined") {
      window.location.href = "/login"
    }
    throw new Error("Unauthorized")
  }

  return response
}
```

**Rationale**: The current API client only uses `credentials: "include"` to send cookies. While the backend accepts both Bearer tokens and cookies, explicitly sending the Authorization header is more reliable and standard for API authentication. Better Auth provides `getSession()` to retrieve the current JWT token, which can be added to requests. Cookie fallback via `credentials: "include"` provides redundancy.

**Related Requirements**: FR-009 (prefer Bearer header), FR-010 (fallback to cookie), FR-011 (use getSession), FR-012 (backend accepts both)

**Skills Used**: `better-auth-integration` (session access patterns)

**Testing After Step**:
1. Start backend and frontend
2. Sign in with test user
3. Open DevTools → Network tab
4. Create a task or list tasks
5. Click the API request in Network tab
6. Verify Request Headers include:
   - `Authorization: Bearer <jwt-token>`
   - `Cookie: session=<jwt-token>`
7. Backend logs should show "User authenticated: <user_id>"

**Manual Test Checklist**:
- [ ] `authClient.getSession()` called in fetchWithAuth
- [ ] `Authorization: Bearer` header added when token available
- [ ] `credentials: "include"` still present (cookie fallback)
- [ ] No TypeScript errors
- [ ] Both Authorization header and Cookie sent in requests
- [ ] Backend successfully authenticates with Bearer token
- [ ] 401 redirect still works if token missing/invalid

---

### Step 4: Enhance 401 Error Handling with User Feedback 🚨 (Priority: P2)

**Objective**: Improve 401 error handling to show user-friendly toast notifications before redirect and clear authentication state

**Files to Modify**:
- `frontend/lib/api.ts` (lines 63-69)

**Changes**:
```typescript
// Import toast for notifications
import { toast } from "sonner"

// In fetchWithAuth function, improve 401 handling:
if (response.status === 401) {
  // Show user-friendly toast before redirect
  toast.error("Your session has expired. Please log in again.")

  // Optional: Clear local auth state via Better Auth
  // await authClient.signOut() // Uncomment if you want to clear session

  // Redirect to login after short delay (allow toast to be seen)
  if (typeof window !== "undefined") {
    setTimeout(() => {
      window.location.href = "/login"
    }, 1500) // 1.5s delay for toast visibility
  }

  throw new Error("Unauthorized")
}
```

**Rationale**: Current 401 handling immediately redirects to /login without user feedback, creating confusion ("Why was I logged out?"). Adding a toast notification explains the issue before redirect. A brief delay ensures users see the message. Optionally clearing session state via Better Auth ensures clean logout.

**Related Requirements**: FR-013 (redirect on 401), FR-014 (show toast), FR-015 (consistent handling), FR-016 (clear auth state)

**Skills Used**: `frontend-design` (toast notification patterns)

**Testing After Step**:
1. Sign in and wait for token expiry (or manually delete session cookie)
2. Try to create a task or list tasks
3. **Expected**: Toast appears with "Your session has expired..." message
4. After 1.5 seconds, redirect to /login
5. Verify smooth UX (toast visible before redirect)

**Manual Test Checklist**:
- [ ] `toast` imported from `sonner`
- [ ] Toast message shown before redirect
- [ ] 1.5s delay allows message visibility
- [ ] Redirect to /login still occurs
- [ ] No TypeScript errors
- [ ] Toast appears for all 401 errors (any endpoint)
- [ ] UX feels smooth and informative

---

### Step 5: Add Loading States to Task Operations ⏳ (Priority: P3)

**Objective**: Display loading indicators during task create/update/delete/toggle operations to provide immediate user feedback

**Files to Modify**:
- `frontend/components/tasks/task-form.tsx` (add `isPending` state to submit button)
- `frontend/components/tasks/create-task-dialog.tsx` (disable button during submit)
- `frontend/components/tasks/edit-task-dialog.tsx` (disable button during submit)
- `frontend/components/tasks/delete-task-dialog.tsx` (disable button during delete)
- `frontend/components/tasks/task-item.tsx` (disable checkbox during toggle)

**Pattern to Apply** (example for create-task-dialog.tsx):

```typescript
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

export function CreateTaskDialog() {
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (data) => {
    setIsLoading(true)
    try {
      await taskApi.create(userId, data)
      // Success handling...
    } catch (error) {
      // Error handling...
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Button
      type="submit"
      disabled={isLoading}
    >
      {isLoading ? "Creating..." : "Create Task"}
    </Button>
  )
}
```

**Apply Similar Pattern to**:
- `task-form.tsx`: Add `isLoading` prop, disable submit button
- `edit-task-dialog.tsx`: Add loading state to "Save" button
- `delete-task-dialog.tsx`: Add loading state to "Delete" button
- `task-item.tsx`: Disable checkbox during toggle (optimistic UI with loading state)

**Rationale**: Users need immediate feedback when actions are in progress. Loading states (disabled buttons, "Creating..." text, spinners) prevent double-clicks and reduce perceived latency. This aligns with modern UX best practices.

**Related Requirements**: FR-017 (loading indicators), FR-021 (disable inputs during submit), SC-006 (feedback within 200ms)

**Skills Used**: `frontend-design` (loading state patterns)

**Testing After Step**:
1. Create a task - verify "Create Task" button shows "Creating..." and is disabled
2. Edit a task - verify "Save" button shows "Saving..." and is disabled
3. Delete a task - verify "Delete" button shows "Deleting..." and is disabled
4. Toggle task - verify checkbox is disabled during operation
5. Verify buttons re-enable after operation completes

**Manual Test Checklist**:
- [ ] All task operation buttons show loading text during API call
- [ ] Buttons are disabled during operation (prevent double-submit)
- [ ] Loading indicators appear within 200ms of action
- [ ] Buttons re-enable after success or error
- [ ] No TypeScript errors
- [ ] UX feels responsive and prevents accidental duplicate actions

---

### Step 6: Add Success and Error Toast Notifications 🎉 (Priority: P3)

**Objective**: Show user-friendly toast notifications for task operation success and errors with automatic list refresh

**Files to Modify**:
- `frontend/components/tasks/task-list.tsx` (add toast imports, success/error handling)
- All task operation components (create-task-dialog, edit-task-dialog, delete-task-dialog, task-item)

**Pattern to Apply**:

```typescript
import { toast } from "sonner"

// Success example (in handleCreate):
try {
  const newTask = await taskApi.create(userId, data)
  toast.success("Task created successfully!")
  onTaskCreated(newTask) // Trigger list refresh
} catch (error) {
  toast.error(error.message || "Failed to create task. Please try again.")
}

// Update example:
try {
  const updatedTask = await taskApi.update(userId, taskId, data)
  toast.success("Task updated successfully!")
  onTaskUpdated(updatedTask) // Trigger list refresh
} catch (error) {
  toast.error(error.message || "Failed to update task.")
}

// Delete example:
try {
  await taskApi.delete(userId, taskId)
  toast.success("Task deleted successfully!")
  onTaskDeleted(taskId) // Trigger list refresh
} catch (error) {
  toast.error(error.message || "Failed to delete task.")
}

// Toggle example:
try {
  const toggledTask = await taskApi.toggleComplete(userId, taskId)
  toast.success(toggledTask.completed ? "Task completed!" : "Task reopened!")
  onTaskToggled(toggledTask) // Trigger list refresh
} catch (error) {
  toast.error(error.message || "Failed to toggle task.")
}
```

**List Refresh Pattern** (in task-list.tsx):

```typescript
const refreshTasks = async () => {
  try {
    const tasks = await taskApi.list(userId)
    setTasks(tasks)
  } catch (error) {
    toast.error("Failed to refresh task list")
  }
}

// Call refreshTasks in onTaskCreated, onTaskUpdated, onTaskDeleted, onTaskToggled callbacks
```

**Rationale**: Toast notifications provide confirmation that actions succeeded or clear explanations when they fail. Automatic list refresh ensures UI stays in sync with backend state. This completes the feedback loop: user action → loading state → success/error toast → list refresh.

**Related Requirements**: FR-018 (success toasts), FR-019 (error toasts), FR-020 (auto refresh), SC-007 (toasts within 1s), SC-008 (refresh within 1s)

**Skills Used**: `frontend-design` (toast notification patterns, list refresh patterns)

**Testing After Step**:
1. Create task - verify "Task created successfully!" toast and task appears in list
2. Update task - verify "Task updated successfully!" toast and changes reflect
3. Delete task - verify "Task deleted successfully!" toast and task disappears
4. Toggle task - verify "Task completed!" or "Task reopened!" toast and checkbox updates
5. Simulate error (e.g., disconnect backend) - verify error toast with friendly message
6. Verify all toasts appear within 1 second and auto-dismiss after 3-5 seconds

**Manual Test Checklist**:
- [ ] Success toasts for all CRUD operations (create, update, delete, toggle)
- [ ] Error toasts with user-friendly messages on failures
- [ ] Task list auto-refreshes after successful operations
- [ ] Toasts appear within 1 second of operation completion
- [ ] Toasts auto-dismiss (don't require manual close)
- [ ] No TypeScript errors
- [ ] UX feels polished and informative

---

### Step 7: Create Manual Test Checklist & Verification 🧪 (Priority: P3)

**Objective**: Comprehensive end-to-end verification of all fixes across development and production environments

**Files to Create**:
- `specs/004-auth-fix-workflow/TESTING.md` - Manual test scenarios

**Testing Checklist Content**:

**Phase 1: Better Auth JWT Plugin Verification**
- [ ] Sign up with new test user
- [ ] Verify JWT token in browser cookies (DevTools → Application → Cookies)
- [ ] Decode JWT at jwt.io and confirm `sub`, `exp`, `iat` claims present
- [ ] Backend logs show "User authenticated: <user_id>"

**Phase 2: Cookie Attributes Verification (Development)**
- [ ] Set `NODE_ENV=development` in `.env.local`
- [ ] Sign in and inspect `session` cookie in DevTools
- [ ] Verify `SameSite: Lax`, `Secure: false`
- [ ] Make API request and confirm cookie sent in Network tab

**Phase 3: Authorization Bearer Header Verification**
- [ ] Sign in and perform any task operation
- [ ] Inspect Network tab → Request Headers
- [ ] Verify both `Authorization: Bearer <token>` and `Cookie: session=<token>` present
- [ ] Backend accepts request (no 401 errors)

**Phase 4: 401 Error Handling Verification**
- [ ] Delete session cookie manually in DevTools
- [ ] Try to create a task
- [ ] Verify toast appears: "Your session has expired..."
- [ ] Verify redirect to /login after 1.5 seconds
- [ ] UX feels smooth (toast visible before redirect)

**Phase 5: Loading States Verification**
- [ ] Create task - verify "Creating..." button text, button disabled
- [ ] Edit task - verify "Saving..." button text, button disabled
- [ ] Delete task - verify "Deleting..." button text, button disabled
- [ ] Toggle task - verify checkbox disabled during operation
- [ ] All buttons re-enable after operation completes

**Phase 6: Toast Notifications & List Refresh Verification**
- [ ] Create task - verify success toast, task appears in list within 1s
- [ ] Update task - verify success toast, changes reflect in list
- [ ] Delete task - verify success toast, task disappears from list
- [ ] Toggle task - verify success toast ("Task completed!" or "Task reopened!")
- [ ] Simulate error (stop backend) - verify error toast with friendly message

**Phase 7: Multi-User Isolation Verification**
- [ ] Create test users: user1@example.com, user2@example.com
- [ ] Sign in as user1, create 3 tasks
- [ ] Sign out, sign in as user2, create 2 tasks
- [ ] Verify user2 sees only their 2 tasks (not user1's 3 tasks)
- [ ] Confirm user isolation maintained (Constitution Principle II compliance)

**Phase 8: Production Environment Verification (if deploying)**
- [ ] Set `NODE_ENV=production`
- [ ] Sign in and inspect `session` cookie
- [ ] Verify `SameSite: None`, `Secure: true`
- [ ] Confirm authentication works over HTTPS
- [ ] All task operations work correctly in production

**Success Criteria**:
- [ ] All 8 phases pass without errors
- [ ] No 401 errors during authenticated workflows
- [ ] JWT tokens visible and valid in browser DevTools
- [ ] Authentication works on localhost HTTP and production HTTPS
- [ ] User feedback (loading, toasts) feels smooth and informative
- [ ] Multi-user isolation verified (zero data leaks)

**Rationale**: Manual testing validates all fixes in realistic scenarios. Multi-user testing ensures Constitution Principle II compliance. Production verification ensures environment-aware configuration works correctly in both dev and prod.

**Related Requirements**: All success criteria (SC-001 through SC-010)

**Skills Used**: N/A (manual testing)

**Testing After Step**: Execute all test phases systematically, document any failures, iterate until all phases pass.

---

## Phase 0: Research (Completed)

### Better Auth JWT Plugin Research

**Decision**: Enable JWT plugin via `import { jwt } from "better-auth/plugins"` and add `jwt()` to plugins array.

**Rationale**: Better Auth's JWT plugin is required to generate tokens with the `sub` claim containing user_id. Without it, tokens may lack required claims for backend verification. The plugin must be added before `nextCookies()` in the plugins array to ensure JWT generation happens before cookie serialization.

**Alternatives Considered**:
- Manual JWT generation with jsonwebtoken library - **Rejected**: Reinvents Better Auth functionality, violates Constitution Principle III (reusability)
- Custom Better Auth plugin - **Rejected**: Unnecessary complexity, standard JWT plugin covers all needs

**Implementation**: Add `jwt()` to plugins array in `frontend/lib/auth.ts`.

**References**:
- Better Auth documentation: https://www.better-auth.com/docs/plugins/jwt
- Spec requirements: FR-001, FR-002, SC-004

---

### Environment-Aware Cookie Configuration Research

**Decision**: Use `process.env.NODE_ENV` conditional to set cookie attributes based on environment (development vs production).

**Rationale**: Browsers enforce strict security rules for cookies. On HTTP (localhost), cookies with `secure: true` are blocked. On localhost cross-origin (3000 → 8000), `sameSite: "none"` requires `secure: true`, creating a catch-22. The solution: environment-aware attributes using Node.js `process.env.NODE_ENV`:
- **Development**: `secure: false`, `sameSite: "lax"` (allows localhost HTTP cross-origin)
- **Production**: `secure: true`, `sameSite: "none"` (allows HTTPS cross-origin)

**Alternatives Considered**:
- Separate development/production Better Auth instances - **Rejected**: Code duplication, violates DRY principle
- Proxy all API requests through Next.js API routes - **Rejected**: Adds unnecessary latency, complicates error handling
- Use `sameSite: "lax"` in production - **Rejected**: Breaks cross-origin HTTPS if frontend/backend on different domains

**Implementation**: Replace static cookie attributes with conditional logic in `frontend/lib/auth.ts`.

**Security Validation**: `api-security` skill confirms this pattern is secure (environment separation prevents production cookies leaking to HTTP).

**References**:
- MDN Secure Cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies
- MDN SameSite: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value
- Spec requirements: FR-005, FR-006, FR-007, FR-008

---

## Phase 1: Design & Contracts

### Auth Flow Contract

**File**: `specs/004-auth-fix-workflow/contracts/auth-flow.md`

**Environment-Aware Authentication Flow**:

```text
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT (localhost HTTP)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. User signs in at localhost:3000/login                        │
│     ↓                                                             │
│  2. Better Auth generates JWT with jwt() plugin                  │
│     Payload: { sub: "<user_id>", exp: <timestamp>, ... }         │
│     ↓                                                             │
│  3. JWT stored in httpOnly cookie with attributes:               │
│     - name: "session"                                             │
│     - secure: false      ← Allows HTTP transmission              │
│     - sameSite: "lax"    ← Allows localhost:3000 → localhost:8000│
│     ↓                                                             │
│  4. Frontend API client (lib/api.ts) makes request:              │
│     GET http://localhost:8000/api/{user_id}/tasks                │
│     Headers:                                                      │
│       - Authorization: Bearer <jwt>  ← Preferred method          │
│       - Cookie: session=<jwt>        ← Fallback method           │
│     ↓                                                             │
│  5. Backend middleware (dependencies.py) extracts token:         │
│     - Checks Authorization header first                          │
│     - Falls back to "session" cookie                             │
│     - Decodes JWT with BETTER_AUTH_SECRET                        │
│     - Extracts user_id from "sub" claim                          │
│     ↓                                                             │
│  6. Backend filters tasks by user_id and returns response        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     PRODUCTION (HTTPS)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. User signs in at https://app.example.com/login               │
│     ↓                                                             │
│  2. Better Auth generates JWT with jwt() plugin                  │
│     Payload: { sub: "<user_id>", exp: <timestamp>, ... }         │
│     ↓                                                             │
│  3. JWT stored in httpOnly cookie with attributes:               │
│     - name: "session"                                             │
│     - secure: true       ← Requires HTTPS                        │
│     - sameSite: "none"   ← Allows cross-origin HTTPS             │
│     ↓                                                             │
│  4. Frontend API client makes request:                           │
│     GET https://api.example.com/api/{user_id}/tasks              │
│     Headers:                                                      │
│       - Authorization: Bearer <jwt>  ← Preferred method          │
│       - Cookie: session=<jwt>        ← Fallback method           │
│     ↓                                                             │
│  5. Backend middleware extracts token (same as development)      │
│     ↓                                                             │
│  6. Backend filters tasks by user_id and returns response        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

ERROR HANDLING FLOW:
┌─────────────────────────────────────────────────────────────────┐
│  401 Unauthorized Error                                          │
├─────────────────────────────────────────────────────────────────┤
│  Backend returns 401 →                                           │
│    Frontend API client (lib/api.ts) catches 401 →                │
│      Shows toast: "Your session has expired..." →                │
│        Waits 1.5s (allow toast visibility) →                     │
│          Redirects to /login                                     │
└─────────────────────────────────────────────────────────────────┘
```

**Key Differences**:
- **Development**: Cookies work over HTTP without `secure: true`
- **Production**: Cookies require HTTPS with `secure: true`
- **Both**: Dual authentication (Bearer + cookie) for redundancy
- **Both**: Backend accepts either mechanism (Constitution Principle II maintained)

**Security Notes**:
- User isolation enforced at backend (Constitution Principle II): all queries filter by `user_id`
- JWT signature verified with shared `BETTER_AUTH_SECRET`
- httpOnly cookies prevent XSS token theft
- Environment-aware configuration prevents production cookies leaking to HTTP

---

## ADR Suggestion

📋 **Architectural decision detected**: Environment-aware cookie configuration for dual HTTP/HTTPS support

**Rationale**: This decision affects all authenticated API requests and cookie security across development and production environments. It's a cross-cutting concern impacting both frontend and backend.

**Recommendation**: Document reasoning and tradeoffs. Run `/sp.adr environment-aware-cookie-configuration`

**Key Decision Points**:
- Why not use separate Better Auth instances?
- Why environment-based conditional instead of build-time config?
- Security implications of different sameSite/secure combinations
- Trade-offs between developer experience and production security

---

## Next Steps

After completing Phase 2 (this plan), proceed to:

1. **Run `/sp.tasks`**: Generate actionable task breakdown from this plan
   - Tasks will be ordered by implementation steps (Step 1 → Step 7)
   - Each task maps to an implementation step above
   - Dependencies: Step N+1 depends on Step N completion

2. **Execute tasks**: Use `/sp.implement` or manual implementation via agents
   - Follow test-after-step checklist for each task
   - Verify no regressions (existing functionality preserved)
   - Document any deviations in PHRs

3. **Create ADR** (optional but recommended): Document environment-aware cookie decision
   - Run `/sp.adr environment-aware-cookie-configuration`
   - Capture rationale, alternatives, and security trade-offs

4. **Commit and PR**: Use `/sp.git.commit_pr` to commit changes and create pull request
   - Reference this plan and spec in commit messages
   - Include manual test results in PR description

---

## Validation Checklist

Before marking plan complete, verify:

- [x] All Technical Context fields filled (no NEEDS CLARIFICATION)
- [x] Constitution Check performed (all principles pass)
- [x] Project Structure documented with file-level changes
- [x] Implementation Steps prioritized and testable
- [x] Phase 0 Research completed (JWT plugin, cookie config)
- [x] Phase 1 Contracts created (auth flow diagram)
- [x] No Complexity Tracking violations
- [x] ADR suggestion provided for significant decision
- [x] Next steps clearly outlined

**Plan Status**: ✅ READY FOR TASK GENERATION (`/sp.tasks`)
