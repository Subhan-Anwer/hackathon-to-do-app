# Authentication Flow Contract: Environment-Aware JWT

**Feature**: `004-auth-fix-workflow`
**Created**: 2026-02-07
**Purpose**: Define environment-aware authentication flow supporting localhost HTTP (dev) and HTTPS (prod)

## Overview

This contract defines how JWT authentication works across development (localhost HTTP) and production (HTTPS) environments. The key innovation is environment-aware cookie attributes that allow cookies to work on HTTP during local development while maintaining security in production.

## Development Flow (localhost HTTP)

```text
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: User Authentication                                       │
├──────────────────────────────────────────────────────────────────┤
│ User signs in at: http://localhost:3000/login                    │
│ Better Auth validates credentials and generates JWT              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: JWT Token Generation (jwt() plugin)                      │
├──────────────────────────────────────────────────────────────────┤
│ Payload: {                                                        │
│   sub: "<user_id>",        // User ID for backend isolation      │
│   exp: <timestamp>,        // Expiration (7 days)                │
│   iat: <timestamp>         // Issued at                          │
│ }                                                                 │
│ Signed with: BETTER_AUTH_SECRET (shared with backend)            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: Cookie Storage (environment-aware)                       │
├──────────────────────────────────────────────────────────────────┤
│ Cookie Name: "session"                                            │
│ Cookie Value: <JWT token>                                         │
│ Attributes:                                                       │
│   - httpOnly: true                    (XSS protection)           │
│   - secure: false                     ← HTTP compatible          │
│   - sameSite: "lax"                   ← Localhost cross-origin   │
│   - path: "/"                                                     │
│   - maxAge: 604800 (7 days)                                       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 4: API Request (dual authentication)                        │
├──────────────────────────────────────────────────────────────────┤
│ Request: GET http://localhost:8000/api/{user_id}/tasks           │
│                                                                   │
│ Headers:                                                          │
│   Authorization: Bearer <jwt>         ← Preferred method         │
│   Cookie: session=<jwt>               ← Fallback method          │
│   Content-Type: application/json                                 │
│                                                                   │
│ Note: Browser automatically includes cookie via credentials      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 5: Backend JWT Verification                                 │
├──────────────────────────────────────────────────────────────────┤
│ Middleware: get_current_user (dependencies.py)                   │
│                                                                   │
│ 1. Check Authorization header for "Bearer <token>"               │
│    ↓ (if not found)                                               │
│ 2. Check Cookie header for "session=<token>"                     │
│    ↓ (if neither found)                                           │
│ 3. Return 401 Unauthorized                                        │
│                                                                   │
│ If token found:                                                   │
│ - Decode with BETTER_AUTH_SECRET + HS256 algorithm               │
│ - Extract user_id from "sub" claim                               │
│ - Attach user_id to request.state.user_id                        │
│ - Log authentication success                                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 6: Data Isolation & Response                                │
├──────────────────────────────────────────────────────────────────┤
│ Endpoint filters tasks by authenticated user_id:                 │
│ tasks = session.exec(                                             │
│     select(Task).where(Task.user_id == user_id)                  │
│ ).all()                                                           │
│                                                                   │
│ Returns: JSON array of tasks (only user's own tasks)             │
└──────────────────────────────────────────────────────────────────┘
```

## Production Flow (HTTPS)

```text
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: User Authentication                                       │
├──────────────────────────────────────────────────────────────────┤
│ User signs in at: https://app.example.com/login                  │
│ Better Auth validates credentials and generates JWT              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: JWT Token Generation (same as dev)                       │
├──────────────────────────────────────────────────────────────────┤
│ Payload: { sub, exp, iat } (identical structure)                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: Cookie Storage (PRODUCTION attributes)                   │
├──────────────────────────────────────────────────────────────────┤
│ Cookie Name: "session"                                            │
│ Cookie Value: <JWT token>                                         │
│ Attributes:                                                       │
│   - httpOnly: true                    (XSS protection)           │
│   - secure: true                      ← HTTPS required           │
│   - sameSite: "none"                  ← Cross-origin HTTPS       │
│   - path: "/"                                                     │
│   - maxAge: 604800 (7 days)                                       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 4: API Request (same dual auth pattern)                     │
├──────────────────────────────────────────────────────────────────┤
│ Request: GET https://api.example.com/api/{user_id}/tasks         │
│                                                                   │
│ Headers:                                                          │
│   Authorization: Bearer <jwt>         ← Preferred method         │
│   Cookie: session=<jwt>               ← Fallback method          │
│   Content-Type: application/json                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 5 & 6: Backend processing (identical to dev)                │
├──────────────────────────────────────────────────────────────────┤
│ Same JWT verification and data isolation logic                   │
└──────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

### 401 Unauthorized

```text
┌──────────────────────────────────────────────────────────────────┐
│ Trigger: Missing, invalid, or expired JWT token                  │
├──────────────────────────────────────────────────────────────────┤
│ Backend returns:                                                  │
│   Status: 401 Unauthorized                                        │
│   Body: { "detail": "Not authenticated - missing token" }        │
│                                                                   │
│ Frontend API client (lib/api.ts) catches 401:                    │
│   1. Shows toast: "Your session has expired..."                  │
│   2. Waits 1.5 seconds (allow user to read toast)                │
│   3. Redirects to /login                                          │
│   4. Optional: Clears auth state via authClient.signOut()        │
└──────────────────────────────────────────────────────────────────┘
```

### 403 Forbidden

```text
┌──────────────────────────────────────────────────────────────────┐
│ Trigger: Valid JWT but user_id mismatch (trying to access        │
│          another user's resources)                                │
├──────────────────────────────────────────────────────────────────┤
│ Backend returns:                                                  │
│   Status: 404 Not Found (privacy-preserving, not 403)            │
│   Body: { "detail": "Task not found" }                            │
│                                                                   │
│ Rationale: Return 404 instead of 403 to avoid leaking            │
│            information about existence of other users' tasks      │
└──────────────────────────────────────────────────────────────────┘
```

## Environment Configuration

### Development (.env.local)

```bash
NODE_ENV=development                          # Triggers secure:false, sameSite:lax
BETTER_AUTH_SECRET=<32-char-secret>           # Shared with backend
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production

```bash
NODE_ENV=production                           # Triggers secure:true, sameSite:none
BETTER_AUTH_SECRET=<32-char-secret>           # Same secret as backend (critical!)
BETTER_AUTH_URL=https://app.example.com
NEXT_PUBLIC_API_URL=https://api.example.com
```

## Cookie Attribute Decision Matrix

| Environment | secure | sameSite | Reason |
|-------------|--------|----------|--------|
| Development | `false` | `"lax"` | Allows cookies over HTTP (localhost), permits localhost:3000 → localhost:8000 |
| Production | `true` | `"none"` | Requires HTTPS, allows cross-origin requests (app.example.com → api.example.com) |

**Why not use "lax" in production?**
`sameSite: "lax"` blocks cross-origin requests in HTTPS contexts if frontend and backend are on different domains (e.g., `app.example.com` → `api.example.com`). Only `sameSite: "none"` allows this, but requires `secure: true`.

**Why not use "none" in development?**
`sameSite: "none"` requires `secure: true`, which browsers reject over HTTP. This would block all cookies on localhost.

## Security Guarantees

### XSS Protection
- **httpOnly cookies**: JavaScript cannot access JWT token via `document.cookie`
- **No local storage**: Tokens never stored in `localStorage` (vulnerable to XSS)

### CSRF Protection
- **SameSite cookies**: Development uses "lax" (some CSRF protection), production uses "none" (requires explicit origin checks)
- **CORS configuration**: Backend only accepts requests from configured `FRONTEND_ORIGIN`

### User Isolation (Constitution Principle II)
- **Backend middleware**: Extracts `user_id` from JWT `sub` claim
- **Database filtering**: All queries filter by `Task.user_id == authenticated_user_id`
- **Privacy-preserving errors**: Return 404 (not 403) for unauthorized resource access

### Token Verification
- **Shared secret**: `BETTER_AUTH_SECRET` must be identical in frontend and backend
- **Algorithm**: HS256 (HMAC-SHA256) signing and verification
- **Expiration**: JWT `exp` claim enforced (7-day default)

## Testing Validation

### Development Testing
1. **Cookie transmission**: Verify `session` cookie sent in Network tab on API requests
2. **Cookie attributes**: Inspect cookie in DevTools → `SameSite: Lax`, `Secure: false`
3. **Dual auth**: Confirm both `Authorization` header and `Cookie` sent
4. **Backend acceptance**: Backend logs "User authenticated: <user_id>"

### Production Testing
1. **HTTPS enforcement**: Verify cookies only work over HTTPS
2. **Cookie attributes**: Inspect cookie → `SameSite: None`, `Secure: true`
3. **Cross-origin**: Confirm cookies sent to different domain (if applicable)
4. **Same security**: Backend JWT verification identical to development

### Multi-User Isolation Testing
1. Create user1@example.com, user2@example.com
2. User1 creates 3 tasks → User2 creates 2 tasks
3. **Verify**: User2 sees only 2 tasks (not user1's 3 tasks)
4. **Verify**: Backend logs show different `user_id` values per request
5. **Verify**: Attempting to access user1's task as user2 returns 404

## Implementation Checklist

- [ ] Better Auth JWT plugin enabled (`jwt()` in plugins array)
- [ ] Cookie attributes environment-aware (`process.env.NODE_ENV` conditional)
- [ ] API client sends Authorization Bearer header (via `authClient.getSession()`)
- [ ] API client includes credentials for cookie fallback (`credentials: "include"`)
- [ ] 401 handler shows toast before redirect (1.5s delay for visibility)
- [ ] Backend middleware accepts both Bearer token and cookie
- [ ] Backend extracts `user_id` from JWT `sub` claim
- [ ] All database queries filter by `user_id`
- [ ] Multi-user isolation tested and verified

## References

- **Better Auth JWT Plugin**: https://www.better-auth.com/docs/plugins/jwt
- **MDN Secure Cookies**: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies
- **MDN SameSite**: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value
- **Spec**: `specs/004-auth-fix-workflow/spec.md`
- **Plan**: `specs/004-auth-fix-workflow/plan.md`
