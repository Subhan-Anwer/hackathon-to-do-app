---
id: 0002
title: auth-workflow-reliability-plan
stage: plan
date: 2026-02-07T00:00:00Z
surface: CLI
model: claude-sonnet-4-5
feature: 004-auth-fix-workflow
branch: 004-auth-fix-workflow
user: Subhan Anwer
command: /sp.plan
labels: [authentication, bug-fix, ux-improvement, jwt, better-auth, environment-aware-config]
links:
  spec: specs/004-auth-fix-workflow/spec.md
  ticket: N/A
  adr: specs/004-auth-fix-workflow/adr-environment-aware-cookies.md (suggested, not created)
  pr: N/A
files:
  - path: specs/004-auth-fix-workflow/plan.md
    status: created
    lines: 785
  - path: specs/004-auth-fix-workflow/contracts/auth-flow.md
    status: created
    lines: 211
tests: []
---

## Prompt

Use the specification file: @specs/004-auth-fix-workflow/spec.md

Create a prioritized implementation plan to fix authentication and make the Todo app workflow smooth.

Break it into 6–8 clear, sequential steps that can be implemented one by one.

Prioritize in this order:
1. Fix Better Auth configuration (enable JWT plugin)
2. Fix cookie attributes for localhost compatibility
3. Improve API client to send Authorization Bearer header
4. Enhance 401 handling and user feedback
5. Add loading + error states to task actions
6. Final verification steps (manual test checklist)

For each step:
- Specify file(s) to modify
- Describe the change in 1–2 sentences
- Mention relevant skills (better-auth-integration, frontend-design)
- Note what to test after the step

## Response snapshot

Created comprehensive implementation plan with 7 prioritized steps addressing authentication and UX issues in the full-stack Todo application.

**Plan Structure:**

1. **Summary**: Identified 5 core problems - JWT plugin not enabled, cookie blocking on localhost, missing Bearer header, poor 401 handling, lack of loading/toast feedback

2. **Technical Context**: Filled completely (no NEEDS CLARIFICATION) - TypeScript/Python, Next.js/FastAPI stack, Neon PostgreSQL, manual testing approach, localhost HTTP + production HTTPS support

3. **Constitution Check**: All 6 principles PASS
   - Spec-driven development ✅
   - User isolation & security ✅ (maintained, enhanced)
   - Reusability via skills ✅ (better-auth-integration, api-security, frontend-design)
   - Clarity & consistency ✅
   - Test-first for security ✅ (manual test checklists per step)
   - Simplicity & smallest viable change ✅

4. **Implementation Steps (7 steps, prioritized P1-P3)**:

   **Step 1 (P1)**: Enable Better Auth JWT Plugin 🔑
   - File: `frontend/lib/auth.ts`
   - Change: Add `jwt()` plugin to generate tokens with `sub` claim
   - Skills: better-auth-integration
   - Test: Verify JWT contains `sub`, `exp`, `iat` claims in DevTools

   **Step 2 (P1)**: Fix Cookie Attributes for Localhost 🍪
   - File: `frontend/lib/auth.ts`
   - Change: Environment-aware cookie attributes (dev: secure=false, sameSite=lax; prod: secure=true, sameSite=none)
   - Skills: better-auth-integration, api-security
   - Test: Verify cookies sent on localhost HTTP, correct attributes in DevTools

   **Step 3 (P1)**: Add Authorization Bearer Header 📡
   - Files: `frontend/lib/api.ts`, `frontend/lib/auth-client.ts`
   - Change: Prefer `Authorization: Bearer` header using `authClient.getSession()`, keep cookie fallback
   - Skills: better-auth-integration
   - Test: Verify both Authorization and Cookie headers sent in Network tab

   **Step 4 (P2)**: Enhance 401 Error Handling 🚨
   - File: `frontend/lib/api.ts`
   - Change: Show toast "Your session has expired..." before redirect (1.5s delay)
   - Skills: frontend-design
   - Test: Delete cookie, verify toast appears, then redirect to /login

   **Step 5 (P3)**: Add Loading States ⏳
   - Files: task-form.tsx, create/edit/delete-task-dialog.tsx, task-item.tsx
   - Change: Add `isLoading` state, disable buttons during operations
   - Skills: frontend-design
   - Test: Verify "Creating..." text, disabled buttons during operations

   **Step 6 (P3)**: Add Success/Error Toasts 🎉
   - Files: task-list.tsx, all task components
   - Change: Toast notifications for CRUD operations, auto-refresh list
   - Skills: frontend-design
   - Test: Verify toasts appear within 1s, list refreshes after operations

   **Step 7 (P3)**: Manual Test Checklist 🧪
   - File: Create `specs/004-auth-fix-workflow/TESTING.md`
   - Change: Comprehensive 8-phase testing guide (JWT, cookies, headers, 401, loading, toasts, multi-user isolation, production)
   - Skills: N/A (manual testing)
   - Test: Execute all 8 phases systematically

5. **Phase 0 Research**: Completed
   - Better Auth JWT plugin research (decision: use jwt() plugin)
   - Environment-aware cookie configuration (decision: process.env.NODE_ENV conditional)
   - Alternatives considered and rejected with rationales

6. **Phase 1 Contracts**: Created `contracts/auth-flow.md`
   - Environment-aware authentication flow diagrams (dev + prod)
   - Cookie attribute decision matrix
   - Security guarantees (XSS, CSRF, user isolation)
   - Error handling flows (401, 403)

7. **ADR Suggestion**: Environment-aware cookie configuration
   - Rationale: Cross-cutting decision affecting all authenticated requests
   - Recommended: `/sp.adr environment-aware-cookie-configuration`

8. **Complexity Tracking**: Empty (no constitution violations)

**Key Technical Decisions:**

- **Environment-aware cookies**: `process.env.NODE_ENV` conditional for secure/sameSite attributes
  - Development: `secure: false`, `sameSite: "lax"` (allows localhost HTTP cross-origin)
  - Production: `secure: true`, `sameSite: "none"` (allows HTTPS cross-origin)

- **Dual authentication**: Both Authorization Bearer + cookie fallback for resilience

- **User feedback**: 3-layer feedback (loading states → success/error toasts → list refresh)

**Files Modified** (planned):
- `frontend/lib/auth.ts` - JWT plugin, environment-aware cookies
- `frontend/lib/api.ts` - Bearer header, 401 toast handling
- Multiple task components - Loading states, toast notifications
- Backend: No changes needed (already accepts both Bearer and cookie)

**Success Validation**:
- Manual test checklist per step (total 8 phases for final verification)
- Multi-user isolation testing (Constitution Principle II)
- Production environment testing (HTTPS cookie attributes)

## Outcome

- ✅ Impact: Created production-ready implementation plan addressing 5 critical auth/UX issues with 7 prioritized, testable steps
- 🧪 Tests: Manual test checklists created for each step (total 8 phases for comprehensive verification)
- 📁 Files: Created 2 files (plan.md with 785 lines, auth-flow.md contract with 211 lines)
- 🔁 Next prompts: `/sp.tasks` to generate actionable task breakdown, `/sp.adr environment-aware-cookie-configuration` to document architectural decision
- 🧠 Reflection: Successfully translated 25 functional requirements into 7 concrete implementation steps with environment-aware solutions. Key insight: Cookie security attributes are the root cause of localhost authentication failures - environment-based conditionals solve the HTTP/HTTPS compatibility issue without code duplication or security trade-offs.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan created successfully on first iteration
- Graders run and results (PASS/FAIL): Constitution Check PASSED all 6 principles
- Prompt variant (if applicable): User provided specific guidance (6-8 steps, prioritized order, file-level details)
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to validate plan completeness and generate dependency-ordered task breakdown
