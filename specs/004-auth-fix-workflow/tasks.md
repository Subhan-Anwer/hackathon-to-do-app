---
description: "Task breakdown for Authentication & Workflow Reliability Fixes"
---

# Tasks: Authentication & Workflow Reliability Fixes

**Input**: Design documents from `/specs/004-auth-fix-workflow/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), contracts/auth-flow.md

**Tests**: Manual testing only (no automated test tasks) - see Step 7 for comprehensive manual test checklist

**Organization**: Tasks are grouped by user story priority (P1, P2, P3) to enable sequential implementation with independent verification at each step.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1=Local Dev Auth, US2=Production HTTPS Auth, US3=Error Feedback, US4=Loading States, US5=Toast Notifications)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/lib/`, `frontend/components/`
- **Backend**: `backend/` (no changes needed - already supports dual authentication)
- This is a web application monorepo structure

---

## Phase 1: Setup (Prerequisites Verification)

**Purpose**: Verify existing project structure and dependencies are ready for authentication fixes

- [ ] T001 Verify Better Auth is installed in frontend/package.json (better-auth dependency)
- [ ] T002 Verify sonner toast library is installed in frontend/package.json (for notifications)
- [ ] T003 Verify BETTER_AUTH_SECRET is set in frontend/.env.local and backend/.env
- [ ] T004 Verify backend is running and accepts JWT authentication (test health endpoint)

**Checkpoint**: All dependencies verified - ready to implement authentication fixes

---

## Phase 2: User Story 1 - Authenticated Task Creation Flow (Priority: P1) 🎯 MVP

**Goal**: Enable JWT plugin and environment-aware cookies so logged-in users can create/manage tasks without 401 errors on localhost HTTP

**Independent Test**: Sign in → create task → verify task appears in list without 401 errors, JWT visible in DevTools with `sub` claim

### Step 1: Enable Better Auth JWT Plugin (Implementation Tasks)

- [ ] T005 [US1] Add JWT plugin import to frontend/lib/auth.ts (line 20)
- [ ] T006 [US1] Add jwt() to plugins array in frontend/lib/auth.ts (line 83-85, before nextCookies)
- [ ] T007 [US1] Verify TypeScript compilation succeeds for frontend/lib/auth.ts
- [ ] T008 [US1] Test JWT plugin: sign up new user, verify session cookie contains JWT with sub claim in DevTools

### Step 2: Fix Cookie Attributes for Localhost Compatibility (Implementation Tasks)

- [ ] T009 [US1] Replace static cookie attributes with environment-aware logic in frontend/lib/auth.ts (lines 71-74)
- [ ] T010 [US1] Add conditional for sameSite: process.env.NODE_ENV === "production" ? "none" : "lax"
- [ ] T011 [US1] Add conditional for secure: process.env.NODE_ENV === "production"
- [ ] T012 [US1] Verify TypeScript compilation succeeds for frontend/lib/auth.ts
- [ ] T013 [US1] Test cookie attributes: verify sameSite=Lax and secure=false in DevTools for localhost
- [ ] T014 [US1] Test cookie transmission: create task, verify Cookie header sent in Network tab

### Step 3: Add Authorization Bearer Header (Implementation Tasks)

- [ ] T015 [US1] Import authClient from frontend/lib/auth-client.ts in frontend/lib/api.ts (line 1)
- [ ] T016 [US1] Modify fetchWithAuth to call authClient.getSession() in frontend/lib/api.ts (line 54)
- [ ] T017 [US1] Extract token from session.session.token in frontend/lib/api.ts
- [ ] T018 [US1] Add Authorization: Bearer header when token available in frontend/lib/api.ts (line 58-62)
- [ ] T019 [US1] Preserve credentials: "include" for cookie fallback in frontend/lib/api.ts
- [ ] T020 [US1] Verify TypeScript compilation succeeds for frontend/lib/api.ts
- [ ] T021 [US1] Test dual authentication: verify both Authorization and Cookie headers in Network tab
- [ ] T022 [US1] Verify backend logs show "User authenticated" for Bearer token requests

**Checkpoint**: User Story 1 complete - authenticated task operations work on localhost HTTP without 401 errors, JWT plugin enabled, cookies work on HTTP, Bearer header sent

---

## Phase 3: User Story 2 - Production HTTPS Authentication (Priority: P2)

**Goal**: Ensure authentication works correctly in production HTTPS environment with secure cookies

**Independent Test**: Deploy to production HTTPS → sign in → verify session cookie has sameSite=None and secure=true → create task successfully

### Production Environment Configuration (Implementation Tasks)

- [ ] T023 [US2] Document NODE_ENV=production requirement in frontend/.env.example
- [ ] T024 [US2] Document production cookie behavior in specs/004-auth-fix-workflow/TESTING.md (Phase 8)
- [ ] T025 [US2] Verify environment-aware code from US1 handles production correctly (manual code review)

**Checkpoint**: User Story 2 complete - environment-aware configuration supports both localhost HTTP (dev) and production HTTPS

---

## Phase 4: User Story 3 - Clear Authentication Error Feedback (Priority: P2)

**Goal**: Show user-friendly toast notifications when authentication fails (401 errors) before redirecting to login

**Independent Test**: Delete session cookie → attempt task operation → verify toast appears "Your session has expired..." → verify redirect to /login after 1.5s

### Enhance 401 Error Handling (Implementation Tasks)

- [ ] T026 [P] [US3] Import toast from "sonner" in frontend/lib/api.ts (line 1)
- [ ] T027 [US3] Add toast.error() call on 401 in frontend/lib/api.ts (line 64)
- [ ] T028 [US3] Wrap redirect in setTimeout with 1500ms delay in frontend/lib/api.ts (line 66-70)
- [ ] T029 [US3] Verify TypeScript compilation succeeds for frontend/lib/api.ts
- [ ] T030 [US3] Test 401 handling: delete cookie manually, attempt operation, verify toast visible before redirect
- [ ] T031 [US3] Test redirect timing: verify redirect occurs 1.5 seconds after toast appears

**Checkpoint**: User Story 3 complete - users receive clear feedback on authentication failures before redirect

---

## Phase 5: User Story 4 - Task Operation Loading States (Priority: P3)

**Goal**: Display loading indicators during task operations to provide immediate user feedback and prevent double-clicks

**Independent Test**: Create task → verify "Creating..." button text and button disabled → operation completes → button re-enables

### Add Loading States to Task Components (Implementation Tasks)

- [ ] T032 [P] [US4] Add isLoading state to CreateTaskDialog in frontend/components/tasks/create-task-dialog.tsx
- [ ] T033 [P] [US4] Add isLoading state to EditTaskDialog in frontend/components/tasks/edit-task-dialog.tsx
- [ ] T034 [P] [US4] Add isLoading state to DeleteTaskDialog in frontend/components/tasks/delete-task-dialog.tsx
- [ ] T035 [P] [US4] Add isLoading state to task toggle checkbox in frontend/components/tasks/task-item.tsx
- [ ] T036 [US4] Update submit button to show loading text in create-task-dialog.tsx ("Creating..." when isLoading)
- [ ] T037 [US4] Update submit button to show loading text in edit-task-dialog.tsx ("Saving..." when isLoading)
- [ ] T038 [US4] Update delete button to show loading text in delete-task-dialog.tsx ("Deleting..." when isLoading)
- [ ] T039 [US4] Disable submit buttons during operations using disabled={isLoading} prop
- [ ] T040 [US4] Disable checkbox during toggle operation in task-item.tsx
- [ ] T041 [US4] Set isLoading=true at start of handleSubmit/handleDelete/handleToggle functions
- [ ] T042 [US4] Set isLoading=false in finally blocks after operations complete
- [ ] T043 [US4] Verify TypeScript compilation succeeds for all modified components
- [ ] T044 [US4] Test loading states: verify buttons disabled and show loading text during API calls
- [ ] T045 [US4] Test button re-enable: verify buttons become enabled after operation completes
- [ ] T046 [US4] Test loading feedback appears within 200ms of action (performance requirement)

**Checkpoint**: User Story 4 complete - all task operations show immediate loading feedback and prevent duplicate submissions

---

## Phase 6: User Story 5 - Task Operation Toast Notifications (Priority: P3)

**Goal**: Show success and error toast notifications for task operations with automatic list refresh

**Independent Test**: Create task → verify "Task created successfully!" toast → verify task appears in list within 1 second

### Add Toast Notifications to Task Operations (Implementation Tasks)

- [ ] T047 [P] [US5] Import toast from "sonner" in frontend/components/tasks/create-task-dialog.tsx
- [ ] T048 [P] [US5] Import toast from "sonner" in frontend/components/tasks/edit-task-dialog.tsx
- [ ] T049 [P] [US5] Import toast from "sonner" in frontend/components/tasks/delete-task-dialog.tsx
- [ ] T050 [P] [US5] Import toast from "sonner" in frontend/components/tasks/task-item.tsx
- [ ] T051 [US5] Add toast.success("Task created successfully!") to create-task-dialog.tsx on success
- [ ] T052 [US5] Add toast.error() with descriptive message to create-task-dialog.tsx on error
- [ ] T053 [US5] Add toast.success("Task updated successfully!") to edit-task-dialog.tsx on success
- [ ] T054 [US5] Add toast.error() with descriptive message to edit-task-dialog.tsx on error
- [ ] T055 [US5] Add toast.success("Task deleted successfully!") to delete-task-dialog.tsx on success
- [ ] T056 [US5] Add toast.error() with descriptive message to delete-task-dialog.tsx on error
- [ ] T057 [US5] Add conditional toast for toggle: "Task completed!" or "Task reopened!" in task-item.tsx
- [ ] T058 [US5] Add toast.error() for toggle failures in task-item.tsx
- [ ] T059 [US5] Implement refreshTasks callback in task-list.tsx to fetch latest tasks
- [ ] T060 [US5] Call refreshTasks in onTaskCreated callback after success toast
- [ ] T061 [US5] Call refreshTasks in onTaskUpdated callback after success toast
- [ ] T062 [US5] Call refreshTasks in onTaskDeleted callback after success toast
- [ ] T063 [US5] Call refreshTasks in onTaskToggled callback after success toast
- [ ] T064 [US5] Verify TypeScript compilation succeeds for all modified components
- [ ] T065 [US5] Test success toasts: verify "Task created/updated/deleted successfully!" messages appear
- [ ] T066 [US5] Test error toasts: disconnect backend, verify user-friendly error messages
- [ ] T067 [US5] Test list refresh: verify task list updates within 1 second after operations
- [ ] T068 [US5] Test toast timing: verify toasts appear within 1 second of operation completion
- [ ] T069 [US5] Test toast auto-dismiss: verify toasts disappear automatically after 3-5 seconds

**Checkpoint**: User Story 5 complete - all task operations provide clear success/error feedback with automatic list synchronization

---

## Phase 7: Manual Testing & Verification

**Purpose**: Comprehensive end-to-end validation of all authentication and UX fixes

### Create Manual Test Documentation (Documentation Tasks)

- [ ] T070 Create comprehensive manual test checklist in specs/004-auth-fix-workflow/TESTING.md
- [ ] T071 Document Phase 1: JWT Plugin Verification (sign up, decode JWT, verify sub claim)
- [ ] T072 Document Phase 2: Cookie Attributes Development (verify sameSite=Lax, secure=false)
- [ ] T073 Document Phase 3: Authorization Bearer Header (verify both headers sent)
- [ ] T074 Document Phase 4: 401 Error Handling (delete cookie, verify toast and redirect)
- [ ] T075 Document Phase 5: Loading States (verify disabled buttons, loading text)
- [ ] T076 Document Phase 6: Toast Notifications (verify success/error messages, list refresh)
- [ ] T077 Document Phase 7: Multi-User Isolation (create 2 users, verify data separation)
- [ ] T078 Document Phase 8: Production Environment (verify sameSite=None, secure=true on HTTPS)

### Execute Manual Testing (Validation Tasks)

- [ ] T079 Execute Phase 1 tests: JWT Plugin Verification (all checklist items pass)
- [ ] T080 Execute Phase 2 tests: Cookie Attributes Development (all checklist items pass)
- [ ] T081 Execute Phase 3 tests: Authorization Bearer Header (all checklist items pass)
- [ ] T082 Execute Phase 4 tests: 401 Error Handling (all checklist items pass)
- [ ] T083 Execute Phase 5 tests: Loading States (all checklist items pass)
- [ ] T084 Execute Phase 6 tests: Toast Notifications & List Refresh (all checklist items pass)
- [ ] T085 Execute Phase 7 tests: Multi-User Isolation (verify zero data leaks between users)
- [ ] T086 Document test results: record pass/fail for each phase in TESTING.md
- [ ] T087 Address any test failures: fix issues and re-test until all phases pass

**Checkpoint**: All 8 manual test phases pass - authentication and UX fixes verified end-to-end

---

## Phase 8: Documentation & Polish

**Purpose**: Update documentation and finalize implementation

- [ ] T088 [P] Update frontend/.env.example with NODE_ENV documentation
- [ ] T089 [P] Update frontend/CLAUDE.md with JWT plugin and environment-aware cookie details
- [ ] T090 [P] Update specs/004-auth-fix-workflow/plan.md with "Implemented" status
- [ ] T091 [P] Create ADR for environment-aware cookie configuration (optional but recommended)
- [ ] T092 Verify no TypeScript errors across entire frontend codebase (npm run build)
- [ ] T093 Verify no console.log statements in production code (code review)
- [ ] T094 Run ESLint and fix any warnings in modified files
- [ ] T095 Final smoke test: complete user flow from signup → signin → create task → verify in list

**Checkpoint**: Implementation complete, documented, and ready for commit/PR

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup completion - MUST complete before other user stories
- **User Story 2 (Phase 3)**: Depends on US1 completion (uses same environment-aware code)
- **User Story 3 (Phase 4)**: Depends on US1 completion (enhances existing 401 handling)
- **User Story 4 (Phase 5)**: Can start after US1, parallel with US2/US3
- **User Story 5 (Phase 6)**: Can start after US1, parallel with US2/US3/US4
- **Manual Testing (Phase 7)**: Depends on all user stories being complete
- **Documentation (Phase 8)**: Depends on Manual Testing phase passing

### User Story Dependencies

- **User Story 1 (P1)**: Foundational - blocks US2, US3, US4, US5
  - Reason: Establishes JWT plugin and environment-aware cookies that other stories build upon
- **User Story 2 (P2)**: Depends on US1 (verifies same code works in production)
- **User Story 3 (P2)**: Depends on US1 (enhances 401 handling in api.ts)
- **User Story 4 (P3)**: Depends on US1 (adds loading states to task operations)
- **User Story 5 (P3)**: Depends on US1 (adds toast notifications to task operations)

**Note**: US4 and US5 can be implemented in parallel after US1 completes (different component files)

### Within Each User Story

**User Story 1** (Sequential steps):
1. Enable JWT plugin (T005-T008) → MUST complete first
2. Fix cookie attributes (T009-T014) → Depends on JWT plugin
3. Add Bearer header (T015-T022) → Depends on JWT plugin and cookies

**User Story 2** (Documentation only):
- All tasks can run in parallel (T023-T025)

**User Story 3** (Sequential):
- All tasks modify same file (api.ts), must be sequential (T026-T031)

**User Story 4** (Parallel opportunities):
- Tasks T032-T035 can run in parallel (different component files)
- Tasks T036-T042 sequential per component (same file edits)
- Tasks T043-T046 sequential (validation tasks)

**User Story 5** (Parallel opportunities):
- Tasks T047-T050 can run in parallel (import statements in different files)
- Tasks T051-T058 sequential per component (same file edits)
- Tasks T059-T063 sequential (task-list.tsx modifications)
- Tasks T064-T069 sequential (validation tasks)

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run in parallel (T001-T004)

**Phase 2 (US1)**:
- No parallel opportunities - sequential steps required

**Phase 3 (US2)**:
- Tasks T023-T025 can run in parallel (documentation only)

**Phase 4 (US3)**:
- No parallel opportunities - all modify same file

**Phase 5 (US4)**:
- Initial state additions to different components (T032-T035) can run in parallel
- Other tasks sequential per component

**Phase 6 (US5)**:
- Toast imports for different components (T047-T050) can run in parallel
- Other tasks sequential per component

**Phase 7 (Manual Testing)**:
- Documentation tasks (T070-T078) can run in parallel
- Execution tasks (T079-T087) must be sequential (depends on implementation)

**Phase 8 (Documentation)**:
- Tasks T088-T091 can run in parallel (different files)
- Tasks T092-T095 sequential (validation tasks)

---

## Parallel Example: User Story 4 (Loading States)

```bash
# Launch initial state additions together (different component files):
Task T032: "Add isLoading state to CreateTaskDialog"
Task T033: "Add isLoading state to EditTaskDialog"
Task T034: "Add isLoading state to DeleteTaskDialog"
Task T035: "Add isLoading state to task toggle checkbox"

# Then sequentially update each component with loading text, disabling, etc.
```

---

## Parallel Example: User Story 5 (Toast Notifications)

```bash
# Launch toast imports together (different component files):
Task T047: "Import toast in create-task-dialog.tsx"
Task T048: "Import toast in edit-task-dialog.tsx"
Task T049: "Import toast in delete-task-dialog.tsx"
Task T050: "Import toast in task-item.tsx"

# Then sequentially add toast.success/error calls per component
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: User Story 1 (T005-T022)
3. **STOP and VALIDATE**: Test US1 independently
   - Sign in → create task → verify no 401 errors
   - Check DevTools: JWT with sub claim, cookies sent on localhost HTTP
   - Verify both Authorization and Cookie headers in Network tab
4. If US1 passes: Proceed to US2-US5 or stop at minimal fix

### Incremental Delivery (Recommended)

1. Complete Setup (Phase 1) → Dependencies verified
2. Complete US1 (Phase 2) → Core auth fixes working ✅
3. Complete US2 (Phase 3) → Production-ready ✅
4. Complete US3 (Phase 4) → Better error UX ✅
5. Complete US4 (Phase 5) → Loading feedback ✅
6. Complete US5 (Phase 6) → Complete UX polish ✅
7. Complete Manual Testing (Phase 7) → Validated end-to-end
8. Complete Documentation (Phase 8) → Ready for commit/PR

### Sequential Strategy (Single Developer)

With one developer, follow priority order:

1. Phase 1: Setup (verify environment)
2. Phase 2: US1 (P1) - Core authentication fixes
3. Phase 3: US2 (P2) - Production verification
4. Phase 4: US3 (P2) - Error feedback
5. Phase 5: US4 (P3) - Loading states
6. Phase 6: US5 (P3) - Toast notifications
7. Phase 7: Manual testing
8. Phase 8: Documentation

Each user story is independently testable at completion.

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[US#] label**: Maps task to specific user story for traceability
- **Sequential steps in US1**: JWT plugin → cookie attributes → Bearer header (order matters)
- **US4 and US5**: Can run in parallel after US1 (different component files)
- **No automated tests**: All validation via manual testing (Phase 7)
- **Stop at any checkpoint**: Each user story should be independently verifiable
- **Constitution compliance**: All changes maintain user isolation (backend unchanged)
- **Commits**: Commit after completing each user story phase for clean history

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (US1 - P1)**: 18 tasks
- **Phase 3 (US2 - P2)**: 3 tasks
- **Phase 4 (US3 - P2)**: 6 tasks
- **Phase 5 (US4 - P3)**: 15 tasks
- **Phase 6 (US5 - P3)**: 23 tasks
- **Phase 7 (Testing)**: 9 tasks
- **Phase 8 (Polish)**: 8 tasks

**Total**: 95 tasks across 8 phases

**MVP Scope**: Phases 1-2 (22 tasks) = Core authentication fixes

**Parallel Opportunities**:
- Phase 1: 4 tasks can run in parallel
- Phase 3: 3 tasks can run in parallel
- Phase 5: 4 tasks can run in parallel (initial state additions)
- Phase 6: 4 tasks can run in parallel (toast imports)
- Phase 8: 4 tasks can run in parallel (documentation)

**Independent Test Criteria Met**:
- ✅ US1: Testable after T022 (sign in → create task → no 401)
- ✅ US2: Testable after T025 (production cookie attributes verified)
- ✅ US3: Testable after T031 (delete cookie → verify toast → redirect)
- ✅ US4: Testable after T046 (all loading states working)
- ✅ US5: Testable after T069 (all toasts and list refresh working)
