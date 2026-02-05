---
id: 001
title: Multi-User Todo Constitution Ratification
stage: constitution
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: subhan
command: /sp.constitution
labels: ["constitution", "security", "spec-driven-development", "multi-user"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document, no tests)
---

## Prompt

Multi-User Todo Full-Stack Web Application
Core principles:
- Spec-driven development only (write spec → generate plan → break into tasks → implement via Claude Code)
- No manual coding; all changes via /sp commands and agents
- User isolation and security first (JWT auth, task ownership enforcement)
- Reusability through skills/agents (e.g., better-auth-integration, database-schema-designer)
- Clarity and consistency (align with CLAUDE.md files, reference specs/skills explicitly)
Key standards:
- Tech stack: Next.js 16+ (frontend), FastAPI (backend with uv deps), SQLModel ORM, Neon Serverless PostgreSQL, Better Auth (JWT)
- API: RESTful endpoints as specified (GET/POST/PUT/DELETE/PATCH /api/{user_id}/tasks/...), all require valid JWT
- Auth: Shared BETTER_AUTH_SECRET, middleware verifies token/extracts user_id, 401 on failures, filter responses to user's data only
- Features: Implement all 5 basics (Add/Delete/Update/View Tasks, Mark Complete) with persistent storage and responsive UI
- Monorepo: Use existing structure, reference @.claude/ and @.specify/ paths
Constraints:
- No shared DB sessions; stateless auth with token expiry (e.g., 7 days)
- Responsive frontend (Tailwind, server components default)
- Multi-user: Each user sees/modifies only own tasks; enforce on every operation
- Testing: Include security checks (e.g., via api-security skill), no production deploys without verification
Success criteria:
- All features functional with user isolation (test via multiple logins)
- JWT auth integrates seamlessly (frontend issues, backend verifies)
- No hallucinations (all implementations trace to specs/constitution)

## Response snapshot

Created Multi-User Todo Full-Stack Web Application Constitution (v1.0.0) with comprehensive governance framework:

**Core Principles Established:**
1. Spec-Driven Development (NON-NEGOTIABLE) - All changes via /sp commands, zero manual coding
2. User Isolation and Security First - JWT auth, middleware verification, database-level filtering
3. Reusability Through Skills and Agents - better-auth-integration, database-schema-designer, api-security
4. Clarity and Consistency - CLAUDE.md alignment, explicit spec references, monorepo conventions
5. Test-First for Security-Critical Paths - TDD mandatory for auth/isolation logic
6. Simplicity and Smallest Viable Change - YAGNI, no premature abstraction

**Technology Standards Codified:**
- Stack: Next.js 16+ (App Router, RSC, Tailwind) + FastAPI (uv, SQLModel) + Neon PostgreSQL + Better Auth JWT
- API Design: RESTful `/api/{user_id}/tasks/...`, standardized error codes (401/403/404/422)
- Auth Flow: httpOnly cookies, 7-day expiry, shared BETTER_AUTH_SECRET, stateless tokens
- Data Isolation: All queries MUST filter by user_id (code example provided)

**Development Workflow Defined:**
- Phases: Specify → Plan → Tasks → Implement → Validate
- PHR routing: constitution/, <feature-name>/, general/
- ADR triggers: Impact + Alternatives + Scope (all three required)

**Quality Gates:**
- Feature completion checklist (8 items including multi-user test validation)
- Security checklist (7 mandatory items for all features)
- Non-negotiable principles (I, II, V cannot be amended without unanimous consent)

**Governance:**
- Amendment process with semver versioning (MAJOR/MINOR/PATCH rules defined)
- Compliance review requirements (PR statements, Constitution Check in plans)
- Template validation on amendments

## Outcome

- ✅ Impact: Established comprehensive constitutional framework for Multi-User Todo application with security-first principles, tech stack standards, and development workflow. All 6 core principles defined with rationale and tests. Non-negotiable principles protected.
- 🧪 Tests: No tests (constitutional document). Future features MUST comply with Security Checklist (7 items) and Feature Completion Criteria (8 items).
- 📁 Files: Created/Updated .specify/memory/constitution.md (260 lines, v1.0.0), Created history/prompts/constitution/ directory structure
- 🔁 Next prompts: Run `/sp.specify <feature-description>` to create first feature spec (e.g., Task CRUD operations). Review existing templates for constitution alignment. Consider ADR for tech stack choices if alternatives were evaluated.
- 🧠 Reflection: Constitution successfully ratified with all placeholders filled. Tech stack and security requirements clearly defined. User isolation principle emphasized throughout (Principle II, Data Isolation section, Quality Gates). Templates already align with structure, no immediate updates required. Ready for feature specification phase.

## Evaluation notes (flywheel)

- Failure modes observed: None (first ratification, no prior state to compare). Potential risk: Constitution length (260 lines) may cause TL;DR - mitigate via CLAUDE.md summaries.
- Graders run and results (PASS/FAIL): N/A (no automated graders for constitution documents)
- Prompt variant (if applicable): N/A (standard /sp.constitution workflow)
- Next experiment (smallest change to try): Test constitution compliance during first feature spec (`/sp.specify`) - verify Constitution Check section generation in plan.md references correct principles (I-VI). Validate PHR routing to feature-name subdirectory.
