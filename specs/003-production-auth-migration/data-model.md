# Data Model: Production Authentication Migration

**Feature**: 003-production-auth-migration
**Date**: 2026-02-06
**Stage**: Phase 1 - Data Design

## Overview

This feature migrates from in-memory demo authentication to Better Auth's PostgreSQL-backed user management. No new entities are created - we leverage Better Auth's auto-generated user schema and connect it to existing Task entities.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────┐
│  Better Auth Tables (Auto-Generated)        │
│  ┌──────────┐         ┌──────────┐         │
│  │   user   │         │ session  │         │
│  ├──────────┤         ├──────────┤         │
│  │ id       │◄────────│ userId   │         │
│  │ email    │         │ token    │         │
│  │ password │         │ expiresAt│         │
│  │ name     │         │ createdAt│         │
│  │ createdAt│         └──────────┘         │
│  │ updatedAt│                               │
│  └──────────┘                               │
│       ▲                                     │
└───────┼─────────────────────────────────────┘
        │
        │ user_id foreign key
        │
┌───────┼─────────────────────────────────────┐
│  Application Tables (Existing)              │
│  ┌──────────┐                               │
│  │   Task   │                               │
│  ├──────────┤                               │
│  │ id       │                               │
│  │ user_id  │ (references user.id)          │
│  │ title    │                               │
│  │ description                               │
│  │ is_completed                              │
│  │ created_at                                │
│  │ updated_at                                │
│  └──────────┘                               │
└─────────────────────────────────────────────┘
```

---

## Entities

### 1. User (Better Auth Auto-Generated)

**Table Name**: `user`
**Managed By**: Better Auth framework
**Schema**: Auto-created on first signup

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (login credential) |
| `emailVerified` | BOOLEAN | DEFAULT FALSE | Email verification status (not used in this feature) |
| `name` | VARCHAR(255) | NULLABLE | User's display name (optional) |
| `image` | TEXT | NULLABLE | Profile picture URL (not used) |
| `password` | TEXT | NOT NULL | bcrypt-hashed password (10 rounds) |
| `createdAt` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updatedAt` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Password minimum 8 characters (enforced in frontend forms)
- Password hashed before storage (Better Auth automatic)

**State Transitions**: None - user records are immutable except for `updatedAt`

---

### 2. Session (Better Auth Auto-Generated)

**Table Name**: `session`
**Managed By**: Better Auth framework
**Schema**: Auto-created on first login

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Session identifier (random token) |
| `userId` | UUID | NOT NULL, FOREIGN KEY → user(id) | Owner of this session |
| `token` | TEXT | NOT NULL, UNIQUE | JWT token value |
| `expiresAt` | TIMESTAMP | NOT NULL | Session expiration (7 days from creation) |
| `createdAt` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Session start time |
| `updatedAt` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last session refresh |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `userId` (for user logout/session retrieval)
- UNIQUE INDEX on `token`

**Cleanup**: Better Auth automatically deletes expired sessions (background job)

---

### 3. Task (Existing - No Changes)

**Table Name**: `task`
**Managed By**: Backend SQLModel ORM
**Schema**: Already exists

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Task identifier |
| `user_id` | UUID | NOT NULL, INDEX | Owner (references `user.id`) |
| `title` | VARCHAR(500) | NOT NULL | Task title |
| `description` | VARCHAR(2000) | NULLABLE | Task description |
| `is_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (critical for user isolation queries)

**Foreign Key** (conceptual - not enforced in database):
- `user_id` → `user.id`
- Reason: Better Auth and backend use separate ORMs, explicit FK not created
- User isolation enforced via application-level filtering

---

## Relationships

### User ↔ Task (One-to-Many)

**Type**: One user has many tasks
**Cardinality**: `1:N`
**Implementation**: `task.user_id` references `user.id`

**Query Patterns**:
```sql
-- Get all tasks for a user
SELECT * FROM task WHERE user_id = $1;

-- Get user for a specific task
SELECT u.* FROM user u
JOIN task t ON t.user_id = u.id
WHERE t.id = $2;
```

**Deletion Behavior** (not implemented in this feature):
- User deletion: Would require deleting or orphaning tasks
- Out of scope: User deletion not part of authentication migration

---

### User ↔ Session (One-to-Many)

**Type**: One user can have multiple active sessions (multi-device support)
**Cardinality**: `1:N`
**Implementation**: `session.userId` references `user.id`

**Query Patterns**:
```sql
-- Get all active sessions for a user
SELECT * FROM session
WHERE userId = $1 AND expiresAt > NOW();

-- Invalidate all sessions for a user (logout all devices)
DELETE FROM session WHERE userId = $1;
```

**Better Auth Handles**:
- Session creation on login
- Session validation on request
- Session cleanup on expiry

---

## Data Flow

### Signup Flow

```
1. Frontend SignupForm
   ↓ (email, password)
2. Server Action signup()
   ↓
3. Better Auth API
   ├─ Validate email format
   ├─ Hash password (bcrypt, 10 rounds)
   ├─ INSERT INTO user (id, email, password, createdAt, updatedAt)
   ├─ Generate JWT token (sub: user.id)
   ├─ INSERT INTO session (id, userId, token, expiresAt)
   └─ Set httpOnly cookie (session=<JWT>)
   ↓
4. Return success + userId
   ↓
5. Frontend redirects to /tasks
```

### Login Flow

```
1. Frontend LoginForm
   ↓ (email, password)
2. Server Action signin()
   ↓
3. Better Auth API
   ├─ SELECT * FROM user WHERE email = $1
   ├─ Verify password (bcrypt.compare)
   ├─ Generate JWT token (sub: user.id)
   ├─ INSERT INTO session (id, userId, token, expiresAt)
   └─ Set httpOnly cookie (session=<JWT>)
   ↓
4. Return success + userId
   ↓
5. Frontend redirects to /tasks
```

### Authenticated API Request Flow

```
1. Frontend TaskList Component
   ↓ (taskApi.list(userId))
2. fetchWithAuth() adds credentials: "include"
   ↓
3. Browser sends request with Cookie: session=<JWT>
   ↓
4. Backend FastAPI Middleware
   ├─ Extract JWT from cookie
   ├─ Verify signature with BETTER_AUTH_SECRET
   ├─ Decode payload.sub → user_id
   └─ Attach to request.state.user_id
   ↓
5. Route Handler
   ├─ Verify path user_id == request.state.user_id (403 if mismatch)
   ├─ SELECT * FROM task WHERE user_id = $1
   └─ Return filtered tasks
   ↓
6. Frontend receives JSON response
```

---

## Migration Strategy

### No Data Migration Required

**Reason**: Demo environment has no production users
**Assumption**: All existing demo users are disposable

**If migration needed** (future reference):
```sql
-- Hypothetical: Migrate from old_user table to Better Auth user table
INSERT INTO user (id, email, password, createdAt, updatedAt)
SELECT id, email, password_hash, created_at, updated_at
FROM old_user;

-- Update task foreign keys (if user IDs changed)
UPDATE task
SET user_id = (SELECT new_id FROM user_mapping WHERE old_id = task.user_id);
```

---

## Database Initialization

### Development Setup

```bash
# 1. Set DATABASE_URL in .env.local
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/todo_app

# 2. Start Next.js server (Better Auth auto-creates tables)
cd frontend && npm run dev

# 3. First signup triggers table creation
# POST /api/auth/signup → Better Auth creates user/session tables

# 4. Verify tables exist
psql $DATABASE_URL -c "\dt"
# Expected output: user, session, account, verification
```

### Production Setup

```bash
# 1. Set DATABASE_URL to Neon PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db?ssl=require

# 2. Deploy frontend to Vercel/similar
# Better Auth auto-creates tables on first signup

# 3. No manual migration scripts needed
```

---

## Constraints & Validation

### User Entity

| Constraint | Type | Rule | Enforcement |
|------------|------|------|-------------|
| Email uniqueness | Database | UNIQUE INDEX | PostgreSQL |
| Email format | Application | RFC 5322 regex | Zod schema + Better Auth |
| Password length | Application | Minimum 8 characters | Zod schema (frontend) |
| Password hashing | Application | bcrypt 10 rounds | Better Auth automatic |

### Session Entity

| Constraint | Type | Rule | Enforcement |
|------------|------|------|-------------|
| Token uniqueness | Database | UNIQUE INDEX | PostgreSQL |
| Expiry validation | Application | expiresAt > NOW() | Better Auth + backend middleware |
| Session cleanup | Background | Delete expired sessions | Better Auth cron job |

### Task Entity

| Constraint | Type | Rule | Enforcement |
|------------|------|------|-------------|
| User isolation | Application | user_id filter in all queries | Backend route handlers |
| Title required | Database | NOT NULL | PostgreSQL + Pydantic validation |
| Title length | Application | Max 500 characters | SQLModel Field definition |

---

## Performance Considerations

### Indexes

All critical query paths are indexed:

| Query Pattern | Index | Cardinality | Performance |
|---------------|-------|-------------|-------------|
| `SELECT FROM user WHERE email = ?` | `email` UNIQUE | ~10K users | O(log n) |
| `SELECT FROM session WHERE userId = ?` | `userId` | ~100K sessions | O(log n) |
| `SELECT FROM task WHERE user_id = ?` | `user_id` | ~1M tasks | O(log n) |

**Expected Query Performance**:
- User login: < 50ms (1 email lookup + 1 bcrypt verify)
- Session validation: < 10ms (1 token lookup + JWT decode)
- Task list: < 100ms (1 indexed query + JSON serialization)

### Connection Pooling

Better Auth uses default PostgreSQL connection pool:
- **Min**: 2 connections
- **Max**: 10 connections
- **Idle Timeout**: 30 seconds

**Capacity**: Supports 1000+ concurrent users (per SC-009)

---

## Security Design

### Password Storage

```
User Input Password: "MyPassword123"
      ↓
Frontend Zod Validation (min 8 chars)
      ↓
Sent to Server Action (HTTPS only)
      ↓
Better Auth bcrypt Hash (10 rounds)
      ↓
Database Storage: "$2b$10$N9qo8uLOickgx2ZMRZoMye..."
```

**Attack Resistance**:
- Rainbow tables: Ineffective (bcrypt salt per user)
- Brute force: ~10 hashes/second (bcrypt work factor)
- Database breach: Passwords remain unreadable

### User Isolation

```
API Request with JWT
      ↓
Middleware extracts user_id from token
      ↓
Route handler receives authenticated_user_id
      ↓
Verify path user_id == authenticated_user_id (403 if mismatch)
      ↓
Database query: WHERE user_id = authenticated_user_id
      ↓
Return only user's data
```

**Attack Prevention**:
- URL manipulation: Blocked by path parameter check
- Token forgery: Blocked by signature verification
- SQL injection: Blocked by ORM parameterization
- Cross-user access: Blocked by user_id filter

---

## Conclusion

Data model requires **no schema changes** - leveraging Better Auth's auto-generated user/session tables and connecting to existing Task entities via application-level foreign keys. All security and isolation requirements met through indexed queries and middleware validation.

**Key Takeaway**: Migration is code-only (remove demo, activate Better Auth), not a database migration.
