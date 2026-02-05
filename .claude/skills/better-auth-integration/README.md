# Better Auth Integration Skill

A comprehensive skill for implementing Better Auth authentication with JWT tokens in Next.js + FastAPI applications.

## What This Skill Does

This skill helps Claude implement production-ready authentication systems that:
- Set up Better Auth with JWT token generation in Next.js
- Handle httpOnly cookies securely (preventing XSS attacks)
- Create signup/login/logout flows
- Implement server-side API proxying for token forwarding
- Verify JWT tokens in FastAPI backends
- Enforce user isolation and access control

## When to Use

Use this skill when:
- Setting up authentication in Next.js + FastAPI applications
- Implementing JWT-based authentication
- Creating user signup/login systems
- Securing API endpoints with user isolation
- User asks to "add authentication", "implement Better Auth", "set up JWT"

## What's Included

### SKILL.md
Main skill documentation with:
- Complete implementation workflow
- Installation instructions
- Environment configuration
- Code examples for auth pages
- Common patterns and pitfalls
- Security checklist

### references/
Detailed documentation loaded as needed:
- **jwt-flow.md** - Complete JWT authentication flow, token structure, and security concepts
- **troubleshooting.md** - Common issues, debugging steps, and solutions

### assets/templates/
Production-ready code templates:

**Frontend (TypeScript/Next.js):**
- `auth-config.ts` - Better Auth configuration with JWT plugin
- `auth-client.ts` - Client-side auth hooks
- `api-route.ts` - Better Auth API handler
- `proxy-route.ts` - Server-side proxy for httpOnly cookie forwarding ⚠️ CRITICAL
- `api-client.ts` - Frontend API client with credential handling
- `middleware-config.ts` - Route protection middleware

**Backend (Python/FastAPI):**
- `jwt-middleware.py` - JWT verification middleware with user isolation
- `protected-route-example.py` - Example protected endpoints

## Key Concepts

### httpOnly Cookie Security

The core security pattern this skill implements:

```
User Login → Better Auth → JWT in httpOnly Cookie
                              ↓
                    (JavaScript CANNOT read this)
                              ↓
Frontend Request → Server-Side Proxy (can read cookie)
                              ↓
                    Extract JWT Token
                              ↓
              Forward to Backend with Authorization Header
                              ↓
                    Backend Verifies JWT
                              ↓
                    Return User Data
```

**Why this matters:**
- httpOnly cookies prevent XSS attacks from stealing tokens
- JavaScript cannot access these cookies
- Server-side proxy is essential to forward tokens to backend

### Critical Security Features

1. **User Isolation** - Every endpoint verifies user owns the requested resource
2. **httpOnly Cookies** - Prevents token theft via XSS
3. **JWT Verification** - Backend validates token signature and expiration
4. **Matching Secrets** - Frontend and backend use identical BETTER_AUTH_SECRET

## Quick Start

Once the skill is loaded, Claude can:

1. Set up Better Auth configuration
2. Create signup/login/logout pages
3. Implement the API proxy (critical for httpOnly cookies)
4. Set up JWT verification in FastAPI
5. Protect routes with user isolation

All templates are production-ready and can be copied directly into projects.

## Installation

### Prerequisites
- Next.js 15+ with App Router
- FastAPI backend
- PostgreSQL database

### Frontend
```bash
npm install better-auth @better-auth/react
```

### Backend
```bash
pip install pyjwt python-jose cryptography
```

## Common Pitfalls This Skill Prevents

1. ❌ Trying to read httpOnly cookies from JavaScript
   ✅ Uses server-side proxy pattern

2. ❌ Forgetting `credentials: "include"` in fetch calls
   ✅ Template API client includes it by default

3. ❌ Mismatched BETTER_AUTH_SECRET
   ✅ Explicit documentation about matching secrets

4. ❌ No user isolation (User A can access User B's data)
   ✅ Includes `verify_user_access` helper

5. ❌ Direct backend calls (bypassing proxy)
   ✅ API client always routes through proxy

## Testing the Skill

After implementation, verify:
- [ ] User can sign up with email/password
- [ ] User can log in
- [ ] Session persists across page refreshes
- [ ] Logout works correctly
- [ ] API requests include JWT token
- [ ] Backend verifies token correctly
- [ ] User isolation works (User A can't access User B's data)
- [ ] Expired tokens are rejected
- [ ] Invalid tokens are rejected

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Next.js Frontend               │
│                                                  │
│  ┌──────────────┐         ┌──────────────┐     │
│  │ Auth Pages   │────────▶│ Better Auth  │     │
│  │ (Signup/Login│         │ (JWT Plugin) │     │
│  └──────────────┘         └──────────────┘     │
│                                  │               │
│                                  ▼               │
│                         httpOnly Cookie          │
│                         (JWT Token)              │
│                                  │               │
│  ┌──────────────┐               │               │
│  │ Components   │               │               │
│  │ (API Calls)  │               │               │
│  └──────┬───────┘               │               │
│         │                        │               │
│         ▼                        │               │
│  ┌──────────────┐               │               │
│  │  API Client  │               │               │
│  │ (lib/api.ts) │               │               │
│  └──────┬───────┘               │               │
│         │                        │               │
│         │ credentials: "include" │               │
│         │ (sends cookie)         │               │
│         ▼                        ▼               │
│  ┌────────────────────────────────┐             │
│  │     Server-Side API Proxy      │             │
│  │  (app/api/proxy/[...path])     │             │
│  │                                 │             │
│  │  1. Read httpOnly cookie       │             │
│  │  2. Extract JWT token          │             │
│  │  3. Add Authorization header   │             │
│  └────────────┬───────────────────┘             │
└───────────────┼─────────────────────────────────┘
                │
                │ Authorization: Bearer <JWT>
                ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                     │
│                                                  │
│  ┌────────────────────────────┐                 │
│  │    JWT Middleware          │                 │
│  │  (middleware/jwt.py)       │                 │
│  │                             │                 │
│  │  1. Verify signature        │                 │
│  │  2. Decode user_id          │                 │
│  │  3. Check expiration        │                 │
│  └────────────┬───────────────┘                 │
│               │                                  │
│               ▼                                  │
│  ┌────────────────────────────┐                 │
│  │   Protected Endpoints      │                 │
│  │                             │                 │
│  │  1. Verify user access      │                 │
│  │  2. Fetch user data         │                 │
│  │  3. Return response         │                 │
│  └────────────────────────────┘                 │
└─────────────────────────────────────────────────┘
```

## Support

This skill includes comprehensive troubleshooting documentation in `references/troubleshooting.md` covering:
- Token undefined errors
- CORS issues
- Invalid token errors
- User isolation failures
- Session persistence problems
- Proxy routing issues

Each issue includes symptoms, causes, and solutions.

## License

This skill is part of the Claude Code skill ecosystem.
