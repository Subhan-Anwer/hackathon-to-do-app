# Feature Specification: JWT Bearer Token Authentication Fix

**Feature Branch**: `004-auth-fix-workflow`
**Created**: 2026-02-08
**Status**: Draft
**Input**: Fix 401 Unauthorized errors by implementing proper JWT Bearer token authentication between Next.js frontend and FastAPI backend

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated Task Creation (Priority: P1)

A logged-in user wants to create a new task and have it successfully saved to their account without encountering 401 Unauthorized errors.

**Why this priority**: This is the core authentication flow that's currently broken. Without this, users cannot use the application.

**Independent Test**: Sign in with valid credentials, fill out the task creation form, submit it, and verify the task appears in the task list without 401 errors in the browser console or network tab.

**Acceptance Scenarios**:

1. **Given** a user has successfully signed in, **When** they submit the task creation form, **Then** the request includes `Authorization: Bearer <token>` header and the task is created successfully
2. **Given** a user performs any task operation (create/update/delete/toggle), **When** the request is sent to the backend, **Then** the `Authorization: Bearer <token>` header is present with a valid JWT token
3. **Given** a user's JWT token is valid, **When** the backend receives an authenticated request, **Then** it successfully verifies the token and returns the expected response

---

### User Story 2 - Cross-Origin Authentication (Priority: P1)

Developers working on localhost need task operations to work between frontend (localhost:3000) and backend (localhost:8000) without relying on cross-origin cookie transmission.

**Why this priority**: Cookie-based auth fails across different ports in development due to browser security policies. Bearer token authentication solves this.

**Independent Test**: Run frontend on port 3000 and backend on port 8000, sign in, create a task, and verify the Authorization header is sent (not relying on cookies being sent cross-origin).

**Acceptance Scenarios**:

1. **Given** the frontend runs on localhost:3000 and backend on localhost:8000, **When** a user creates a task, **Then** the request uses Authorization Bearer header instead of relying on cross-origin cookies
2. **Given** a user is authenticated, **When** any API request is made, **Then** the JWT token is extracted from the Better Auth session and included in the Authorization header
3. **Given** the backend receives a request with Authorization header, **When** it validates the JWT, **Then** it successfully extracts user_id and allows the operation

---

### User Story 3 - Production Deployment (Priority: P2)

Users accessing the production application need the same authentication mechanism to work seamlessly in production environments.

**Why this priority**: The solution must work in both development and production without environment-specific code changes.

**Independent Test**: Deploy to production, sign in, perform task operations, and verify Authorization Bearer headers are used consistently.

**Acceptance Scenarios**:

1. **Given** the application is deployed to production, **When** a user signs in, **Then** Better Auth generates a JWT token that can be extracted and used for API requests
2. **Given** a user performs task operations in production, **When** requests are sent to the backend, **Then** the Authorization Bearer header is included regardless of environment
3. **Given** the backend verifies JWT tokens, **When** it receives production requests, **Then** it uses the same BETTER_AUTH_SECRET to validate tokens

---

### Edge Cases

- What happens when Better Auth session doesn't contain an accessible JWT token?
- How does the system handle JWT token extraction if Better Auth changes its session structure?
- What happens if BETTER_AUTH_SECRET is misconfigured (different between frontend and backend)?
- How does the frontend handle 401 errors when the token is expired or invalid?
- What happens when a user manually clears cookies but the session state still exists?

## Requirements *(mandatory)*

### Functional Requirements

**JWT Token Extraction:**

- **FR-001**: Frontend MUST extract JWT token from Better Auth session object server-side using `getSession()`
- **FR-002**: System MUST identify the correct session property containing the JWT token (e.g., `session.token`, `session.access_token`, `session.jwt`)
- **FR-003**: Token extraction MUST occur in Next.js server-side context (Server Components, Server Actions, or API Routes)

**Authorization Header Implementation:**

- **FR-004**: All API requests to the FastAPI backend MUST include `Authorization: Bearer <token>` header
- **FR-005**: Frontend MUST implement server-side API proxy or wrapper functions that add the Bearer token to requests
- **FR-006**: Client-side components MUST call Next.js internal API routes (same-origin) instead of directly calling the backend
- **FR-007**: Next.js API routes MUST forward requests to FastAPI backend with Authorization header added

**Backend Token Verification:**

- **FR-008**: FastAPI backend MUST read JWT token from `Authorization` header (format: `Bearer <token>`)
- **FR-009**: Backend MUST verify JWT token using the shared `BETTER_AUTH_SECRET` environment variable
- **FR-010**: Backend MUST extract `user_id` from verified JWT token for user isolation
- **FR-011**: Backend MUST return 401 Unauthorized if Authorization header is missing or token is invalid

**Error Handling:**

- **FR-012**: Frontend MUST handle 401 responses by redirecting to `/login` page
- **FR-013**: Frontend MUST display user-friendly toast notification when 401 errors occur
- **FR-014**: Frontend MUST clear authentication state when 401 errors are received

**Security Requirements:**

- **FR-015**: System MUST keep httpOnly cookies enabled (no security downgrade)
- **FR-016**: Backend MUST filter all database queries by authenticated `user_id` to enforce user isolation
- **FR-017**: System MUST use the same `BETTER_AUTH_SECRET` value in both frontend and backend environments

### Key Entities

- **JWT Token**: A signed JSON Web Token containing user identity (user_id, email) generated by Better Auth upon authentication
- **Better Auth Session**: Server-side session object containing the JWT token, accessible via `getSession()` in Next.js
- **Authorization Header**: HTTP request header in the format `Authorization: Bearer <token>` that carries the JWT
- **API Proxy/Wrapper**: Next.js Server Actions or API Routes that add Authorization headers before forwarding to the backend
- **User Isolation**: Security principle ensuring all database queries filter by authenticated user_id

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks after signing in without encountering 401 Unauthorized errors (100% success rate)
- **SC-002**: All API requests to the backend include `Authorization: Bearer <token>` header (verifiable in browser DevTools Network tab)
- **SC-003**: Backend successfully verifies JWT tokens and extracts user_id from Authorization header (observable in backend logs)
- **SC-004**: Authentication works in both development (localhost:3000 → localhost:8000) and production environments without code changes
- **SC-005**: httpOnly cookies remain enabled throughout (no `httpOnly: false` in configuration)
- **SC-006**: Multi-user testing confirms user isolation: User A cannot access User B's tasks (0% data leak rate)

## Assumptions *(optional)*

- Better Auth generates a JWT token during sign-in/sign-up that can be accessed from the session object
- The JWT token structure follows standard JWT format (header.payload.signature)
- Backend already has JWT verification middleware or can easily add it
- Frontend can use Next.js 16+ Server Actions or API Routes for server-side token extraction
- Both frontend and backend have access to the same BETTER_AUTH_SECRET environment variable

## Dependencies & Risks *(optional)*

### Dependencies

- Better Auth library configured with JWT plugin enabled
- Next.js 16+ with App Router for Server Components and Server Actions
- FastAPI backend with JWT verification capability (e.g., PyJWT library)
- Shared `BETTER_AUTH_SECRET` environment variable configured in both frontend and backend

### Risks

- **Risk**: Better Auth session object may not expose JWT token in expected format
  - **Mitigation**: Inspect session object structure and adapt token extraction logic accordingly

- **Risk**: Middleware or API route pattern may add latency to requests
  - **Mitigation**: Use lightweight proxy pattern; measure performance impact

- **Risk**: Server-side token extraction may fail in edge cases (no session, expired session)
  - **Mitigation**: Implement robust error handling with fallback to login redirect

## Files to Modify *(implementation guidance)*

This section provides guidance on which files will need changes. Implementation details will be determined during the planning phase.

**Frontend (Next.js):**

- `frontend/lib/api.ts` - Update to use server-side token extraction or create new server-side wrappers
- `frontend/app/api/tasks/route.ts` - Create API route to proxy task operations with Authorization header (or similar pattern)
- `frontend/app/actions/tasks.ts` - Create Server Actions that add Authorization header (alternative to API routes)
- `frontend/components/task-form.tsx` - Update to call new server-side API wrappers instead of direct backend calls
- `frontend/components/task-list.tsx` - Update task operations to use new authentication pattern

**Backend (FastAPI):**

- `backend/main.py` - Verify JWT token verification middleware extracts token from Authorization header
- `backend/routers/tasks.py` - Ensure all endpoints receive authenticated user_id from middleware

**Configuration:**

- `.env.example` - Document BETTER_AUTH_SECRET requirement if not already present
- Verify both `frontend/.env.local` and `backend/.env` contain matching BETTER_AUTH_SECRET values

## Out of Scope *(optional)*

- Implementing refresh token rotation (use simple JWT with expiration)
- Adding token caching or optimization (focus on correctness first)
- Changing Better Auth configuration or JWT plugin settings beyond what's necessary
- Implementing complex middleware patterns (keep it simple)
- Modifying backend user isolation logic (already implemented, just needs correct user_id)
- Changing cookie security settings (keep httpOnly enabled)
