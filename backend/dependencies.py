"""Authentication dependencies for JWT validation.

This module provides the get_current_user dependency that validates JWT tokens
and extracts user_id from Better Auth tokens. Required on all protected endpoints.
"""
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
import os
import logging

logger = logging.getLogger(__name__)

# JWT configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

ALGORITHM = "HS256"  # Better Auth default algorithm


async def get_current_user(request: Request) -> str:
    """Extract and validate user_id from JWT token.

    Checks Authorization header or cookie for JWT token (Better Auth compatibility).
    Decodes token and extracts user_id claim.

    Security checks:
    - FR-001: JWT token validation required
    - FR-002: Extract user_id from token
    - FR-005: Return 401 on missing/invalid token
    - FR-017: Log authentication failures

    Returns:
        str: user_id from token 'sub' claim

    Raises:
        HTTPException 401: Missing or invalid token

    Example usage:
        @router.get("/tasks")
        async def list_tasks(
            current_user_id: str = Depends(get_current_user)
        ):
            # current_user_id is validated and extracted from JWT
            pass
    """
    # Try Authorization header first (Bearer token)
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to cookie (Better Auth httpOnly cookie)
        token = request.cookies.get("session")

    if not token:
        logger.warning("Authentication failed: No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - missing token"
        )

    try:
        # Decode JWT with Better Auth secret
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # Better Auth uses 'sub' claim for user_id

        if user_id is None:
            logger.warning("Authentication failed: Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing user_id"
            )

        logger.info(f"User authenticated: {user_id}")
        return user_id

    except JWTError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - verification failed"
        )
