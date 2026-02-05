# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "Token is undefined" in Backend

**Symptoms:**
- Backend receives `Authorization: Bearer undefined`
- 401 Unauthorized errors

**Causes & Solutions:**

**Cause A: Missing `credentials: "include"` in frontend fetch**
```typescript
// ❌ Wrong
fetch('/api/proxy/tasks')

// ✅ Right
fetch('/api/proxy/tasks', { credentials: 'include' })
```

**Cause B: Proxy not reading cookie correctly**
```typescript
// ❌ Wrong - using wrong cookie name
const token = cookies().get('session_token')

// ✅ Right - exact Better Auth cookie name
const token = cookies().get('better-auth.session_token')
```

---

### Issue 2: CORS Errors

**Symptoms:**
- "Access-Control-Allow-Origin" errors in browser console
- Requests blocked by CORS policy

**Solution:**
Don't call backend directly from frontend. Always use the proxy:

```typescript
// ❌ Wrong - direct backend call triggers CORS
fetch('http://localhost:8000/api/tasks')

// ✅ Right - proxy handles CORS internally
fetch('/api/proxy/api/tasks')
```

---

### Issue 3: "Invalid token" or "Token verification failed"

**Symptoms:**
- Backend returns 401 with "Invalid token" message
- jwt.decode() throws InvalidTokenError

**Causes & Solutions:**

**Cause A: Mismatched BETTER_AUTH_SECRET**
```bash
# Frontend .env
BETTER_AUTH_SECRET=secret123

# Backend .env
BETTER_AUTH_SECRET=differentsecret  # ❌ Must match!
```

**Solution:** Ensure both use identical secret

**Cause B: Wrong algorithm**
```python
# ❌ Wrong algorithm
jwt.decode(token, secret, algorithms=["RS256"])

# ✅ Right - Better Auth uses HS256
jwt.decode(token, secret, algorithms=["HS256"])
```

**Cause C: Token expired**
- Check token expiration settings in Better Auth config
- Verify system clocks are synchronized

---

### Issue 4: User Can Access Other Users' Data

**Symptoms:**
- User A can see User B's todos
- No user isolation

**Cause:**
Backend not verifying user_id matches token:

```python
# ❌ Wrong - no verification
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, current_user: dict = Depends(verify_jwt)):
    return get_user_tasks(user_id)  # Returns ANY user's tasks!

# ✅ Right - verify user_id
@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, current_user: dict = Depends(verify_jwt)):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return get_user_tasks(user_id)
```

---

### Issue 5: Session Not Persisting After Refresh

**Symptoms:**
- User logged out after page refresh
- Session lost on navigation

**Causes & Solutions:**

**Cause A: Cookie not being set**
- Check browser DevTools → Application → Cookies
- Verify `better-auth.session_token` exists

**Cause B: Cookie expiration too short**
```typescript
// Better Auth config
session: {
  cookieCache: {
    enabled: true,
    maxAge: 60 * 60 * 24 * 7, // 7 days - increase if needed
  },
}
```

**Cause C: Not checking session correctly**
```typescript
// ❌ Wrong - only checks on mount
const { session } = useAuth()

// ✅ Right - checks loading state
const { session, isLoading } = useAuth()
if (isLoading) return <Loading />
if (!session) redirect('/login')
```

---

### Issue 6: Proxy Returns 404

**Symptoms:**
- Proxy route not found
- Next.js 404 page shown

**Cause:**
Incorrect proxy route structure:

```typescript
// ❌ Wrong - missing catch-all parameter
// File: app/api/proxy/route.ts

// ✅ Right - catch-all parameter
// File: app/api/proxy/[...path]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
)
```

---

### Issue 7: "Missing authorization header"

**Symptoms:**
- Backend receives no Authorization header
- Even though proxy is working

**Cause:**
Proxy not forwarding the header:

```typescript
// ❌ Wrong - not including Authorization header
const response = await fetch(targetUrl)

// ✅ Right - forward Authorization header
const response = await fetch(targetUrl, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
```

---

## Debugging Checklist

When authentication isn't working, check in this order:

### Frontend (Browser DevTools)

1. **Application Tab → Cookies**
   - [ ] `better-auth.session_token` exists
   - [ ] Cookie is not expired
   - [ ] HttpOnly flag is set

2. **Network Tab → Fetch/XHR**
   - [ ] Request to proxy includes `credentials: include`
   - [ ] Proxy request succeeds (200 status)

3. **Console Tab**
   - [ ] No CORS errors
   - [ ] No JavaScript errors
   - [ ] Session object is populated

### Proxy (Server-Side Logs)

4. **Check proxy route**
   - [ ] Cookie is being read successfully
   - [ ] Token is not undefined
   - [ ] Request is being forwarded to backend

### Backend (FastAPI Logs)

5. **Check JWT verification**
   - [ ] Authorization header is present
   - [ ] Token format is "Bearer <token>"
   - [ ] BETTER_AUTH_SECRET matches frontend
   - [ ] Token decodes successfully
   - [ ] User ID is extracted from `sub` field

6. **Check endpoint logic**
   - [ ] User ID verification happens
   - [ ] Database queries use correct user_id

---

## Environment Variable Checklist

### Frontend (.env.local)
```bash
BETTER_AUTH_SECRET=<must-match-backend>
NEXT_PUBLIC_APP_URL=http://localhost:3000
DATABASE_URL=postgresql://...
```

### Backend (.env)
```bash
BETTER_AUTH_SECRET=<must-match-frontend>
DATABASE_URL=postgresql://...
```

**Critical:** BETTER_AUTH_SECRET must be identical in both!

---

## Testing Commands

### Test Cookie is Set
```bash
# After login, check cookies
curl -v http://localhost:3000/api/auth/session -H "Cookie: better-auth.session_token=..."
```

### Test Proxy Forwards Token
```bash
# Check proxy logs while making request
# Should see token being extracted and forwarded
```

### Test Backend Verifies Token
```python
# Add debug logging in verify_jwt
import logging
logger = logging.getLogger(__name__)

async def verify_jwt(authorization: str = Header(None)) -> dict:
    logger.info(f"Received authorization header: {authorization[:50]}...")
    # ... rest of verification
```
