# Implementation Plan: JWT Bearer Token Authentication Fix

**Branch**: `004-auth-fix-workflow` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-auth-fix-workflow/spec.md`

**Note**: This plan addresses the 401 Unauthorized error by implementing proper JWT Bearer token authentication between Next.js frontend and FastAPI backend.

## Summary

**Problem**: Task operations fail with 401 Unauthorized because JWT tokens are sent via httpOnly cookies, which browsers block on cross-origin requests (localhost:3000 → localhost:8000 in development).

**Solution**: Extract JWT token from Better Auth session server-side using the `set-auth-jwt` response header, then include it in `Authorization: Bearer <token>` header for all backend API requests via Next.js Server Actions.

**Technical Approach** (from research.md):
1. Create Server Actions that call `auth.api.getSession()` with `fetchOptions` callback
2. Extract JWT token from `set-auth-jwt` response header
3. Forward requests to FastAPI backend with `Authorization: Bearer <token>` header
4. Update React components to call Server Actions instead of direct fetch
5. Backend already supports Bearer token authentication (no changes required)

**Key Insight**: Backend already implements dual authentication (Bearer header + cookie fallback). Frontend just needs to use Bearer header pattern instead of relying on cross-origin cookies.

## Technical Context

**Language/Version**: TypeScript 5 (frontend), Python 3.12 (backend)
**Primary Dependencies**:
- Frontend: Next.js 16.1.6, Better Auth (JWT plugin), React 19.2.3
- Backend: FastAPI 0.128.1, python-jose 3.5.0 (JWT validation)

**Storage**: PostgreSQL (Neon Serverless) - no schema changes required
**Testing**: Jest + React Testing Library (frontend), pytest (backend - existing tests remain valid)
**Target Platform**: Web application (development: localhost HTTP, production: HTTPS)
**Project Type**: Full-stack web (monorepo with frontend/ and backend/)
**Performance Goals**:
- JWT extraction: <50ms overhead per request
- Total request latency: <200ms for task operations
- No degradation from current cookie-based auth performance

**Constraints**:
- Must work in both development (localhost different ports) and production (same origin)
- httpOnly cookies must remain enabled (security requirement FR-015)
- No breaking changes to existing authentication flow
- Backend API contracts unchanged

**Scale/Scope**:
- 6 task operations to update (list, create, get, update, delete, toggleComplete)
- 1 new Server Actions file (`app/actions/tasks.ts`)
- 1 file modification (`lib/api.ts` - deprecate or remove)
- ~5 component files to update (task-form, task-list, task-item, dialogs)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅

- ✅ Specification exists: `specs/004-auth-fix-workflow/spec.md`
- ✅ Planning follows spec requirements (FR-001 to FR-017)
- ✅ Implementation via `/sp.*` commands only
- ✅ Traceability: Plan references spec functional requirements

### Principle II: User Isolation and Security First ✅

- ✅ JWT authentication required for all API endpoints (no changes, existing requirement)
- ✅ Middleware extracts user_id from JWT "sub" claim (backend already implements)
- ✅ All database queries filtered by user_id (backend already implements)
- ✅ 401 Unauthorized on missing/invalid tokens (maintained, improved with Bearer header)
- ✅ httpOnly cookies remain enabled (spec FR-015, no security downgrade)

**Security Improvement**: Bearer token approach is MORE secure for cross-origin scenarios because:
- No reliance on browser cookie policies (eliminates CSRF in cross-origin dev environment)
- Explicit token transmission (easier to audit in network logs)
- Backend validates same JWT with same secret (security model unchanged)

### Principle III: Reusability Through Skills and Agents ✅

- ✅ Used `better-auth-integration` skill knowledge (Context7 MCP research)
- ✅ Can invoke `nextjs-builder` agent for implementation phase
- ✅ Patterns from `api-security` skill applied (JWT verification, user isolation)

### Principle IV: Clarity and Consistency ✅

- ✅ Follows `CLAUDE.md` development guidelines
- ✅ References specs explicitly (`specs/004-auth-fix-workflow/spec.md`)
- ✅ Uses monorepo paths (`frontend/`, `backend/`)
- ✅ Maintains single source of truth (constitution for principles, spec for features)

### Principle V: Test-First for Security-Critical Paths ✅

- ✅ Existing backend tests cover JWT authentication (`backend/tests/test_auth.py`)
- ✅ Existing isolation tests verify user_id filtering (`backend/tests/test_isolation.py`)
- ✅ No new backend security logic (existing tests remain valid)
- ⚠️ **TODO**: Add frontend integration tests for Bearer token transmission (Phase 2)

**Test Strategy**:
- Backend tests unchanged (already validate JWT from Authorization header)
- Frontend: Manual testing during development (verify header in DevTools)
- Integration: Multi-user test accounts to verify isolation still works

### Principle VI: Simplicity and Smallest Viable Change ✅

- ✅ No premature abstraction (Server Actions are built-in Next.js 16 feature)
- ✅ Implements only specified features (JWT Bearer header, no extras)
- ✅ Focused diff (single concern: change authentication method)
- ✅ YAGNI: No token caching, no refresh token rotation (out of scope per spec)

**Simplicity Validation**:
- Backend changes: **ZERO** (already supports Bearer tokens)
- New patterns introduced: **ONE** (Server Actions, already standard in Next.js 16)
- Code duplication: **NONE** (Server Actions reused across all task operations)

### Constitution Compliance Summary

**Status**: ✅ **PASSED** - All principles aligned

**No Complexity Violations**: No entries in Complexity Tracking table required.

**Re-check After Phase 1**: Will validate that implementation design maintains compliance (no additional abstractions, patterns stay simple).

## Project Structure

### Documentation (this feature)

```text
specs/004-auth-fix-workflow/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - Better Auth JWT research (COMPLETE)
├── data-model.md        # Phase 1 output - Authentication flow diagrams
├── quickstart.md        # Phase 1 output - Developer testing guide
├── contracts/           # Phase 1 output - API contracts (unchanged)
│   └── README.md        # Note: Backend API contracts unchanged
├── checklists/
│   └── requirements.md  # Spec validation checklist (COMPLETE)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

**Web Application Structure** (frontend + backend):

```text
backend/
├── main.py                  # FastAPI app with CORS (NO CHANGES)
├── dependencies.py          # JWT auth dependency (NO CHANGES - already supports Bearer)
├── routers/
│   └── tasks.py            # Task endpoints (NO CHANGES - user isolation already implemented)
└── tests/
    ├── test_auth.py        # JWT validation tests (NO CHANGES - already validate Bearer header)
    └── test_isolation.py   # User isolation tests (NO CHANGES - remain valid)

frontend/
├── app/
│   ├── actions/
│   │   └── tasks.ts        # NEW: Server Actions for task operations with Bearer token
│   ├── tasks/
│   │   └── page.tsx        # MODIFY: Call Server Actions instead of direct fetch
│   └── api/
│       └── auth/
│           └── [...all]/route.ts  # NO CHANGES - Better Auth routes
├── components/
│   └── tasks/
│       ├── task-form.tsx          # MODIFY: Use Server Actions
│       ├── task-list.tsx          # MODIFY: Use Server Actions
│       ├── task-item.tsx          # MODIFY: Use Server Actions
│       ├── create-task-dialog.tsx # MODIFY: Use Server Actions
│       ├── edit-task-dialog.tsx   # MODIFY: Use Server Actions
│       └── delete-task-dialog.tsx # MODIFY: Use Server Actions
├── lib/
│   ├── auth.ts            # NO CHANGES - Better Auth config already has JWT plugin
│   ├── auth-client.ts     # NO CHANGES - Client-side hooks
│   └── api.ts             # DEPRECATE/REMOVE: Cookie-based client replaced by Server Actions
└── types/
    └── task.ts            # NO CHANGES - TypeScript interfaces unchanged
```

**Structure Decision**: Web application monorepo structure selected (frontend + backend).

**Rationale**:
- Existing monorepo structure maintained (no restructuring)
- Backend requires **zero changes** (already supports Authorization Bearer header)
- Frontend changes localized to:
  - **New file**: `app/actions/tasks.ts` (Server Actions)
  - **Modifications**: Component files (6 files) to call Server Actions
  - **Deprecation**: `lib/api.ts` (old cookie-based client)

**Impact Analysis**:
- ✅ Minimal blast radius (7 frontend files touched)
- ✅ No database migrations
- ✅ No API contract changes
- ✅ No breaking changes (authentication flow enhanced, not replaced)
- ✅ Backward compatible (backend still accepts cookies as fallback)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. Constitution Principle VI (Simplicity) fully satisfied.

**Validation**:
- No premature abstractions (Server Actions are Next.js 16 built-in feature)
- No repository pattern introduced (direct Better Auth API usage)
- No additional middleware layers (use existing middleware pattern)
- No token caching mechanism (simple stateless JWT validation)
- No complex error handling hierarchies (use try/catch with user-friendly messages)

**Table**: N/A (no entries required)
