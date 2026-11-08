"""Request-bound verified identity for internal tools; never populated from a body."""
from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Any
import time

from fastapi import HTTPException
from app.auth.oidc import extract_roles, extract_scopes


@dataclass(frozen=True)
class Principal:
    issuer: str
    tenant_id: str
    subject: str
    roles: frozenset[str]
    scopes: frozenset[str]
    claims: Mapping[str, Any] = field(repr=False)
    bearer: str = field(repr=False)


_identity: ContextVar[Principal | None] = ContextVar('verified_identity', default=None)


def set_current_identity(claims: dict, bearer: str) -> Token:
    from app.core.tenant_binding import checked_tenant
    return _identity.set(Principal(claims['iss'], checked_tenant(claims), claims['sub'],
        frozenset(extract_roles(claims)), frozenset(extract_scopes(claims)),
        MappingProxyType(dict(claims)), bearer))


def reset_current_identity(token: Token) -> None:
    _identity.reset(token)


def current_identity() -> Principal:
    principal = _identity.get()
    if principal is None:
        raise HTTPException(401, 'Verified execution identity required')
    if time.time() >= principal.claims['exp']:
        raise HTTPException(401, 'Execution identity expired')
    from app.core.identity_session import validate
    validate(dict(principal.claims), principal.bearer, touch=False)
    return principal
