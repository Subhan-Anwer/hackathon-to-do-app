# OWASP Top 10 Protection for FastAPI

Protection strategies against the OWASP Top 10 web application security risks in FastAPI applications with JWT authentication.

## Overview

The OWASP Top 10 represents the most critical security risks to web applications. This guide shows how to prevent each vulnerability in FastAPI applications.

---

## 1. Broken Access Control

**Risk:** Users can access resources they shouldn't have permission to access.

### Common Attacks
- Accessing other users' data by changing user_id in URL
- Modifying resources that don't belong to the user
- Privilege escalation

### Prevention

```python
from fastapi import APIRouter, Depends, HTTPException
from middleware.jwt import verify_jwt, verify_user_access, verify_resource_ownership

@router.get("/api/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_jwt),
    session: Session = Depends(get_session),
):
    # ✅ Verify user owns endpoint
    verify_user_access(user_id, current_user)

    # ✅ Fetch resource
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404)

    # ✅ Verify user owns resource
    verify_resource_ownership(task.user_id, current_user, "task")

    return task
```

### Best Practices
- ✅ Verify JWT on all protected endpoints
- ✅ Validate user_id in URL matches token
- ✅ Check resource ownership before read/update/delete
- ✅ Filter all queries by authenticated user_id
- ✅ Use principle of least privilege

---

## 2. Cryptographic Failures

**Risk:** Sensitive data exposed due to weak encryption or improper handling.

### Common Issues
- Weak JWT secrets
- Passwords stored in plaintext
- Sensitive data in logs
- No HTTPS in production

### Prevention

```python
import os
from passlib.context import CryptContext

# ✅ Strong JWT secret (32+ characters)
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError("Secret must be at least 32 characters")

# ✅ Password hashing (handled by Better Auth)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Environment variables for secrets
DATABASE_URL = os.getenv("DATABASE_URL")  # Not hardcoded!

# ✅ HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### Best Practices
- ✅ Generate strong secrets: `openssl rand -hex 32`
- ✅ Use environment variables, never hardcode
- ✅ Enable HTTPS in production
- ✅ Use bcrypt/argon2 for password hashing
- ✅ Never log sensitive data (passwords, tokens, secrets)
- ✅ Use encrypted database connections (SSL)

---

## 3. Injection

**Risk:** Attackers inject malicious code into queries or commands.

### SQL Injection Prevention

```python
from sqlmodel import select, Session

# ❌ VULNERABLE - String formatting
user_id = request.query_params.get("user_id")
query = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"  # SQL injection!

# ✅ SAFE - SQLModel/SQLAlchemy parameterized queries
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)  # Automatically parameterized
).all()
```

### Command Injection Prevention

```python
import subprocess

# ❌ VULNERABLE - Shell injection
filename = request.query_params.get("file")
subprocess.run(f"cat {filename}", shell=True)  # Command injection!

# ✅ SAFE - No shell, use list
subprocess.run(["cat", filename], shell=False)

# ✅ BETTER - Validate input first
import re
if not re.match(r'^[\w\-\.]+$', filename):
    raise HTTPException(400, "Invalid filename")
subprocess.run(["cat", filename], shell=False)
```

### Best Practices
- ✅ Use ORM (SQLModel/SQLAlchemy) instead of raw SQL
- ✅ Never construct SQL with string formatting
- ✅ Validate and sanitize all user input
- ✅ Use parameterized queries
- ✅ Avoid shell=True in subprocess
- ✅ Use allowlists for file paths

---

## 4. Insecure Design

**Risk:** Fundamental flaws in application architecture.

### Prevention Strategies

```python
# ✅ Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, credentials: LoginRequest):
    ...

# ✅ User enumeration prevention
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    user = get_user_by_email(credentials.email)

    # Same error for wrong email or password (don't reveal which)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

# ✅ Token expiration
jwt_payload = {
    "sub": user_id,
    "exp": datetime.utcnow() + timedelta(hours=24)  # Limited lifetime
}
```

### Best Practices
- ✅ Implement rate limiting on sensitive endpoints
- ✅ Use short-lived tokens (24 hours max)
- ✅ Prevent user enumeration (same errors)
- ✅ Design with security from start (not bolted on)
- ✅ Principle of least privilege
- ✅ Defense in depth (multiple security layers)

---

## 5. Security Misconfiguration

**Risk:** Insecure default settings, incomplete config, verbose errors.

### Prevention

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# ✅ Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # Specific origins, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods
    allow_headers=["Authorization", "Content-Type"],  # Explicit headers
)

# ✅ Disable debug in production
DEBUG = os.getenv("ENVIRONMENT") != "production"
app = FastAPI(debug=DEBUG)

# ✅ Configure proper logging
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ✅ Generic error messages to client
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log full details server-side
    logging.error(f"Unhandled error: {str(exc)}", exc_info=True)

    # Return generic message to client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Best Practices
- ✅ Disable debug mode in production
- ✅ Use specific CORS origins (not "*")
- ✅ Set secure cookie flags (httpOnly, secure, sameSite)
- ✅ Remove default credentials
- ✅ Keep dependencies updated
- ✅ Use security headers

---

## 6. Vulnerable and Outdated Components

**Risk:** Using libraries with known vulnerabilities.

### Prevention

```bash
# ✅ Keep dependencies updated
pip list --outdated

# ✅ Use security scanners
pip install safety
safety check

# ✅ Pin dependency versions
# requirements.txt
fastapi==0.104.1
sqlmodel==0.0.14
pyjwt==2.8.0
uvicorn[standard]==0.24.0

# ✅ Regular updates
pip install --upgrade fastapi sqlmodel pyjwt
```

### Best Practices
- ✅ Pin dependency versions in requirements.txt
- ✅ Run `safety check` in CI/CD
- ✅ Subscribe to security advisories
- ✅ Update dependencies regularly
- ✅ Remove unused dependencies
- ✅ Use dependabot or similar tools

---

## 7. Identification and Authentication Failures

**Risk:** Weak authentication allows unauthorized access.

### Prevention

```python
from middleware.jwt import verify_jwt

# ✅ Strong JWT verification
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),  # Requires valid JWT
):
    if current_user["user_id"] != user_id:
        raise HTTPException(403)
    ...

# ✅ Password requirements (Better Auth handles this)
# - Minimum 8 characters
# - Mix of letters, numbers, symbols
# - Check against common passwords

# ✅ Account lockout after failed attempts
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    attempts = get_login_attempts(credentials.email)

    if attempts >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(429, "Too many attempts. Try again later.")

    user = authenticate(credentials)
    if not user:
        increment_login_attempts(credentials.email)
        raise HTTPException(401, "Invalid credentials")

    clear_login_attempts(credentials.email)
    return create_session(user)
```

### Best Practices
- ✅ Enforce strong password policies
- ✅ Implement account lockout
- ✅ Use multi-factor authentication (MFA)
- ✅ Implement session timeout
- ✅ Use secure session management
- ✅ Prevent brute force with rate limiting

---

## 8. Software and Data Integrity Failures

**Risk:** Insecure CI/CD pipeline, unsigned updates, untrusted data.

### Prevention

```python
# ✅ Verify JWT signature (integrity check)
import jwt

try:
    payload = jwt.decode(
        token,
        BETTER_AUTH_SECRET,
        algorithms=["HS256"]  # Verify signature
    )
except jwt.InvalidSignatureError:
    raise HTTPException(401, "Invalid token signature")

# ✅ Database constraints for data integrity
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)  # Constraints
    user_id: str = Field(foreign_key="user.id")  # Foreign key integrity

# ✅ Input validation with Pydantic
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

### Best Practices
- ✅ Verify JWT signatures
- ✅ Use database constraints (foreign keys, NOT NULL)
- ✅ Validate all input with Pydantic
- ✅ Use checksum verification for downloads
- ✅ Sign releases
- ✅ Secure CI/CD pipeline

---

## 9. Security Logging and Monitoring Failures

**Risk:** Attacks go undetected due to insufficient logging.

### Prevention

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ✅ Log authentication events
@app.post("/api/auth/login")
async def login(credentials: LoginRequest, request: Request):
    logger.info(
        f"Login attempt for {credentials.email} "
        f"from {request.client.host}"
    )

    user = authenticate(credentials)

    if not user:
        logger.warning(
            f"Failed login for {credentials.email} "
            f"from {request.client.host}"
        )
        raise HTTPException(401)

    logger.info(f"Successful login for {user.email}")
    return create_session(user)

# ✅ Log security events
@router.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(user_id: str, task_id: int, current_user: dict):
    logger.info(
        f"User {current_user['user_id']} deleted task {task_id}"
    )
    ...

# ✅ Log authorization failures
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        logger.warning(
            f"Authorization failure: {request.url} "
            f"by {request.headers.get('Authorization', 'anonymous')}"
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### What to Log
- ✅ Authentication events (login, logout, failures)
- ✅ Authorization failures (403 errors)
- ✅ Input validation failures
- ✅ Critical operations (delete, update sensitive data)
- ✅ Security exceptions

### What NOT to Log
- ❌ Passwords
- ❌ JWT tokens
- ❌ Secrets/API keys
- ❌ Personal data (PII)
- ❌ Credit card numbers

### Best Practices
- ✅ Log security-relevant events
- ✅ Include timestamp, user, IP, action
- ✅ Use structured logging (JSON)
- ✅ Monitor logs for suspicious patterns
- ✅ Set up alerts for repeated failures
- ✅ Protect log integrity

---

## 10. Server-Side Request Forgery (SSRF)

**Risk:** Attacker makes server perform requests to internal resources.

### Prevention

```python
from urllib.parse import urlparse
import ipaddress

def is_safe_url(url: str) -> bool:
    """Validate URL is safe to fetch"""
    parsed = urlparse(url)

    # ✅ Only allow HTTP/HTTPS
    if parsed.scheme not in ['http', 'https']:
        return False

    # ✅ Resolve hostname
    try:
        ip = ipaddress.ip_address(parsed.hostname)

        # ✅ Block private/internal IPs
        if ip.is_private or ip.is_loopback:
            return False
    except ValueError:
        pass  # Hostname, not IP

    # ✅ Blocklist dangerous domains
    blocked_domains = ['localhost', '127.0.0.1', 'metadata.google.internal']
    if parsed.hostname in blocked_domains:
        return False

    return True

# ✅ Validate URLs before fetching
@app.post("/api/fetch-url")
async def fetch_url(url: str):
    if not is_safe_url(url):
        raise HTTPException(400, "Invalid URL")

    # Safe to fetch
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=False)
        return response.text
```

### Best Practices
- ✅ Validate all user-provided URLs
- ✅ Block private IP ranges (10.0.0.0/8, 192.168.0.0/16, 127.0.0.1)
- ✅ Block metadata services (169.254.169.254)
- ✅ Use allowlist of permitted domains
- ✅ Disable redirects or validate redirect targets
- ✅ Use network segmentation

---

## Security Headers

Add security headers to all responses:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Force HTTPS (production only)
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Security Checklist

Use this checklist to verify your FastAPI application is secure:

### Authentication & Authorization
- [ ] JWT verification on all protected endpoints
- [ ] User ID verification (token vs URL)
- [ ] Resource ownership verification
- [ ] Database queries filtered by user_id
- [ ] Rate limiting on auth endpoints

### Cryptography
- [ ] Strong JWT secret (32+ characters)
- [ ] HTTPS in production
- [ ] Secrets in environment variables
- [ ] Password hashing (bcrypt/argon2)
- [ ] No sensitive data in logs

### Input Validation
- [ ] Pydantic models for all input
- [ ] SQLModel ORM (no raw SQL)
- [ ] URL validation for user-provided URLs
- [ ] File path validation
- [ ] SQL injection prevented

### Configuration
- [ ] Debug mode disabled in production
- [ ] Specific CORS origins (not "*")
- [ ] Security headers configured
- [ ] Error messages don't leak info
- [ ] Dependencies up to date

### Monitoring
- [ ] Log authentication events
- [ ] Log authorization failures
- [ ] Monitor for suspicious patterns
- [ ] Alerts for repeated failures
- [ ] No sensitive data in logs

### Testing
- [ ] Security tests for each endpoint
- [ ] Test cross-user access
- [ ] Test injection attempts
- [ ] Test rate limiting
- [ ] Penetration testing

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
