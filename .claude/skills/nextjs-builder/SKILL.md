---
name: nextjs-builder
description: Generate production-ready Next.js 16+ applications with App Router, Better Auth JWT integration, and httpOnly cookie handling. Use when building React frontends, implementing authentication, or creating Next.js projects that consume FastAPI backends.
---

# Next.js 16+ Builder

Generate production-ready Next.js 16+ frontend applications with correct App Router patterns, Better Auth integration, TypeScript, Tailwind CSS, and httpOnly cookie authentication.

## Critical Next.js 16 Breaking Changes

**1. params and searchParams are NOW PROMISES** (most common error):
```typescript
// ❌ WRONG - Next.js 15 pattern
export default function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>
}

// ✅ CORRECT - Next.js 16 pattern
export default async function Page({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <div>{id}</div>
}
```

**2. middleware.ts renamed to proxy.ts** - File and function both renamed

**3. Turbopack is default** - No `--turbopack` flag needed

**4. cacheComponents replaces dynamicIO** in config

**5. httpOnly cookies** - JavaScript CANNOT read them (security feature)

## httpOnly Cookie Authentication Pattern

**Critical**: httpOnly cookies cannot be accessed from client JavaScript. Must create server-side API proxy.

### API Proxy Route (REQUIRED)
```typescript
// app/api/proxy/[...path]/route.ts
import { cookies } from "next/headers"
import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params  // MUST await params in Next.js 16
  const cookieStore = await cookies()
  const token = cookieStore.get("better-auth.session_token")?.value

  if (!token) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 })
  }

  const response = await fetch(`${BACKEND_URL}/api/${path.join("/")}`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  return NextResponse.json(await response.json(), { status: response.status })
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params
  const cookieStore = await cookies()
  const token = cookieStore.get("better-auth.session_token")?.value

  if (!token) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 })
  }

  const response = await fetch(`${BACKEND_URL}/api/${path.join("/")}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: await request.text(),
  })

  return NextResponse.json(await response.json(), { status: response.status })
}

// Add PUT, PATCH, DELETE as needed
```

### API Client Pattern
```typescript
// lib/api.ts
const API_BASE = "/api/proxy"  // Routes through server-side proxy

export const api = {
  async getTasks(userId: string) {
    const res = await fetch(`${API_BASE}/${userId}/tasks`, {
      credentials: "include",  // Sends httpOnly cookies
    })
    if (!res.ok) throw new Error("Failed to fetch tasks")
    return res.json()
  },

  async createTask(userId: string, data: { title: string; description?: string }) {
    const res = await fetch(`${API_BASE}/${userId}/tasks`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to create task")
    return res.json()
  },
}
```

## Better Auth Setup

### Installation
```bash
npm install better-auth @better-auth/react
```

### Configuration
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  database: {
    // Use your database connection
    url: process.env.DATABASE_URL!,
  },
  plugins: [jwt()],  // Enable JWT tokens
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7, // 7 days
    },
  },
})
```

### Auth API Route
```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
```

### Client Provider
```typescript
// lib/auth-client.ts
"use client"
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL!,
})
```

### Login/Signup Components
```typescript
// app/login/page.tsx
"use client"
import { authClient } from "@/lib/auth-client"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await authClient.signIn.email({ email, password })
      router.push("/")
    } catch (err) {
      setError("Invalid credentials")
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {error && <p>{error}</p>}
      <button type="submit">Sign In</button>
    </form>
  )
}
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   └── api/
│   │       ├── auth/[...all]/route.ts
│   │       └── proxy/[...path]/route.ts    # httpOnly cookie proxy
│   ├── lib/
│   │   ├── api.ts                          # API client
│   │   ├── auth.ts                         # Better Auth config
│   │   └── auth-client.ts                  # Client-side auth
│   └── components/
│       ├── TaskList.tsx
│       └── ui/
├── proxy.ts                                # NOT middleware.ts
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

## Server vs Client Components

**Server Components** (default):
- Data fetching
- Backend API calls
- Database queries
- No useState, useEffect, event handlers

**Client Components** ('use client'):
- Interactivity (onClick, onChange)
- useState, useEffect, useContext
- Browser APIs
- Event handlers

## Common Pitfalls

1. **Forgetting to await params** - Next.js 16 requires it
2. **Creating middleware.ts** - Use proxy.ts instead
3. **Reading httpOnly cookies from JavaScript** - Impossible, use server proxy
4. **Missing 'use client'** - Required for interactive components
5. **Missing credentials: "include"** - Required to send httpOnly cookies
6. **Not handling loading/error states** - Always implement

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_APP_URL=http://localhost:3000
DATABASE_URL=postgresql://...
```

## Quick Start

```bash
npx create-next-app@latest my-app --typescript --tailwind --app
cd my-app
npm install better-auth @better-auth/react
# Set up .env file
# Create lib/auth.ts and app/api/auth/[...all]/route.ts
# Create app/api/proxy/[...path]/route.ts for httpOnly cookie handling
npm run dev
```

## Quality Checklist

- [ ] All dynamic params use `await params`
- [ ] Auth uses httpOnly cookies with server proxy
- [ ] API client routes through `/api/proxy`
- [ ] Client components have 'use client'
- [ ] Fetch calls include `credentials: "include"`
- [ ] Loading/error states implemented
- [ ] TypeScript types defined
- [ ] Responsive design (mobile-first)
- [ ] No middleware.ts file (use proxy.ts)
