# Implementation Plan: Multi-User Todo Frontend with Authentication

**Branch**: `002-frontend-auth` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-frontend-auth/spec.md`

## Summary

Build a production-ready Next.js 16+ frontend with full authentication using Better Auth JWT integration. The frontend will consume the existing FastAPI backend (already implemented at `/backend`) to provide all 5 required task features (Add, Delete, Update, View List, Mark Complete) with strict user isolation enforcement. All UI will be built exclusively with shadcn/ui components and Tailwind CSS, following React Server Components patterns with client components only where necessary for interactivity.

**Technical Approach**: Incremental implementation starting with Better Auth setup, then API client with automatic JWT attachment, followed by authentication pages, protected routing, and finally task CRUD operations with optimistic UI updates.

## Technical Context

**Language/Version**: TypeScript 5+ with strict mode, Node.js 20+
**Primary Dependencies**: Next.js 16.1.6, React 19.2.3, Better Auth (with JWT plugin), shadcn/ui components, Tailwind CSS 4
**Storage**: N/A (frontend only, backend handles database)
**Testing**: Manual testing against live backend, browser DevTools verification of JWT headers
**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web frontend (Next.js App Router)
**Performance Goals**: <2s initial task list load, <100ms optimistic UI updates, <500ms auth redirects
**Constraints**: Server components by default, httpOnly cookies for JWT (no localStorage), shadcn/ui only for UI, no custom CSS files
**Scale/Scope**: Single-page application with 4 routes (/login, /signup, /tasks, /), ~15-20 React components, authenticated API calls to localhost:8000

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- **Compliance**: This plan is generated from `specs/002-frontend-auth/spec.md` via `/sp.plan` command
- **Verification**: All implementation steps reference spec requirements (FR-001 to FR-030, SC-001 to SC-015)
- **Traceability**: Each task will link back to specific functional requirements

### Principle II: User Isolation and Security First ✅
- **Frontend Responsibility**:
  - Automatically attach JWT to all API requests (FR-005)
  - Handle 401 responses by redirecting to login (FR-008)
  - Verify backend enforces isolation (frontend trusts backend's user_id filtering)
- **Security Measures**:
  - httpOnly cookies prevent XSS token theft (FR-004)
  - No client-side token storage in localStorage/sessionStorage
  - JWT automatically managed by Better Auth
- **Testing**: Login as multiple users, verify each sees only their own tasks (SC-013)

### Principle III: Reusability Through Skills and Agents ✅
- **Skills to Use**:
  - `better-auth-integration`: JWT setup, API client patterns, auth hooks
  - `frontend-design`: shadcn/ui component patterns, responsive layouts
  - `nextjs-frontend-builder`: App Router structure, server/client component patterns
- **Rationale**: Leverage existing patterns instead of custom implementations

### Principle IV: Clarity and Consistency ✅
- **CLAUDE.md Compliance**: Follow `frontend/CLAUDE.md` conventions
  - API client in `/lib/api.ts`
  - Server components by default
  - Tailwind classes only (no inline styles)
- **Path Aliases**: Use Next.js `@/` aliases for imports
- **Single Source of Truth**: Spec for requirements, constitution for principles

### Principle V: Test-First for Security-Critical Paths ⚠️
- **Deviation**: Manual testing instead of automated tests in this phase
- **Justification**: Frontend primarily consumes backend API which already has comprehensive test coverage (34 passing tests including isolation tests). Frontend testing will be manual via DevTools and multi-user scenarios.
- **Mitigation**: Detailed test scenarios in implementation steps, multi-user isolation testing as acceptance criteria

### Principle VI: Simplicity and Smallest Viable Change ✅
- **YAGNI Compliance**: Implement only specified features (no dark mode, no i18n, no offline support per Out of Scope)
- **Incremental Approach**: Each step delivers testable functionality
- **No Premature Abstraction**: Direct API calls, simple state management (no Redux/Zustand in this phase)

**GATE RESULT**: ✅ PASS (with justified deviation documented in Complexity Tracking)

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-auth/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (Phase 1 output)
├── research.md          # Phase 0 output (Better Auth, shadcn/ui patterns)
├── data-model.md        # Phase 1 output (TypeScript interfaces for API)
├── quickstart.md        # Phase 1 output (developer guide)
├── contracts/
│   └── api-types.ts     # TypeScript types matching backend schemas
└── checklists/
    └── requirements.md  # Spec quality checklist (COMPLETE)
```

### Source Code (frontend/ directory)

```text
frontend/
├── app/                         # Next.js App Router
│   ├── layout.tsx              # Root layout (EXISTING)
│   ├── page.tsx                # Root redirect (TO MODIFY)
│   ├── globals.css             # Tailwind globals (EXISTING)
│   ├── login/
│   │   └── page.tsx            # Login page (NEW - CLIENT)
│   ├── signup/
│   │   └── page.tsx            # Signup page (NEW - CLIENT)
│   └── tasks/
│       └── page.tsx            # Tasks dashboard (NEW - SERVER + CLIENT)
├── components/                  # React components (NEW DIRECTORY)
│   ├── auth/
│   │   ├── login-form.tsx      # Login form with shadcn/ui (CLIENT)
│   │   └── signup-form.tsx     # Signup form with shadcn/ui (CLIENT)
│   ├── tasks/
│   │   ├── task-list.tsx       # Task list container (SERVER)
│   │   ├── task-item.tsx       # Individual task card (CLIENT)
│   │   ├── task-form.tsx       # Create/Edit task form (CLIENT)
│   │   └── empty-state.tsx     # Empty state UI (SERVER)
│   ├── layout/
│   │   ├── header.tsx          # App header with logout (CLIENT)
│   │   └── protected-layout.tsx # Auth-protected wrapper (SERVER)
│   └── ui/                     # shadcn/ui components (TO ADD)
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── form.tsx
│       ├── checkbox.tsx
│       ├── dialog.tsx
│       ├── toast.tsx
│       ├── skeleton.tsx
│       └── alert-dialog.tsx
├── lib/
│   ├── utils.ts                # Utility functions (EXISTING)
│   ├── auth.ts                 # Better Auth client config (NEW)
│   └── api.ts                  # API client with JWT (NEW)
├── hooks/                       # Custom React hooks (NEW DIRECTORY)
│   └── use-auth.ts             # Auth state and session hooks (NEW)
├── types/                       # TypeScript types (NEW DIRECTORY)
│   └── task.ts                 # Task-related types (NEW)
├── middleware.ts                # Next.js middleware for auth (NEW)
├── .env.local                  # Environment variables (EXISTING)
└── package.json                # Dependencies (TO UPDATE)
```

**Structure Decision**: Chose Next.js App Router with feature-based component organization (`components/auth/`, `components/tasks/`) per frontend/CLAUDE.md guidelines. Server components used for layouts and static content, client components ('use client') only for forms and interactive elements.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Manual testing instead of automated tests (Principle V) | Frontend primarily consumes backend API which already has 34 passing tests covering auth and isolation | Writing frontend tests would duplicate backend coverage; manual testing with multi-user scenarios provides sufficient validation for this phase |

## Phase 0: Research & Dependencies

### Research Tasks

1. **Better Auth Configuration**
   - **Research**: Better Auth JWT plugin setup for Next.js App Router
   - **Questions**:
     - How to configure Better Auth client with JWT plugin?
     - How to share BETTER_AUTH_SECRET between Next.js and FastAPI?
     - How to handle httpOnly cookies in Next.js API routes?
     - How to create auth hooks for session state?
   - **Output**: Configuration patterns for `lib/auth.ts`

2. **API Client with JWT Attachment**
   - **Research**: Automatic JWT header injection in fetch calls
   - **Questions**:
     - How to extract JWT from Better Auth session?
     - How to create typed fetch wrapper with automatic Authorization header?
     - How to handle 401 responses globally (redirect to login)?
     - How to type API responses matching backend schemas?
   - **Output**: API client patterns for `lib/api.ts`

3. **shadcn/ui Installation & Usage**
   - **Research**: Required shadcn/ui components for task management UI
   - **Questions**:
     - How to install Button, Card, Input, Form, Checkbox, Dialog, Toast, Skeleton, AlertDialog?
     - How to use shadcn/ui Form component with validation?
     - How to create accessible forms with proper error states?
   - **Output**: Component installation commands and usage patterns

4. **Protected Routes & Middleware**
   - **Research**: Next.js middleware for authentication checks
   - **Questions**:
     - How to implement middleware.ts for protected routes?
     - How to check Better Auth session in middleware?
     - How to redirect unauthenticated users to /login?
     - How to redirect authenticated users from /login to /tasks?
   - **Output**: Middleware patterns for `middleware.ts`

5. **Server vs Client Components**
   - **Research**: When to use 'use client' in Next.js App Router
   - **Questions**:
     - Which components must be client components (forms, interactive elements)?
     - Which components can be server components (layouts, static UI)?
     - How to pass data from server components to client components?
     - How to handle loading states with React Suspense?
   - **Output**: Component architecture patterns

### Dependencies to Add

Run these commands in `frontend/` directory:

```bash
# Better Auth with JWT plugin
npm install better-auth @better-auth/jwt

# shadcn/ui components (already configured, just install components)
npx shadcn@latest add button card input form checkbox dialog toast skeleton alert-dialog label textarea

# Additional utilities
npm install zod react-hook-form @hookform/resolvers  # For form validation
npm install sonner  # Toast notifications (shadcn/ui compatible)
```

### Research Output

Create `specs/002-frontend-auth/research.md` with findings for each research task.

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

Based on backend schemas (TaskRead, TaskCreate, TaskUpdate), define TypeScript interfaces:

```typescript
// User entity (from Better Auth session)
interface User {
  id: string;        // UUID from backend
  email: string;     // User email
  name?: string;     // Optional display name
}

// Task entity (matches TaskRead from backend schemas.py)
interface Task {
  id: string;                // UUID
  title: string;             // Required, max 200 chars
  description: string | null; // Optional
  completed: boolean;        // Completion status
  created_at: string;        // ISO datetime
  updated_at: string;        // ISO datetime
}

// Task creation payload (matches TaskCreate)
interface TaskCreateInput {
  title: string;             // Required, 1-200 chars
  description?: string;      // Optional
}

// Task update payload (matches TaskUpdate)
interface TaskUpdateInput {
  title?: string;            // Optional, 1-200 chars if provided
  description?: string;      // Optional
  completed?: boolean;       // Optional
}

// API response wrapper
interface ApiResponse<T> {
  data?: T;
  error?: string;
  code?: string;
}

// Session state
interface Session {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}
```

### API Contracts (`contracts/api-types.ts`)

Document all backend API endpoints the frontend will consume:

```typescript
// Authentication endpoints (Better Auth proxy)
POST /api/auth/signup
  Body: { email: string; password: string }
  Response: { user: User; token: string }

POST /api/auth/login
  Body: { email: string; password: string }
  Response: { user: User; token: string }

POST /api/auth/logout
  Response: { success: boolean }

// Task endpoints (backend API)
GET /api/{user_id}/tasks
  Headers: Authorization: Bearer <token>
  Response: Task[]

POST /api/{user_id}/tasks
  Headers: Authorization: Bearer <token>
  Body: TaskCreateInput
  Response: Task

GET /api/{user_id}/tasks/{task_id}
  Headers: Authorization: Bearer <token>
  Response: Task

PUT /api/{user_id}/tasks/{task_id}
  Headers: Authorization: Bearer <token>
  Body: TaskUpdateInput
  Response: Task

DELETE /api/{user_id}/tasks/{task_id}
  Headers: Authorization: Bearer <token>
  Response: { success: boolean }

PATCH /api/{user_id}/tasks/{task_id}/complete
  Headers: Authorization: Bearer <token>
  Response: Task
```

### Quickstart Guide (`quickstart.md`)

Step-by-step setup for developers:

1. Install dependencies
2. Configure environment variables (.env.local)
3. Run backend (localhost:8000)
4. Run frontend (localhost:3000)
5. Create test users
6. Test authentication flow
7. Test task CRUD operations

### Agent Context Update

Run agent context script (if available):

```bash
.specify/scripts/bash/update-agent-context.sh claude
```

Add technology stack for this feature:
- Next.js 16+ App Router
- Better Auth with JWT
- shadcn/ui components
- Tailwind CSS 4

## Phase 2: Implementation Steps

### Step 1: Environment Setup & Dependency Installation

**Objective**: Verify project structure and install all required dependencies

**Files to Create/Modify**:
- `frontend/.env.local` (modify)
- `frontend/package.json` (update)

**Actions**:
1. Add environment variables to `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   BETTER_AUTH_SECRET=<same-value-as-backend>
   BETTER_AUTH_URL=http://localhost:3000
   ```

2. Install Better Auth and JWT plugin:
   ```bash
   cd frontend
   npm install better-auth @better-auth/jwt
   ```

3. Install form validation libraries:
   ```bash
   npm install zod react-hook-form @hookform/resolvers
   npm install sonner  # Toast notifications
   ```

4. Install shadcn/ui components:
   ```bash
   npx shadcn@latest add button card input form checkbox dialog toast skeleton alert-dialog label textarea
   ```

**Key Patterns**:
- Use `NEXT_PUBLIC_` prefix for client-accessible variables
- Share `BETTER_AUTH_SECRET` exactly as defined in backend/.env
- Verify `components.json` configuration (already set up)

**Reference**:
- Spec: FR-021 (configurable API URL), FR-025 (BETTER_AUTH_SECRET)
- Skill: `better-auth-integration` for auth config patterns

**Test**:
- Run `npm run dev` → no errors
- Verify shadcn/ui components appear in `frontend/components/ui/`
- Check `.env.local` has all 3 variables

---

### Step 2: Better Auth Configuration

**Objective**: Set up Better Auth client with JWT plugin

**Files to Create**:
- `frontend/lib/auth.ts` (NEW)
- `frontend/app/api/auth/[...all]/route.ts` (NEW - Better Auth API route)

**Actions**:
1. Create `lib/auth.ts`:
   ```typescript
   import { createAuthClient } from "better-auth/client";
   import { jwtPlugin } from "@better-auth/jwt";

   export const authClient = createAuthClient({
     baseURL: process.env.BETTER_AUTH_URL,
     plugins: [
       jwtPlugin({
         expiresIn: 7 * 24 * 60 * 60, // 7 days
       }),
     ],
   });
   ```

2. Create Better Auth API route handler at `app/api/auth/[...all]/route.ts`

3. Configure httpOnly cookie settings

**Key Patterns**:
- Use Better Auth client hooks for session state
- JWT stored in httpOnly cookie (automatic)
- Token expiry matches backend (7 days)

**Reference**:
- Spec: FR-003, FR-004, FR-025
- Skill: `better-auth-integration` (auth-client.ts template)
- Context7: Query "Better Auth JWT plugin Next.js App Router"

**Test**:
- Visit `/api/auth/session` → returns session structure
- DevTools → Application → Cookies → verify httpOnly cookie created after login

---

### Step 3: TypeScript Types & API Client

**Objective**: Create typed API client with automatic JWT attachment

**Files to Create**:
- `frontend/types/task.ts` (NEW)
- `frontend/lib/api.ts` (NEW)

**Actions**:
1. Create `types/task.ts`:
   ```typescript
   export interface Task {
     id: string;
     title: string;
     description: string | null;
     completed: boolean;
     created_at: string;
     updated_at: string;
   }

   export interface TaskCreateInput {
     title: string;
     description?: string;
   }

   export interface TaskUpdateInput {
     title?: string;
     description?: string;
     completed?: boolean;
   }
   ```

2. Create `lib/api.ts`:
   ```typescript
   import { authClient } from "./auth";
   import { redirect } from "next/navigation";
   import type { Task, TaskCreateInput, TaskUpdateInput } from "@/types/task";

   const API_URL = process.env.NEXT_PUBLIC_API_URL;

   async function fetchWithAuth(url: string, options: RequestInit = {}) {
     const session = await authClient.getSession();

     if (!session?.user?.id || !session?.token) {
       redirect("/login");
     }

     const response = await fetch(url, {
       ...options,
       headers: {
         "Authorization": `Bearer ${session.token}`,
         "Content-Type": "application/json",
         ...options.headers,
       },
     });

     if (response.status === 401) {
       redirect("/login");
     }

     return response;
   }

   export const api = {
     tasks: {
       list: async (userId: string): Promise<Task[]> => {
         const res = await fetchWithAuth(`${API_URL}/api/${userId}/tasks`);
         return res.json();
       },
       create: async (userId: string, data: TaskCreateInput): Promise<Task> => {
         const res = await fetchWithAuth(`${API_URL}/api/${userId}/tasks`, {
           method: "POST",
           body: JSON.stringify(data),
         });
         return res.json();
       },
       // ... update, delete, toggleComplete methods
     },
   };
   ```

**Key Patterns**:
- Automatic JWT attachment from Better Auth session
- Automatic 401 redirect to login
- Typed request/response interfaces
- Centralized error handling

**Reference**:
- Spec: FR-005 (JWT header), FR-008 (401 redirect), FR-024 (typed API client)
- Skill: `better-auth-integration` (api-client.ts template)
- Backend: `backend/schemas.py` for type matching

**Test**:
- Call `api.tasks.list(userId)` → verify Authorization header in DevTools
- Simulate 401 response → verify redirect to /login

---

### Step 4: Authentication Custom Hook

**Objective**: Create reusable hook for auth state

**Files to Create**:
- `frontend/hooks/use-auth.ts` (NEW)

**Actions**:
1. Create `hooks/use-auth.ts`:
   ```typescript
   "use client";

   import { useEffect, useState } from "react";
   import { authClient } from "@/lib/auth";
   import { useRouter } from "next/navigation";

   export function useAuth() {
     const [session, setSession] = useState(null);
     const [loading, setLoading] = useState(true);
     const router = useRouter();

     useEffect(() => {
       authClient.getSession().then((session) => {
         setSession(session);
         setLoading(false);
       });
     }, []);

     const logout = async () => {
       await authClient.signOut();
       router.push("/login");
     };

     return {
       user: session?.user,
       isAuthenticated: !!session?.user,
       loading,
       logout,
     };
   }
   ```

**Key Patterns**:
- Client-side hook ('use client')
- Session state management
- Logout with redirect

**Reference**:
- Spec: FR-016 (logout functionality)
- Context7: Query "Better Auth session hooks Next.js"

**Test**:
- Use hook in component → verify session state
- Call logout → verify cookie cleared and redirect

---

### Step 5: Login & Signup Pages

**Objective**: Create authentication forms with shadcn/ui

**Files to Create**:
- `frontend/app/login/page.tsx` (NEW)
- `frontend/app/signup/page.tsx` (NEW)
- `frontend/components/auth/login-form.tsx` (NEW)
- `frontend/components/auth/signup-form.tsx` (NEW)

**Actions**:
1. Create `components/auth/login-form.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { useRouter } from "next/navigation";
   import { authClient } from "@/lib/auth";
   import { Button } from "@/components/ui/button";
   import { Input } from "@/components/ui/input";
   import { Card } from "@/components/ui/card";
   import { toast } from "sonner";

   export function LoginForm() {
     const [email, setEmail] = useState("");
     const [password, setPassword] = useState("");
     const [loading, setLoading] = useState(false);
     const router = useRouter();

     const handleSubmit = async (e: React.FormEvent) => {
       e.preventDefault();
       setLoading(true);

       try {
         await authClient.signIn.email({ email, password });
         toast.success("Login successful!");
         router.push("/tasks");
       } catch (error) {
         toast.error("Invalid credentials");
       } finally {
         setLoading(false);
       }
     };

     return (
       <Card className="w-full max-w-md p-6">
         <form onSubmit={handleSubmit} className="space-y-4">
           <Input
             type="email"
             placeholder="Email"
             value={email}
             onChange={(e) => setEmail(e.target.value)}
             required
           />
           <Input
             type="password"
             placeholder="Password"
             value={password}
             onChange={(e) => setPassword(e.target.value)}
             required
             minLength={8}
           />
           <Button type="submit" className="w-full" disabled={loading}>
             {loading ? "Signing in..." : "Sign In"}
           </Button>
         </form>
       </Card>
     );
   }
   ```

2. Create `app/login/page.tsx`:
   ```typescript
   import { LoginForm } from "@/components/auth/login-form";
   import Link from "next/link";

   export default function LoginPage() {
     return (
       <div className="min-h-screen flex items-center justify-center p-4">
         <div className="w-full max-w-md space-y-4">
           <h1 className="text-3xl font-bold text-center">Sign In</h1>
           <LoginForm />
           <p className="text-center text-sm">
             Don't have an account?{" "}
             <Link href="/signup" className="text-blue-600 hover:underline">
               Sign up
             </Link>
           </p>
         </div>
       </div>
     );
   }
   ```

3. Create similar pattern for signup page

**Key Patterns**:
- Client components for forms ('use client')
- shadcn/ui Card, Input, Button components
- Toast notifications for feedback
- Validation (email format, password length)
- Loading states

**Reference**:
- Spec: FR-001, FR-002 (auth forms), SC-001 (60s completion time)
- Skill: `frontend-design` for shadcn/ui patterns
- Context7: Query "shadcn/ui Form component with validation"

**Test**:
- Visit /login → see form
- Submit invalid credentials → see error toast
- Submit valid credentials → redirect to /tasks
- Click "Sign Up" link → navigate to /signup
- Verify responsive layout on mobile (320px width)

---

### Step 6: Protected Route Middleware

**Objective**: Implement authentication middleware for protected routes

**Files to Create**:
- `frontend/middleware.ts` (NEW)

**Actions**:
1. Create `middleware.ts`:
   ```typescript
   import { NextResponse } from "next/server";
   import type { NextRequest } from "next/server";
   import { authClient } from "./lib/auth";

   export async function middleware(request: NextRequest) {
     const { pathname } = request.nextUrl;

     const session = await authClient.getSession();
     const isAuthenticated = !!session?.user;

     // Redirect authenticated users from auth pages to /tasks
     if (isAuthenticated && (pathname === "/login" || pathname === "/signup")) {
       return NextResponse.redirect(new URL("/tasks", request.url));
     }

     // Redirect unauthenticated users from protected routes to /login
     if (!isAuthenticated && pathname.startsWith("/tasks")) {
       return NextResponse.redirect(new URL("/login", request.url));
     }

     return NextResponse.next();
   }

   export const config = {
     matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
   };
   ```

**Key Patterns**:
- Server-side middleware
- Session check before route access
- Redirect based on auth state
- Matcher configuration

**Reference**:
- Spec: FR-006 (redirect unauthenticated), FR-007 (redirect authenticated)
- Context7: Query "Next.js middleware authentication redirect"

**Test**:
- Visit /tasks without login → redirect to /login
- Login → visit /login → redirect to /tasks
- Verify redirect happens within 500ms (SC-006)

---

### Step 7: Root Page Redirect

**Objective**: Handle root path (/) based on auth state

**Files to Modify**:
- `frontend/app/page.tsx` (MODIFY)

**Actions**:
1. Update `app/page.tsx`:
   ```typescript
   import { redirect } from "next/navigation";
   import { authClient } from "@/lib/auth";

   export default async function HomePage() {
     const session = await authClient.getSession();

     if (session?.user) {
       redirect("/tasks");
     } else {
       redirect("/login");
     }
   }
   ```

**Key Patterns**:
- Server component (async)
- Conditional redirect based on session

**Reference**:
- Spec: User Story 1, Scenario 1 and 7

**Test**:
- Visit / without login → redirect to /login
- Visit / with active session → redirect to /tasks

---

### Step 8: App Header with Logout

**Objective**: Create persistent header with user info and logout button

**Files to Create**:
- `frontend/components/layout/header.tsx` (NEW)

**Actions**:
1. Create `components/layout/header.tsx`:
   ```typescript
   "use client";

   import { useAuth } from "@/hooks/use-auth";
   import { Button } from "@/components/ui/button";

   export function Header() {
     const { user, logout } = useAuth();

     return (
       <header className="border-b">
         <div className="container mx-auto px-4 py-4 flex items-center justify-between">
           <h1 className="text-2xl font-bold">My Tasks</h1>
           <div className="flex items-center gap-4">
             <span className="text-sm text-gray-600">{user?.email}</span>
             <Button variant="outline" onClick={logout}>
               Logout
             </Button>
           </div>
         </div>
       </header>
     );
   }
   ```

2. Add Header to tasks layout

**Key Patterns**:
- Client component for logout interaction
- useAuth hook for user info
- shadcn/ui Button component

**Reference**:
- Spec: FR-016 (logout), SC-010 (logout completes in <1s)

**Test**:
- See user email in header
- Click Logout → redirect to /login within 1 second
- Verify cookie cleared

---

### Step 9: Task List Page (Server Component)

**Objective**: Create tasks dashboard with server-side data fetching

**Files to Create**:
- `frontend/app/tasks/page.tsx` (NEW)
- `frontend/components/tasks/task-list.tsx` (NEW)
- `frontend/components/tasks/empty-state.tsx` (NEW)

**Actions**:
1. Create `app/tasks/page.tsx`:
   ```typescript
   import { api } from "@/lib/api";
   import { authClient } from "@/lib/auth";
   import { TaskList } from "@/components/tasks/task-list";
   import { EmptyState } from "@/components/tasks/empty-state";
   import { Header } from "@/components/layout/header";
   import { Suspense } from "react";
   import { Skeleton } from "@/components/ui/skeleton";

   export default async function TasksPage() {
     const session = await authClient.getSession();
     const userId = session?.user?.id;

     if (!userId) return null;

     const tasks = await api.tasks.list(userId);

     return (
       <div className="min-h-screen">
         <Header />
         <main className="container mx-auto px-4 py-8">
           <Suspense fallback={<Skeleton className="h-96" />}>
             {tasks.length === 0 ? (
               <EmptyState />
             ) : (
               <TaskList initialTasks={tasks} userId={userId} />
             )}
           </Suspense>
         </main>
       </div>
     );
   }
   ```

2. Create `components/tasks/empty-state.tsx`:
   ```typescript
   import { Button } from "@/components/ui/button";

   export function EmptyState() {
     return (
       <div className="text-center py-16">
         <h2 className="text-2xl font-semibold mb-4">No tasks yet</h2>
         <p className="text-gray-600 mb-6">
           Get started by creating your first task
         </p>
         <Button>Add Task</Button>
       </div>
     );
   }
   ```

**Key Patterns**:
- Server component for initial data fetch
- Suspense for loading state
- Pass data to client components via props
- Responsive container

**Reference**:
- Spec: FR-009 (display task list), FR-029 (empty state), SC-003 (2s load time)
- Context7: Query "Next.js App Router server components data fetching"

**Test**:
- Login → see task list (or empty state)
- Verify list loads within 2 seconds
- Verify responsive layout on mobile and desktop

---

### Step 10: Task Item Component (Client)

**Objective**: Create interactive task card with checkbox and actions

**Files to Create**:
- `frontend/components/tasks/task-item.tsx` (NEW)

**Actions**:
1. Create `components/tasks/task-item.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { Card } from "@/components/ui/card";
   import { Checkbox } from "@/components/ui/checkbox";
   import { Button } from "@/components/ui/button";
   import { api } from "@/lib/api";
   import { toast } from "sonner";
   import type { Task } from "@/types/task";

   interface TaskItemProps {
     task: Task;
     userId: string;
     onUpdate: (task: Task) => void;
     onDelete: (taskId: string) => void;
   }

   export function TaskItem({ task, userId, onUpdate, onDelete }: TaskItemProps) {
     const [completed, setCompleted] = useState(task.completed);

     const handleToggle = async () => {
       // Optimistic UI update
       setCompleted(!completed);

       try {
         const updated = await api.tasks.toggleComplete(userId, task.id);
         onUpdate(updated);
         toast.success("Task updated");
       } catch (error) {
         // Revert on error
         setCompleted(completed);
         toast.error("Failed to update task");
       }
     };

     const handleDelete = async () => {
       try {
         await api.tasks.delete(userId, task.id);
         onDelete(task.id);
         toast.success("Task deleted");
       } catch (error) {
         toast.error("Failed to delete task");
       }
     };

     return (
       <Card className="p-4">
         <div className="flex items-start gap-4">
           <Checkbox
             checked={completed}
             onCheckedChange={handleToggle}
             className="mt-1"
           />
           <div className="flex-1">
             <h3 className={`font-medium ${completed ? "line-through text-gray-500" : ""}`}>
               {task.title}
             </h3>
             {task.description && (
               <p className="text-sm text-gray-600 mt-1">{task.description}</p>
             )}
           </div>
           <div className="flex gap-2">
             <Button variant="outline" size="sm">Edit</Button>
             <Button variant="destructive" size="sm" onClick={handleDelete}>
               Delete
             </Button>
           </div>
         </div>
       </Card>
     );
   }
   ```

**Key Patterns**:
- Client component for interactivity
- Optimistic UI updates
- Error handling with revert
- shadcn/ui Card, Checkbox, Button

**Reference**:
- Spec: FR-013 (toggle complete), FR-030 (optimistic UI), SC-004 (100ms feedback)
- Skill: `frontend-design` for shadcn/ui component patterns

**Test**:
- Click checkbox → immediate visual update, API call in background
- Network error → checkbox reverts, error toast shown
- Verify completed tasks have line-through style

---

### Step 11: Task Creation Form (Dialog)

**Objective**: Create modal form for adding new tasks

**Files to Create**:
- `frontend/components/tasks/task-form.tsx` (NEW)
- `frontend/components/tasks/create-task-dialog.tsx` (NEW)

**Actions**:
1. Create `components/tasks/create-task-dialog.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
   import { Button } from "@/components/ui/button";
   import { TaskForm } from "./task-form";
   import type { Task } from "@/types/task";

   interface CreateTaskDialogProps {
     userId: string;
     onTaskCreated: (task: Task) => void;
   }

   export function CreateTaskDialog({ userId, onTaskCreated }: CreateTaskDialogProps) {
     const [open, setOpen] = useState(false);

     const handleSuccess = (task: Task) => {
       onTaskCreated(task);
       setOpen(false);
     };

     return (
       <Dialog open={open} onOpenChange={setOpen}>
         <DialogTrigger asChild>
           <Button size="lg">Add Task</Button>
         </DialogTrigger>
         <DialogContent>
           <DialogHeader>
             <DialogTitle>Create New Task</DialogTitle>
           </DialogHeader>
           <TaskForm userId={userId} onSuccess={handleSuccess} />
         </DialogContent>
       </Dialog>
     );
   }
   ```

2. Create `components/tasks/task-form.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { useForm } from "react-hook-form";
   import { zodResolver } from "@hookform/resolvers/zod";
   import * as z from "zod";
   import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
   import { Input } from "@/components/ui/input";
   import { Textarea } from "@/components/ui/textarea";
   import { Button } from "@/components/ui/button";
   import { api } from "@/lib/api";
   import { toast } from "sonner";
   import type { Task, TaskCreateInput } from "@/types/task";

   const taskSchema = z.object({
     title: z.string().min(1, "Title is required").max(200, "Title too long"),
     description: z.string().max(1000, "Description too long").optional(),
   });

   interface TaskFormProps {
     userId: string;
     task?: Task;
     onSuccess: (task: Task) => void;
   }

   export function TaskForm({ userId, task, onSuccess }: TaskFormProps) {
     const [loading, setLoading] = useState(false);

     const form = useForm<TaskCreateInput>({
       resolver: zodResolver(taskSchema),
       defaultValues: {
         title: task?.title || "",
         description: task?.description || "",
       },
     });

     const onSubmit = async (data: TaskCreateInput) => {
       setLoading(true);

       try {
         const result = task
           ? await api.tasks.update(userId, task.id, data)
           : await api.tasks.create(userId, data);

         toast.success(task ? "Task updated" : "Task created");
         onSuccess(result);
       } catch (error) {
         toast.error(task ? "Failed to update task" : "Failed to create task");
       } finally {
         setLoading(false);
       }
     };

     return (
       <Form {...form}>
         <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
           <FormField
             control={form.control}
             name="title"
             render={({ field }) => (
               <FormItem>
                 <FormLabel>Title</FormLabel>
                 <FormControl>
                   <Input placeholder="Enter task title" {...field} />
                 </FormControl>
                 <FormMessage />
               </FormItem>
             )}
           />
           <FormField
             control={form.control}
             name="description"
             render={({ field }) => (
               <FormItem>
                 <FormLabel>Description (Optional)</FormLabel>
                 <FormControl>
                   <Textarea
                     placeholder="Enter task description"
                     {...field}
                     value={field.value || ""}
                   />
                 </FormControl>
                 <FormMessage />
               </FormItem>
             )}
           />
           <Button type="submit" className="w-full" disabled={loading}>
             {loading ? "Saving..." : task ? "Update Task" : "Create Task"}
           </Button>
         </form>
       </Form>
     );
   }
   ```

**Key Patterns**:
- shadcn/ui Dialog for modal
- react-hook-form with zod validation
- Reusable form for create and edit
- Client-side validation before API call
- Loading states

**Reference**:
- Spec: FR-010 (task creation), FR-020 (shadcn/ui Form), FR-026 (inline validation), SC-002 (15s creation time)
- Context7: Query "shadcn/ui Dialog component" and "react-hook-form with zod"

**Test**:
- Click "Add Task" → dialog opens
- Submit empty title → validation error shown inline
- Submit valid task → success toast, task appears in list
- Verify creation completes in <15 seconds

---

### Step 12: Task Editing & Deletion

**Objective**: Implement edit and delete functionality with confirmation

**Files to Create**:
- `frontend/components/tasks/edit-task-dialog.tsx` (NEW)
- `frontend/components/tasks/delete-task-dialog.tsx` (NEW)

**Actions**:
1. Create `components/tasks/edit-task-dialog.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
   import { Button } from "@/components/ui/button";
   import { TaskForm } from "./task-form";
   import type { Task } from "@/types/task";

   interface EditTaskDialogProps {
     task: Task;
     userId: string;
     onTaskUpdated: (task: Task) => void;
   }

   export function EditTaskDialog({ task, userId, onTaskUpdated }: EditTaskDialogProps) {
     const [open, setOpen] = useState(false);

     const handleSuccess = (updated: Task) => {
       onTaskUpdated(updated);
       setOpen(false);
     };

     return (
       <Dialog open={open} onOpenChange={setOpen}>
         <DialogTrigger asChild>
           <Button variant="outline" size="sm">Edit</Button>
         </DialogTrigger>
         <DialogContent>
           <DialogHeader>
             <DialogTitle>Edit Task</DialogTitle>
           </DialogHeader>
           <TaskForm userId={userId} task={task} onSuccess={handleSuccess} />
         </DialogContent>
       </Dialog>
     );
   }
   ```

2. Create `components/tasks/delete-task-dialog.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
   import { Button } from "@/components/ui/button";
   import { api } from "@/lib/api";
   import { toast } from "sonner";

   interface DeleteTaskDialogProps {
     taskId: string;
     userId: string;
     onTaskDeleted: () => void;
   }

   export function DeleteTaskDialog({ taskId, userId, onTaskDeleted }: DeleteTaskDialogProps) {
     const [loading, setLoading] = useState(false);

     const handleDelete = async () => {
       setLoading(true);

       try {
         await api.tasks.delete(userId, taskId);
         toast.success("Task deleted");
         onTaskDeleted();
       } catch (error) {
         toast.error("Failed to delete task");
       } finally {
         setLoading(false);
       }
     };

     return (
       <AlertDialog>
         <AlertDialogTrigger asChild>
           <Button variant="destructive" size="sm">Delete</Button>
         </AlertDialogTrigger>
         <AlertDialogContent>
           <AlertDialogHeader>
             <AlertDialogTitle>Are you sure?</AlertDialogTitle>
             <AlertDialogDescription>
               This action cannot be undone. This will permanently delete your task.
             </AlertDialogDescription>
           </AlertDialogHeader>
           <AlertDialogFooter>
             <AlertDialogCancel>Cancel</AlertDialogCancel>
             <AlertDialogAction onClick={handleDelete} disabled={loading}>
               {loading ? "Deleting..." : "Delete"}
             </AlertDialogAction>
           </AlertDialogFooter>
         </AlertDialogContent>
       </AlertDialog>
     );
   }
   ```

3. Update `TaskItem` to use these dialogs

**Key Patterns**:
- AlertDialog for destructive actions
- Confirmation before delete
- Reuse TaskForm for editing
- Loading states during deletion

**Reference**:
- Spec: FR-011 (edit), FR-012 (delete confirmation), User Story 4 & 5

**Test**:
- Click Edit → dialog opens with pre-filled data
- Update task → changes reflected in list
- Click Delete → confirmation dialog appears
- Cancel delete → dialog closes, task remains
- Confirm delete → task removed from list

---

### Step 13: Task List State Management

**Objective**: Create client component for managing task list state

**Files to Modify**:
- `frontend/components/tasks/task-list.tsx` (MODIFY)

**Actions**:
1. Update `components/tasks/task-list.tsx`:
   ```typescript
   "use client";

   import { useState } from "react";
   import { TaskItem } from "./task-item";
   import { CreateTaskDialog } from "./create-task-dialog";
   import type { Task } from "@/types/task";

   interface TaskListProps {
     initialTasks: Task[];
     userId: string;
   }

   export function TaskList({ initialTasks, userId }: TaskListProps) {
     const [tasks, setTasks] = useState(initialTasks);

     const handleTaskCreated = (newTask: Task) => {
       setTasks([newTask, ...tasks]);
     };

     const handleTaskUpdated = (updated: Task) => {
       setTasks(tasks.map(t => t.id === updated.id ? updated : t));
     };

     const handleTaskDeleted = (taskId: string) => {
       setTasks(tasks.filter(t => t.id !== taskId));
     };

     return (
       <div className="space-y-4">
         <div className="flex justify-between items-center">
           <h2 className="text-2xl font-bold">Your Tasks</h2>
           <CreateTaskDialog userId={userId} onTaskCreated={handleTaskCreated} />
         </div>
         <div className="space-y-2">
           {tasks.map((task) => (
             <TaskItem
               key={task.id}
               task={task}
               userId={userId}
               onUpdate={handleTaskUpdated}
               onDelete={handleTaskDeleted}
             />
           ))}
         </div>
       </div>
     );
   }
   ```

**Key Patterns**:
- Client component for state management
- Server component passes initial data
- Optimistic updates without full page refresh
- Callback props for state updates

**Reference**:
- Spec: FR-028 (preserve scroll position), SC-004 (100ms feedback)

**Test**:
- Create task → appears at top of list without page reload
- Update task → changes appear immediately
- Delete task → removed immediately
- Verify scroll position maintained after operations

---

### Step 14: Loading States & Skeletons

**Objective**: Add loading indicators for better UX

**Files to Create**:
- `frontend/components/tasks/task-skeleton.tsx` (NEW)

**Files to Modify**:
- Update task-item.tsx, task-form.tsx with loading states

**Actions**:
1. Create `components/tasks/task-skeleton.tsx`:
   ```typescript
   import { Card } from "@/components/ui/card";
   import { Skeleton } from "@/components/ui/skeleton";

   export function TaskSkeleton() {
     return (
       <Card className="p-4">
         <div className="flex items-start gap-4">
           <Skeleton className="h-5 w-5 mt-1" />
           <div className="flex-1 space-y-2">
             <Skeleton className="h-5 w-3/4" />
             <Skeleton className="h-4 w-full" />
           </div>
           <div className="flex gap-2">
             <Skeleton className="h-8 w-16" />
             <Skeleton className="h-8 w-16" />
           </div>
         </div>
       </Card>
     );
   }

   export function TaskListSkeleton() {
     return (
       <div className="space-y-2">
         {Array.from({ length: 3 }).map((_, i) => (
           <TaskSkeleton key={i} />
         ))}
       </div>
     );
   }
   ```

2. Use Suspense with TaskListSkeleton in tasks page

**Key Patterns**:
- Skeleton loading states
- Suspense boundaries
- Loading spinners on buttons

**Reference**:
- Spec: FR-014 (loading states), SC-003 (2s load time), SC-004 (100ms feedback)

**Test**:
- Initial page load → see skeleton while fetching
- Button clicks → see loading spinner
- Verify smooth transitions

---

### Step 15: Toast Notifications Setup

**Objective**: Configure toast notifications for user feedback

**Files to Modify**:
- `frontend/app/layout.tsx` (MODIFY)

**Actions**:
1. Update `app/layout.tsx`:
   ```typescript
   import { Toaster } from "sonner";
   import "./globals.css";

   export default function RootLayout({
     children,
   }: {
     children: React.ReactNode;
   }) {
     return (
       <html lang="en">
         <body>
           {children}
           <Toaster position="top-right" />
         </body>
       </html>
     );
   }
   ```

**Key Patterns**:
- Global toast provider
- Positioned top-right
- sonner library (shadcn/ui compatible)

**Reference**:
- Spec: FR-015 (toast notifications), SC-009 (clear error messages)

**Test**:
- Create task → success toast
- API error → error toast
- Verify toasts appear top-right
- Verify messages are user-friendly (not raw API errors)

---

### Step 16: Error Handling & User-Friendly Messages

**Objective**: Improve error messages and edge case handling

**Files to Modify**:
- `frontend/lib/api.ts` (MODIFY - add error parsing)

**Actions**:
1. Update `lib/api.ts` with error wrapper:
   ```typescript
   function parseError(error: unknown): string {
     if (error instanceof Error) {
       // Map technical errors to user-friendly messages
       if (error.message.includes("Failed to fetch")) {
         return "Unable to connect to server. Please check your internet connection.";
       }
       if (error.message.includes("401")) {
         return "Your session has expired. Please log in again.";
       }
       return "Something went wrong. Please try again.";
     }
     return "An unexpected error occurred.";
   }
   ```

2. Add error boundaries (optional)

**Key Patterns**:
- Map technical errors to user messages
- Consistent error messaging
- Graceful degradation

**Reference**:
- Spec: FR-027 (meaningful errors), SC-009 (non-technical messages)

**Test**:
- Disconnect internet → see friendly error message
- Expired token → see session expired message
- Backend down → see server error message

---

### Step 17: Responsive Design & Mobile Optimization

**Objective**: Ensure mobile responsiveness per spec

**Files to Modify**:
- All component files (add responsive Tailwind classes)

**Actions**:
1. Review all components for responsive breakpoints:
   - Use `sm:`, `md:`, `lg:` Tailwind prefixes
   - Ensure touch-friendly targets (min 44x44px)
   - Test at 320px, 768px, 1024px, 1920px widths

2. Update task list for mobile:
   ```typescript
   <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
     {tasks.map(task => <TaskItem key={task.id} task={task} />)}
   </div>
   ```

**Key Patterns**:
- Mobile-first Tailwind classes
- Touch-friendly button sizes
- Readable font sizes
- No horizontal scroll

**Reference**:
- Spec: FR-017 (responsive layouts), SC-007 (320px usable), SC-008 (1920px usable)

**Test**:
- Test at 320px width → no horizontal scroll, all buttons tappable
- Test at 1920px width → proper spacing, no awkward layouts
- Verify touch targets at least 44x44px

---

### Step 18: Keyboard Navigation & Accessibility

**Objective**: Ensure keyboard accessibility

**Files to Modify**:
- All interactive components (verify tab order)

**Actions**:
1. Verify tab order on all pages:
   - Login form → Email → Password → Submit → Sign Up link
   - Tasks page → Add Task → Each task checkbox → Edit → Delete

2. Ensure Escape key closes dialogs (built into shadcn/ui)

3. Ensure Enter key submits forms

**Key Patterns**:
- Semantic HTML (button, form, input)
- Focus visible styles
- Logical tab order
- Keyboard shortcuts (Enter, Escape)

**Reference**:
- Spec: SC-011 (keyboard navigation)

**Test**:
- Navigate entire app using only Tab, Enter, Escape keys
- Verify focus indicators visible
- Verify no keyboard traps

---

### Step 19: Multi-User Isolation Testing

**Objective**: Verify user isolation enforcement

**Actions**:
1. Create two test accounts:
   - User A: `usera@example.com` / `password123`
   - User B: `userb@example.com` / `password123`

2. Test scenarios:
   - Login as User A → create tasks
   - Login as User B → verify User A's tasks NOT visible
   - Check DevTools Network → verify user_id in API path matches logged-in user
   - Attempt to manually craft request with different user_id → verify backend returns 404

**Key Patterns**:
- Backend enforces isolation (frontend trusts backend)
- Each user sees only their own data
- DevTools verification

**Reference**:
- Spec: SC-013 (0% data leakage), Constitution Principle II

**Test**:
- 0 cross-user data leaks
- Verify isolation at API level (backend responsibility)
- Frontend correctly displays only returned data

---

### Step 20: Final Polish & Production Checklist

**Objective**: Review and finalize for production readiness

**Actions**:
1. **Environment Variables**:
   - Verify `.env.local` has all required variables
   - Create `.env.example` with placeholders
   - Document required variables in quickstart.md

2. **Code Quality**:
   - Run `npm run lint` → fix all warnings
   - Check TypeScript → no type errors (`npm run build`)
   - Remove console.logs

3. **Performance**:
   - Verify task list loads <2s
   - Verify optimistic updates <100ms
   - Verify auth redirects <500ms

4. **Documentation**:
   - Update `frontend/CLAUDE.md` with new structure
   - Create/update quickstart guide
   - Document component patterns

5. **Final Testing**:
   - Complete all user stories from spec
   - Verify all 30 functional requirements
   - Verify all 15 success criteria

**Checklist**:
- [ ] All shadcn/ui components installed
- [ ] Better Auth configured and working
- [ ] All 5 task features implemented (Add, Delete, Update, View, Complete)
- [ ] Authentication flow complete (signup, login, logout)
- [ ] Protected routes working
- [ ] Responsive design (mobile + desktop)
- [ ] Keyboard navigation functional
- [ ] Multi-user isolation verified
- [ ] Error handling with user-friendly messages
- [ ] Loading states on all async operations
- [ ] Toast notifications for feedback
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] Environment variables documented

**Reference**:
- Spec: All functional requirements (FR-001 to FR-030)
- Spec: All success criteria (SC-001 to SC-015)

**Test**:
- Run through all user stories end-to-end
- Verify spec compliance
- Document any deviations in plan.md

---

## Constitution Re-Check (Post-Design)

*Re-evaluate after Phase 1 design complete:*

### Principle I: Spec-Driven Development ✅
- All steps reference spec requirements
- Clear traceability from spec → plan → implementation
- No implementation details in spec

### Principle II: User Isolation and Security First ✅
- Frontend enforces: JWT attachment (FR-005), 401 handling (FR-008), httpOnly cookies (FR-004)
- Backend enforces: user_id filtering (already implemented)
- Testing: Multi-user isolation test in Step 19

### Principle III: Reusability Through Skills and Agents ✅
- `better-auth-integration` used for auth patterns
- `frontend-design` used for shadcn/ui patterns
- `nextjs-frontend-builder` used for App Router structure

### Principle IV: Clarity and Consistency ✅
- All file paths follow Next.js App Router conventions
- Component organization by feature (auth/, tasks/, layout/)
- TypeScript strict mode throughout

### Principle V: Test-First for Security-Critical Paths ⚠️
- Manual testing approach justified (backend has comprehensive tests)
- Multi-user isolation test in Step 19
- DevTools verification of JWT headers

### Principle VI: Simplicity and Smallest Viable Change ✅
- No premature abstraction (direct API calls, no state management library)
- Only specified features implemented
- Simple, incremental steps

**FINAL GATE RESULT**: ✅ PASS

## Next Steps

After completing this plan:

1. Run `/sp.tasks` to generate task breakdown from this plan
2. Execute tasks via `/sp.implement` or manually
3. Verify all acceptance criteria from spec
4. Create PHR documenting implementation
5. Run `/sp.git.commit_pr` to create pull request

## References

- **Spec**: [specs/002-frontend-auth/spec.md](./spec.md)
- **Backend API**: `backend/routers/tasks.py` (6 endpoints)
- **Backend Schemas**: `backend/schemas.py` (TaskRead, TaskCreate, TaskUpdate)
- **Constitution**: `.specify/memory/constitution.md`
- **Skills**:
  - `@.claude/skills/better-auth-integration/SKILL.md`
  - `@.claude/skills/frontend-design/SKILL.md`
  - `@.claude/skills/nextjs-builder/SKILL.md`
