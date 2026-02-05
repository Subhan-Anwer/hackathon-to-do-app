# middleware/jwt.py - FastAPI JWT Verification Middleware
from fastapi import HTTPException, Header
import jwt
import os

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise RuntimeError("BETTER_AUTH_SECRET environment variable not set")


async def verify_jwt(authorization: str = Header(None)) -> dict:
    """
    Verify JWT token and return user data.

    Args:
        authorization: Authorization header in format "Bearer <token>"

    Returns:
        dict: User data containing user_id and email

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Expected 'Bearer <token>'"
            )

        token = parts[1]

        # Verify and decode JWT
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user data
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID"
            )

        return {
            "user_id": user_id,
            "email": email,
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )


def verify_user_access(requested_user_id: str, authenticated_user: dict):
    """
    Verify that the authenticated user has access to the requested resource.

    Args:
        requested_user_id: User ID from the URL/request
        authenticated_user: User data from verify_jwt()

    Raises:
        HTTPException: If user IDs don't match
    """
    if authenticated_user["user_id"] != requested_user_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You don't have access to this resource"
        )
