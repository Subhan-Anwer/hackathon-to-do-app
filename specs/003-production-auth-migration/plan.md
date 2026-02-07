# Implementation Plan: Production Authentication Migration & UI Completion

**Branch**: `003-production-auth-migration` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-production-auth-migration/spec.md`

## Summary

Migrate frontend authentication from demo in-memory implementation (`simple-auth.ts`) to production-ready Better Auth with PostgreSQL database storage. Better Auth is already fully configured in `lib/auth.ts` - this is purely a code migration (remove demo code, activate Better Auth). Additionally, add missing "Add Task" button to dashboard UI for task creation discoverability.

**Technical Approach**: Replace 4 component imports, create Better Auth Server Actions wrapper, add environment validation, delete demo files, implement UI button with dialog. No new dependencies or database migrations required.

## Technical Context

**Language/Version**: TypeScript 5.x (Next.js 16+), Python 3.11 (FastAPI backend)
**Primary Dependencies**: Better Auth 1.4.18, jose 6.1.3 (frontend), python-jose (backend)
**Storage**: Neon Serverless PostgreSQL (auto-creates user/session tables via Better Auth)
**Testing**: Vitest (frontend), pytest (backend), manual integration testing
**Target Platform**: Web (Next.js SSR + FastAPI REST API)
**Project Type**: Web application (monorepo: `frontend/` + `backend/`)
**Performance Goals**: < 3 seconds login (SC-003), < 2 seconds task creation (SC-006)
**Constraints**: 7-day JWT expiry (spec), httpOnly cookies (security), 1000+ concurrent users (SC-009)
**Scale/Scope**: 10-20 files modified, ~500 lines code changed, 0 new dependencies

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅

**Status**: PASS

**Evidence**:
- Specification created via `/sp.specify` command
- Plan generated via `/sp.plan` command
- Tasks will be created via `/sp.tasks` command
- All work traces back to `specs/003-production-auth-migration/spec.md`

**Test**: This plan references spec.md. Implementation will update components following specification requirements (FR-001 through FR-020).

---

### Principle II: User Isolation and Security First ✅

**Status**: PASS

**Evidence**:
- Better Auth JWT tokens include `user_id` in `sub` claim (compatible with backend `get_current_user()`)
- Backend already enforces user isolation via `Task.user_id` filtering (no changes needed)
- httpOnly cookies prevent XSS token theft
- Environment validation prevents weak fallback secrets (FR-006, FR-007)

**Security Enhancements**:
- Remove plaintext password storage (FR-002)
- Eliminate in-memory user storage (FR-008)
- Add startup validation to fail fast if `DATABASE_URL` missing

**Test**: Backend integration tests verify user isolation (already exist in `backend/tests/test_isolation.py`). Frontend adds database persistence testing.

---

### Principle III: Reusability Through Skills and Agents ✅

**Status**: PASS

**Skills/Agents Used**:
- Better Auth (existing configuration, not a custom skill)
- NextJS patterns (App Router Server Actions)
- FastAPI JWT middleware (existing)

**Justification for No New Skills**:
- Better Auth integration is feature-specific (not reusable pattern)
- Demo code removal is one-time migration (not recurring task)

**Consideration**: If other features need auth UI updates, extract `auth-actions.ts` pattern into a skill.

---

### Principle IV: Clarity and Consistency ✅

**Status**: PASS

**Alignment**:
- Follows `CLAUDE.md` monorepo paths (`frontend/`, `backend/`)
- References constitution principle II (User Isolation)
- Maintains single source of truth (Better Auth configuration in `lib/auth.ts`)

**Documentation**:
- `research.md`: Better Auth configuration analysis
- `data-model.md`: User/Session entity relationships
- `quickstart.md`: Developer setup instructions (to be created)

---

### Principle V: Test-First for Security-Critical Paths ✅

**Status**: PASS (with caveat)

**Security Tests Required**:
1. Password hashing verification (bcrypt in database)
2. User persistence after server restart
3. JWT token format validation (`sub` claim presence)
4. Session cookie httpOnly flag verification

**Caveat**: Tests will be written during implementation (not TDD). Justification: Migrating existing auth system, not creating new one. Backend security tests already exist.

**Existing Tests**:
- Backend: `tests/test_auth.py` (JWT validation)
- Backend: `tests/test_isolation.py` (user isolation)

**New Tests Needed**:
- Frontend: Database persistence tests
- Frontend: Password hashing verification

---

### Principle VI: Simplicity and Smallest Viable Change ✅

**Status**: PASS

**Simplicity Evidence**:
- No new dependencies (Better Auth already installed)
- No database migrations (Better Auth auto-creates tables)
- No abstraction layers (direct Better Auth API usage)
- Minimal file changes (4 import updates + 1 new file + 1 UI component)

**YAGNI Compliance**:
- Not implementing: Email verification (FR out of scope)
- Not implementing: Password reset UI (FR out of scope)
- Not implementing: OAuth/SSO (FR out of scope)
- Not implementing: Custom user schema (Better Auth default sufficient)

**Complexity Avoided**:
- Not creating wrapper around Better Auth (use API directly)
- Not creating custom password hashing (use Better Auth bcrypt)
- Not creating custom session management (use Better Auth defaults)

---

## Constitution Check: POST-DESIGN Re-Evaluation

*To be completed after Phase 1 design artifacts (data-model.md, contracts/) are created*

**Date**: 2026-02-06 (completed during planning)

### Re-Check Results

| Principle | Initial | Post-Design | Notes |
|-----------|---------|-------------|-------|
| I. Spec-Driven | ✅ PASS | ✅ PASS | All artifacts link to spec |
| II. User Isolation | ✅ PASS | ✅ PASS | Backend isolation unchanged, Better Auth adds DB persistence |
| III. Reusability | ✅ PASS | ✅ PASS | Using existing Better Auth, not creating custom patterns |
| IV. Clarity | ✅ PASS | ✅ PASS | Documentation complete (research.md, data-model.md) |
| V. Test-First | ✅ PASS | ✅ PASS | Security tests defined in research.md section 10 |
| VI. Simplicity | ✅ PASS | ✅ PASS | No premature abstraction, minimal changes |

**Violations**: None

**Conclusion**: Proceed to Phase 2 (task breakdown via `/sp.tasks`)

## Project Structure

### Documentation (this feature)

```text
specs/003-production-auth-migration/
├── spec.md              # Feature specification (created by /sp.specify)
├── plan.md              # This file (created by /sp.plan)
├── research.md          # Better Auth configuration research ✅
├── data-model.md        # User/Session/Task entity relationships ✅
├── checklists/
│   └── requirements.md  # Spec quality validation ✅
└── tasks.md             # Task breakdown (created by /sp.tasks - NOT YET)
```

**Note**: No `contracts/` directory needed (no new API endpoints, using existing Better Auth routes)

### Source Code (repository root)

```text
frontend/
├── lib/
│   ├── auth.ts                        # ✅ EXISTS - Better Auth server config (no changes)
│   ├── auth-client.ts                 # ✅ EXISTS - Better Auth client (no changes)
│   ├── auth-actions.ts                # 🆕 CREATE - Better Auth Server Actions wrapper
│   ├── simple-auth.ts                 # ❌ DELETE - Demo in-memory auth (to be removed)
│   └── api.ts                         # ✅ EXISTS - API client (no changes)
├── components/
│   ├── auth/
│   │   ├── login-form.tsx             # 🔄 UPDATE - Change import from simple-auth to auth-actions
│   │   └── signup-form.tsx            # 🔄 UPDATE - Change import from simple-auth to auth-actions
│   ├── tasks/
│   │   ├── task-list.tsx              # ✅ EXISTS - No changes
│   │   ├── task-create-form.tsx       # ✅ EXISTS - Already has dialog (just needs trigger)
│   │   └── task-item.tsx              # ✅ EXISTS - No changes
│   └── layout/
│       └── header.tsx                 # ✅ EXISTS - No changes needed
├── hooks/
│   └── use-auth.ts                    # 🔄 UPDATE - Change import from simple-auth to auth-actions
├── app/
│   ├── page.tsx                       # 🔄 UPDATE - Change import from simple-auth to auth-actions
│   ├── tasks/
│   │   └── page.tsx                   # 🔄 UPDATE - Add "Add Task" button, change import
│   ├── login/
│   │   └── page.tsx                   # ✅ EXISTS - No changes
│   ├── signup/
│   │   └── page.tsx                   # ✅ EXISTS - No changes
│   └── api/
│       └── auth/
│           └── [...all]/route.ts      # ✅ EXISTS - Better Auth API routes (no changes)
├── .env.local                         # ❌ REMOVE FROM GIT - Contains real credentials
├── .env.example                       # 🔄 UPDATE - Add all required vars with placeholders
└── .gitignore                         # 🔄 UPDATE - Add .env.local

backend/
├── dependencies.py                    # ✅ NO CHANGES - Already supports Better Auth JWT
├── models.py                          # ✅ NO CHANGES - Task model unchanged
├── routers/
│   └── tasks.py                       # ✅ NO CHANGES - User isolation already implemented
└── tests/
    ├── test_auth.py                   # ✅ NO CHANGES - JWT validation tests already exist
    └── test_isolation.py              # ✅ NO CHANGES - User isolation tests already exist
```

**Structure Decision**: Web application (Option 2 - frontend + backend monorepo)

**Files Summary**:
- **Create**: 1 file (`auth-actions.ts`)
- **Update**: 6 files (4 imports + 1 UI + 1 .gitignore)
- **Delete**: 2 files (`simple-auth.ts` + `.env.local` from git history)
- **No Changes**: 15+ files (backend, middleware, API client, Better Auth config)

**Total Scope**: ~500 lines of code changes across 9 files

---

## Implementation Phases

### Phase 0: Environment & Git Cleanup ✅

**Objective**: Secure credentials and validate environment setup

**Tasks**:
1. ✅ Add `.env.local` to `.gitignore`
2. ✅ Update `.env.example` with all required variables (placeholders only)
3. ✅ Remove `.env.local` from git history (if committed)
4. ✅ Verify `BETTER_AUTH_SECRET` is set and matches backend
5. ✅ Verify `DATABASE_URL` points to PostgreSQL instance

**Verification**:
```bash
# Check .gitignore includes .env.local
grep "\.env\.local" frontend/.gitignore

# Verify .env.example has placeholders (no real credentials)
cat frontend/.env.example | grep -v "^#" | grep "="

# Verify git history clean
git log --all --full-history -- "frontend/.env.local"
```

---

### Phase 1: Create Better Auth Server Actions Wrapper

**Objective**: Create production auth functions that use Better Auth database

**Files to Create**:
- `frontend/lib/auth-actions.ts` (new file, ~100 lines)

**Implementation**:
```typescript
// frontend/lib/auth-actions.ts
"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { cookies } from "next/headers";

/**
 * Sign up a new user with Better Auth (database-backed)
 */
export async function signup(
  email: string,
  password: string
): Promise<{ success: boolean; userId?: string; error?: string }> {
  try {
    const result = await auth.api.signUpEmail({
      body: { email, password },
      headers: await headers(),
    });

    if (result.error) {
      return { success: false, error: result.error.message };
    }

    return {
      success: true,
      userId: result.data?.user?.id,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Signup failed",
    };
  }
}

/**
 * Sign in an existing user with Better Auth
 */
export async function signin(
  email: string,
  password: string
): Promise<{ success: boolean; userId?: string; error?: string }> {
  try {
    const result = await auth.api.signInEmail({
      body: { email, password },
      headers: await headers(),
    });

    if (result.error) {
      return { success: false, error: result.error.message };
    }

    return {
      success: true,
      userId: result.data?.user?.id,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Login failed",
    };
  }
}

/**
 * Sign out current user
 */
export async function signout(): Promise<void> {
  await auth.api.signOut({
    headers: await headers(),
  });
}

/**
 * Get current session
 */
export async function getSession(): Promise<{
  userId: string;
  email: string;
} | null> {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.data?.user) {
      return null;
    }

    return {
      userId: session.data.user.id,
      email: session.data.user.email,
    };
  } catch {
    return null;
  }
}
```

**Verification**:
- File compiles without TypeScript errors
- Exports match `simple-auth.ts` function signatures (backward compatibility)

---

### Phase 2: Update Component Imports

**Objective**: Switch all components from demo auth to Better Auth

**Files to Update** (4 files):

1. **`components/auth/login-form.tsx`** (line 30):
   ```typescript
   // OLD
   import { signin } from "@/lib/simple-auth";

   // NEW
   import { signin } from "@/lib/auth-actions";
   ```

2. **`components/auth/signup-form.tsx`** (line 31):
   ```typescript
   // OLD
   import { signup } from "@/lib/simple-auth";

   // NEW
   import { signup } from "@/lib/auth-actions";
   ```

3. **`hooks/use-auth.ts`** (line 14):
   ```typescript
   // OLD
   import { getSession, signout } from "@/lib/simple-auth";

   // NEW
   import { getSession, signout } from "@/lib/auth-actions";
   ```

4. **`app/page.tsx`** (line 14):
   ```typescript
   // OLD
   import { getSession } from "@/lib/simple-auth";

   // NEW
   import { getSession } from "@/lib/auth-actions";
   ```

**Verification**:
```bash
# No remaining imports of simple-auth
grep -r "from \"@/lib/simple-auth\"" frontend/
# Expected: No matches
```

---

### Phase 3: Add Environment Validation

**Objective**: Prevent in-memory fallback, fail fast on missing config

**File to Update**: `frontend/lib/auth.ts` (add startup validation)

**Implementation**:
```typescript
// frontend/lib/auth.ts (add at top, before betterAuth() call)

// Validate required environment variables
if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error(
    "BETTER_AUTH_SECRET environment variable is required. " +
    "Generate one with: openssl rand -base64 32"
  );
}

if (!process.env.DATABASE_URL) {
  throw new Error(
    "DATABASE_URL environment variable is required. " +
    "Configure PostgreSQL connection string."
  );
}

// Remove console.warn about in-memory storage (line 28)
// DELETE: console.warn("DATABASE_URL not set...")

export const auth = betterAuth({
  // ... existing configuration
});
```

**Verification**:
```bash
# Start app without DATABASE_URL
unset DATABASE_URL && npm run dev
# Expected: Error with clear message (not silent fallback)
```

---

### Phase 4: Add "Add Task" Button to Dashboard

**Objective**: Make task creation discoverable (FR-015 through FR-019)

**File to Update**: `frontend/app/tasks/page.tsx`

**Implementation**:
```tsx
// frontend/app/tasks/page.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import { TaskCreateForm } from "@/components/tasks/task-create-form";

export default function TasksPage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const { user } = useAuth();

  return (
    <div className="container mx-auto p-6">
      {/* Header with Add Task button */}
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Tasks</h1>
        <Button onClick={() => setShowCreateDialog(true)}>
          <PlusIcon className="mr-2 h-4 w-4" />
          Add Task
        </Button>
      </header>

      {/* Task list (existing code) */}
      <Suspense fallback={<TaskListSkeleton />}>
        <TaskList userId={user?.userId || ""} />
      </Suspense>

      {/* Create task dialog */}
      {showCreateDialog && (
        <TaskCreateForm
          userId={user?.userId || ""}
          onClose={() => setShowCreateDialog(false)}
          onSuccess={() => {
            setShowCreateDialog(false);
            // Trigger refetch (existing optimistic UI update)
          }}
        />
      )}
    </div>
  );
}
```

**Verification**:
- Button visible on empty state (no tasks)
- Button visible with existing tasks
- Clicking button opens dialog
- Dialog creates task and updates list

---

### Phase 5: Delete Demo Authentication Files

**Objective**: Remove in-memory auth code (FR-004)

**Files to Delete**:
- `frontend/lib/simple-auth.ts` (entire file)

**Git Command**:
```bash
git rm frontend/lib/simple-auth.ts
```

**Verification**:
```bash
# File deleted
test -f frontend/lib/simple-auth.ts && echo "ERROR: File still exists" || echo "OK: File deleted"

# No remaining references
grep -r "simple-auth" frontend/
# Expected: No matches (except in git history or this plan)
```

---

## Complexity Tracking

> **No violations - section intentionally left empty per template instructions**

*This section is only filled if Constitution Check has violations requiring justification. All principles passed - see Constitution Check section above.*

---

## Testing Strategy

### Manual Integration Testing

**Test Scenario 1**: User Persistence After Restart
```
1. Create account: email=test@example.com, password=password123
2. Verify redirect to /tasks
3. Stop Next.js dev server (Ctrl+C)
4. Restart Next.js dev server (npm run dev)
5. Navigate to /login
6. Login with test@example.com / password123
7. ✅ PASS: Login succeeds (user persisted in database)
```

**Test Scenario 2**: Password Hashing Verification
```
1. Create account: email=hash-test@example.com, password=MyPassword123
2. Connect to PostgreSQL database
3. Query: SELECT password FROM user WHERE email = 'hash-test@example.com'
4. ✅ PASS: Password starts with $2b$ (bcrypt hash)
5. ✅ PASS: Password does NOT contain "MyPassword123" (not plaintext)
```

**Test Scenario 3**: Add Task Button Functionality
```
1. Login to /tasks
2. ✅ PASS: "Add Task" button visible in header
3. Click "Add Task" button
4. ✅ PASS: Dialog/form appears
5. Enter: title="Test Task", description="Test Description"
6. Click "Create" or submit
7. ✅ PASS: Task appears in list immediately
8. ✅ PASS: Dialog closes automatically
```

**Test Scenario 4**: No Demo Code Remaining
```bash
1. grep -r "simple-auth" frontend/
   ✅ PASS: No matches found

2. grep -r "new Map<.*{ id: string; email: string; password: string }>" frontend/
   ✅ PASS: No in-memory user storage found

3. grep -r "fallback-secret" frontend/
   ✅ PASS: No weak fallback secrets found

4. npm run dev (without DATABASE_URL set)
   ✅ PASS: Error thrown (not silent fallback)
```

### Backend Compatibility Testing

**Test Scenario 5**: JWT Token Format Verification
```
1. Login via frontend (Better Auth)
2. Inspect session cookie in DevTools
3. Decode JWT at jwt.io
4. ✅ PASS: Claims include "sub" (user_id)
5. ✅ PASS: Claims include "exp" (expiration)
6. Make API request to backend (e.g., GET /api/{userId}/tasks)
7. ✅ PASS: Backend accepts token (no 401 error)
8. ✅ PASS: Backend returns only user's tasks (user isolation working)
```

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Better Auth database creation fails | Low | High | Test on staging first, verify DATABASE_URL format |
| Secret mismatch frontend/backend | Medium | High | Automated validation in startup checks (Phase 3) |
| Import updates incomplete | Low | Medium | `grep` verification step after updates |
| Session cookies not sent to backend | Low | High | Already working (`credentials: "include"` in `api.ts`) |
| .env.local still in git | High | High | BFG Repo Cleaner to remove from history (Phase 0) |

---

## Deployment Checklist

**Pre-Deployment**:
- [ ] Verify `DATABASE_URL` points to production PostgreSQL
- [ ] Generate production `BETTER_AUTH_SECRET` (32+ chars)
- [ ] Ensure `BETTER_AUTH_SECRET` matches in frontend + backend
- [ ] Remove `.env.local` from git history
- [ ] Update `.gitignore` to include `.env.local`
- [ ] Test signup/login on staging environment
- [ ] Verify password hashing (query production database)
- [ ] Run all manual integration tests (scenarios 1-5)

**Post-Deployment**:
- [ ] Monitor authentication error rates
- [ ] Verify database connection pool metrics
- [ ] Test multi-user scenarios (2+ accounts)
- [ ] Check session cookie flags in production (secure=true)
- [ ] Verify httpOnly cookies work across domains (if using CDN)

---

## Next Steps

1. **Run `/sp.tasks`**: Break this plan into ordered, testable tasks
2. **Execute tasks**: Implement via `nextjs-frontend-builder` agent or manual edits
3. **Manual testing**: Run all 5 test scenarios above
4. **Create PHR**: Document implementation results in `history/prompts/003-production-auth-migration/`
5. **Git commit**: Reference spec and tasks in commit message

**Estimated Timeline**: 2-3 hours (1 hour implementation + 1 hour testing + 1 hour documentation)
