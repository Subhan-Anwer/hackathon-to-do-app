"""
JWT Authentication Middleware for FastAPI

Provides JWT token verification using Better Auth tokens with proper
error handling, user data extraction, and security best practices.

Usage:
    from middleware.jwt import verify_jwt

    @router.get("/api/{user_id}/resource")
    async def get_resource(
        user_id: str,
        current_user: dict = Depends(verify_jwt),
    ):
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        # Fetch and return user's resource
"""

from fastapi import HTTPException, Header, Depends
from typing import Annotated, Optional
import jwt
import os
from datetime import datetime

# Load and validate environment variables
BETTER_AUTH_SECRET: Optional[str] = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is required. "
        "Set it in .env file and ensure it matches the frontend secret."
    )

if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError(
        f"BETTER_AUTH_SECRET must be at least 32 characters for security. "
        f"Current length: {len(BETTER_AUTH_SECRET)}"
    )

ALGORITHM = "HS256"  # HMAC with SHA-256 (matches Better Auth default)


class JWTBearer:
    """
    JWT authentication dependency for FastAPI routes.

    Verifies JWT tokens from Authorization header and returns user data.

    Returns:
        dict: User information with keys:
            - user_id (str): Unique user identifier from token 'sub' claim
            - email (str): User email address
            - exp (int): Token expiration timestamp

    Raises:
        HTTPException: 401 for missing, invalid, or expired tokens
        HTTPException: 500 for unexpected authentication errors
    """

    async def __call__(
        self,
        authorization: Annotated[str | None, Header()] = None
    ) -> dict:
        """
        Verify JWT token and return user data.

        Args:
            authorization: Authorization header value (format: "Bearer <token>")

        Returns:
            dict: {"user_id": str, "email": str, "exp": int}

        Raises:
            HTTPException: 401 for invalid/missing token, 500 for other errors
        """
        # Check for Authorization header
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Parse "Bearer <token>" format
            parts = authorization.split()

            if len(parts) != 2:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Authorization header format. Expected: 'Bearer <token>'",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            scheme, token = parts

            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid authentication scheme: '{scheme}'. Expected: 'Bearer'",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify and decode JWT
            payload = jwt.decode(
                token,
                BETTER_AUTH_SECRET,
                algorithms=[ALGORITHM]
            )

            # Extract user data from JWT payload
            user_id = payload.get("sub")  # Standard JWT claim for subject (user ID)
            email = payload.get("email")
            exp = payload.get("exp")  # Expiration timestamp

            # Validate required fields
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload: missing user ID (sub claim)"
                )

            # Return user data for use in route handlers
            return {
                "user_id": user_id,
                "email": email,
                "exp": exp,
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            # Covers InvalidSignatureError, DecodeError, etc.
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except ValueError as e:
            # Split or parsing errors
            raise HTTPException(
                status_code=401,
                detail=f"Malformed Authorization header: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            # Unexpected errors - log these but don't expose details
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected authentication error: {str(e)}", exc_info=True)

            raise HTTPException(
                status_code=500,
                detail="Authentication error occurred. Please try again."
            )


# Create reusable dependency instance
verify_jwt = JWTBearer()


def verify_user_access(url_user_id: str, current_user: dict) -> None:
    """
    Verify that the authenticated user matches the user_id in the URL path.

    This prevents users from accessing other users' resources by checking
    that the JWT token's user_id matches the user_id in the request URL.

    Args:
        url_user_id: User ID from URL path parameter
        current_user: User data from verify_jwt dependency

    Raises:
        HTTPException: 403 if user_id mismatch

    Example:
        @router.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: str,
            current_user: dict = Depends(verify_jwt),
        ):
            verify_user_access(user_id, current_user)
            # Continue with authorized request
    """
    if current_user["user_id"] != url_user_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "Access forbidden: You can only access your own resources. "
                f"Token user_id: {current_user['user_id']}, "
                f"Requested user_id: {url_user_id}"
            )
        )


def verify_resource_ownership(
    resource_user_id: str,
    current_user: dict,
    resource_name: str = "resource"
) -> None:
    """
    Verify that a resource belongs to the authenticated user.

    Use this after fetching a resource from the database to ensure
    the resource's user_id matches the authenticated user.

    Args:
        resource_user_id: The user_id field from the resource
        current_user: User data from verify_jwt dependency
        resource_name: Name of resource for error message (e.g., "task", "project")

    Raises:
        HTTPException: 403 if resource doesn't belong to user

    Example:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404)
        verify_resource_ownership(task.user_id, current_user, "task")
    """
    if resource_user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to access this {resource_name}"
        )
