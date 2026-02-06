# Tasks: Multi-User Todo Frontend with Authentication

**Input**: Design documents from `/specs/002-frontend-auth/`
**Prerequisites**: plan.md (complete), spec.md (complete, 6 user stories with priorities)

**Tests**: Manual testing only - no automated test tasks per spec FR-014 and constitution justified deviation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` directory with Next.js App Router structure
- Paths follow Next.js 16+ conventions: `app/`, `components/`, `lib/`, `hooks/`, `types/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure

- [ ] T001 Configure environment variables in frontend/.env.local (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL)
- [ ] T002 [P] Install Better Auth and JWT plugin via npm (better-auth @better-auth/jwt)
- [ ] T003 [P] Install form validation libraries via npm (zod react-hook-form @hookform/resolvers sonner)
- [ ] T004 [P] Install shadcn/ui components via npx shadcn (button card input form checkbox dialog toast skeleton alert-dialog label textarea)
- [ ] T005 Verify Next.js 16+ setup and run npm run dev successfully

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create TypeScript types for Task entity in frontend/types/task.ts (Task, TaskCreateInput, TaskUpdateInput matching backend schemas)
- [ ] T007 Configure Better Auth client with JWT plugin in frontend/lib/auth.ts (createAuthClient, jwtPlugin, 7-day expiry)
- [ ] T008 [P] Create Better Auth API route handler in frontend/app/api/auth/[...all]/route.ts
- [ ] T009 Implement API client with automatic JWT attachment in frontend/lib/api.ts (fetchWithAuth helper, 401 redirect, typed methods)
- [ ] T010 [P] Create custom auth hook in frontend/hooks/use-auth.ts (useAuth with session state, loading, logout)
- [ ] T011 Implement Next.js middleware for protected routes in frontend/middleware.ts (session check, redirect logic)
- [ ] T012 [P] Configure toast notifications in frontend/app/layout.tsx (Toaster from sonner, positioned top-right)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Account Creation and First Login (Priority: P1) 🎯 MVP

**Goal**: Implement complete authentication flow allowing new users to create accounts, login, and access a protected dashboard. This is the minimal viable product.

**Independent Test**: Create account via signup form → login with credentials → verify redirect to protected /tasks dashboard → verify httpOnly cookie exists in DevTools

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create login form component in frontend/components/auth/login-form.tsx (shadcn/ui Card, Input, Button, email/password validation, toast feedback)
- [ ] T014 [P] [US1] Create signup form component in frontend/components/auth/signup-form.tsx (shadcn/ui Card, Input, Button, email/password validation, toast feedback)
- [ ] T015 [P] [US1] Create login page in frontend/app/login/page.tsx (server component, import LoginForm, link to signup)
- [ ] T016 [P] [US1] Create signup page in frontend/app/signup/page.tsx (server component, import SignupForm, link to login)
- [ ] T017 [US1] Update root page redirect logic in frontend/app/page.tsx (check session, redirect authenticated to /tasks, unauthenticated to /login)
- [ ] T018 [US1] Create empty tasks page scaffold in frontend/app/tasks/page.tsx (server component with header, placeholder content)
- [ ] T019 [US1] Manual test: Signup flow (create account → JWT cookie → redirect to /tasks)
- [ ] T020 [US1] Manual test: Login flow (valid credentials → JWT cookie → redirect to /tasks)
- [ ] T021 [US1] Manual test: Invalid credentials (error toast, remain on login page)
- [ ] T022 [US1] Manual test: Protected route (visit /tasks without auth → redirect to /login)
- [ ] T023 [US1] Manual test: Auth redirect (login → visit /login → redirect to /tasks)
- [ ] T024 [US1] Manual test: Root redirect (/ without auth → /login, / with auth → /tasks)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can signup, login, and access protected dashboard independently

---

## Phase 4: User Story 6 - Session Management and Logout (Priority: P2)

**Goal**: Implement logout functionality to securely end sessions and redirect users to login page

**Independent Test**: Login → click logout button → verify JWT cookie cleared → verify redirect to /login → attempt to access /tasks → verify redirect to /login

**Why This Order**: Logout is foundational for multi-user scenarios and should be implemented before task features to enable proper session management during development

### Implementation for User Story 6

- [ ] T025 [US6] Create header component with logout in frontend/components/layout/header.tsx (useAuth hook, user email display, logout button with onClick)
- [ ] T026 [US6] Add header to tasks page layout in frontend/app/tasks/page.tsx (import Header component)
- [ ] T027 [US6] Manual test: Logout button (click logout → session cleared → redirect to /login within 1s)
- [ ] T028 [US6] Manual test: Cookie cleared (verify JWT cookie removed in DevTools after logout)
- [ ] T029 [US6] Manual test: Protected access after logout (logout → try /tasks → redirect to /login)
- [ ] T030 [US6] Manual test: Multi-tab logout (logout in tab A → verify tab B also logged out on navigation)

**Checkpoint**: At this point, User Story 1 AND 6 work independently - complete auth flow with secure logout

---

## Phase 5: User Story 2 - View and Manage Personal Task List (Priority: P2)

**Goal**: Display authenticated user's task list with clear completion status indicators, responsive layout, and empty state UI

**Independent Test**: Login as user with tasks → verify only own tasks displayed → verify completion status visible → verify responsive on mobile (320px) and desktop (1920px) → login as different user → verify data isolation

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create empty state component in frontend/components/tasks/empty-state.tsx (server component, shadcn/ui with "Add Task" placeholder)
- [ ] T032 [P] [US2] Create task skeleton loading component in frontend/components/tasks/task-skeleton.tsx (Skeleton from shadcn/ui, card layout)
- [ ] T033 [US2] Create task item component in frontend/components/tasks/task-item.tsx (client component, shadcn/ui Card, Checkbox, completed styling with line-through, edit/delete button placeholders)
- [ ] T034 [US2] Create task list client component in frontend/components/tasks/task-list.tsx (client component, state management, map tasks to TaskItem, header with title)
- [ ] T035 [US2] Implement tasks page with data fetching in frontend/app/tasks/page.tsx (async server component, getSession, api.tasks.list, conditional render TaskList or EmptyState, Suspense with skeleton)
- [ ] T036 [US2] Add responsive styling to all task components (Tailwind breakpoints: sm:, md:, lg:, touch-friendly targets min 44x44px)
- [ ] T037 [US2] Manual test: Task list load (login → tasks load within 2s)
- [ ] T038 [US2] Manual test: Empty state (login with no tasks → see empty state UI)
- [ ] T039 [US2] Manual test: Completion status (tasks with completed=true show line-through style)
- [ ] T040 [US2] Manual test: Responsive mobile (resize to 320px → no horizontal scroll, all elements readable)
- [ ] T041 [US2] Manual test: Responsive desktop (resize to 1920px → proper spacing, no awkward layouts)
- [ ] T042 [US2] Manual test: Multi-user isolation (login as User A → create tasks → login as User B → verify User A tasks NOT visible)
- [ ] T043 [US2] Manual test: 401 handling (expire token or backend down → redirect to /login)

**Checkpoint**: At this point, User Stories 1, 2, and 6 work independently - auth flow + task viewing + logout

---

## Phase 6: User Story 3 - Create New Tasks (Priority: P2)

**Goal**: Implement task creation form allowing users to add new tasks with title and optional description, see immediate feedback with toast notifications

**Independent Test**: Login → click "Add Task" → fill title and description → submit → verify new task appears in list → verify success toast → test validation by submitting empty title → verify error toast on API failure

### Implementation for User Story 3

- [ ] T044 [P] [US3] Create task form component in frontend/components/tasks/task-form.tsx (client component, react-hook-form with zod schema, shadcn/ui Form/Input/Textarea/Button, title 1-200 chars required, description optional max 1000 chars, loading state)
- [ ] T045 [US3] Create task creation dialog in frontend/components/tasks/create-task-dialog.tsx (client component, shadcn/ui Dialog, "Add Task" trigger button, TaskForm with onSuccess callback to close dialog)
- [ ] T046 [US3] Integrate create dialog into task list in frontend/components/tasks/task-list.tsx (add CreateTaskDialog to header, handleTaskCreated to prepend new task to state)
- [ ] T047 [US3] Implement task.create API method in frontend/lib/api.ts (POST /api/{user_id}/tasks with TaskCreateInput body, return Task)
- [ ] T048 [US3] Manual test: Task creation success (click Add Task → fill form → submit → task appears in list within 15s → success toast)
- [ ] T049 [US3] Manual test: Validation empty title (submit without title → see inline validation error, submission blocked)
- [ ] T050 [US3] Manual test: Validation title length (submit 201+ chars → see validation error)
- [ ] T051 [US3] Manual test: Optional description (create task without description → succeeds)
- [ ] T052 [US3] Manual test: API error handling (backend down → submit form → error toast with user-friendly message)
- [ ] T053 [US3] Manual test: JWT header (DevTools Network → verify Authorization: Bearer header on create request)
- [ ] T054 [US3] Manual test: Keyboard navigation (Tab through form fields → Enter submits → Escape closes dialog)

**Checkpoint**: At this point, User Stories 1-3 and 6 work independently - auth + view + create + logout

---

## Phase 7: User Story 4 - Update and Complete Tasks (Priority: P3)

**Goal**: Implement task editing form and checkbox toggling for completion status with optimistic UI updates

**Independent Test**: Login → edit task title/description → verify changes persist → toggle checkbox → verify immediate UI update → verify API call → test error revert by simulating network failure

### Implementation for User Story 4

- [ ] T055 [P] [US4] Create edit task dialog in frontend/components/tasks/edit-task-dialog.tsx (client component, shadcn/ui Dialog, "Edit" trigger button, reuse TaskForm with task prop, onSuccess callback)
- [ ] T056 [US4] Implement optimistic toggle in task item in frontend/components/tasks/task-item.tsx (handleToggle with setState before API call, revert on error, toast feedback)
- [ ] T057 [US4] Integrate edit dialog into task item in frontend/components/tasks/task-item.tsx (replace edit button placeholder with EditTaskDialog, handleTaskUpdated callback)
- [ ] T058 [US4] Implement task.update API method in frontend/lib/api.ts (PUT /api/{user_id}/tasks/{task_id} with TaskUpdateInput, return Task)
- [ ] T059 [US4] Implement task.toggleComplete API method in frontend/lib/api.ts (PATCH /api/{user_id}/tasks/{task_id}/complete, return Task)
- [ ] T060 [US4] Update task list to handle updates in frontend/components/tasks/task-list.tsx (handleTaskUpdated to map and replace updated task in state)
- [ ] T061 [US4] Manual test: Edit task (click Edit → modify title → save → changes reflected in list → success toast)
- [ ] T062 [US4] Manual test: Edit validation (edit to empty title → see validation error)
- [ ] T063 [US4] Manual test: Toggle complete (click checkbox → immediate visual update within 100ms → API call verifies)
- [ ] T064 [US4] Manual test: Toggle error revert (simulate network error → checkbox reverts → error toast)
- [ ] T065 [US4] Manual test: Completed styling (toggle to completed → line-through and gray text)
- [ ] T066 [US4] Manual test: JWT header on update (DevTools → verify Authorization header on PUT and PATCH)

**Checkpoint**: At this point, User Stories 1-4 and 6 work independently - full CRUD except delete

---

## Phase 8: User Story 5 - Delete Unwanted Tasks (Priority: P3)

**Goal**: Implement task deletion with confirmation dialog to prevent accidental deletions

**Independent Test**: Login → click delete on task → verify confirmation dialog → cancel → verify task remains → click delete → confirm → verify task removed from list and database → verify success toast

### Implementation for User Story 5

- [ ] T067 [US5] Create delete confirmation dialog in frontend/components/tasks/delete-task-dialog.tsx (client component, shadcn/ui AlertDialog, "Delete" trigger button, confirmation text, Cancel/Delete actions with loading state)
- [ ] T068 [US5] Integrate delete dialog into task item in frontend/components/tasks/task-item.tsx (replace delete button placeholder with DeleteTaskDialog, handleTaskDeleted callback)
- [ ] T069 [US5] Implement task.delete API method in frontend/lib/api.ts (DELETE /api/{user_id}/tasks/{task_id})
- [ ] T070 [US5] Update task list to handle deletions in frontend/components/tasks/task-list.tsx (handleTaskDeleted to filter out deleted task from state)
- [ ] T071 [US5] Manual test: Delete confirmation (click Delete → dialog appears with warning text)
- [ ] T072 [US5] Manual test: Cancel delete (click Cancel → dialog closes, task remains in list)
- [ ] T073 [US5] Manual test: Confirm delete (click Delete → Confirm → task removed from list → success toast)
- [ ] T074 [US5] Manual test: Delete API call (DevTools → verify DELETE request with JWT header)
- [ ] T075 [US5] Manual test: Delete error (backend down → error toast, task remains)

**Checkpoint**: All user stories (1-6) now fully functional - complete feature set implemented

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, final production readiness

- [ ] T076 [P] Implement user-friendly error parsing in frontend/lib/api.ts (parseError function mapping technical errors to user messages)
- [ ] T077 [P] Add keyboard navigation verification across all pages (Tab order: Email → Password → Submit → Links; Escape closes dialogs)
- [ ] T078 [P] Verify responsive design at all breakpoints (320px, 768px, 1024px, 1920px - no horizontal scroll, touch targets 44x44px min)
- [ ] T079 [P] Add scroll position preservation in frontend/components/tasks/task-list.tsx (maintain scroll after create/update/delete)
- [ ] T080 [P] Implement loading state for task list initial load in frontend/app/tasks/page.tsx (Suspense with TaskListSkeleton)
- [ ] T081 Run TypeScript build check (npm run build → verify no type errors)
- [ ] T082 Run ESLint check (npm run lint → fix all warnings)
- [ ] T083 Remove all console.logs from production code
- [ ] T084 Create .env.example in frontend/ (document NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL with placeholder values)
- [ ] T085 Update frontend/CLAUDE.md with new component structure and patterns (document auth/, tasks/, layout/ organization)
- [ ] T086 Manual test: Multi-user isolation end-to-end (User A creates tasks → User B login → verify 0% data leakage → DevTools verify user_id in API paths)
- [ ] T087 Manual test: All 30 functional requirements (FR-001 to FR-030 from spec.md)
- [ ] T088 Manual test: All 15 success criteria (SC-001 to SC-015 from spec.md)
- [ ] T089 Manual test: Performance benchmarks (task list load <2s, optimistic updates <100ms, auth redirects <500ms)
- [ ] T090 Manual test: Accessibility (keyboard-only navigation through entire app, focus indicators visible, no keyboard traps)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 6 (P2): Can start after Foundational - No dependencies (runs after US1 for logical flow)
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories
  - User Story 3 (P2): Can start after Foundational - Integrates with US2 (task list state)
  - User Story 4 (P3): Can start after Foundational - Integrates with US2 (task list state)
  - User Story 5 (P3): Can start after Foundational - Integrates with US2 (task list state)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - auth flow with protected dashboard
- **User Story 6 (P2)**: Independent - logout functionality (runs after US1 for dev workflow)
- **User Story 2 (P2)**: Independent - task viewing (integrates with US1 via auth)
- **User Story 3 (P2)**: Soft dependency on US2 (needs task list component to show created tasks)
- **User Story 4 (P3)**: Soft dependency on US2 (needs task list component to show updated tasks)
- **User Story 5 (P3)**: Soft dependency on US2 (needs task list component to remove deleted tasks)

### Within Each User Story

- Components can be created in parallel if marked [P]
- Pages depend on their component imports
- Manual tests run after implementation complete
- Each story should be testable independently before moving to next

### Parallel Opportunities

- All Setup tasks (T002, T003, T004) can run in parallel
- All Foundational tasks (T008, T010, T012) can run in parallel within phase
- Within US1: T013, T014, T015, T016 can run in parallel (different components/pages)
- Within US2: T031, T032, T033 can run in parallel (different components)
- Within US3: T044, T045 can run in parallel initially
- Within US4: T055, T056 can start in parallel
- Within US5: T067, T069 can start in parallel
- Within Polish: T076, T077, T078, T079, T080 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all auth components together:
Task: "T013 - Create login form component in frontend/components/auth/login-form.tsx"
Task: "T014 - Create signup form component in frontend/components/auth/signup-form.tsx"
Task: "T015 - Create login page in frontend/app/login/page.tsx"
Task: "T016 - Create signup page in frontend/app/signup/page.tsx"

# Then integrate:
Task: "T017 - Update root page redirect logic in frontend/app/page.tsx"
Task: "T018 - Create empty tasks page scaffold in frontend/app/tasks/page.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all task display components together:
Task: "T031 - Create empty state component in frontend/components/tasks/empty-state.tsx"
Task: "T032 - Create task skeleton loading component in frontend/components/tasks/task-skeleton.tsx"
Task: "T033 - Create task item component in frontend/components/tasks/task-item.tsx"

# Then integrate:
Task: "T034 - Create task list client component in frontend/components/tasks/task-list.tsx"
Task: "T035 - Implement tasks page with data fetching in frontend/app/tasks/page.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 6 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T013-T024) - Auth flow
4. Complete Phase 4: User Story 6 (T025-T030) - Logout
5. **STOP and VALIDATE**: Test auth flow + logout independently
6. Deploy/demo if ready (functional auth system)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 6 → Test independently → Deploy/Demo (MVP: Auth + Logout)
3. Add User Story 2 → Test independently → Deploy/Demo (View tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (Create tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (Edit + Complete)
6. Add User Story 5 → Test independently → Deploy/Demo (Delete tasks)
7. Polish phase → Final production readiness
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012)
2. Once Foundational is done:
   - Developer A: User Story 1 (T013-T024)
   - Developer B: User Story 6 (T025-T030) - can run parallel with US1
   - Developer C: User Story 2 (T031-T043) - can run parallel with US1/US6
3. Once US1+US6+US2 complete:
   - Developer A: User Story 3 (T044-T054)
   - Developer B: User Story 4 (T055-T066)
   - Developer C: User Story 5 (T067-T075)
4. All developers: Polish phase together (T076-T090)

---

## Task Summary

**Total Tasks**: 90
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US1 - Auth): 12 tasks
- Phase 4 (US6 - Logout): 6 tasks
- Phase 5 (US2 - View Tasks): 13 tasks
- Phase 6 (US3 - Create Tasks): 11 tasks
- Phase 7 (US4 - Update/Complete): 12 tasks
- Phase 8 (US5 - Delete Tasks): 9 tasks
- Phase 9 (Polish): 15 tasks

**Parallel Opportunities**: 25 tasks marked [P] can run in parallel
**Independent Stories**: All 6 user stories can be tested independently
**MVP Scope**: User Story 1 + 6 (18 tasks) = functional auth system

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing strategy per spec (no automated tests)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are absolute from repository root (frontend/ directory)
- Follow Next.js 16+ App Router conventions throughout
- Use shadcn/ui components exclusively per spec FR-018
- All styling via Tailwind CSS per spec FR-019
- Server components by default, client components ('use client') only for interactivity per spec FR-023
