"""
API authentication helpers.
Provides lightweight bearer-token enforcement that can be toggled via settings.
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

http_bearer = HTTPBearer(auto_error=False)


async def require_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> str:
    """
    Validate bearer token against configured development token.
    Returns the token string for downstream use.
    Raises HTTP 401 when validation fails.
    """
    if _is_path_exempt(request.url.path):
        return ""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = credentials.credentials.strip()
    expected = settings.API_DEV_TOKEN

    if expected and token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    return token


def _is_path_exempt(path: str) -> bool:
    """
    Determine whether the request path is exempt from authentication.
    """
    if not path.startswith("/api"):
        return True

    normalized = path.rstrip("/")
    return normalized in {p.rstrip("/") for p in settings.API_AUTH_EXEMPT_PATHS}
