"""
Tenant context helpers.
"""

from fastapi import Header

from app.core.config import settings
from app.core.tenant_context import get_current_tenant_id


def get_tenant_id(x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID")) -> str:
    """
    Resolve tenant from request header with configured default fallback.
    """
    tenant_id = (x_tenant_id or "").strip()
    return tenant_id or get_current_tenant_id() or settings.DEFAULT_TENANT_ID
