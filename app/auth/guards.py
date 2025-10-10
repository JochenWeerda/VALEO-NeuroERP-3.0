"""
RBAC Guards für Endpoints
Scope-basierte Zugriffskontrolle
"""

from fastapi import HTTPException, Depends
from typing import List, Optional
from app.auth.oidc import get_current_user


def require_scopes(*required_scopes: str):
    """
    Decorator-Factory für Scope-basierte Zugriffskontrolle
    
    Usage:
        @router.post("/api/sales")
        async def create_order(
            data: OrderCreate,
            user: dict = Depends(require_scopes("sales:write"))
        ):
            ...
    
    Args:
        *required_scopes: Liste der erforderlichen Scopes (OR-verknüpft)
    
    Returns:
        FastAPI Dependency
    
    Raises:
        HTTPException 403: Wenn User nicht die erforderlichen Scopes hat
    """
    
    async def check_scopes(user: dict = Depends(get_current_user)) -> dict:
        """
        Prüft, ob User mindestens einen der erforderlichen Scopes hat
        """
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        
        # Admin hat immer alle Rechte
        user_scopes = user.get("scopes", [])
        if "admin:all" in user_scopes:
            return user
        
        # Prüfe, ob User mindestens einen der erforderlichen Scopes hat
        has_required_scope = any(
            scope in user_scopes
            for scope in required_scopes
        )
        
        if not has_required_scope:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {', '.join(required_scopes)}"
            )
        
        return user
    
    return check_scopes


def require_all_scopes(*required_scopes: str):
    """
    Decorator-Factory für Scope-basierte Zugriffskontrolle (AND-verknüpft)
    
    Usage:
        @router.post("/api/critical")
        async def critical_action(
            user: dict = Depends(require_all_scopes("sales:write", "sales:approve"))
        ):
            ...
    
    Args:
        *required_scopes: Liste der erforderlichen Scopes (AND-verknüpft)
    
    Returns:
        FastAPI Dependency
    
    Raises:
        HTTPException 403: Wenn User nicht ALLE erforderlichen Scopes hat
    """
    
    async def check_all_scopes(user: dict = Depends(get_current_user)) -> dict:
        """
        Prüft, ob User ALLE erforderlichen Scopes hat
        """
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        
        # Admin hat immer alle Rechte
        user_scopes = user.get("scopes", [])
        if "admin:all" in user_scopes:
            return user
        
        # Prüfe, ob User ALLE erforderlichen Scopes hat
        has_all_scopes = all(
            scope in user_scopes
            for scope in required_scopes
        )
        
        if not has_all_scopes:
            missing_scopes = [s for s in required_scopes if s not in user_scopes]
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Missing: {', '.join(missing_scopes)}"
            )
        
        return user
    
    return check_all_scopes


def optional_scopes(*required_scopes: str):
    """
    Optional Scope-Check (gibt None zurück wenn nicht authenticated)
    
    Usage:
        @router.get("/api/public")
        async def public_endpoint(
            user: Optional[dict] = Depends(optional_scopes("sales:read"))
        ):
            if user:
                # Authenticated user mit Scope
                ...
            else:
                # Public access
                ...
    
    Args:
        *required_scopes: Liste der erforderlichen Scopes
    
    Returns:
        User dict oder None
    """
    
    async def check_optional_scopes(user: Optional[dict] = Depends(get_current_user)) -> Optional[dict]:
        """
        Prüft Scopes, gibt aber None zurück statt 403
        """
        if not user:
            return None
        
        # Admin hat immer alle Rechte
        user_scopes = user.get("scopes", [])
        if "admin:all" in user_scopes:
            return user
        
        # Prüfe Scopes
        has_required_scope = any(
            scope in user_scopes
            for scope in required_scopes
        )
        
        if not has_required_scope:
            return None
        
        return user
    
    return check_optional_scopes

