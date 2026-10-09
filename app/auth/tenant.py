"""Tenant identity derived exclusively from verified OIDC claims."""
from fastapi import Depends, Header, HTTPException
from app.auth.deps_oidc import get_current_user


def tenant_from_claims(raw: object) -> str | None:
    if not isinstance(raw, dict):
        return None
    values = {v.strip() for key in ("tenant_id", "mandanten_id")
              if isinstance(v := raw.get(key), str) and v.strip()}
    return next(iter(values)) if len(values) == 1 else None


def get_verified_tenant_id(
    user: dict = Depends(get_current_user),
    tenant_header: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> str:
    tenant = tenant_from_claims(user.get("raw"))
    if not tenant or not str(user.get("sub") or "").strip() or len(tenant) > 64:
        raise HTTPException(403, "Verified subject and unambiguous tenant claims are required")
    if tenant_header is not None and tenant_header.strip() != tenant:
        raise HTTPException(403, "Tenant header does not match the verified token")
    return tenant
