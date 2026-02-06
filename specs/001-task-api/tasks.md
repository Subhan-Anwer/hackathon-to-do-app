# Tasks: Multi-User Task Management API

**Input**: Design documents from `/specs/001-task-api/`
**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

**Tests**: Tests are included per Constitution Principle V (Test-First for Security-Critical Paths). Security and user isolation tests MUST be written and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` for FastAPI application
- All paths use `backend/` prefix per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [X] T001 Install production dependencies via uv: fastapi, uvicorn[standard], sqlmodel, asyncpg, python-jose[cryptography], python-multipart in backend/pyproject.toml
- [X] T002 Install development dependencies via uv: pytest, pytest-asyncio, httpx in backend/pyproject.toml
- [X] T003 Create environment variable template in backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, FRONTEND_ORIGIN
- [X] T004 Verify dependency installation by running uv sync and importing key packages

**Checkpoint**: ✅ Dependencies installed, project configured for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement async database connection with create_async_engine in backend/db.py
- [X] T006 Implement async session factory with sessionmaker in backend/db.py
- [X] T007 Implement get_db dependency function in backend/db.py for FastAPI dependency injection
- [X] T008 Create Task SQLModel with user_id index, UUID primary key, title (max 200), description (optional), completed (default false), timestamps in backend/models.py
- [X] T009 Create TaskCreate Pydantic schema with title validation (1-200 chars) in backend/schemas.py
- [X] T010 Create TaskUpdate Pydantic schema with optional fields in backend/schemas.py
- [X] T011 Create TaskRead Pydantic schema excluding user_id in backend/schemas.py
- [X] T012 Implement get_current_user dependency with JWT validation (Authorization header + cookie fallback) in backend/dependencies.py
- [X] T013 Extract user_id from JWT 'sub' claim in get_current_user dependency in backend/dependencies.py
- [X] T014 Raise HTTPException 401 for missing/invalid tokens in get_current_user dependency in backend/dependencies.py
- [X] T015 Add logging for authentication failures in get_current_user dependency in backend/dependencies.py
- [X] T016 Create tasks router with /api prefix in backend/routers/tasks.py
- [X] T017 Create empty __init__.py for routers package in backend/routers/__init__.py

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Personal Task List (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can retrieve all their tasks via GET endpoint with strict user isolation

**Independent Test**: Authenticate as User A, create 5 tasks, verify GET returns exactly 5 tasks. Authenticate as User B, verify GET returns empty list (User A's tasks not visible).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T018 [P] [US1] Write test for GET /api/{user_id}/tasks returns 401 when no token provided in backend/tests/test_auth.py
- [X] T019 [P] [US1] Write test for GET /api/{user_id}/tasks returns 403 when path user_id doesn't match token user_id in backend/tests/test_isolation.py
- [X] T020 [P] [US1] Write test for User A cannot see User B's tasks via GET endpoint in backend/tests/test_isolation.py
- [X] T021 [P] [US1] Write test for GET /api/{user_id}/tasks returns empty list for new user in backend/tests/test_tasks.py
- [X] T022 [P] [US1] Write test for GET /api/{user_id}/tasks returns correct task count for authenticated user in backend/tests/test_tasks.py
- [X] T023 [US1] Create pytest conftest.py with test client, database, and mock JWT token fixtures in backend/tests/conftest.py

### Implementation for User Story 1

- [X] T024 [US1] Implement list_tasks endpoint GET /api/{user_id}/tasks in backend/routers/tasks.py
- [X] T025 [US1] Add user_id path parameter validation (verify matches current_user_id) in list_tasks endpoint
- [X] T026 [US1] Add HTTPException 403 Forbidden when user_id mismatch in list_tasks endpoint
- [X] T027 [US1] Add database query with user_id filter: select(Task).where(Task.user_id == user_id) in list_tasks endpoint
- [X] T028 [US1] Add logging for successful task retrieval and authorization failures in list_tasks endpoint
- [X] T029 [US1] Return List[TaskRead] response model in list_tasks endpoint

**Checkpoint**: ✅ User Story 1 fully functional - users can list their tasks with zero cross-user leaks

---

## Phase 4: User Story 2 - Create New Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create tasks with title and optional description

**Independent Test**: Authenticate as user, POST task with title "Buy groceries", verify task created with correct title, user_id, and default values (completed=false, timestamps set).

### Tests for User Story 2 ⚠️

- [X] T030 [P] [US2] Write test for POST /api/{user_id}/tasks returns 401 when no token in backend/tests/test_auth.py
- [X] T031 [P] [US2] Write test for POST /api/{user_id}/tasks returns 403 when user_id mismatch in backend/tests/test_isolation.py
- [X] T032 [P] [US2] Write test for POST /api/{user_id}/tasks returns 422 when title empty in backend/tests/test_tasks.py
- [X] T033 [P] [US2] Write test for POST /api/{user_id}/tasks returns 422 when title exceeds 200 chars in backend/tests/test_tasks.py
- [X] T034 [P] [US2] Write test for POST creates task with correct defaults (completed=false, timestamps) in backend/tests/test_tasks.py
- [X] T035 [P] [US2] Write test for POST creates task with title and description in backend/tests/test_tasks.py

### Implementation for User Story 2

- [X] T036 [US2] Implement create_task endpoint POST /api/{user_id}/tasks with 201 status in backend/routers/tasks.py
- [X] T037 [US2] Add user_id path parameter validation (verify matches current_user_id) in create_task endpoint
- [X] T038 [US2] Add HTTPException 403 Forbidden when user_id mismatch in create_task endpoint
- [X] T039 [US2] Create Task instance with authenticated user_id (NOT from path param) in create_task endpoint
- [X] T040 [US2] Set task title and description from TaskCreate schema in create_task endpoint
- [X] T041 [US2] Add task to database session, commit, and refresh in create_task endpoint
- [X] T042 [US2] Add logging for successful task creation in create_task endpoint
- [X] T043 [US2] Return TaskRead response model in create_task endpoint

**Checkpoint**: ✅ User Stories 1 AND 2 complete - users can list and create tasks (MVP achieved!)

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P2)

**Goal**: Authenticated users can toggle task completion status

**Independent Test**: Create incomplete task, PATCH /complete endpoint, verify completed=true. PATCH again, verify completed=false (toggle works both directions).

### Tests for User Story 3 ⚠️

- [X] T044 [P] [US3] Write test for PATCH /complete returns 401 when no token in backend/tests/test_auth.py
- [X] T045 [P] [US3] Write test for PATCH /complete returns 403 when user_id mismatch in backend/tests/test_isolation.py
- [X] T046 [P] [US3] Write test for PATCH /complete returns 404 when trying to complete other user's task in backend/tests/test_isolation.py
- [X] T047 [P] [US3] Write test for PATCH /complete toggles incomplete to complete in backend/tests/test_tasks.py
- [X] T048 [P] [US3] Write test for PATCH /complete toggles complete back to incomplete in backend/tests/test_tasks.py

### Implementation for User Story 3

- [X] T049 [US3] Implement toggle_task_completion endpoint PATCH /api/{user_id}/tasks/{task_id}/complete in backend/routers/tasks.py
- [X] T050 [US3] Add user_id path parameter validation (verify matches current_user_id) in toggle_task_completion endpoint
- [X] T051 [US3] Add HTTPException 403 Forbidden when user_id mismatch in toggle_task_completion endpoint
- [X] T052 [US3] Add database query with double filter: task_id AND user_id in toggle_task_completion endpoint
- [X] T053 [US3] Add HTTPException 404 Not Found when task doesn't exist or belongs to different user in toggle_task_completion endpoint
- [X] T054 [US3] Toggle task.completed status with 'not task.completed' in toggle_task_completion endpoint
- [X] T055 [US3] Update task.updated_at timestamp to datetime.utcnow() in toggle_task_completion endpoint
- [X] T056 [US3] Commit changes and refresh task in toggle_task_completion endpoint
- [X] T057 [US3] Add logging for successful completion toggle in toggle_task_completion endpoint
- [X] T058 [US3] Return TaskRead response model in toggle_task_completion endpoint

**Checkpoint**: ✅ User Stories 1, 2, AND 3 complete - full task lifecycle (create, list, complete)

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Authenticated users can update task title, description, and completion status

**Independent Test**: Create task, PUT with new title, verify title updated. PUT with new description, verify description updated. PUT with completed=true, verify status changed.

### Tests for User Story 4 ⚠️

- [X] T059 [P] [US4] Write test for PUT /tasks/{task_id} returns 401 when no token in backend/tests/test_auth.py
- [X] T060 [P] [US4] Write test for PUT /tasks/{task_id} returns 403 when user_id mismatch in backend/tests/test_isolation.py
- [X] T061 [P] [US4] Write test for PUT /tasks/{task_id} returns 404 when trying to update other user's task in backend/tests/test_isolation.py
- [X] T062 [P] [US4] Write test for PUT updates title only (partial update) in backend/tests/test_tasks.py
- [X] T063 [P] [US4] Write test for PUT updates description only (partial update) in backend/tests/test_tasks.py
- [X] T064 [P] [US4] Write test for PUT updates completed status in backend/tests/test_tasks.py
- [X] T065 [P] [US4] Write test for PUT returns 422 when title exceeds 200 chars in backend/tests/test_tasks.py

### Implementation for User Story 4

- [X] T066 [US4] Implement update_task endpoint PUT /api/{user_id}/tasks/{task_id} in backend/routers/tasks.py
- [X] T067 [US4] Add user_id path parameter validation (verify matches current_user_id) in update_task endpoint
- [X] T068 [US4] Add HTTPException 403 Forbidden when user_id mismatch in update_task endpoint
- [X] T069 [US4] Add database query with double filter: task_id AND user_id in update_task endpoint
- [X] T070 [US4] Add HTTPException 404 Not Found when task doesn't exist or belongs to different user in update_task endpoint
- [X] T071 [US4] Implement partial update logic (update only provided fields from TaskUpdate) in update_task endpoint
- [X] T072 [US4] Update task.updated_at timestamp to datetime.utcnow() in update_task endpoint
- [X] T073 [US4] Commit changes and refresh task in update_task endpoint
- [X] T074 [US4] Add logging for successful task update in update_task endpoint
- [X] T075 [US4] Return TaskRead response model in update_task endpoint

**Checkpoint**: ✅ User Stories 1-4 complete - full task management (create, list, complete, update)

---

## Phase 7: User Story 5 - View Single Task Details (Priority: P3)

**Goal**: Authenticated users can retrieve details of a specific task by ID

**Independent Test**: Create task, GET /tasks/{task_id}, verify full task details returned. Verify User A cannot GET User B's task (404 response).

### Tests for User Story 5 ⚠️

- [X] T076 [P] [US5] Write test for GET /tasks/{task_id} returns 401 when no token in backend/tests/test_auth.py
- [X] T077 [P] [US5] Write test for GET /tasks/{task_id} returns 403 when user_id mismatch in backend/tests/test_isolation.py
- [X] T078 [P] [US5] Write test for GET /tasks/{task_id} returns 404 when requesting other user's task in backend/tests/test_isolation.py
- [X] T079 [P] [US5] Write test for GET /tasks/{task_id} returns 404 when task doesn't exist in backend/tests/test_tasks.py
- [X] T080 [P] [US5] Write test for GET /tasks/{task_id} returns full task details in backend/tests/test_tasks.py

### Implementation for User Story 5

- [X] T081 [US5] Implement get_task endpoint GET /api/{user_id}/tasks/{task_id} in backend/routers/tasks.py
- [X] T082 [US5] Add user_id path parameter validation (verify matches current_user_id) in get_task endpoint
- [X] T083 [US5] Add HTTPException 403 Forbidden when user_id mismatch in get_task endpoint
- [X] T084 [US5] Add database query with double filter: task_id AND user_id in get_task endpoint
- [X] T085 [US5] Add HTTPException 404 Not Found when task doesn't exist or belongs to different user in get_task endpoint
- [X] T086 [US5] Add logging for successful task retrieval in get_task endpoint
- [X] T087 [US5] Return TaskRead response model in get_task endpoint

**Checkpoint**: ✅ User Stories 1-5 complete - full read/write capabilities

---

## Phase 8: User Story 6 - Delete Tasks (Priority: P3)

**Goal**: Authenticated users can permanently delete tasks they own

**Independent Test**: Create task, DELETE /tasks/{task_id}, verify task removed. Verify deleted task doesn't appear in GET /tasks list. Verify User A cannot delete User B's task (404 response).

### Tests for User Story 6 ⚠️

- [X] T088 [P] [US6] Write test for DELETE /tasks/{task_id} returns 401 when no token in backend/tests/test_auth.py
- [X] T089 [P] [US6] Write test for DELETE /tasks/{task_id} returns 403 when user_id mismatch in backend/tests/test_isolation.py
- [X] T090 [P] [US6] Write test for DELETE /tasks/{task_id} returns 404 when trying to delete other user's task in backend/tests/test_isolation.py
- [X] T091 [P] [US6] Write test for DELETE permanently removes task (verify not in list) in backend/tests/test_tasks.py
- [X] T092 [P] [US6] Write test for DELETE returns success response in backend/tests/test_tasks.py

### Implementation for User Story 6

- [X] T093 [US6] Implement delete_task endpoint DELETE /api/{user_id}/tasks/{task_id} in backend/routers/tasks.py
- [X] T094 [US6] Add user_id path parameter validation (verify matches current_user_id) in delete_task endpoint
- [X] T095 [US6] Add HTTPException 403 Forbidden when user_id mismatch in delete_task endpoint
- [X] T096 [US6] Add database query with double filter: task_id AND user_id in delete_task endpoint
- [X] T097 [US6] Add HTTPException 404 Not Found when task doesn't exist or belongs to different user in delete_task endpoint
- [X] T098 [US6] Delete task from database and commit in delete_task endpoint
- [X] T099 [US6] Add logging for successful task deletion in delete_task endpoint
- [X] T100 [US6] Return {"success": true} response in delete_task endpoint

**Checkpoint**: ✅ All user stories complete - full CRUD + completion toggle functionality

---

## Phase 9: Main Application Integration

**Purpose**: Wire all components together and add cross-cutting concerns

- [X] T101 Create FastAPI app instance with title and description in backend/main.py
- [X] T102 Configure CORS middleware with FRONTEND_ORIGIN environment variable in backend/main.py
- [X] T103 Set CORS allow_credentials=true for httpOnly cookies in backend/main.py
- [X] T104 Set CORS allow_methods to include GET, POST, PUT, DELETE, PATCH in backend/main.py
- [X] T105 Include tasks router in FastAPI app in backend/main.py
- [X] T106 Add startup event to create database tables with SQLModel.metadata.create_all in backend/main.py
- [X] T107 Add health check endpoint GET /health returning status and service name in backend/main.py
- [X] T108 Configure logging with basicConfig (INFO level, structured format) in backend/main.py

**Checkpoint**: ✅ Application fully integrated and runnable

---

## Phase 10: Error Handling & Database Resilience

**Purpose**: Graceful error handling for database failures

- [X] T109 [P] Wrap database operations in list_tasks with SQLAlchemyError exception handler in backend/routers/tasks.py
- [X] T110 [P] Wrap database operations in create_task with SQLAlchemyError exception handler in backend/routers/tasks.py
- [X] T111 [P] Wrap database operations in toggle_task_completion with SQLAlchemyError exception handler in backend/routers/tasks.py
- [X] T112 [P] Wrap database operations in update_task with SQLAlchemyError exception handler in backend/routers/tasks.py
- [X] T113 [P] Wrap database operations in get_task with SQLAlchemyError exception handler in backend/routers/tasks.py
- [X] T114 [P] Wrap database operations in delete_task with SQLAlchemyError exception handler in backend/routers/tasks.py
- [X] T115 Log database errors with detailed messages (without exposing to client) in all endpoints
- [X] T116 Return HTTPException 500 Internal Server Error for database failures in all endpoints

**Checkpoint**: ✅ Application handles database failures gracefully

---

## Phase 11: Polish & Validation

**Purpose**: Final checks and documentation updates

- [X] T117 Run all tests with pytest and verify 100% pass rate
- [X] T118 Test user isolation: create User A and User B tokens, verify complete isolation across all 6 endpoints
- [X] T119 Start server with uvicorn and verify health check responds correctly
- [X] T120 Verify quickstart.md instructions work end-to-end
- [X] T121 Test all 6 endpoints with curl commands from quickstart.md
- [X] T122 Verify SQL queries include user_id filter (check logs with echo=True)
- [X] T123 Verify all spec success criteria met (SC-001 to SC-008)
- [X] T124 Run security audit checklist from research.md

**Checkpoint**: ✅ Production-ready, all acceptance criteria met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Main Integration (Phase 9)**: Depends on at least User Story 1 and 2 (MVP)
- **Error Handling (Phase 10)**: Depends on all endpoints being implemented
- **Polish (Phase 11)**: Depends on all user stories and integration being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)

### Within Each User Story

- Tests (included) MUST be written and FAIL before implementation
- Tests can run in parallel (all marked [P])
- Implementation tasks run sequentially within story
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase**:
- T001-T004 can run together (dependency installation, env setup)

**Foundational Phase**:
- T005-T007 (database) can run together
- T008 (models) can run parallel with T005-T007
- T009-T011 (schemas) can run parallel with database/models
- T012-T015 (auth dependency) can run parallel with models/schemas
- T016-T017 (router setup) can run parallel with other foundational tasks

**User Story Tests**:
- All tests within a user story marked [P] can run in parallel
- Example: T018-T022 (US1 tests) can all run together

**User Story Implementation**:
- Different user stories can be worked on in parallel by different team members
- Example: After Foundational complete, Team Member A works on US1 while Team Member B works on US2

**Error Handling Phase**:
- T109-T114 (all marked [P]) can wrap different endpoints in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational Phase completes, launch all US1 tests in parallel:
Task T018: "Write test for GET /api/{user_id}/tasks returns 401 when no token provided"
Task T019: "Write test for GET /api/{user_id}/tasks returns 403 when path user_id doesn't match token user_id"
Task T020: "Write test for User A cannot see User B's tasks via GET endpoint"
Task T021: "Write test for GET /api/{user_id}/tasks returns empty list for new user"
Task T022: "Write test for GET /api/{user_id}/tasks returns correct task count for authenticated user"

# Verify all tests FAIL (no implementation yet)

# Then implement US1 sequentially:
Task T023: "Create pytest conftest.py with fixtures"
Task T024-T029: "Implement list_tasks endpoint"

# Verify all tests PASS
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational Phase completes, different team members work in parallel:

# Developer A: User Story 1 (View Tasks)
# Completes T018-T029

# Developer B: User Story 2 (Create Tasks)
# Completes T030-T043

# Developer C: User Story 3 (Mark Complete)
# Completes T044-T058

# All stories integrate independently without conflicts
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T017) - CRITICAL BLOCKING PHASE
3. Complete Phase 3: User Story 1 (T018-T029)
4. Complete Phase 4: User Story 2 (T030-T043)
5. Complete Phase 9: Main Integration (T101-T108)
6. **STOP and VALIDATE**: Test MVP independently
7. Deploy/demo if ready

**MVP Deliverable**: Users can list and create tasks with full JWT authentication and user isolation.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (View Tasks) → Test independently → Deploy/Demo
3. Add User Story 2 (Create Tasks) → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 (Mark Complete) → Test independently → Deploy/Demo
5. Add User Story 4 (Update Tasks) → Test independently → Deploy/Demo
6. Add User Story 5 (View Single) → Test independently → Deploy/Demo
7. Add User Story 6 (Delete Tasks) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T017)
2. Once Foundational is done:
   - Developer A: User Story 1 (T018-T029)
   - Developer B: User Story 2 (T030-T043)
   - Developer C: User Story 3 (T044-T058)
3. Stories complete and integrate independently
4. Team integrates in Phase 9 together
5. Team completes error handling and polish together

---

## Task Statistics

**Total Tasks**: 124
**Setup**: 4 tasks
**Foundational (BLOCKING)**: 13 tasks
**User Story 1 (P1)**: 12 tasks (6 tests + 6 implementation)
**User Story 2 (P1)**: 14 tasks (6 tests + 8 implementation)
**User Story 3 (P2)**: 15 tasks (5 tests + 10 implementation)
**User Story 4 (P2)**: 17 tasks (7 tests + 10 implementation)
**User Story 5 (P3)**: 12 tasks (5 tests + 7 implementation)
**User Story 6 (P3)**: 13 tasks (5 tests + 8 implementation)
**Main Integration**: 8 tasks
**Error Handling**: 8 tasks
**Polish & Validation**: 8 tasks

**Parallel Tasks**: 67 tasks marked [P] (54% of total)
**MVP Tasks**: 47 tasks (Setup + Foundational + US1 + US2 + Integration)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests MUST be written first and FAIL before implementation (TDD for security)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User isolation is CRITICAL - every endpoint verifies user_id match and filters queries
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
