"""
Authentication Dependencies
FastAPI dependencies for JWT-based authentication and authorization
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import settings
from ..infrastructure.repositories import UserRepository
from ..core.dependency_container import container

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication exception"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization exception"""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate JWT token and return current user information
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        Dict with user_id, tenant_id, roles, and user details
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id", "default")
        roles: list = payload.get("roles", [])
        
        if user_id is None:
            logger.warning("Token missing subject (user_id)")
            raise AuthenticationError("Invalid token: missing user identifier")
        
        # Verify user exists in database
        user_repo = container.resolve(UserRepository)
        user = await user_repo.get_by_id(user_id, tenant_id)
        
        if not user:
            logger.warning(f"User not found in database: {user_id}")
            raise AuthenticationError("User not found")
        
        # Check if user is active
        if not getattr(user, 'is_active', True):
            logger.warning(f"User account is inactive: {user_id}")
            raise AuthenticationError("User account is inactive")
        
        logger.info(f"Authenticated user: {user_id} in tenant: {tenant_id}")
        
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "roles": roles,
            "user": user
        }
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise AuthenticationError("Authentication failed")


async def require_role(required_role: str):
    """
    Dependency factory for role-based authorization
    
    Args:
        required_role: Required role for endpoint access
        
    Returns:
        Dependency that enforces role requirements
    """
    async def role_checker(current_user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        
        if required_role not in user_roles and "admin" not in user_roles:
            logger.warning(
                f"Access denied for user {current_user['user_id']}: "
                f"requires role '{required_role}', has roles: {user_roles}"
            )
            raise AuthorizationError(f"Insufficient permissions: requires role '{required_role}'")
        
        return current_user
    
    return role_checker


async def require_any_role(allowed_roles: list):
    """
    Dependency factory for multiple role authorization
    
    Args:
        allowed_roles: List of allowed roles
        
    Returns:
        Dependency that enforces any-of-roles requirements
    """
    async def roles_checker(current_user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        
        # Admin role has access to everything
        if "admin" in user_roles:
            return current_user
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in allowed_roles):
            logger.warning(
                f"Access denied for user {current_user['user_id']}: "
                f"requires any of roles {allowed_roles}, has roles: {user_roles}"
            )
            raise AuthorizationError(f"Insufficient permissions: requires any of roles {allowed_roles}")
        
        return current_user
    
    return roles_checker


async def require_scopes(required_scopes: list):
    """
    Dependency factory for OAuth2 scope-based authorization
    
    Args:
        required_scopes: List of required scopes
        
    Returns:
        Dependency that enforces scope requirements
    """
    async def scope_checker(current_user: Dict[str, Any] = Depends(require_authenticated_user)) -> Dict[str, Any]:
        user_scopes = current_user.get("scopes", [])
        
        # Check if user has all required scopes
        if not all(scope in user_scopes for scope in required_scopes):
            logger.warning(
                f"Access denied for user {current_user['user_id']}: "
                f"requires scopes {required_scopes}, has scopes: {user_scopes}"
            )
            raise AuthorizationError(f"Insufficient permissions: requires scopes {required_scopes}")
        
        return current_user
    
    return scope_checker


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user info if valid token provided,
    returns None if no token or invalid token
    
    Args:
        credentials: Optional Bearer token
        db: Database session
        
    Returns:
        User info dict or None
    """
    if not credentials:
        return None
    
    try:
        return await require_authenticated_user(credentials, db)
    except AuthenticationError:
        # For optional auth, we just return None on auth failure
        return None