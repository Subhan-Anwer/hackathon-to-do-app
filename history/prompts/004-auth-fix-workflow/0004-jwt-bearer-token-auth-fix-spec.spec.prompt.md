---
id: 0004
title: jwt-bearer-token-auth-fix-spec
stage: spec
date: 2026-02-08
surface: claude-code-cli
model: claude-sonnet-4-5
feature: 004-auth-fix-workflow
branch: 004-auth-fix-workflow
user: subhan
command: /sp.specify
labels: [authentication, jwt, bearer-token, fix, spec]
links:
  spec: specs/004-auth-fix-workflow/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-auth-fix-workflow/spec.md
  - specs/004-auth-fix-workflow/checklists/requirements.md
tests: []
---

## Prompt

User requested creation of a targeted specification to fix 401 Unauthorized errors when creating tasks. The spec must focus on implementing proper JWT Bearer token authentication between Next.js frontend and FastAPI backend.

Key requirements from user:
- Frontend extracts JWT token from Better Auth session
- Every API request includes `Authorization: Bearer <token>` header
- No reliance on cross-origin cookie transmission (different ports in development)
- Works in both development (localhost:3000 → localhost:8000) and production
- Keep httpOnly cookies enabled (no security downgrade)
- Use Next.js server components/server actions/API routes for server-side token extraction
- Backend verifies token from Authorization header using shared BETTER_AUTH_SECRET
- All task endpoints require valid token → 401 Unauthorized otherwise

Implementation guidance requested:
- Use getSession() server-side to extract JWT token
- Create server-side API proxy/wrappers to add Bearer header
- Client-side code calls Next.js internal routes (same origin)
- Handle 401 → redirect to /login + toast message
- Files to modify: lib/api.ts, app/api/tasks/route.ts, components, backend middleware

Success criteria:
- After login, creating a task sends Authorization: Bearer <token> header
- No more 401 Unauthorized when authenticated
- Cookie not required cross-origin
- Matches PDF requirement: frontend issues JWT, attaches in header, backend verifies from header

## Response snapshot

Created comprehensive specification document at `specs/004-auth-fix-workflow/spec.md` with:

**User Scenarios (3 stories):**
1. Authenticated Task Creation (P1) - Core authentication flow fix
2. Cross-Origin Authentication (P1) - Development localhost:3000 → localhost:8000
3. Production Deployment (P2) - HTTPS production environment

**Functional Requirements (17 total):**
- FR-001 to FR-003: JWT Token Extraction from Better Auth session
- FR-004 to FR-007: Authorization Header Implementation via server-side proxies
- FR-008 to FR-011: Backend Token Verification from Authorization header
- FR-012 to FR-014: Error Handling (401 → redirect to /login)
- FR-015 to FR-017: Security Requirements (httpOnly, user isolation, shared secret)

**Success Criteria (6 measurable outcomes):**
- SC-001: 100% success rate creating tasks without 401 errors
- SC-002: All requests include Authorization: Bearer <token> (verifiable in DevTools)
- SC-003: Backend successfully verifies JWT and extracts user_id (observable in logs)
- SC-004: Works in both development and production without code changes
- SC-005: httpOnly cookies remain enabled
- SC-006: 0% data leak rate (multi-user isolation testing)

**Implementation Guidance:**
- Frontend files: lib/api.ts, app/api/tasks/route.ts, app/actions/tasks.ts, components
- Backend files: main.py (middleware), routers/tasks.py
- Configuration: .env files with matching BETTER_AUTH_SECRET

**Validation:**
Created requirements checklist at `specs/004-auth-fix-workflow/checklists/requirements.md`
- All checklist items passed on first validation
- No [NEEDS CLARIFICATION] markers
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- Spec ready for /sp.plan phase

## Outcome

- ✅ Impact: Created targeted spec to fix critical 401 authentication issue blocking task creation
- 🧪 Tests: Specification defines 9 acceptance scenarios across 3 user stories + 5 edge cases
- 📁 Files: Created spec.md and checklists/requirements.md in specs/004-auth-fix-workflow/
- 🔁 Next prompts: Run /sp.plan to design implementation architecture for JWT Bearer token auth
- 🧠 Reflection: Spec successfully narrowed from broad auth fix to specific JWT Bearer header implementation. Clear separation between requirements (WHAT) and implementation guidance (HOW). All validation items passed, no clarifications needed.

## Evaluation notes (flywheel)

- Failure modes observed: None - spec validated successfully on first attempt
- Graders run and results (PASS/FAIL): Requirements checklist PASSED all items
- Prompt variant (if applicable): Standard /sp.specify workflow with existing branch
- Next experiment (smallest change to try): N/A - ready to proceed to planning phase
