---
name: better-auth-integration
description: Implement Better Auth with JWT tokens for Next.js frontends and FastAPI backends. Use when setting up authentication, implementing signup/login flows, configuring JWT token sharing, or integrating Next.js with FastAPI backends requiring user authentication. Handles httpOnly cookies, API proxying, and user isolation security.
---

# Better Auth Integration

## Overview

Implement Better Auth authentication with JWT tokens for Next.js applications that communicate with FastAPI backends. This skill covers JWT generation, httpOnly cookie handling, signup/login flows, API proxying for token forwarding, and backend JWT verification with user isolation.

## When to Use This Skill

- Setting up user authentication in Next.js + FastAPI applications
- Implementing Better Auth with JWT token generation
- Creating signup/login/logout flows
- Configuring secure token sharing between frontend and backend
- Establishing user isolation in multi-user applications
- User asks to "add authentication", "implement Better Auth", "set up JWT auth"

## Core Concept: httpOnly Cookie Security

**Critical Understanding:** httpOnly cookies CANNOT be read by JavaScript (this is a security feature to prevent XSS attacks). Only server-side code can access them. This requires using an API proxy pattern.

**Authentication Flow:**
```
User Login → Better Auth → JWT Token → httpOnly Cookie →
Frontend Request → Server-Side Proxy → Extract Cookie →
Forward to Backend with Authorization Header → JWT Verification → User Data
```

## Installation

### Frontend (Next.js)
```bash
npm install better-auth @better-auth/react
```

### Backend (FastAPI)
```bash
pip install pyjwt python-jose cryptography
```

## Environment Variables

Both frontend and backend MUST have matching secrets:

**Frontend (.env.local):**
```bash
BETTER_AUTH_SECRET=your-secret-key-here-make-it-long-and-random
NEXT_PUBLIC_APP_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

**Backend (.env):**
```bash
BETTER_AUTH_SECRET=your-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

## Implementation Workflow

### 1. Frontend Setup

**Step 1.1: Create Better Auth Config**

Copy `assets/templates/auth-config.ts` to `lib/auth.ts`. This configures Better Auth with JWT plugin, session management, and database connection.

**Step 1.2: Create API Handler**

Copy `assets/templates/api-route.ts` to `app/api/auth/[...all]/route.ts`. This exposes Better Auth endpoints for signup/login/logout.

**Step 1.3: Create Auth Client**

Copy `assets/templates/auth-client.ts` to `lib/auth-client.ts`. This provides React hooks for authentication.

**Step 1.4: Create API Proxy** (CRITICAL)

Copy `assets/templates/proxy-route.ts` to `app/api/proxy/[...path]/route.ts`.

This proxy:
- Runs server-side (can read httpOnly cookies)
- Extracts JWT token from cookie
- Forwards requests to FastAPI backend with Authorization header
- Returns backend responses to frontend

**Step 1.5: Create API Client**

Copy `assets/templates/api-client.ts` to `lib/api.ts`. This client:
- Routes all requests through `/api/proxy`
- Includes `credentials: "include"` (critical for cookie forwarding)
- Provides typed request methods

**Step 1.6: Add Middleware for Protected Routes** (Optional)

Copy `assets/templates/middleware-config.ts` to `middleware.ts` to protect routes that require authentication.

### 2. Backend Setup

**Step 2.1: Create JWT Middleware**

Copy `assets/templates/jwt-middleware.py` to `middleware/jwt.py`. This:
- Extracts token from Authorization header
- Verifies token signature with BETTER_AUTH_SECRET
- Decodes user data (user_id, email)
- Provides user isolation verification

**Step 2.2: Protect Routes**

Use `verify_jwt` and `verify_user_access` in route handlers. See `assets/templates/protected-route-example.py` for examples.

Pattern:
```python
from fastapi import APIRouter, Depends
from middleware.jwt import verify_jwt, verify_user_access

@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
):
    verify_user_access(user_id, current_user)
    # Fetch and return user's tasks
```

### 3. Create Auth Pages

**Signup Page Pattern:**
```typescript
'use client'
import { useState } from 'react'
import { authClient } from '@/lib/auth-client'
import { useRouter } from 'next/navigation'

export default function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await authClient.signUp({ email, password, name: email.split('@')[0] })
      router.push('/dashboard')
    } catch (err) {
      setError('Signup failed')
    }
  }

  return (
    <form onSubmit={handleSignup}>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} required />
      {error && <p>{error}</p>}
      <button type="submit">Sign Up</button>
    </form>
  )
}
```

**Login Page:** Similar structure to signup, use `authClient.signIn({ email, password })`

**Logout:**
```typescript
const handleLogout = async () => {
  await authClient.signOut()
  router.push('/login')
}
```

### 4. Session Management

**Check Auth in Components:**
```typescript
import { useAuth } from '@/lib/auth-client'

export function ProtectedComponent() {
  const { session, isLoading } = useAuth()

  if (isLoading) return <div>Loading...</div>
  if (!session) redirect('/login')

  return <div>Welcome, {session.user.email}</div>
}
```

**Server-Side Session Check:**
```typescript
import { auth } from '@/lib/auth'
import { redirect } from 'next/navigation'
import { headers } from 'next/headers'

export default async function Page() {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session) redirect('/login')

  return <div>Protected content</div>
}
```

## Common Patterns

### Making API Requests

```typescript
import { api } from '@/lib/api'

// GET request
const tasks = await api.get('/api/user123/tasks')

// POST request
const newTask = await api.post('/api/user123/tasks', {
  title: 'New task',
  completed: false
})

// Custom request
const data = await api.request('/api/custom', {
  method: 'PUT',
  body: { field: 'value' }
})
```

### User Isolation in Backend

Always verify user_id matches authenticated user:

```python
@router.get("/api/{user_id}/resource")
async def get_resource(user_id: str, current_user: dict = Depends(verify_jwt)):
    verify_user_access(user_id, current_user)  # CRITICAL
    return fetch_user_resource(user_id)
```

## Security Checklist

- [ ] BETTER_AUTH_SECRET is strong (32+ characters, random)
- [ ] Secrets match exactly between frontend and backend
- [ ] httpOnly cookies enabled in Better Auth config
- [ ] All API requests use proxy (never direct backend calls)
- [ ] `credentials: "include"` set in all fetch calls
- [ ] User ID verification in all protected endpoints
- [ ] Token expiration configured appropriately
- [ ] HTTPS enabled in production
- [ ] Error messages don't leak sensitive information

## Common Pitfalls

### 1. Missing `credentials: "include"`
Without this, cookies won't be sent to proxy, causing authentication failures.

### 2. Trying to Read httpOnly Cookies from JavaScript
This will always fail. Use server-side proxy instead.

### 3. Mismatched BETTER_AUTH_SECRET
Frontend and backend must use identical secret for token verification.

### 4. Not Verifying user_id in Backend
Always compare token user_id with requested user_id to prevent unauthorized access.

### 5. Wrong JWT Payload Field
User ID is in `sub` field (standard JWT claim), not `user_id`.

### 6. Direct Backend Calls
Always route through `/api/proxy` to include JWT token.

## Troubleshooting

For detailed troubleshooting, see `references/troubleshooting.md`:
- "Token is undefined" in backend
- CORS errors
- "Invalid token" errors
- User isolation failures
- Session not persisting
- Proxy 404 errors

## Resources

### references/
- `jwt-flow.md` - Detailed JWT authentication flow and token structure
- `troubleshooting.md` - Common issues and solutions with debugging steps

### assets/templates/
Complete, production-ready templates:
- `auth-config.ts` - Better Auth configuration with JWT plugin
- `auth-client.ts` - Client-side auth hooks
- `api-route.ts` - Better Auth API handler
- `proxy-route.ts` - Server-side proxy for httpOnly cookie forwarding
- `api-client.ts` - Frontend API client with credential handling
- `jwt-middleware.py` - Backend JWT verification middleware
- `protected-route-example.py` - Example protected routes with user isolation
- `middleware-config.ts` - Next.js middleware for route protection

Copy templates to appropriate locations in project and customize as needed.
