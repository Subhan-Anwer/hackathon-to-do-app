# Feature Specification: Production Authentication Migration & UI Completion

**Feature Branch**: `003-production-auth-migration`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "from the above summary, write the specification to complete the frontend and implemented full secure authentication using better auth and switch to production code from mock or demo code and demo files. Missing Add Tasks button in the frontend dashboard."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persistent User Accounts (Priority: P1)

Users need their accounts and login sessions to persist across server restarts so they don't lose access to their tasks and don't have to re-register every time the application restarts.

**Why this priority**: This is the most critical blocker for production deployment. Without persistent authentication, the application cannot function as a multi-user system. Users will lose access after any server maintenance or restart, making the application unusable in a real-world scenario.

**Independent Test**: Can be fully tested by creating a user account, logging in, restarting the server, and verifying the user can still log in with the same credentials and access their tasks. Delivers reliable, production-ready authentication.

**Acceptance Scenarios**:

1. **Given** the server is running, **When** a user creates an account with email and password, **Then** their credentials are stored in the PostgreSQL database (not in-memory)
2. **Given** a user has created an account, **When** the server restarts, **Then** the user can still log in with their credentials
3. **Given** a user is logged in, **When** they close the browser and return later (within 7 days), **Then** they are still authenticated and can access their tasks
4. **Given** a user account exists, **When** another user tries to register with the same email, **Then** the system prevents duplicate registration with a clear error message

---

### User Story 2 - Secure Password Storage (Priority: P1)

User passwords must be securely hashed and never stored in plaintext to protect user accounts from data breaches and unauthorized access.

**Why this priority**: Security is non-negotiable for production. Plaintext passwords violate fundamental security principles and expose users to credential theft. This is a critical compliance requirement for any production application.

**Independent Test**: Can be fully tested by creating a user account, inspecting the database to verify the password is hashed (not plaintext), and successfully authenticating with the original password. Delivers industry-standard password security.

**Acceptance Scenarios**:

1. **Given** a user creates an account with password "MyPassword123", **When** their record is stored in the database, **Then** the password field contains a bcrypt hash (not "MyPassword123")
2. **Given** a user's password is hashed in the database, **When** they attempt to log in with the correct password, **Then** authentication succeeds
3. **Given** a user's password is hashed in the database, **When** they attempt to log in with an incorrect password, **Then** authentication fails with appropriate error message
4. **Given** the database is compromised, **When** an attacker accesses the user table, **Then** they cannot read user passwords in plaintext

---

### User Story 3 - Add Task Button in Dashboard (Priority: P2)

Users need a visible and accessible button to create new tasks directly from the dashboard so they can quickly add tasks without confusion.

**Why this priority**: While not a security blocker, this is a core usability feature that prevents user frustration. Users currently cannot discover how to create tasks, which defeats the purpose of a task management application.

**Independent Test**: Can be fully tested by navigating to the tasks dashboard and clicking the "Add Task" button to create a new task. Delivers immediate value by making the primary user action discoverable.

**Acceptance Scenarios**:

1. **Given** a user is viewing the tasks dashboard, **When** they look for a way to add a task, **Then** they see a clearly labeled "Add Task" or "Create Task" button
2. **Given** a user clicks the "Add Task" button, **When** the action completes, **Then** a form or dialog appears allowing them to enter task details
3. **Given** a user enters task details and submits, **When** the task is created, **Then** it appears in their task list immediately
4. **Given** a user has no tasks, **When** they view the empty state, **Then** the "Add Task" button is prominently displayed

---

### User Story 4 - Remove Demo Authentication Code (Priority: P2)

The codebase must be cleaned of demo/mock authentication implementations to prevent confusion, reduce maintenance burden, and eliminate security vulnerabilities from fallback code.

**Why this priority**: Leaving demo code in production creates security risks (weak fallback secrets, in-memory storage fallbacks) and maintenance confusion. Clean code is essential for long-term maintainability.

**Independent Test**: Can be fully tested by searching the codebase for `simple-auth.ts` references, verifying all components use Better Auth exclusively, and confirming no in-memory user stores exist. Delivers a clean, production-ready codebase.

**Acceptance Scenarios**:

1. **Given** the frontend codebase, **When** searching for `simple-auth.ts` imports, **Then** no components import from this file
2. **Given** the authentication system, **When** inspecting user storage, **Then** no in-memory Map or Array stores are used for user data
3. **Given** the authentication configuration, **When** inspecting environment variable handling, **Then** there are no weak fallback secrets (like "fallback-secret")
4. **Given** the Better Auth configuration, **When** the DATABASE_URL is missing, **Then** the application fails to start with a clear error (no in-memory fallback)

---

### User Story 5 - Secure Environment Configuration (Priority: P3)

Sensitive credentials must never be committed to version control, ensuring database passwords and secrets remain private and secure.

**Why this priority**: While critical for security, this is primarily a deployment concern. The application can function with proper .env files locally, but production security requires proper secret management.

**Independent Test**: Can be fully tested by checking git history for `.env.local` files, verifying `.gitignore` prevents future commits, and confirming environment variables work from external configuration. Delivers secure credential management.

**Acceptance Scenarios**:

1. **Given** the git repository, **When** checking commit history, **Then** no `.env.local` or `.env` files with real credentials are committed
2. **Given** the `.gitignore` file, **When** a developer creates a `.env.local` file, **Then** git does not track or stage the file
3. **Given** the application startup, **When** required environment variables are missing, **Then** the application fails with clear error messages indicating which variables are required
4. **Given** deployment to production, **When** environment variables are provided via platform configuration (not files), **Then** the application uses them correctly

---

### Edge Cases

- What happens when a user tries to log in while the database is temporarily unavailable?
- How does the system handle password reset requests when Better Auth email is not configured?
- What happens if a user's session cookie is manually deleted or expires?
- How does the system handle race conditions when multiple tabs are open and one logs out?
- What happens when a user tries to access protected routes with an expired JWT token?
- How does the system handle database migration if user schema changes in Better Auth?

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication System

- **FR-001**: System MUST store user accounts in PostgreSQL database using Better Auth's user table schema
- **FR-002**: System MUST hash all user passwords using bcrypt (minimum 10 rounds) before storage
- **FR-003**: System MUST use Better Auth's database integration (`lib/auth.ts`) for all authentication operations
- **FR-004**: System MUST completely remove the `lib/simple-auth.ts` file and all references to it
- **FR-005**: System MUST update all authentication imports in components to use Better Auth client (`lib/auth-client.ts`)
- **FR-006**: System MUST validate that `BETTER_AUTH_SECRET` environment variable is set (no fallback secret allowed)
- **FR-007**: System MUST validate that `DATABASE_URL` environment variable is set and fail startup if missing
- **FR-008**: System MUST NOT use in-memory storage for user data (no Map, Array, or similar structures for users)
- **FR-009**: System MUST issue JWT tokens with user_id in the "sub" claim (consistent with current backend implementation)
- **FR-010**: System MUST maintain httpOnly cookie-based authentication (preserve current security model)

#### Environment & Security

- **FR-011**: System MUST remove `.env.local` from git repository and add it to `.gitignore`
- **FR-012**: System MUST provide `.env.example` with placeholder values (no real credentials)
- **FR-013**: System MUST log clear error messages when required environment variables are missing
- **FR-014**: System MUST remove any `console.warn` statements from production authentication code

#### User Interface

- **FR-015**: Dashboard MUST display an "Add Task" button prominently when viewing the task list
- **FR-016**: "Add Task" button MUST be visible in both empty state (no tasks) and populated state (existing tasks)
- **FR-017**: Clicking "Add Task" button MUST open a form or dialog for creating a new task
- **FR-018**: Task creation form MUST include title field (required) and description field (optional)
- **FR-019**: After task creation, the new task MUST appear in the task list immediately (optimistic UI update)

#### Data Migration

- **FR-020**: System MUST provide documentation for migrating existing demo users to Better Auth database (if any exist)

### Key Entities

- **User Account**: Represents a registered user with email, hashed password, unique ID, and creation timestamp. Stored in PostgreSQL via Better Auth's user schema.
- **Authentication Session**: Represents an active user login session with JWT token, expiry time (7 days), and associated user ID. Stored in httpOnly cookies.
- **Task**: Represents a to-do item owned by a specific user. Each task belongs to exactly one user (via user_id foreign key).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create accounts that persist across server restarts (100% retention after restart)
- **SC-002**: User passwords are never stored in plaintext (0% plaintext passwords in database inspection)
- **SC-003**: Users can log in and access their tasks within 3 seconds of entering credentials
- **SC-004**: No authentication-related errors occur due to in-memory storage limitations (0 errors in production logs)
- **SC-005**: New users can discover the "Add Task" button without instruction within 5 seconds of viewing the dashboard
- **SC-006**: Task creation completes in under 2 seconds from button click to task appearing in list
- **SC-007**: Zero sensitive credentials (database passwords, secrets) are committed to git repository (verified via git history scan)
- **SC-008**: Application fails to start gracefully with clear error messages when required environment variables are missing (100% of missing variables detected)
- **SC-009**: Authentication system supports 1000+ concurrent users without performance degradation
- **SC-010**: User authentication remains secure even if database is compromised (passwords remain hashed)

## Assumptions

1. **Better Auth Configuration**: The existing Better Auth configuration in `lib/auth.ts` is correctly set up and tested
2. **Database Schema**: Better Auth will automatically create/manage the user table schema via migrations
3. **Backward Compatibility**: No existing production users need migration (demo/hackathon environment only)
4. **Email Configuration**: Email-based features (password reset, email verification) will be configured separately and are out of scope for this feature
5. **Frontend Framework**: Next.js 16+ App Router patterns remain consistent with existing codebase
6. **Backend API**: Backend JWT verification endpoints remain unchanged and compatible with Better Auth tokens
7. **UI Components**: Existing shadcn/ui components (Button, Dialog, Form) are available and functional
8. **Testing Environment**: Development environment has access to a test PostgreSQL database

## Dependencies

- **Better Auth**: v1.4.18 (already installed in package.json)
- **PostgreSQL Database**: Neon serverless PostgreSQL instance must be accessible via DATABASE_URL
- **Existing Backend API**: Backend must continue accepting JWT tokens with user_id in "sub" claim
- **Environment Variables**: `BETTER_AUTH_SECRET` and `DATABASE_URL` must be configured in deployment environment

## Out of Scope

- Email verification workflow (users can log in immediately after signup)
- Password reset functionality (Better Auth supports this, but UI implementation is deferred)
- OAuth/SSO integration (email/password only for this feature)
- User profile editing (name, avatar, preferences)
- Multi-factor authentication (MFA)
- Session management UI (view/revoke active sessions)
- Password strength requirements beyond minimum length
- Rate limiting on authentication endpoints (security enhancement for future)
- Database migration from demo users to production (assume fresh start)
