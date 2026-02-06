---
id: 0002
title: frontend-auth-implementation-plan
stage: plan
date: 2026-02-06
surface: cli
model: claude-sonnet-4-5
feature: 002-frontend-auth
branch: 002-frontend-auth
user: user
command: /sp.plan
labels: [plan, frontend, authentication, nextjs, better-auth, implementation-steps]
links:
  spec: specs/002-frontend-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/002-frontend-auth/plan.md
    status: created
    type: implementation-plan
tests: []
---

## Prompt

User requested implementation plan via `/sp.plan` command with detailed guidance:

**Specification**: `specs/002-frontend-auth/spec.md`

**User Request**: Create a clear, sequential, incremental implementation plan for building the complete Next.js 16 frontend + authentication system.

**Prioritized Implementation Order**:
1. Project setup verification & dependencies
2. Better Auth installation & configuration (JWT enabled)
3. API client with automatic JWT attachment
4. Authentication pages & logic (/login, /signup, logout)
5. Protected layout / middleware (redirect if not authenticated)
6. Main task dashboard page (/tasks)
7. Reusable UI components (TaskCard, TaskForm, etc.) using shadcn/ui
8. CRUD operations integration (list, create, update, delete, toggle)
9. Error handling, loading states, toasts
10. Final polish, responsiveness, accessibility checks

**Requirements for Each Step**:
- Specify which files to create or modify
- List key imports and patterns to follow
- Reference exact sections from frontend.md and frontend/CLAUDE.md
- Mention which skills to use (better-auth-integration, frontend-design, nextjs-frontend-builder)
- Note what to test after completing the step

**Goal**: Produce a polished, responsive frontend that:
- Fully authenticates via Better Auth + JWT
- Seamlessly consumes the already-built backend API
- Implements all 5 required features correctly
- Uses shadcn/ui components exclusively for UI
- Handles errors and loading states gracefully

## Response snapshot

Created comprehensive 1751-line implementation plan with:

**Constitution Check** (✅ PASSED):
- Principle I: Spec-Driven Development ✅
- Principle II: User Isolation and Security ✅ (frontend JWT attachment, 401 handling, httpOnly cookies)
- Principle III: Reusability Through Skills ✅ (better-auth-integration, frontend-design, nextjs-frontend-builder)
- Principle IV: Clarity and Consistency ✅ (Next.js App Router conventions, TypeScript strict mode)
- Principle V: Test-First for Security Paths ⚠️ (manual testing justified - backend has 34 passing tests)
- Principle VI: Simplicity and Smallest Change ✅ (no premature abstraction, YAGNI compliance)

**Technical Context**:
- Language: TypeScript 5+ with strict mode
- Dependencies: Next.js 16.1.6, React 19.2.3, Better Auth, shadcn/ui, Tailwind CSS 4
- Performance: <2s load, <100ms optimistic updates, <500ms auth redirects
- Scope: 4 routes, ~15-20 components, authenticated API calls

**Project Structure Designed**:
- Frontend directory structure with feature-based organization
- Components organized by domain: auth/, tasks/, layout/, ui/
- Server components by default, client components only for interactivity
- Middleware for protected routes
- TypeScript types matching backend schemas

**Phase 0: Research & Dependencies** (5 research tasks):
1. Better Auth JWT configuration for Next.js App Router
2. API client with automatic JWT header injection
3. shadcn/ui component installation and usage patterns
4. Protected routes and Next.js middleware
5. Server vs client component architecture

**Phase 1: Design & Contracts**:
- Data model with TypeScript interfaces matching backend schemas
- API contracts documenting all backend endpoints
- Quickstart guide for developers
- Agent context update with technology stack

**Phase 2: Implementation Steps** (20 detailed steps):
1. Environment setup & dependency installation
2. Better Auth configuration with JWT plugin
3. TypeScript types & API client with automatic JWT attachment
4. Authentication custom hook (useAuth)
5. Login & signup pages with shadcn/ui forms
6. Protected route middleware
7. Root page redirect based on auth state
8. App header with logout button
9. Task list page (server component with data fetching)
10. Task item component (client component with optimistic updates)
11. Task creation form (Dialog with react-hook-form + zod)
12. Task editing & deletion with confirmation
13. Task list state management (client component)
14. Loading states & skeleton components
15. Toast notifications setup (sonner)
16. Error handling with user-friendly messages
17. Responsive design & mobile optimization
18. Keyboard navigation & accessibility
19. Multi-user isolation testing (2 test accounts)
20. Final polish & production checklist

**Key Implementation Patterns**:
- Better Auth JWT stored in httpOnly cookies
- Automatic Authorization header attachment in API client
- 401 responses trigger redirect to /login
- Optimistic UI updates for checkbox toggles
- shadcn/ui for all UI components (Button, Card, Form, Dialog, Toast, etc.)
- react-hook-form with zod validation
- Tailwind CSS responsive breakpoints (sm:, md:, lg:)
- Server components for layouts, client components for forms
- Suspense boundaries with skeleton loading states

**Constitution Complexity Tracking**:
- Manual testing justified (backend has comprehensive tests covering auth and isolation)
- Multi-user scenario testing as acceptance criteria

## Outcome

- ✅ Impact: Created comprehensive 20-step implementation plan for Next.js 16 frontend with Better Auth JWT integration. Plan provides clear, sequential, incremental steps with testable acceptance criteria for each step.
- 🧪 Tests: Manual testing strategy defined with multi-user isolation testing, DevTools verification, and responsive design testing at 320px/768px/1024px/1920px breakpoints.
- 📁 Files: Created specs/002-frontend-auth/plan.md (1751 lines) with complete implementation roadmap, constitution compliance, and 20 detailed implementation steps.
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown, then `/sp.implement` or manual implementation via specialized agents (nextjs-frontend-builder, better-auth-integration, frontend-design)
- 🧠 Reflection: Plan successfully balances comprehensive guidance with practical incrementality. Each step is independently testable and references specific spec requirements. Constitution compliance verified with justified deviation for manual testing (backend already has 34 passing tests). Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Plan generated successfully with clear constitution compliance and justified deviations.
- Graders run and results (PASS/FAIL): Constitution Check - PASSED (6/6 principles, 1 justified deviation documented)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided detailed implementation order and step requirements
- Next experiment (smallest change to try): N/A - plan is complete and ready for task generation
