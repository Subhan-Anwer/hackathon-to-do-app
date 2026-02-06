# Frontend - Next.js 16 Application

## Current Structure

```
frontend/
├── app/                          # Next.js App Router (v16.1.6)
│   ├── layout.tsx               # Root layout with Toaster
│   ├── page.tsx                 # Home page (auth redirect logic)
│   ├── globals.css              # Global styles with Tailwind
│   ├── favicon.ico
│   ├── login/
│   │   └── page.tsx            # Login page (server component)
│   ├── signup/
│   │   └── page.tsx            # Signup page (server component)
│   ├── tasks/
│   │   └── page.tsx            # Tasks dashboard (server component with Suspense)
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/route.ts  # Better Auth API routes
│   └── proxy.ts                 # Server-side API proxy (NOT middleware.ts)
├── components/
│   ├── auth/
│   │   ├── login-form.tsx      # Login form (client component)
│   │   └── signup-form.tsx     # Signup form (client component)
│   ├── layout/
│   │   └── header.tsx          # Header with logout (client component)
│   ├── tasks/
│   │   ├── task-list.tsx       # Task list container (client component)
│   │   ├── task-item.tsx       # Individual task card (client component)
│   │   ├── task-form.tsx       # Reusable task form (client component)
│   │   ├── create-task-dialog.tsx  # Create task dialog (client component)
│   │   ├── edit-task-dialog.tsx    # Edit task dialog (client component)
│   │   ├── delete-task-dialog.tsx  # Delete confirmation (client component)
│   │   ├── empty-state.tsx     # Empty state when no tasks
│   │   └── task-list-skeleton.tsx  # Loading skeleton
│   └── ui/                     # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── checkbox.tsx
│       ├── dialog.tsx
│       ├── alert-dialog.tsx
│       ├── form.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── skeleton.tsx
│       └── ...
├── lib/
│   ├── auth.ts                 # Better Auth configuration
│   ├── simple-auth.ts          # Session utilities (getSession, logout)
│   ├── api.ts                  # API client with taskApi methods
│   └── utils.ts                # Utility functions (cn helper)
├── types/
│   └── task.ts                 # Task TypeScript interfaces
├── .env.local                  # Environment variables (gitignored)
├── .env.example                # Environment variable template
├── components.json             # shadcn/ui configuration
├── next.config.ts              # Next.js configuration
├── package.json                # Dependencies
└── tsconfig.json               # TypeScript configuration
```

## Installed Dependencies

**Core:**
- `next@16.1.6` - React framework with App Router
- `react@19.2.3` / `react-dom@19.2.3` - React 19
- `typescript@5` - Type safety

**UI & Styling:**
- `tailwindcss@4` - Utility-first CSS framework
- `@tailwindcss/postcss@4` - PostCSS plugin
- `class-variance-authority` - CVA for component variants
- `clsx` + `tailwind-merge` - Conditional class merging
- `tw-animate-css` - Animation utilities
- `sonner` - Toast notifications

**shadcn/ui Configuration:**
- Style: `new-york`
- Icon library: `lucide-react@0.563.0`
- Base color: `neutral`
- CSS variables enabled
- Path aliases configured
- Installed components: button, card, checkbox, dialog, alert-dialog, form, input, textarea, label, skeleton, sonner

**Authentication:**
- `better-auth` - JWT authentication with httpOnly cookies
- `react-hook-form` - Form state management
- `zod` - Schema validation
- `@hookform/resolvers` - Zod integration with react-hook-form

**Development:**
- ESLint with Next.js config
- TypeScript strict mode

## Scripts

- `npm run dev` - Development server (localhost:3000)
- `npm run build` - Production build
- `npm start` - Production server
- `npm run lint` - Run ESLint

## Context7 MCP Integration

**CRITICAL: Always use Context7 MCP proactively** for documentation, code generation, and configuration without waiting for explicit requests.

**Automatic Usage Triggers:**
- Next.js 16 App Router patterns and best practices
- React 19 Server Components and Client Components
- Tailwind CSS utility classes and configuration
- shadcn/ui component installation and usage
- Better Auth JWT integration and configuration
- TypeScript types and interfaces for libraries
- API route handlers and middleware setup

**Common Frontend Queries:**
- Next.js App Router file conventions (layout.tsx, page.tsx, route.ts)
- React Server Component vs Client Component patterns
- shadcn/ui component props and customization
- Tailwind CSS class names and responsive design
- Better Auth client setup and authentication hooks
- Next.js API proxy configuration for backend communication
- TypeScript strict mode best practices

**When to Query:**
1. **Before creating components** - Verify Next.js 16 App Router conventions
2. **During UI implementation** - Look up shadcn/ui component APIs
3. **For styling** - Check Tailwind CSS utility classes and variants
4. **For auth flows** - Reference Better Auth documentation
5. **For API calls** - Verify fetch patterns with JWT token handling

**Benefits:**
- Ensures Next.js 16 App Router best practices
- Correct shadcn/ui component usage
- Up-to-date Tailwind CSS patterns
- Proper Better Auth JWT integration
- TypeScript type safety with library types

Use Context7 silently and proactively to deliver accurate, documentation-backed implementations.

## Architecture Patterns

### Authentication Flow
1. **Better Auth with JWT tokens** stored in httpOnly cookies
2. **Server-side API proxy** (`app/proxy.ts`) forwards requests with JWT
3. **Session utilities** (`lib/simple-auth.ts`) for getSession/logout
4. **Protected routes** redirect to /login if unauthenticated
5. **Automatic redirect** on 401 responses from API

### Component Organization
- **Server Components**: Pages (login, signup, tasks) for SEO and initial data fetching
- **Client Components**: Interactive UI (forms, dialogs, task items) marked with "use client"
- **Suspense Boundaries**: Task list wrapped in Suspense with TaskListSkeleton fallback
- **Optimistic UI**: Task toggle/delete update immediately, revert on error

### Task Management Pattern
1. **Server component** (`app/tasks/page.tsx`) fetches initial tasks
2. **Client component** (`TaskList`) manages state with useState
3. **Child components** trigger callbacks (onCreate, onUpdate, onDelete)
4. **Parent state updates** via callback functions from child components
5. **API calls** use `taskApi` from `lib/api.ts` with automatic JWT inclusion

### Form Validation
- **react-hook-form** for form state management
- **zod schemas** for validation rules
- **Inline error display** with FormMessage component
- **Client-side validation** before API calls
- **Server error handling** with user-friendly toast messages

### API Client Pattern (`lib/api.ts`)
```typescript
const taskApi = {
  list: (userId) => GET /api/{userId}/tasks
  create: (userId, data) => POST /api/{userId}/tasks
  get: (userId, taskId) => GET /api/{userId}/tasks/{taskId}
  update: (userId, taskId, data) => PUT /api/{userId}/tasks/{taskId}
  delete: (userId, taskId) => DELETE /api/{userId}/tasks/{taskId}
  toggleComplete: (userId, taskId) => PATCH /api/{userId}/tasks/{taskId}/complete
}
```
All methods:
- Include `credentials: "include"` for httpOnly cookies
- Handle 401 by redirecting to /login
- Parse errors into user-friendly messages
- Return typed Task objects

### Type Safety
All TypeScript interfaces defined in `types/task.ts`:
- `Task` - Full task object from API
- `TaskCreateInput` - Create task payload (title, description?)
- `TaskUpdateInput` - Update task payload (title, description?)

### Environment Variables
Required in `.env.local` (see `.env.example`):
- `NEXT_PUBLIC_API_URL` - Backend API URL (http://localhost:8000)
- `BETTER_AUTH_SECRET` - Shared secret with backend (min 32 chars)
- `BETTER_AUTH_URL` - Frontend URL (http://localhost:3000)

## Implementation Status

### Completed Features
- ✅ Authentication (signup, login, logout, protected routes)
- ✅ Session management with httpOnly cookies
- ✅ Task viewing with responsive design
- ✅ Task creation with validation and dialog
- ✅ Task editing with reusable form component
- ✅ Task completion toggle with optimistic UI
- ✅ Task deletion with confirmation dialog
- ✅ Loading states with Suspense and skeleton
- ✅ Error handling with user-friendly messages
- ✅ Toast notifications for all CRUD operations
- ✅ Keyboard navigation and accessibility

### Production Readiness
- ✅ TypeScript strict mode with no type errors
- ✅ ESLint passing with no warnings
- ✅ No console.log statements in production code
- ✅ Environment variables documented in .env.example
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Accessible markup with ARIA labels

## Development Workflow

1. **Start backend**: `cd backend && uv run uvicorn main:app --reload`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Access app**: http://localhost:3000
4. **Backend API**: http://localhost:8000/docs (Swagger UI)

## Testing Checklist

See `/frontend/TESTING.md` for comprehensive manual test scenarios covering:
- Phase 3: Authentication (signup, login, protected routes)
- Phase 4: Logout functionality
- Phase 5: Task viewing and empty states
- Phase 6: Task creation with validation
- Phase 7: Task editing and completion toggle
- Phase 8: Task deletion with confirmation
- Phase 9: Multi-user isolation, performance, accessibility
