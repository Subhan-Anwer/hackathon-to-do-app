# Cookie Configuration Fix - SameSite Cross-Origin Issue

## Problem

**Symptom:** Task creation was failing with "Session expired" error despite user being logged in. The session cookie was correctly named "session" but wasn't being sent with API requests.

**Root Cause:** Better Auth's default cookie configuration uses `sameSite: "lax"`, which prevents cookies from being sent with cross-origin POST requests made via JavaScript fetch().

## Why This Happens

When the frontend (localhost:3000) makes a POST request to the backend (localhost:8000):
- **Different ports = Different origins** (cross-origin request)
- **SameSite=Lax** cookies are only sent with:
  - Same-origin requests
  - Top-level navigation (clicking a link)
- **SameSite=Lax** cookies are NOT sent with:
  - Cross-origin fetch() POST requests
  - AJAX requests to different origins

## The Fix

Updated `frontend/lib/auth.ts` to configure the session cookie with `sameSite: "none"`:

```typescript
advanced: {
  cookies: {
    session_token: {
      name: "session",
      attributes: {
        sameSite: "none", // Allow cross-origin requests
        secure: true,     // Required when sameSite=none
      },
    },
  },
},
```

## Why It Works

- **sameSite: "none"** - Allows cookies to be sent with ALL requests, including cross-origin POST
- **secure: true** - Required by browsers when sameSite=none
- **Localhost is secure** - Browsers treat localhost as a secure context even over HTTP, so `secure: true` works in development

## Production Considerations

This configuration is correct for both development and production:

**Development (localhost):**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Browsers treat localhost as secure, so `secure: true` works

**Production (deployed):**
- Must use HTTPS for both frontend and backend
- `secure: true` ensures cookies only sent over HTTPS
- `sameSite: "none"` allows cross-origin requests if frontend/backend on different domains

## Alternative Solutions

If you want to avoid `sameSite: "none"` in development, you could:

1. **Use a proxy** - Configure Next.js to proxy `/api/*` requests to backend
   - Frontend and backend appear same-origin
   - Can keep `sameSite: "lax"` (more secure)
   - Requires Next.js rewrites configuration

2. **Use same domain in production** - Deploy frontend and backend under same domain
   - Example: frontend at `app.example.com`, backend at `app.example.com/api`
   - Not applicable for localhost development

3. **Conditional configuration** - Set sameSite based on environment
   - Development: `sameSite: "none"`
   - Production: `sameSite: "lax"` (if same domain)
   - Requires environment-aware config

## Related Files

- `frontend/lib/auth.ts` - Better Auth configuration with cookie settings
- `frontend/lib/api.ts` - API client with `credentials: "include"`
- `backend/main.py` - CORS middleware with `allow_credentials=True`
- `backend/dependencies.py` - JWT validation that reads "session" cookie

## Testing the Fix

1. Clear all cookies in browser
2. Restart frontend server (npm run dev)
3. Signup/login to create new session
4. Verify cookie in DevTools: `SameSite=None; Secure`
5. Create a task - should work without "session expired" error

## References

- [MDN: SameSite cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
- [Better Auth: Cookie configuration](https://github.com/better-auth/better-auth)
- [Chrome: SameSite cookie changes](https://www.chromium.org/updates/same-site)
