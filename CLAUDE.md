# Todo App - Hackathon II

## Project Overview
Multi-user Todo full-stack web application built with **strict spec-driven development**. NO manual coding allowed—all implementation via `/sp.*` commands and specialized agents.

**Core Features:** Add/Delete/Update/View Tasks, Mark as Complete
**Critical Requirement:** User isolation via JWT authentication (users can ONLY access their own data)

## 🚨 Critical Security Principles (NON-NEGOTIABLE)

From `@.specify/memory/constitution.md` Principle II:
- **ALL** API endpoints MUST verify JWT and extract `user_id`
- **ALL** database queries MUST filter by authenticated `user_id`
- **NEVER** expose cross-user data (test with multiple user accounts)
- Return 401 on missing/invalid tokens, 403 on user_id mismatch

```python
# ✅ CORRECT - User isolation enforced
tasks = session.exec(
    select(Task).where(Task.user_id == request.state.user_id)
).all()

# ❌ WRONG - Security violation, exposes all users' data
tasks = session.exec(select(Task)).all()
```

## Tech Stack (Constitution-Mandated)

**Frontend:** Next.js 16+ (App Router), React Server Components, Tailwind CSS
**Backend:** FastAPI (Python), uv dependency manager, SQLModel ORM
**Database:** Neon Serverless PostgreSQL
**Auth:** Better Auth with JWT (httpOnly cookies, 7-day expiry)
**Monorepo:** `frontend/`, `backend/`, `.claude/`, `.specify/`

**Required Environment Variables:**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Shared secret (same value frontend + backend)

## Development Workflow (Mandatory Sequence)

### Phase 1: Constitution & Specs
```bash
1. /sp.constitution <principles>     # Set/update project principles
2. /sp.specify <feature-description> # Create feature spec
```

### Phase 2: Architecture & Planning
```bash
3. /sp.plan                          # Generate architecture plan
   - Reads: specs/<feature>/spec.md
   - Creates: specs/<feature>/plan.md, research.md, data-model.md
   - Triggers ADR suggestion if significant decisions made
```

### Phase 3: Task Breakdown
```bash
4. /sp.tasks                         # Break plan into testable tasks
   - Reads: plan.md, spec.md
   - Creates: specs/<feature>/tasks.md
   - Groups by user story for independent implementation
```

### Phase 4: Implementation
```bash
5. /sp.implement                     # Execute tasks via agents
   OR use specialized agents directly (see Agent Decision Tree below)
```

### Phase 5: Version Control
```bash
6. /sp.git.commit_pr                 # Commit and create PR
   - Auto-generates commit message
   - References spec/tasks
   - Creates PR with description
```

## Agent & Skill Decision Tree

### When to Use Which Tool

**Creating Specifications:**
- Use: `/sp.specify` command or `spec-writer` skill
- Trigger: Starting new feature, documenting requirements
- Output: `specs/<feature>/spec.md`

**Database Schema Design:**
- Use: `database-schema-designer` skill
- Trigger: Need to design tables, relationships, indexes
- Read: Constitution Data Isolation principle first
- Output: SQLModel models with `user_id` foreign keys

**Backend API Implementation:**
- Use: `fastapi-backend-builder` agent
- Trigger: Implementing REST endpoints, JWT middleware
- Reads: `specs/<feature>/spec.md`, `specs/<feature>/plan.md`
- Ensures: All endpoints verify JWT, all queries filter by user_id

**Frontend Implementation:**
- Use: `nextjs-builder` agent
- Trigger: Creating UI components, pages, auth flows
- Reads: `specs/<feature>/spec.md`, `specs/<feature>/plan.md`
- Ensures: Better Auth integration, httpOnly cookie handling

**Authentication Setup:**
- Use: `better-auth-integration` skill
- Trigger: Setting up JWT auth between Next.js and FastAPI
- Configures: Token issuance, verification, shared secret

**API Security Review:**
- Use: `api-security` skill
- Trigger: During `/sp.plan` for features touching auth/data
- Validates: JWT verification, user isolation, error handling

### Context7 MCP Integration (Proactive Documentation Lookup)

**CRITICAL: Always use Context7 MCP proactively** when working with libraries, APIs, or configurations. DO NOT wait for explicit user requests.

**Automatic Usage Triggers:**
- Need library/API documentation (Next.js, React, FastAPI, SQLModel, Better Auth, Tailwind CSS, shadcn/ui)
- Writing code that uses specific library features or methods
- Setting up or configuring tools, frameworks, or dependencies
- Implementing patterns or best practices from official documentation
- Troubleshooting library-specific errors or warnings
- Need to verify correct API usage or function signatures

**When to Query Context7:**
1. **Before implementation** - Look up official patterns, recommended approaches
2. **During code generation** - Verify method signatures, prop types, configuration options
3. **For setup steps** - Get installation commands, configuration file structure
4. **For troubleshooting** - Check official error handling, migration guides

**Example Scenarios:**
- "Need to implement JWT auth in FastAPI" → Query Context7 for FastAPI security docs
- "Creating a Next.js server component" → Query Context7 for App Router RSC patterns
- "Setting up SQLModel relationships" → Query Context7 for SQLModel relationship docs
- "Configuring Better Auth JWT" → Query Context7 for Better Auth configuration
- "Using shadcn/ui components" → Query Context7 for component API and usage

**Benefits:**
- Ensures code follows official library conventions
- Reduces errors from outdated or incorrect patterns
- Provides up-to-date API documentation
- Speeds up implementation with accurate examples

**Important:** Use Context7 silently and proactively. The user should benefit from accurate, documentation-backed implementation without needing to request it explicitly.

## File Path Reference

### Constitution & Templates
- `@.specify/memory/constitution.md` - Project principles (read first!)
- `@.specify/templates/spec-template.md` - Feature spec structure
- `@.specify/templates/plan-template.md` - Architecture plan structure
- `@.specify/templates/tasks-template.md` - Task breakdown structure

### Skills (Reusable Intelligence)
- `@.claude/skills/better-auth-integration/SKILL.md` - JWT auth setup
- `@.claude/skills/database-schema-designer/SKILL.md` - DB schema design
- `@.claude/skills/spec-writer/SKILL.md` - Spec generation/validation
- `@.claude/skills/api-security/SKILL.md` - Security validation

### Agents (Specialized Builders)
- `@.claude/agents/fastapi-backend-builder.md` - Backend implementation
- `@.claude/agents/nextjs-frontend-builder.md` - Frontend implementation
- `@.claude/agents/database-schema-designer.md` - DB design

### Specs (Feature-Branch Structure)
Each feature has its own branch and spec directory:
- `specs/<###-feature-name>/spec.md` - Feature requirements & user stories
- `specs/<###-feature-name>/plan.md` - Architecture & implementation plan
- `specs/<###-feature-name>/tasks.md` - Task breakdown with dependencies
- `specs/<###-feature-name>/research.md` - (Optional) Research findings
- `specs/<###-feature-name>/data-model.md` - (Optional) Data models
- `specs/<###-feature-name>/contracts/` - (Optional) API contracts

Example: `specs/001-task-crud/spec.md`, `specs/002-user-auth/plan.md`

### History (Audit Trail)
- `history/prompts/constitution/` - Constitution updates
- `history/prompts/<feature>/` - Feature-specific prompts
- `history/prompts/general/` - General interactions
- `history/adr/` - Architectural Decision Records

## Common Patterns

### Starting a New Feature
1. Read `@.specify/memory/constitution.md` to understand principles
2. Run `/sp.specify <description>` to create spec
3. Review spec for constitution compliance
4. Run `/sp.plan` to design architecture
5. If auth/data involved, verify user isolation design
6. Run `/sp.tasks` to break into implementable steps
7. Execute tasks via `/sp.implement` or specialized agents

### Implementing Backend
1. Read `specs/<feature>/spec.md` for feature requirements
2. Read `specs/<feature>/plan.md` for architecture decisions
3. Read `specs/<feature>/data-model.md` (if exists) for data models
4. Invoke `fastapi-backend-builder` agent
5. Verify JWT middleware on ALL endpoints
6. Verify user_id filtering on ALL database queries
7. Test with multiple user accounts

### Implementing Frontend
1. Read `specs/<feature>/spec.md` for feature requirements
2. Read `specs/<feature>/plan.md` for architecture & API contracts
3. Invoke `nextjs-builder` agent
4. Ensure Better Auth JWT token handling
5. Verify httpOnly cookie configuration
6. Test authentication flow end-to-end

## Anti-Patterns (DO NOT DO)

❌ **Manual Coding** - Never write code without spec → plan → tasks
❌ **Skip User Isolation** - Never query without filtering by user_id
❌ **Hardcode Secrets** - Always use `.env` variables
❌ **Assume Requirements** - Always read specs before implementing
❌ **Skip JWT Verification** - Every endpoint must verify token
❌ **Cross-User Data Leaks** - Test isolation with multiple accounts
❌ **Premature Abstraction** - Implement only what's specified (YAGNI)
❌ **Skip PHR Creation** - Must document all significant interactions

## Validation Checklist

### Before Implementation
- [ ] Constitution principles understood
- [ ] Spec exists and reviewed (`specs/<feature>/spec.md`)
- [ ] Plan exists and includes Constitution Check (`specs/<feature>/plan.md`)
- [ ] Tasks broken down with clear acceptance criteria

### During Implementation
- [ ] Reading from correct spec files (not inventing requirements)
- [ ] Using appropriate agent/skill for the task
- [ ] Following constitution's tech stack (no framework substitutions)
- [ ] Implementing user isolation on every operation

### After Implementation
- [ ] All API endpoints verify JWT
- [ ] All database queries filter by user_id
- [ ] No hardcoded secrets (check .env.example)
- [ ] PHR created in appropriate directory
- [ ] Tests pass (especially security/isolation tests)
- [ ] Multiple user accounts tested for isolation

## Quick Commands Reference

```bash
# Development
cd frontend && npm run dev              # Start Next.js dev server (port 3000)
cd backend && uv run uvicorn main:app --reload  # Start FastAPI server (port 8000)

# Spec-Driven Workflow
/sp.constitution <principles>           # Set/update constitution
/sp.specify <description>               # Create feature spec
/sp.plan                                # Generate architecture plan
/sp.tasks                               # Break into tasks
/sp.implement                           # Execute tasks
/sp.git.commit_pr                       # Commit and create PR

# Skills (invoke when needed)
/better-auth-integration                # Set up JWT auth
/database-schema-designer               # Design DB schema
/api-security                           # Security validation
/spec-writer                            # Generate/validate specs
```

## Troubleshooting

**"No spec found"** → Run `/sp.specify <description>` first
**"User data leak detected"** → Add `.where(Entity.user_id == auth_user_id)` to query
**"JWT verification failed"** → Check `BETTER_AUTH_SECRET` matches in both frontend and backend
**"Constitution violation"** → Review `@.specify/memory/constitution.md` and align implementation
**"Template not found"** → Check `.specify/templates/` directory exists with required templates

## Decision Framework

**If unclear about requirements:**
1. Check relevant spec file first (`specs/<feature>/`)
2. Review constitution principles (`@.specify/memory/constitution.md`)
3. If still unclear, ask user with 2-3 targeted questions

**If multiple valid approaches exist:**
1. Prefer simplicity (YAGNI principle from Constitution VI)
2. Choose approach consistent with existing patterns
3. Prioritize security over convenience (Constitution II)
4. Document significant decisions via ADR

**If discovering missing requirements:**
1. Surface the gap: "Spec doesn't define X, needed for Y"
2. Propose solution: "Recommend A because B"
3. Wait for user confirmation before proceeding

## Success Criteria (From Constitution)

A feature is complete when:
- [ ] Spec, plan, tasks files exist and cross-reference correctly
- [ ] All tasks marked complete
- [ ] Integration tests pass (including user isolation tests)
- [ ] All error paths handled with documented error codes
- [ ] PHR created for each workflow phase
- [ ] ADR created for significant decisions (if applicable)
- [ ] Frontend UI responsive (mobile + desktop)
- [ ] Multi-user test accounts validated (no data leaks)

## Remember

This is a **security-critical multi-user application**. Every line of code must uphold the principle: **users can only access their own data, always and without exception.**

Refer to `@.specify/memory/constitution.md` as the single source of truth for all principles, standards, and governance.
