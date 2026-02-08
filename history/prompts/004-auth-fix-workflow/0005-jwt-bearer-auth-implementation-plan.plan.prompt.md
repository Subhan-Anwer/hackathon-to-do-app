---
id: 0005
title: jwt-bearer-auth-implementation-plan
stage: plan
date: 2026-02-08
surface: claude-code-cli
model: claude-sonnet-4-5
feature: 004-auth-fix-workflow
branch: 004-auth-fix-workflow
user: subhan
command: /sp.plan
labels: [authentication, jwt, bearer-token, planning, architecture]
links:
  spec: specs/004-auth-fix-workflow/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-auth-fix-workflow/plan.md
  - specs/004-auth-fix-workflow/research.md
  - specs/004-auth-fix-workflow/data-model.md
  - specs/004-auth-fix-workflow/quickstart.md
  - specs/004-auth-fix-workflow/contracts/README.md
  - CLAUDE.md (updated via update-agent-context.sh)
tests: []
---

## Prompt

User invoked `/sp.plan` command to generate implementation plan for feature 004-auth-fix-workflow (JWT Bearer Token Authentication Fix).

**Context from /sp.specify**:
- Problem: 401 Unauthorized errors when creating tasks
- Root Cause: JWT tokens sent via httpOnly cookies blocked on cross-origin requests (localhost:3000 → localhost:8000)
- Solution: Extract JWT from Better Auth session, include in Authorization: Bearer <token> header

**Planning Workflow Executed**:
1. Load specification from specs/004-auth-fix-workflow/spec.md
2. Load constitution principles from .specify/memory/constitution.md
3. Phase 0: Research Better Auth JWT extraction methods using Context7 MCP
4. Phase 1: Design authentication flow, create data model, generate contracts
5. Update agent context with technology stack
6. Create PHR for audit trail

## Response snapshot

**Phase 0: Research Completed**

Created `research.md` documenting:
- Better Auth JWT token extraction via `set-auth-jwt` response header (recommended method)
- Session object structure: `session.user.id` for user_id, `session.session` for metadata
- Backend already supports Authorization Bearer header (dependencies.py:51-59)
- Next.js 16 Server Actions pattern selected for implementation
- All technical unknowns resolved

**Phase 1: Design & Contracts Completed**

Created `data-model.md` with:
- JWT token structure (header.payload.signature, HS256 algorithm)
- Better Auth session object TypeScript types
- Authentication flow diagrams (cookie-based BROKEN vs Bearer token FIXED)
- Error handling flows for missing/invalid tokens
- Security model (defense in depth: frontend validation + backend JWT verification + user isolation)

Created `quickstart.md` with:
- Developer testing checklist (10 verification steps)
- Browser DevTools verification instructions
- Common issues & solutions troubleshooting guide
- curl examples for direct backend testing

Created `contracts/README.md` documenting:
- NO API contract changes (backend endpoints unchanged)
- Authentication header change: Cookie → Authorization: Bearer <token>
- Backward compatibility: backend accepts both cookie and Bearer token
- Contract compatibility matrix (development vs production scenarios)

**Plan.md Updated**:
- Summary: Problem statement + solution approach
- Technical Context: TypeScript 5 (frontend), Python 3.12 (backend), Next.js 16, Better Auth, FastAPI
- Constitution Check: ALL principles passed (✅)
  - Principle I: Spec-driven development ✅
  - Principle II: User isolation and security first ✅
  - Principle III: Reusability through skills ✅
  - Principle IV: Clarity and consistency ✅
  - Principle V: Test-first for security ✅
  - Principle VI: Simplicity and smallest viable change ✅
- Project Structure: Web application monorepo, backend requires ZERO changes
- Complexity Tracking: N/A (no violations, simplicity maintained)

**Agent Context Updated**:
- Ran `.specify/scripts/bash/update-agent-context.sh claude`
- Added TypeScript 5, Python 3.12, PostgreSQL (no schema changes) to CLAUDE.md

## Outcome

- ✅ Impact: Comprehensive implementation plan with research-backed solution for JWT Bearer token authentication. Backend requires zero changes (already supports Bearer tokens). Frontend changes localized to 7 files (1 new, 6 modified).
- 🧪 Tests: Existing backend tests remain valid (already validate Bearer token authentication). Manual testing guide provided in quickstart.md.
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, quickstart.md, contracts/README.md) totaling ~1500 lines of documentation.
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation task breakdown from plan
- 🧠 Reflection: Research phase successfully leveraged Context7 MCP to get up-to-date Better Auth JWT documentation. Discovered `set-auth-jwt` header method which is simpler than separate token endpoint. Backend analysis revealed no changes needed (already implements dual authentication). Constitution compliance perfect (all 6 principles aligned). Plan maintains simplicity (Server Actions are Next.js built-in, no custom abstractions).

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully
- Graders run and results (PASS/FAIL): Constitution Check PASSED all 6 principles without violations
- Prompt variant (if applicable): Standard /sp.plan workflow with Context7 MCP integration for research
- Next experiment (smallest change to try): N/A - ready for task generation phase (/sp.tasks)
