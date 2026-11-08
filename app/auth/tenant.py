"""Tenant identity derived exclusively from verified OIDC claims."""
from fastapi import Depends, Header, HTTPException
from app.auth.deps_oidc import get_current_user


def tenant_from_claims(raw: object) -> str | None:
    if not isinstance(raw, dict):
        return None
    candidates = [raw[key] for key in ("tenant_id", "mandanten_id") if key in raw]
    if any(not isinstance(v, str) or not v.strip() for v in candidates):
        return None
    values = {v.strip() for v in candidates}
    if any(len(v) > 64 or not v.isascii() or not v.isprintable() or any(c.isspace() for c in v) for v in values):
        return None
    return next(iter(values)) if len(values) == 1 else None


def get_verified_tenant_id(
    user: dict = Depends(get_current_user),
    tenant_header: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> str:
    tenant = tenant_from_claims(user.get("raw"))
    if not tenant or not isinstance(user.get("sub"), str) or not user["sub"].strip():
        raise HTTPException(403, "Verified subject and unambiguous tenant claims are required")
    if tenant_header is not None and tenant_header.strip() != tenant:
        raise HTTPException(403, "Tenant header does not match the verified token")
    return tenant
