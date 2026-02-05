# JWT Verification Deep Dive

Complete guide to JWT token structure, verification process, and security considerations for Better Auth integration.

## Table of Contents

- [JWT Structure](#jwt-structure)
- [Verification Process](#verification-process)
- [Better Auth Token Format](#better-auth-token-format)
- [Common Issues](#common-issues)
- [Security Best Practices](#security-best-practices)

## JWT Structure

A JWT (JSON Web Token) consists of three Base64-encoded parts separated by dots:

```
<header>.<payload>.<signature>
```

### Example Token

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTcwNjg5MDAwMH0.Xj8K_ZvN2qR5tPwQ9m3hLbYvGfUn4jWx1aS8dE7rK6M
```

### Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- `alg`: Algorithm used for signing (HS256 = HMAC SHA-256)
- `typ`: Token type (always "JWT")

### Payload (Claims)

```json
{
  "sub": "user_123",
  "email": "user@example.com",
  "exp": 1706890000,
  "iat": 1706803600
}
```

**Standard Claims:**
- `sub` (subject): User identifier (CRITICAL - use this for user_id)
- `exp` (expiration): Unix timestamp when token expires
- `iat` (issued at): Unix timestamp when token was created
- `iss` (issuer): Token issuer (optional)
- `aud` (audience): Token audience (optional)

**Custom Claims:**
- `email`: User's email address
- Any other user-specific data

### Signature

Created by:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  BETTER_AUTH_SECRET
)
```

The signature ensures:
1. Token hasn't been tampered with
2. Token was created by your application (has correct secret)

## Verification Process

### Step-by-Step Verification

1. **Parse Authorization Header**
   ```python
   authorization = request.headers.get("Authorization")
   # Expected format: "Bearer <token>"

   scheme, token = authorization.split()
   assert scheme.lower() == "bearer"
   ```

2. **Decode and Verify Signature**
   ```python
   import jwt

   payload = jwt.decode(
       token,
       BETTER_AUTH_SECRET,
       algorithms=["HS256"]
   )
   ```

   This automatically:
   - Verifies signature matches
   - Checks token hasn't expired
   - Validates token structure

3. **Extract User Data**
   ```python
   user_id = payload["sub"]  # Standard claim for user ID
   email = payload.get("email")  # Custom claim
   exp = payload["exp"]  # Expiration timestamp
   ```

4. **Validate Required Fields**
   ```python
   if not user_id:
       raise HTTPException(401, "Invalid token: missing user ID")
   ```

### Verification Failures

| Error | Meaning | Status Code |
|-------|---------|-------------|
| `jwt.ExpiredSignatureError` | Token has expired | 401 |
| `jwt.InvalidSignatureError` | Signature doesn't match (wrong secret) | 401 |
| `jwt.DecodeError` | Token is malformed | 401 |
| `jwt.InvalidTokenError` | Other token issues | 401 |

## Better Auth Token Format

### Token Generation (Frontend)

Better Auth generates tokens with the `jwt` plugin:

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  plugins: [
    jwt({
      jwt: {
        expiresIn: "24h",  // Token lifetime
      }
    })
  ],
  secret: process.env.BETTER_AUTH_SECRET,
})
```

### Token Payload Structure

Better Auth tokens include:

```json
{
  "sub": "cm4abc123def456ghi",  // User ID (UUID from database)
  "email": "user@example.com",
  "exp": 1706890000,  // 24 hours from creation
  "iat": 1706803600
}
```

**Critical Notes:**
- User ID is in `sub` claim (NOT `user_id`)
- `sub` is the UUID from the `user` table
- Token expiration is Unix timestamp (seconds since epoch)

### Token Delivery

Tokens are stored in httpOnly cookies:

```typescript
// Cookie name: auth.session_token (configurable)
// HttpOnly: true (cannot be read by JavaScript)
// Secure: true (HTTPS only in production)
// SameSite: Lax (CSRF protection)
```

### Token Extraction (Backend)

Since httpOnly cookies can't be read by JavaScript, use API proxy:

**Next.js Proxy:**
```typescript
// app/api/proxy/[...path]/route.ts
import { cookies } from 'next/headers'

export async function GET(request: Request) {
  const cookieStore = await cookies()
  const token = cookieStore.get('auth.session_token')?.value

  // Forward to backend with Authorization header
  const response = await fetch(backendUrl, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
}
```

**Backend Verification:**
```python
# middleware/jwt.py
authorization = request.headers.get("Authorization")
scheme, token = authorization.split()
payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
```

## Common Issues

### Issue 1: "Token is undefined" in Backend

**Symptom:**
```python
TypeError: 'NoneType' object is not subscriptable
```

**Causes:**
- Authorization header not included in request
- Frontend not using proxy (trying to read httpOnly cookie)
- Missing `credentials: "include"` in fetch

**Solution:**
```typescript
// ✅ Correct - Use proxy
const response = await fetch('/api/proxy/api/user123/tasks', {
  credentials: 'include'  // Required!
})

// ❌ Wrong - Direct backend call
const response = await fetch('http://localhost:8000/api/user123/tasks')
```

### Issue 2: "Invalid token signature"

**Symptom:**
```
jwt.exceptions.InvalidSignatureError: Signature verification failed
```

**Causes:**
- BETTER_AUTH_SECRET mismatch between frontend and backend
- Secret was changed but old tokens still in use
- Different secret in .env vs .env.local

**Solution:**
```bash
# Ensure secrets match EXACTLY
# Frontend (.env.local)
BETTER_AUTH_SECRET=same-secret-here-32-chars-minimum!

# Backend (.env)
BETTER_AUTH_SECRET=same-secret-here-32-chars-minimum!
```

### Issue 3: "Token has expired"

**Symptom:**
```
jwt.exceptions.ExpiredSignatureError
```

**Causes:**
- Token lifetime exceeded (default 24 hours)
- Server time mismatch
- Token created long ago

**Solution:**
- User must log in again to get new token
- Consider refresh token mechanism for long-lived sessions
- Verify server times are synchronized

### Issue 4: Wrong User ID Field

**Symptom:**
```python
KeyError: 'user_id'
```

**Cause:**
Using `payload["user_id"]` instead of `payload["sub"]`

**Solution:**
```python
# ❌ Wrong
user_id = payload["user_id"]

# ✅ Correct - JWT standard is 'sub'
user_id = payload["sub"]
```

### Issue 5: CORS Preflight Failures

**Symptom:**
```
Access to fetch has been blocked by CORS policy
```

**Causes:**
- Missing `allow_credentials=True` in CORS config
- Frontend origin not in `allow_origins`
- Authorization header not allowed

**Solution:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # Required!
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Security Best Practices

### 1. Secret Management

**Strong Secret:**
```bash
# Generate strong secret
openssl rand -hex 32
# Output: a3f2c9d8e7b6f5a4c3d2e1f0b9a8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0
```

**Requirements:**
- Minimum 32 characters
- Random, unpredictable
- Never commit to version control
- Same secret in frontend and backend

**Storage:**
```bash
# .env (backend)
BETTER_AUTH_SECRET=<generated-secret>

# .env.local (frontend)
BETTER_AUTH_SECRET=<same-generated-secret>

# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

### 2. Token Expiration

**Recommended Settings:**
```typescript
jwt({
  jwt: {
    expiresIn: "24h",  // Short-lived for security
  }
})
```

**Considerations:**
- Shorter = more secure (limits exposure if stolen)
- Longer = better UX (fewer re-logins)
- Balance based on sensitivity of data

### 3. Algorithm Selection

**Use HMAC (HS256):**
```python
ALGORITHM = "HS256"  # Symmetric - fast, secure for single-server
```

**Avoid "none" algorithm:**
```python
# ❌ NEVER accept unsigned tokens
algorithms=["none"]  # CRITICAL VULNERABILITY

# ✅ Explicitly specify algorithm
algorithms=["HS256"]
```

### 4. Token Validation

**Always validate:**
```python
# ✅ Check signature
jwt.decode(token, secret, algorithms=["HS256"])

# ✅ Check expiration (automatic in decode)
# ✅ Check required claims
if not payload.get("sub"):
    raise HTTPException(401, "Missing user ID")
```

### 5. Error Handling

**Don't leak information:**
```python
# ❌ Reveals secret weakness
raise HTTPException(401, f"Secret is wrong: {BETTER_AUTH_SECRET}")

# ✅ Generic message
raise HTTPException(401, "Invalid or expired token")
```

**Log details server-side:**
```python
import logging
logger = logging.getLogger(__name__)

try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
except jwt.InvalidTokenError as e:
    logger.error(f"JWT verification failed: {str(e)}")
    raise HTTPException(401, "Invalid token")
```

### 6. HTTPS in Production

**Always use HTTPS for:**
- Token transmission
- API requests
- Cookie delivery

**Configuration:**
```python
# Force HTTPS redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Cookie settings:**
```typescript
// Secure cookies in production
cookies: {
  sessionToken: {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",  // HTTPS only
    sameSite: "lax",
  }
}
```

## Testing JWT Verification

### Manual Testing

**Test with curl:**
```bash
# 1. Get token (login)
TOKEN=$(curl -X POST http://localhost:3000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  -c cookies.txt -s | jq -r '.token')

# 2. Use token
curl http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer $TOKEN"

# 3. Test expiration (wait until expired)
# Should return 401
```

**Decode token (debugging):**
```bash
# Install jwt-cli
cargo install jwt-cli

# Decode token
jwt decode <token>

# Verify signature
jwt verify <token> <secret>
```

### Automated Testing

```python
import pytest
import jwt
from datetime import datetime, timedelta

def test_valid_token_accepted():
    payload = {
        "sub": "user123",
        "email": "user@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_expired_token_rejected():
    payload = {
        "sub": "user123",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401

def test_invalid_signature_rejected():
    token = jwt.encode({"sub": "user123"}, "wrong-secret", algorithm="HS256")

    response = client.get(
        "/api/user123/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
```

## Reference Links

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519) - JWT specification
- [PyJWT Documentation](https://pyjwt.readthedocs.io/) - Python JWT library
- [Better Auth JWT Plugin](https://better-auth.com/plugins/jwt) - Better Auth JWT docs
