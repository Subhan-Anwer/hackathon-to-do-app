"""
CORS Configuration for FastAPI with Next.js Frontend

Production-ready CORS configuration that enables:
- JWT token forwarding via Authorization header
- Cookie-based authentication
- Secure cross-origin requests
- Environment-specific origins

CRITICAL: allow_credentials=True is required for JWT authentication
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware with environment-specific settings.

    Args:
        app: FastAPI application instance

    Environment Variables:
        ENVIRONMENT: "development" or "production"
        FRONTEND_URL: Production frontend URL (e.g., https://app.example.com)
        ALLOWED_ORIGINS: Comma-separated list of allowed origins (optional)
    """
    environment = os.getenv("ENVIRONMENT", "development")

    # Determine allowed origins based on environment
    allowed_origins = get_allowed_origins(environment)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,  # CRITICAL: Required for JWT auth
        allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],     # Allow all headers including Authorization
        expose_headers=["*"],    # Expose all response headers to frontend
        max_age=600,            # Cache preflight requests for 10 minutes
    )

    print(f"✓ CORS configured for {environment}")
    print(f"✓ Allowed origins: {allowed_origins}")


def get_allowed_origins(environment: str) -> List[str]:
    """
    Get allowed origins based on environment.

    Args:
        environment: "development" or "production"

    Returns:
        List of allowed origin URLs

    Notes:
        - Development: Allows localhost on common ports
        - Production: Uses FRONTEND_URL or ALLOWED_ORIGINS env var
    """
    # Check for explicit ALLOWED_ORIGINS env var
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
    if allowed_origins_env:
        # Parse comma-separated list
        return [origin.strip() for origin in allowed_origins_env.split(",")]

    if environment == "production":
        # Production: Use FRONTEND_URL
        frontend_url = os.getenv("FRONTEND_URL")

        if not frontend_url:
            raise ValueError(
                "FRONTEND_URL environment variable is required in production. "
                "Example: https://app.example.com"
            )

        # Allow production frontend URL
        return [frontend_url]

    else:
        # Development: Allow common localhost ports
        return [
            "http://localhost:3000",      # Next.js default
            "http://localhost:3001",      # Alternative port
            "http://127.0.0.1:3000",      # Explicit 127.0.0.1
            "http://localhost:8000",      # FastAPI (for testing)
        ]


def configure_security_headers(app: FastAPI) -> None:
    """
    Add security headers middleware (optional but recommended).

    Headers added:
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter (legacy browsers)
    - Strict-Transport-Security: Force HTTPS (production only)
    """
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request

    environment = os.getenv("ENVIRONMENT", "development")

    # Force HTTPS in production
    if environment == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
        print("✓ HTTPS redirect enabled (production)")

    # Trusted host middleware (prevent Host header attacks)
    allowed_hosts = get_allowed_hosts(environment)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
    print(f"✓ Trusted hosts: {allowed_hosts}")

    # Custom security headers
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)

            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"

            # HSTS in production (force HTTPS for 1 year)
            if environment == "production":
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )

            return response

    app.add_middleware(SecurityHeadersMiddleware)
    print("✓ Security headers configured")


def get_allowed_hosts(environment: str) -> List[str]:
    """
    Get allowed hosts for TrustedHostMiddleware.

    Args:
        environment: "development" or "production"

    Returns:
        List of allowed hostnames
    """
    if environment == "production":
        backend_url = os.getenv("BACKEND_URL", "")

        if not backend_url:
            raise ValueError("BACKEND_URL required in production")

        # Extract hostname from URL
        from urllib.parse import urlparse
        hostname = urlparse(backend_url).netloc

        return [hostname, "localhost"]

    else:
        # Development: Allow common local addresses
        return ["localhost", "127.0.0.1", "0.0.0.0"]


# ==============================================================================
# Usage Example
# ==============================================================================

if __name__ == "__main__":
    """
    Example usage in main.py:

    from fastapi import FastAPI
    from cors_config import configure_cors, configure_security_headers

    app = FastAPI()

    # Configure CORS (required for Next.js frontend)
    configure_cors(app)

    # Configure security headers (recommended)
    configure_security_headers(app)

    # Add your routes
    # ...
    """
    pass


# ==============================================================================
# Environment Variable Reference
# ==============================================================================

"""
Required Environment Variables:

Development (.env):
--------------------
ENVIRONMENT=development
# CORS will use default localhost origins


Production (.env):
--------------------
ENVIRONMENT=production
FRONTEND_URL=https://app.example.com
BACKEND_URL=https://api.example.com

# OR use explicit list:
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com


Testing CORS:
-------------
# From frontend console:
fetch('http://localhost:8000/api/user123/tasks', {
    method: 'GET',
    credentials: 'include',  // REQUIRED for cookies/auth
    headers: {
        'Authorization': 'Bearer <token>'
    }
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error('CORS error:', err))


Common CORS Errors:
-------------------
1. "Access to fetch has been blocked by CORS policy"
   → Check allow_origins includes your frontend URL
   → Verify frontend URL matches exactly (http vs https, port, trailing slash)

2. "Credentials flag is 'true', but access control... is not '*'"
   → Set allow_credentials=True in CORS config

3. "Authorization header is missing"
   → Ensure allow_headers includes 'Authorization'
   → Check frontend includes credentials: 'include'

4. "Preflight request didn't succeed"
   → Add allow_methods=["*"] to allow all HTTP methods
   → Check OPTIONS requests are not blocked
"""
