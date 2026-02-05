# JWT Authentication Flow

## Complete Flow Diagram

```
User Action (Signup/Login)
    ↓
Better Auth (Next.js API Route)
    ↓
Generate JWT Token + Set httpOnly Cookie
    ↓
Frontend Component (receives session)
    ↓
User Makes API Request
    ↓
Next.js API Proxy (Server-Side)
    ↓
Read httpOnly Cookie (only server can access)
    ↓
Extract JWT Token
    ↓
Forward to FastAPI Backend with Authorization Header
    ↓
FastAPI JWT Middleware
    ↓
Verify Token Signature
    ↓
Decode User Data (user_id, email)
    ↓
Protected Endpoint Handler
    ↓
Verify user_id matches authenticated user
    ↓
Return User-Specific Data
```

## Why httpOnly Cookies Cannot Be Read by JavaScript

**Security Feature:**
- httpOnly cookies are a browser security mechanism
- Prevents XSS (Cross-Site Scripting) attacks from stealing tokens
- JavaScript code (including malicious scripts) cannot access these cookies via `document.cookie`

**Server-Side Only:**
- Only HTTP requests can send/receive httpOnly cookies
- Server-side code (API routes, middleware) can read them
- This is why the proxy pattern is essential

## Token Flow Details

### 1. Token Creation (Better Auth)
```typescript
// Better Auth automatically handles this
const token = jwt.sign(
  {
    sub: user.id,        // Subject = user ID
    email: user.email,
    iat: Date.now(),     // Issued at
    exp: Date.now() + (7 * 24 * 60 * 60 * 1000) // 7 days
  },
  BETTER_AUTH_SECRET,
  { algorithm: 'HS256' }
)
```

### 2. Cookie Setting
```typescript
Set-Cookie: better-auth.session_token=<JWT>; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

### 3. Token Verification (Backend)
```python
import jwt

payload = jwt.decode(
    token,
    BETTER_AUTH_SECRET,
    algorithms=["HS256"]
)

user_id = payload["sub"]  # Extract user ID
```

## Common Security Pitfalls

### ❌ Wrong: Trying to read cookie from client
```typescript
// This will ALWAYS be undefined
const token = document.cookie.split(';').find(c => c.includes('better-auth'))
```

### ✅ Right: Use server-side proxy
```typescript
// app/api/proxy/[...path]/route.ts
const cookieStore = await cookies()
const token = cookieStore.get("better-auth.session_token")?.value
```

### ❌ Wrong: Direct backend call
```typescript
// Cookie won't be included
fetch('http://localhost:8000/api/tasks')
```

### ✅ Right: Call through proxy
```typescript
// Cookie automatically included by browser
fetch('/api/proxy/api/tasks', { credentials: 'include' })
```

## Token Payload Structure

```json
{
  "sub": "user-id-here",           // User ID (standard JWT claim)
  "email": "user@example.com",     // Email address
  "iat": 1735689600,                // Issued at (Unix timestamp)
  "exp": 1736294400                 // Expiration (Unix timestamp)
}
```

**Important Fields:**
- `sub` (subject): Contains the user ID - always use this in backend
- `email`: User's email address
- `exp`: Token expiration - automatically checked by jwt.decode()
