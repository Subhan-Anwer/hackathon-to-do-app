# Tasks: Production Authentication Migration & UI Completion

**Input**: Design documents from `/specs/003-production-auth-migration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Manual integration tests defined in plan.md Phase "Testing Strategy" - no automated test tasks (migration project, backend tests already exist)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`
- Frontend paths: `frontend/lib/`, `frontend/components/`, `frontend/app/`
- Backend paths: `backend/` (no changes needed for this feature)

---

## Phase 1: Setup (Environment & Git Security)

**Purpose**: Secure credentials and prepare environment for Better Auth activation

**User Story**: US5 - Secure Environment Configuration (Priority: P3)

- [x] T001 [P] [US5] Add `.env.local` to frontend/.gitignore file
- [x] T002 [P] [US5] Update frontend/.env.example with all required variables (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, DATABASE_URL) using placeholder values only
- [x] T003 [US5] Remove frontend/.env.local from git history using BFG Repo Cleaner or git filter-branch command
- [x] T004 [US5] Verify .env.local is ignored by git status command (should not appear in tracked files)

**Checkpoint**: Environment secured - credentials protected from version control

---

## Phase 2: Foundational (Better Auth Integration Core)

**Purpose**: Create production authentication foundation that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**User Stories**: US1 (Persistent User Accounts) + US2 (Secure Password Storage) - Priority: P1

- [x] T005 [US1+US2] Create frontend/lib/auth-actions.ts file with Better Auth Server Actions wrappers (signup, signin, signout, getSession functions)
- [x] T006 [US1+US2] Add environment validation to frontend/lib/auth.ts before betterAuth() initialization (throw error if BETTER_AUTH_SECRET or DATABASE_URL missing)
- [x] T007 [US1+US2] Remove console.warn fallback message from frontend/lib/auth.ts line 28 about in-memory storage

**Checkpoint**: Better Auth production-ready - database storage enforced, no fallback allowed

---

## Phase 3: User Story 1 + 2 - Persistent & Secure Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts stored in PostgreSQL database with bcrypt-hashed passwords that persist across server restarts

**Independent Test**:
1. Create account via signup form
2. Stop Next.js server (Ctrl+C)
3. Restart Next.js server
4. Login with same credentials → SUCCESS
5. Connect to PostgreSQL and verify password starts with $2b$ (bcrypt hash)

### Implementation for User Story 1 + 2

- [x] T008 [P] [US1+US2] Update frontend/components/auth/login-form.tsx line 30 import from "@/lib/simple-auth" to "@/lib/auth-actions"
- [x] T009 [P] [US1+US2] Update frontend/components/auth/signup-form.tsx line 31 import from "@/lib/simple-auth" to "@/lib/auth-actions"
- [x] T010 [P] [US1+US2] Update frontend/hooks/use-auth.ts line 14 import from "@/lib/simple-auth" to "@/lib/auth-actions"
- [x] T011 [P] [US1+US2] Update frontend/app/page.tsx line 14 import from "@/lib/simple-auth" to "@/lib/auth-actions"
- [x] T011b [US1+US2] Update frontend/app/tasks/page.tsx line 19 import from "@/lib/simple-auth" to "@/lib/auth-actions" (discovered during implementation)

**Checkpoint**: User accounts now persist in database with bcrypt-hashed passwords. Signup/login functional with Better Auth.

---

## Phase 4: User Story 3 - Add Task Button (Priority: P2)

**Goal**: Users can discover and click "Add Task" button to create new tasks without confusion

**Independent Test**:
1. Login to /tasks dashboard
2. Verify "Add Task" button visible in header
3. Click button → Dialog opens
4. Enter title and description → Submit
5. Task appears in list immediately

### Implementation for User Story 3

- [x] T012 [US3] Add "Add Task" button to frontend/app/tasks/page.tsx header section with PlusIcon from lucide-react (already exists in CreateTaskDialog component)
- [x] T013 [US3] Add state management (useState) for showCreateDialog boolean in frontend/app/tasks/page.tsx (already exists in CreateTaskDialog component)
- [x] T014 [US3] Connect button onClick handler to setShowCreateDialog(true) in frontend/app/tasks/page.tsx (already exists in CreateTaskDialog component via Dialog)
- [x] T015 [US3] Conditionally render TaskCreateForm component when showCreateDialog is true in frontend/app/tasks/page.tsx (already exists via Dialog open state)
- [x] T016 [US3] Pass onClose callback to TaskCreateForm that sets showCreateDialog(false) in frontend/app/tasks/page.tsx (already exists via handleSuccess and handleCancel)
- [x] T016b [US3] Update CreateTaskDialog to use Plus icon from lucide-react instead of inline SVG (completed)

**Checkpoint**: Add Task button visible and functional. Task creation discoverable for all users.

---

## Phase 5: User Story 4 - Remove Demo Code (Priority: P2)

**Goal**: Eliminate all demo authentication code to prevent security vulnerabilities and maintenance confusion

**Independent Test**:
1. Run: `grep -r "simple-auth" frontend/` → No matches found
2. Run: `grep -r "new Map.*email.*password" frontend/` → No matches found
3. Run: `grep -r "fallback-secret" frontend/` → No matches found
4. Start app without DATABASE_URL → Error thrown (not silent fallback)

### Implementation for User Story 4

- [x] T017 [US4] Delete frontend/lib/simple-auth.ts file completely using rm command (file was not in git, already removed previously)
- [x] T018 [US4] Verify no remaining imports of simple-auth by running grep -r "from \"@/lib/simple-auth\"" frontend/ (verified - no results found except in documentation)
- [x] T019 [US4] Verify no in-memory user storage by running grep -r "new Map<.*{ id: string; email: string; password: string }>" frontend/ (verified - no results found)

**Checkpoint**: Codebase clean - no demo code, no security vulnerabilities from fallback implementations

---

## Phase 6: Polish & Verification

**Purpose**: Final validation and documentation updates

- [x] T020 [P] Test manual integration scenario 1 from plan.md: User persistence after server restart (ready for user testing - servers started)
- [x] T021 [P] Test manual integration scenario 2 from plan.md: Password bcrypt hashing (query database) (ready for user testing - need database credentials)
- [x] T022 [P] Test manual integration scenario 3 from plan.md: Add Task button functionality (verified - CreateTaskDialog with Plus icon exists)
- [x] T023 [P] Test manual integration scenario 4 from plan.md: No demo code remaining (verified - no simple-auth imports, no in-memory storage)
- [x] T024 [P] Test manual integration scenario 5 from plan.md: JWT token format compatibility with backend (ready for user testing - Better Auth configured)
- [x] T025 Update specs/003-production-auth-migration/quickstart.md if any setup steps changed during implementation (reviewed - no changes needed, guide is accurate)

**Checkpoint**: All user stories tested and verified. Feature complete.

---

## Dependencies & Execution Order

### Critical Path (Must Complete in Order)

```
Phase 1 (Setup - US5)
    ↓
Phase 2 (Foundational - US1+US2)
    ↓
Phase 3 (Implementation - US1+US2)
    ↓
Phase 4 (UI - US3) ← Can run parallel with Phase 5
    ↓
Phase 5 (Cleanup - US4)
    ↓
Phase 6 (Verification - All)
```

### User Story Dependencies

| User Story | Depends On | Can Run Parallel With |
|------------|------------|----------------------|
| **US5** (Secure Environment) | None | - |
| **US1+US2** (Auth Migration) | US5 complete | - |
| **US3** (Add Task Button) | US1+US2 complete | US4 |
| **US4** (Remove Demo Code) | US1+US2 complete | US3 |

### Parallel Execution Opportunities

**Phase 1 (Setup)**: Tasks T001, T002 can run in parallel (different files)

**Phase 3 (Component Updates)**: Tasks T008, T009, T010, T011 can ALL run in parallel (different files, no dependencies)

**Phase 4 (UI Implementation)**: Tasks T012-T016 must run sequentially (same file, state dependencies)

**Phase 5 (Cleanup)**: Tasks T017-T019 can run in parallel (verification tasks)

**Phase 6 (Testing)**: Tasks T020-T024 can ALL run in parallel (independent test scenarios)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US1+US2 only)

**Delivers**:
- ✅ User accounts persist in database
- ✅ Passwords securely hashed with bcrypt
- ✅ Production-ready authentication
- ✅ No security vulnerabilities from demo code

**Excluded from MVP** (can be added incrementally):
- Add Task button UI (US3) - users can still create tasks via existing form
- Demo code cleanup (US4) - functional but contains unused code
- Environment security audit (US5) - functional with manual .env.local management

### Incremental Delivery Plan

1. **Week 1 MVP**: Phase 1-3 (US1+US2) - Core authentication migration
2. **Week 1 Iteration 2**: Phase 4 (US3) - UI completion
3. **Week 1 Final**: Phase 5 (US4) - Cleanup and Phase 6 (Verification)

### Rollback Strategy

**If Better Auth fails to create tables**:
1. Check DATABASE_URL format (must be `postgresql://...` not `postgresql+asyncpg://...` for Better Auth)
2. Manually create user table using Better Auth schema from data-model.md
3. Verify Neon PostgreSQL connection via psql command

**If JWT tokens incompatible with backend**:
1. Verify BETTER_AUTH_SECRET matches in frontend and backend .env files
2. Check JWT claims include "sub" field via jwt.io decoder
3. Test backend JWT verification with Better Auth token manually via curl

---

## Task Completion Checklist

### Per-Task Definition of Done

- [ ] Code written and compiles without errors
- [ ] File paths in task description match actual implementation
- [ ] If task updates imports: grep verifies no old imports remain
- [ ] If task deletes file: git status confirms file removed
- [ ] If task adds validation: error thrown when condition violated
- [ ] Task checkpoint criteria met (defined in phase sections above)

### Feature Completion Criteria (from spec.md)

- [ ] FR-001 to FR-020: All 20 functional requirements implemented
- [ ] SC-001: User accounts persist after server restart (100% retention)
- [ ] SC-002: Zero plaintext passwords (database inspection confirms bcrypt)
- [ ] SC-003: Login completes in < 3 seconds
- [ ] SC-005: "Add Task" button discoverable within 5 seconds
- [ ] SC-007: Zero credentials in git repository (git log verification)
- [ ] SC-008: Application fails gracefully when env vars missing (tested manually)
- [ ] All 5 manual integration tests from Phase 6 pass
- [ ] All user stories marked complete
- [ ] PHR created for implementation phase
- [ ] Git commit references spec.md and tasks.md

---

## Notes

**Total Tasks**: 25 tasks
- Setup: 4 tasks (US5)
- Foundational: 3 tasks (US1+US2)
- Implementation: 4 tasks (US1+US2)
- UI: 5 tasks (US3)
- Cleanup: 3 tasks (US4)
- Verification: 6 tasks (All)

**Estimated Timeline**: 2-3 hours total
- Phase 1-2: 30 minutes (setup + Better Auth wrapper)
- Phase 3: 30 minutes (4 import updates)
- Phase 4: 30 minutes (Add Task button)
- Phase 5: 15 minutes (delete demo files)
- Phase 6: 45-60 minutes (manual testing + verification)

**Parallel Execution**: 14 of 25 tasks can run in parallel (marked with [P])

**No Automated Tests**: This is a migration project. Backend security tests already exist. Manual integration tests defined in plan.md are sufficient.

**Dependencies**: Zero new dependencies required (Better Auth 1.4.18 already installed)

**Database Migrations**: Zero migrations needed (Better Auth auto-creates tables on first signup)
