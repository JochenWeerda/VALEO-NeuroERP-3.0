"""
Tenant context helpers.
"""

from fastapi import Depends, HTTPException, Request
from app.core.security import require_bearer_token


def get_tenant_id(request: Request, token: str = Depends(require_bearer_token)) -> str:
    """
    Resolve only the server-verified identity, including on standalone routers.
    """
    if not getattr(request.state, "tenant_verified", False):
        raise HTTPException(403, "Verified tenant context required")
    return request.state.tenant_id
