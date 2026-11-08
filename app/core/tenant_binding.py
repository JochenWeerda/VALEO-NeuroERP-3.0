"""Bind declared API tenant selectors to the authenticated request context."""
from __future__ import annotations

import json
import time
from functools import wraps
from typing import get_args, get_origin
from urllib.parse import urlencode, parse_qsl

from fastapi import HTTPException, Request
from fastapi.routing import APIRoute, request_response
from starlette.datastructures import FormData

from app.auth.tenant import tenant_from_claims

TENANT_FIELDS = frozenset({"tenant_id", "mandanten_id", "mandant_id", "x_tenant_id", "tenantId", "mandantenId", "mandantId"})
TENANT_LIST_FIELDS = frozenset({"tenant_ids", "mandanten_ids", "tenantIds", "mandantenIds"})
TENANT_HEADERS = frozenset({b"x-tenant-id", b"x-tenant"})


def _unambiguous_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise HTTPException(400, "Duplicate JSON fields are not allowed")
        result[key] = value
    return result


def checked_tenant(claims: object) -> str:
    if not isinstance(claims, dict):
        raise HTTPException(401, "Verified token claims required")
    tenant = tenant_from_claims(claims)
    if not tenant or not isinstance(claims.get("sub"), str) or not claims["sub"].strip():
        raise HTTPException(403, "Verified subject and unambiguous ERP tenant are required")
    from app.core.config import settings
    from app.core.security import _resolve_issuer
    issuer = _resolve_issuer()
    audience = settings.OIDC_CLIENT_ID or settings.KEYCLOAK_CLIENT_ID
    audiences = claims.get("aud")
    audiences = audiences if isinstance(audiences, list) else [audiences]
    expiry = claims.get("exp")
    if not issuer or not audience or claims.get("iss") != issuer or audience not in audiences:
        raise HTTPException(401, "Token issuer and audience must match the configured provider")
    if isinstance(expiry, bool) or not isinstance(expiry, (int, float)) or expiry <= time.time():
        raise HTTPException(401, "A valid token expiration is required")
    return tenant


def check_selector(value: object, tenant: str) -> None:
    if value is None:
        return
    values = value if isinstance(value, (tuple, list)) else [value]
    if not values or any(not isinstance(v, str) or v.strip() != tenant for v in values):
        raise HTTPException(403, "Requested tenant does not match the verified context")


def bind_headers(scope: dict, tenant: str) -> None:
    headers = list(scope.get("headers", []))
    for key, value in headers:
        if key.lower() in TENANT_HEADERS:
            check_selector(value.decode("latin-1"), tenant)
    scope["headers"] = [(k, v) for k, v in headers if k.lower() not in TENANT_HEADERS] + [
        (b"x-tenant-id", tenant.encode("ascii")), (b"x-tenant", tenant.encode("ascii"))]


def check_body_selectors(value: object, tenant: str) -> None:
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                if key in TENANT_FIELDS | TENANT_LIST_FIELDS:
                    check_selector(child, tenant)
                elif isinstance(child, (dict, list)):
                    pending.append(child)
        elif isinstance(current, list):
            pending.extend(child for child in current if isinstance(child, (dict, list)))


def _fill_declared_tenants(value: object, annotation: object, tenant: str) -> None:
    """Only fill fields actually declared by the route's request model."""
    origin = get_origin(annotation)
    if origin is list and isinstance(value, list):
        args = get_args(annotation)
        for child in value:
            _fill_declared_tenants(child, args[0] if args else None, tenant)
        return
    if origin is not None:
        for alternative in get_args(annotation):
            _fill_declared_tenants(value, alternative, tenant)
        return
    fields = getattr(annotation, "model_fields", None)
    if not fields or not isinstance(value, dict):
        return
    for name, field in fields.items():
        alias = field.alias or name
        if name in TENANT_FIELDS or alias in TENANT_FIELDS:
            check_selector(value.get(alias), tenant)
            value[alias] = tenant
        elif name in TENANT_LIST_FIELDS or alias in TENANT_LIST_FIELDS:
            check_selector(value.get(alias), tenant)
            value[alias] = [tenant]
        elif alias in value:
            _fill_declared_tenants(value[alias], field.annotation, tenant)


def _query_selectors(dependant) -> set[str]:
    result = {p.alias for p in dependant.query_params if p.alias in TENANT_FIELDS | TENANT_LIST_FIELDS}
    for dependency in dependant.dependencies:
        result.update(_query_selectors(dependency))
    return result


def _bound_handler(route: APIRoute, handler):
    declared_queries = _query_selectors(route.dependant)

    @wraps(handler)
    async def bound(request: Request):
        if not getattr(request.state, "tenant_verified", False):
            raise HTTPException(403, "Verified tenant context required before API access")
        tenant = request.state.tenant_id
        for name, value in request.path_params.items():
            if name in TENANT_FIELDS | TENANT_LIST_FIELDS:
                check_selector(value, tenant)
        query = parse_qsl(request.scope.get("query_string", b"").decode("ascii"), keep_blank_values=True)
        for name, value in query:
            if name in TENANT_FIELDS | TENANT_LIST_FIELDS:
                check_selector(value, tenant)
        supplied = {name for name, _ in query}
        query.extend((name, tenant) for name in declared_queries - supplied)
        request.scope["query_string"] = urlencode(query).encode("ascii")
        request.__dict__.pop("_query_params", None)
        request.__dict__.pop("_url", None)

        media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if media_type in ("", "application/json") or media_type.endswith("+json"):
            raw = await request.body()
            if raw:
                try:
                    body = json.loads(raw, object_pairs_hook=_unambiguous_object)
                except (ValueError, UnicodeError):
                    return await handler(request)  # FastAPI retains its normal invalid-JSON contract.
                except RecursionError as exc:
                    raise HTTPException(400, "Invalid structured request body") from exc
                check_body_selectors(body, tenant)
                if route.body_field is not None:
                    if route.body_field.alias in TENANT_FIELDS:
                        check_selector(body, tenant)
                        body = tenant
                    else:
                        _fill_declared_tenants(body, route.body_field.field_info.annotation, tenant)
                request._body = json.dumps(body, ensure_ascii=False).encode("utf-8")
                request._json = body
        elif media_type in ("multipart/form-data", "application/x-www-form-urlencoded") and route.body_field is not None:
            form = await request.form()
            try:
                items = list(form.multi_items())
                for name, value in items:
                    if name in TENANT_FIELDS | TENANT_LIST_FIELDS:
                        check_selector(value, tenant)
                fields = getattr(route.body_field.field_info.annotation, "model_fields", {})
                supplied = {name for name, _ in items}
                items.extend((f.alias or name, tenant) for name, f in fields.items()
                             if (name in TENANT_FIELDS or f.alias in TENANT_FIELDS)
                             and (f.alias or name) not in supplied)
                request._form = FormData(items)
            except HTTPException:
                await form.close()
                raise
        return await handler(request)

    return bound


def install_tenant_bindings(app, *, public_paths: set[str]) -> list[dict]:
    """Apply after router registration; fail closed at each protected HTTP route."""
    inventory = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path in public_paths:
            continue
        if not getattr(route, "tenant_bound", False):
            route.app = request_response(_bound_handler(route, route.get_route_handler()))
            route.tenant_bound = True
        inventory.append({"path": route.path, "methods": sorted(route.methods),
                          "query_selectors": sorted(_query_selectors(route.dependant))})
    app.state.tenant_binding_inventory = inventory
    return inventory
