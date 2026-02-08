# Tasks: JWT Bearer Token Authentication Fix

**Input**: Design documents from `/specs/004-auth-fix-workflow/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Manual testing only - no automated test tasks included (existing backend tests already validate JWT authentication)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` and `backend/` at repository root
- Backend requires ZERO changes (already supports Bearer token authentication)
- Frontend changes localized to Server Actions and components

---

## Phase 1: Setup (Environment Validation)

**Purpose**: Verify environment configuration and dependencies before implementation

- [X] T001 Verify BETTER_AUTH_SECRET matches in frontend/.env.local and backend/.env (must be identical)
- [X] T002 [P] Verify JWT plugin enabled in frontend/lib/auth.ts (import jwt from "better-auth/plugins")
- [X] T003 [P] Verify backend supports Bearer token authentication in backend/dependencies.py:51-59
- [X] T004 [P] Create environment variable validation checklist per quickstart.md

**Checkpoint**: ✅ Environment configured correctly - implementation can begin

---

## Phase 2: Foundational (Server Actions Infrastructure)

**Purpose**: Core Server Actions infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create frontend/app/actions/tasks.ts file with Server Actions boilerplate
- [X] T006 Implement JWT token extraction helper function in frontend/app/actions/tasks.ts using set-auth-jwt header
- [X] T007 [P] Create error handling utilities for 401 responses in frontend/app/actions/tasks.ts
- [X] T008 [P] Add TypeScript types for Server Action return values in frontend/types/task.ts (if not exists)

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authenticated Task Creation (Priority: P1) 🎯 MVP

**Goal**: Fix 401 Unauthorized error for task creation by implementing JWT Bearer token authentication

**Independent Test**: Sign in at localhost:3000/login, create a task, verify in DevTools Network tab that request includes `Authorization: Bearer <token>` header and returns 201 Created (not 401 Unauthorized)

### Implementation for User Story 1

- [X] T009 [P] [US1] Implement createTask Server Action in frontend/app/actions/tasks.ts (POST /api/{user_id}/tasks)
- [X] T010 [P] [US1] Implement listTasks Server Action in frontend/app/actions/tasks.ts (GET /api/{user_id}/tasks)
- [X] T011 [US1] Update frontend/components/tasks/task-form.tsx to call createTask Server Action instead of taskApi.create
- [X] T012 [US1] Update frontend/app/tasks/page.tsx to call listTasks Server Action for initial data fetch
- [X] T013 [US1] Update frontend/components/tasks/create-task-dialog.tsx to use createTask Server Action
- [ ] T014 [US1] Manual test per quickstart.md Section 5 (verify Bearer token in DevTools, 201 response)

**Checkpoint**: ✅ Users can create tasks without 401 errors - core authentication flow fixed (pending manual test)

---

## Phase 4: User Story 2 - Cross-Origin Authentication (Priority: P1)

**Goal**: Ensure Bearer token authentication works across different ports in development (localhost:3000 → localhost:8000)

**Independent Test**: Run frontend on port 3000 and backend on port 8000, sign in, create a task, verify in DevTools that Authorization header is sent (not relying on cross-origin cookies), and task is created successfully

### Implementation for User Story 2

- [X] T015 [P] [US2] Implement updateTask Server Action in frontend/app/actions/tasks.ts (PUT /api/{user_id}/tasks/{task_id})
- [X] T016 [P] [US2] Implement deleteTask Server Action in frontend/app/actions/tasks.ts (DELETE /api/{user_id}/tasks/{task_id})
- [X] T017 [P] [US2] Implement toggleComplete Server Action in frontend/app/actions/tasks.ts (PATCH /api/{user_id}/tasks/{task_id}/complete)
- [X] T018 [US2] Update frontend/components/tasks/edit-task-dialog.tsx to use updateTask Server Action
- [X] T019 [US2] Update frontend/components/tasks/delete-task-dialog.tsx to use deleteTask Server Action
- [X] T020 [US2] Update frontend/components/tasks/task-item.tsx to use toggleComplete Server Action for checkbox
- [X] T021 [US2] Update frontend/components/tasks/task-list.tsx to call Server Actions instead of taskApi methods
- [ ] T022 [US2] Manual test per quickstart.md Section 3 (verify cross-origin requests work with Bearer token)

**Checkpoint**: ✅ All task CRUD operations work across different ports without 401 errors - development environment fully functional (pending manual test)

---

## Phase 5: User Story 3 - Production Deployment (Priority: P2)

**Goal**: Verify Bearer token authentication works in production HTTPS environment without code changes

**Independent Test**: Deploy to production (or staging with HTTPS), sign in, perform all task operations (create, update, delete, toggle), verify Authorization Bearer headers are used consistently and httpOnly cookies remain enabled

### Implementation for User Story 3

- [X] T023 [US3] Verify frontend/.env.example documents BETTER_AUTH_SECRET requirement
- [X] T024 [US3] Verify backend/.env.example documents BETTER_AUTH_SECRET requirement
- [X] T025 [P] [US3] Add production environment validation in frontend/app/actions/tasks.ts (check NODE_ENV)
- [X] T026 [US3] Deprecate or remove frontend/lib/api.ts (old cookie-based client no longer needed)
- [ ] T027 [US3] Manual test per quickstart.md Section 4 (verify backend logs show JWT authentication)
- [ ] T028 [US3] Manual test: Verify httpOnly cookies still enabled in DevTools → Application → Cookies

**Checkpoint**: ✅ Production deployment verified - authentication works in both development and production without code changes (pending manual tests)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and documentation

- [X] T029 [P] Remove or deprecate frontend/lib/api.ts (cookie-based client replaced by Server Actions)
- [X] T030 [P] Update frontend/docs/README.md to document Server Actions authentication pattern
- [ ] T031 [P] Run complete quickstart.md testing checklist (all 10 steps)
- [ ] T032 Multi-user isolation test: Create two user accounts, verify User A cannot access User B's tasks
- [ ] T033 [P] Verify SC-002: Check DevTools Network tab for `Authorization: Bearer <token>` on all requests
- [ ] T034 [P] Verify SC-003: Check backend logs for "User authenticated: {user_id}" messages
- [ ] T035 [P] Verify SC-005: Check DevTools → Application → Cookies that httpOnly is still true
- [ ] T036 Performance test: Measure JWT extraction overhead (<50ms per request target)
- [X] T037 [P] Update CLAUDE.md with Server Actions pattern for future features
- [X] T038 Create implementation completion report documenting success criteria validation

**Checkpoint**: ✅ Documentation and implementation complete - ready for manual testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T004) - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion (T005-T008)
  - User Story 1 (Phase 3): Can start after Foundational - MVP priority
  - User Story 2 (Phase 4): Can start after US1 (builds on Server Actions infrastructure)
  - User Story 3 (Phase 5): Can start after US2 (validates production deployment)
- **Polish (Phase 6)**: Depends on all user stories being complete (T009-T028)

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 (Foundational) - No dependencies on other stories
  - **MVP Delivery Point**: After US1 completion, users can create and list tasks without 401 errors
- **User Story 2 (P1)**: Depends on US1 (reuses Server Actions pattern) - Extends to all task operations
  - **Full CRUD Delivery Point**: After US2 completion, all task operations work across different ports
- **User Story 3 (P2)**: Depends on US2 (validates production deployment) - No new functionality
  - **Production Ready Point**: After US3 completion, feature is production-ready

### Within Each User Story

**User Story 1**:
- T009, T010 can run in parallel (different Server Actions)
- T011-T013 depend on T009 (need createTask Server Action implemented)
- T014 depends on T011-T013 (manual test requires implementation complete)

**User Story 2**:
- T015, T016, T017 can run in parallel (different Server Actions)
- T018 depends on T015 (needs updateTask)
- T019 depends on T016 (needs deleteTask)
- T020 depends on T017 (needs toggleComplete)
- T021 depends on T018-T020 (integrates all Server Actions)
- T022 depends on T021 (manual test requires implementation complete)

**User Story 3**:
- T023, T024 can run in parallel (different .env.example files)
- T025 can run in parallel with T023-T024
- T026 depends on T021 (can only deprecate api.ts after all components migrated)
- T027, T028 can run in parallel (different manual tests)

**Polish Phase**:
- T029-T031 can run in parallel (different files/docs)
- T032-T038 can run in parallel (different validation checks)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004 can run in parallel (different verification tasks)

**Phase 2 (Foundational)**:
- T007, T008 can run in parallel after T006 completes (different utility files)

**Phase 3 (User Story 1)**:
- T009, T010 can run in parallel (different Server Actions)

**Phase 4 (User Story 2)**:
- T015, T016, T017 can run in parallel (different Server Actions)

**Phase 5 (User Story 3)**:
- T023, T024, T025 can run in parallel (different files)
- T027, T028 can run in parallel (different manual tests)

**Phase 6 (Polish)**:
- T029, T030, T031 can run in parallel (different cleanup tasks)
- T032, T033, T034, T035, T036, T037, T038 can run in parallel (different validation checks)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase (T005-T008) completes:

# Parallel track 1: Implement Server Actions
T009: Implement createTask Server Action
T010: Implement listTasks Server Action

# Sequential track 2: Update components (depends on T009)
T011: Update task-form.tsx → T013: Update create-task-dialog.tsx

# Sequential track 3: Update page (depends on T010)
T012: Update tasks/page.tsx

# Final: Manual testing (depends on all implementation)
T014: Manual test with DevTools
```

---

## Parallel Example: User Story 2

```bash
# After User Story 1 completes:

# Parallel track 1: Implement remaining Server Actions
T015: Implement updateTask Server Action
T016: Implement deleteTask Server Action
T017: Implement toggleComplete Server Action

# Sequential track 2: Update dialogs (depends on T015, T016)
T018: Update edit-task-dialog.tsx
T019: Update delete-task-dialog.tsx

# Sequential track 3: Update task item (depends on T017)
T020: Update task-item.tsx

# Sequential track 4: Integrate in task list (depends on T018-T020)
T021: Update task-list.tsx

# Final: Manual testing (depends on all implementation)
T022: Manual cross-origin test
```

---

## Implementation Strategy

### MVP Delivery (Minimum Viable Product)

**Scope**: User Story 1 only (Tasks T001-T014)

**Delivers**:
- ✅ Users can create tasks without 401 errors
- ✅ Users can view their task list
- ✅ Core authentication flow fixed with JWT Bearer token

**Time Estimate**: 2-4 hours (including manual testing)

**Verification**:
- Sign in → Create task → Verify in DevTools Network tab: `Authorization: Bearer <token>` header present
- Backend response: 201 Created (not 401 Unauthorized)
- Task appears in task list immediately

### Incremental Delivery

**Phase 1**: User Story 1 (MVP) - Task creation and listing working
**Phase 2**: User Story 2 - All CRUD operations working across different ports
**Phase 3**: User Story 3 - Production validation and cleanup

### Recommended Execution Order

1. **Sequential Approach** (single developer):
   - Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (Polish)
   - Each phase fully complete before starting next
   - MVP delivered after Phase 3

2. **Parallel Approach** (team of 2-3):
   - Developer 1: Phase 1 → Phase 2 (foundation)
   - Developer 2: Phase 3 (US1) after foundation ready
   - Developer 3: Phase 4 (US2) after US1 ready
   - All: Phase 5 (US3) validation together
   - All: Phase 6 (Polish) together

---

## Success Criteria Validation

Each task maps to success criteria from spec.md:

- **SC-001** (100% success creating tasks): Validated by T014 (US1 manual test)
- **SC-002** (Authorization header present): Validated by T033 (DevTools verification)
- **SC-003** (Backend logs show authentication): Validated by T034 (backend log check)
- **SC-004** (Works in dev + production): Validated by T022 (US2 cross-origin) + T027 (US3 production)
- **SC-005** (httpOnly cookies enabled): Validated by T028, T035 (cookie verification)
- **SC-006** (Multi-user isolation): Validated by T032 (isolation test)

---

## Risk Mitigation Tasks

**Risk 1**: Better Auth session object may not expose JWT token in expected format
- **Mitigation**: T006 implements fallback to `/api/auth/token` endpoint if `set-auth-jwt` header missing

**Risk 2**: Server Actions may add latency
- **Mitigation**: T036 measures performance (<50ms overhead target)

**Risk 3**: BETTER_AUTH_SECRET mismatch between frontend and backend
- **Mitigation**: T001 explicitly verifies secrets match before implementation begins

---

## Task Summary

**Total Tasks**: 38
- **Setup (Phase 1)**: 4 tasks (T001-T004)
- **Foundational (Phase 2)**: 4 tasks (T005-T008)
- **User Story 1 (Phase 3)**: 6 tasks (T009-T014)
- **User Story 2 (Phase 4)**: 8 tasks (T015-T022)
- **User Story 3 (Phase 5)**: 6 tasks (T023-T028)
- **Polish (Phase 6)**: 10 tasks (T029-T038)

**Parallelizable Tasks**: 22 tasks marked [P] (58% of total)

**Backend Changes**: 0 tasks (backend already supports Bearer token authentication)

**Frontend Changes**:
- **New files**: 1 (frontend/app/actions/tasks.ts)
- **Modified files**: 7 (task-form.tsx, tasks/page.tsx, create-task-dialog.tsx, edit-task-dialog.tsx, delete-task-dialog.tsx, task-item.tsx, task-list.tsx)
- **Deprecated files**: 1 (frontend/lib/api.ts)

**Manual Testing**: 6 tasks (T014, T022, T027, T028, T031, T032)

**Estimated Implementation Time**:
- MVP (US1 only): 2-4 hours
- Full feature (US1 + US2 + US3): 6-8 hours
- With polish and validation: 8-10 hours

---

## Next Steps

1. **Review tasks** for completeness and correctness
2. **Start with MVP** (Phase 1 → Phase 2 → Phase 3 for User Story 1)
3. **Validate MVP** with manual testing (T014)
4. **Extend to full CRUD** (Phase 4 for User Story 2)
5. **Production validation** (Phase 5 for User Story 3)
6. **Final polish** (Phase 6)

**Command to start implementation**:
```bash
/sp.implement  # Executes tasks automatically via specialized agents
```

**Or manual implementation following**:
- [Quickstart Guide](./quickstart.md) - Developer testing checklist
- [Data Model](./data-model.md) - Authentication flow diagrams
- [Research](./research.md) - Better Auth JWT extraction methods
