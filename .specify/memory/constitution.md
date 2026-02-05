<!--
Sync Impact Report:
- Version: Initial template → 1.0.0
- Rationale: First ratification with concrete project values
- Modified principles: All placeholders filled with Multi-User Todo App values
- Added sections: None (template structure preserved)
- Removed sections: None
- Templates requiring updates:
  ✅ Updated: N/A (first ratification, templates already align)
  ⚠ Pending: None
- Follow-up TODOs: None (all values provided)
-->

# Multi-User Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All development MUST follow the spec-driven workflow:
- Write specification first (`/sp.specify`) capturing user requirements
- Generate architectural plan (`/sp.plan`) with technical decisions
- Break into testable tasks (`/sp.tasks`) with clear acceptance criteria
- Implement via Claude Code agents and `/sp` commands only

**Rationale**: No manual coding ensures consistency, traceability, and alignment with project goals. Every change traces back to a spec, preventing scope creep and hallucinations.

**Test**: Every implementation artifact (code, config, docs) MUST reference a spec file or constitution principle. Pull requests without spec links are rejected.

### II. User Isolation and Security First

All features MUST enforce multi-user isolation and security:
- JWT authentication required for all API endpoints
- Middleware verifies token and extracts `user_id` before processing
- All database queries filtered by authenticated user's ID
- 401 Unauthorized on missing/invalid tokens
- Users see and modify ONLY their own data

**Rationale**: Multi-user context requires zero-trust security. Shared state or missing auth checks create data leakage risks.

**Test**: Integration tests MUST verify (a) unauthenticated requests fail with 401, (b) User A cannot access User B's tasks via any endpoint or parameter manipulation.

### III. Reusability Through Skills and Agents

Common patterns MUST be encapsulated in reusable skills:
- `better-auth-integration`: JWT auth setup for Next.js + FastAPI
- `database-schema-designer`: SQLModel schema design
- `api-security`: Middleware and isolation enforcement
- `frontend-design`: UI component generation
- `nextjs-builder`, `fastapi-backend-builder`: Stack-specific scaffolding

**Rationale**: Avoids reinventing solutions; skills embed best practices and reduce errors.

**Test**: Before implementing auth or database logic manually, verify no existing skill covers the need. Reference skill usage in PHR and ADR.

### IV. Clarity and Consistency

All artifacts MUST align with project conventions:
- Follow `CLAUDE.md` development guidelines
- Reference specs explicitly (e.g., `specs/001-task-crud/spec.md`)
- Use monorepo paths (`@.claude/`, `@.specify/`) in documentation
- Maintain single source of truth (constitution for principles, specs for features)

**Rationale**: Distributed context (skills, agents, templates) requires explicit alignment to avoid drift.

**Test**: Constitution amendments trigger template validation (plan, spec, tasks templates). All specs MUST include constitution compliance section.

### V. Test-First for Security-Critical Paths

Security and user isolation logic MUST be test-driven:
- Write tests for auth failures, user isolation, data filtering FIRST
- Verify tests FAIL before implementing
- Red-Green-Refactor for authentication, authorization, data access layers

**Rationale**: Security bugs are catastrophic in multi-user systems. TDD prevents regressions.

**Test**: No PR merges without passing tests for (a) invalid token handling, (b) cross-user data access attempts, (c) middleware error paths.

### VI. Simplicity and Smallest Viable Change

Prefer simple, incremental solutions:
- No premature abstraction or over-engineering
- Implement only specified features (no "nice-to-haves")
- Keep diffs focused (single concern per commit)
- YAGNI: You Aren't Gonna Need It

**Rationale**: Complexity is the enemy of maintainability and security. Small changes are easier to review, test, and debug.

**Test**: Plan review MUST challenge unnecessary layers, helpers, or future-proofing. Complexity violations require explicit justification in plan.md.

## Technology Standards

### Tech Stack (MANDATORY)

- **Frontend**: Next.js 16+ with App Router, React Server Components (default), Tailwind CSS
- **Backend**: FastAPI with `uv` dependency management, SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens (httpOnly cookies)
- **Monorepo**: Existing structure (`backend/`, `frontend/`, `.claude/`, `.specify/`)

**Rationale**: Stack chosen for type safety (TypeScript + Python type hints), serverless scalability (Neon), and modern patterns (RSC, Fast refresh).

**Constraints**: No alternative frameworks without ADR documenting migration rationale. Stack changes are MAJOR version bumps.

### API Design (MANDATORY)

All endpoints MUST follow RESTful conventions:
- **Pattern**: `GET/POST/PUT/DELETE/PATCH /api/{user_id}/tasks/...`
- **Auth**: All endpoints require valid JWT in `Authorization: Bearer <token>` or httpOnly cookie
- **Responses**: JSON with standard error shapes (`{ "error": "message", "code": "ERR_CODE" }`)
- **Errors**:
  - `401 Unauthorized`: Missing/invalid token
  - `403 Forbidden`: Valid token but insufficient permissions
  - `404 Not Found`: Resource doesn't exist or belongs to different user
  - `422 Unprocessable Entity`: Validation failures

**Rationale**: Consistent API surface reduces client-side error handling complexity. Path includes `user_id` for explicit ownership context.

**Test**: OpenAPI schema validation for all endpoints. Contract tests verify error codes match spec.

### Authentication Flow (MANDATORY)

- **Token Issuance**: Better Auth generates JWT on successful login/signup
- **Token Storage**: Frontend stores in httpOnly cookie (CSRF-safe)
- **Token Verification**: FastAPI middleware decodes JWT, extracts `user_id`, attaches to request context
- **Token Expiry**: 7-day default, refresh token rotation per Better Auth configuration
- **Shared Secret**: `BETTER_AUTH_SECRET` environment variable (same value frontend + backend)

**Rationale**: httpOnly prevents XSS token theft. Middleware centralization avoids duplicating auth logic.

**Constraints**: No session storage or server-side state. Tokens MUST be stateless (validated via signature, not DB lookup).

### Data Isolation (MANDATORY)

Every database query MUST filter by authenticated user:
```python
# CORRECT
tasks = session.exec(
    select(Task).where(Task.user_id == request.state.user_id)
).all()

# INCORRECT (security violation)
tasks = session.exec(select(Task)).all()
```

**Rationale**: Database-level isolation prevents accidental cross-user leaks.

**Test**: Code review MUST reject any ORM query without `.where(Entity.user_id == ...)`. Integration tests verify isolation.

## Development Workflow

### Workflow Phases (MANDATORY)

1. **Specification** (`/sp.specify <description>`): Capture user requirements, acceptance criteria, edge cases
2. **Planning** (`/sp.plan`): Research, design, ADR for significant decisions
3. **Task Breakdown** (`/sp.tasks`): Convert plan into ordered, testable tasks
4. **Implementation** (`/sp.implement` or manual via agents): Execute tasks via specialized agents
5. **Validation**: Run tests, verify acceptance criteria, update PHR

**Rationale**: Phased workflow ensures no code written before requirements clear. Enables parallel work (multiple features in different phases).

**Test**: PRs without linked spec/plan/tasks are rejected. Each commit message references task ID.

### Prompt History Records (PHR)

Every user interaction MUST generate a PHR:
- **Routing**:
  - Constitution changes → `history/prompts/constitution/`
  - Feature work → `history/prompts/<feature-name>/`
  - General queries → `history/prompts/general/`
- **Content**: Full user prompt (verbatim), assistant response summary, files modified, tests run
- **Naming**: `<ID>-<slug>.<stage>.prompt.md` (e.g., `001-setup-auth.spec.prompt.md`)

**Rationale**: PHRs provide audit trail, enable learning, and support debugging ("what did we decide about X?").

**Test**: No PHR creation for `/sp.phr` itself. All other commands MUST generate PHR or log warning.

### Architectural Decision Records (ADR)

Suggest ADR when ALL of:
- **Impact**: Long-term consequences (framework choice, data model, API design, security model)
- **Alternatives**: Multiple viable options evaluated
- **Scope**: Cross-cutting (affects multiple features or components)

**Suggestion Template**:
```
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
```

**Rationale**: Captures "why" behind non-obvious choices. Prevents revisiting settled debates.

**Test**: Plans introducing new external dependencies, authentication schemes, or deployment patterns MUST trigger ADR suggestion. User approval required before creation.

## Quality Gates

### Feature Completion Criteria

A feature is complete when ALL of:
- [ ] Spec, plan, tasks files exist and cross-reference correctly
- [ ] All tasks marked complete in `tasks.md`
- [ ] Integration tests pass (including user isolation tests for multi-user features)
- [ ] No unhandled error paths (all endpoints return documented error codes)
- [ ] PHR created for each workflow phase
- [ ] ADR created for significant decisions (if applicable)
- [ ] Frontend UI responsive (mobile + desktop tested)
- [ ] Deployed to staging with multi-user test accounts validated

**Rationale**: Checklist prevents premature "done" declarations. User isolation testing is critical gate for this project.

### Security Checklist (MANDATORY for all features)

- [ ] All API endpoints verify JWT and extract `user_id`
- [ ] All database queries filter by `user_id`
- [ ] No hardcoded secrets (check `.env.example` for required vars)
- [ ] CORS configured to allow only frontend origin
- [ ] Input validation on all user-provided data
- [ ] SQL injection prevention via ORM (no raw SQL strings with user input)
- [ ] Rate limiting on auth endpoints (if exposed publicly)

**Rationale**: Multi-user systems have zero margin for security errors. Automated checks (via `api-security` skill) supplement manual review.

**Test**: `api-security` skill MUST be invoked during `/sp.plan` for any feature touching auth or data access.

## Governance

### Amendment Process

1. Propose change in constitution-scoped PHR (`history/prompts/constitution/`)
2. Run `/sp.constitution <proposed-changes>` to update file
3. Validate templates (plan, spec, tasks) still align
4. Update `LAST_AMENDED_DATE` to today, bump `CONSTITUTION_VERSION` per semver
5. Create ADR if amendment introduces new architectural constraint
6. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

**Version Bumps**:
- **MAJOR**: Principle removal, incompatible governance changes (e.g., remove TDD requirement)
- **MINOR**: New principle added, expanded guidance (e.g., add observability principle)
- **PATCH**: Clarifications, typo fixes, wording improvements

**Rationale**: Constitution is living document. Structured amendments prevent drift and ensure team alignment.

### Compliance Review

- Every PR MUST include constitution compliance statement in description
- Plan phase includes "Constitution Check" section mapping principles to feature design
- Violations require explicit justification in `plan.md` Complexity Tracking table

**Enforcement**: CI fails PRs without compliance statement. Manual review for justified violations.

### Non-Negotiable Principles

The following principles CANNOT be amended without project-wide discussion and unanimous consent:
- Spec-Driven Development (Principle I)
- User Isolation and Security First (Principle II)
- Test-First for Security-Critical Paths (Principle V)

**Rationale**: These form project identity and security foundation. Removing them changes project's fundamental nature.

**Version**: 1.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
