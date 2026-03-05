"""
OData v4 query adapter for FastAPI / SQLAlchemy.

Maps standard OData query parameters ($filter, $select, $top, $skip,
$orderby, $expand) to SQLAlchemy query modifiers.

Usage:
    from app.middleware.odata_adapter import apply_odata

    @router.get("/items")
    async def list_items(request: Request, db: Session = Depends(get_db)):
        q = db.query(ItemModel)
        q, meta = apply_odata(q, ItemModel, request.query_params,
                              allowed_fields={"name", "status", "amount"})
        return {"items": q.all(), **meta}
"""

from __future__ import annotations

import operator
from typing import Any

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query as SAQuery

# Supported OData comparison operators
_OPS = {
    "eq": operator.eq,
    "ne": operator.ne,
    "gt": operator.gt,
    "ge": operator.ge,
    "lt": operator.lt,
    "le": operator.le,
}

# Fields that must never be exposed via $filter/$select/$orderby
_BLOCKED_FIELDS = frozenset({
    "tenant_id", "deleted_at", "password_hash", "secret",
    "token", "api_key", "internal_notes",
})


def _parse_filter(model: Any, raw: str, allowed_fields: set[str] | None = None) -> list:
    """Parse a simple $filter expression into SQLAlchemy filter clauses.

    Supports:  field eq value, field ne value, etc.
    Does NOT support nested any()/all() – those require a full OData parser.
    """
    clauses = []
    parts = raw.split(" and ")
    for part in parts:
        part = part.strip()
        tokens = part.split()
        if len(tokens) < 3:
            continue
        field_name, op_str, *value_parts = tokens
        if field_name in _BLOCKED_FIELDS:
            continue
        if allowed_fields is not None and field_name not in allowed_fields:
            continue
        value_raw = " ".join(value_parts).strip("'\"")
        op_func = _OPS.get(op_str.lower())
        if op_func is None:
            continue
        col = getattr(model, field_name, None)
        if col is None:
            continue
        try:
            value: Any = int(value_raw)
        except ValueError:
            try:
                value = float(value_raw)
            except ValueError:
                value = value_raw
        clauses.append(op_func(col, value))
    return clauses


def _parse_orderby(model: Any, raw: str, allowed_fields: set[str] | None = None) -> list:
    """Parse $orderby into SQLAlchemy order_by clauses."""
    clauses = []
    for segment in raw.split(","):
        segment = segment.strip()
        parts = segment.split()
        field_name = parts[0]
        if field_name in _BLOCKED_FIELDS:
            continue
        if allowed_fields is not None and field_name not in allowed_fields:
            continue
        direction = parts[1].lower() if len(parts) > 1 else "asc"
        col = getattr(model, field_name, None)
        if col is None:
            continue
        clauses.append(desc(col) if direction == "desc" else asc(col))
    return clauses


def apply_odata(
    query: SAQuery,
    model: Any,
    params: dict[str, str] | Any,
    *,
    allowed_fields: set[str] | None = None,
) -> tuple[SAQuery, dict[str, Any]]:
    """Apply OData v4 query parameters to a SQLAlchemy query.

    Returns (modified_query, metadata_dict).
    metadata_dict contains keys like 'odata_top', 'odata_skip' for the caller.

    If *allowed_fields* is given, only those columns may be used in
    $filter, $orderby, and $select.  Fields in ``_BLOCKED_FIELDS``
    (e.g. ``tenant_id``) are always rejected regardless.
    """
    meta: dict[str, Any] = {}

    # Accept both dict and starlette QueryParams
    if hasattr(params, "get"):
        get = params.get
    else:
        get = dict(params).get  # type: ignore[arg-type]

    # $filter
    raw_filter = get("$filter") or get("filter")
    if raw_filter:
        clauses = _parse_filter(model, raw_filter, allowed_fields)
        for clause in clauses:
            query = query.filter(clause)

    # $orderby
    raw_order = get("$orderby") or get("orderby")
    if raw_order:
        clauses_order = _parse_orderby(model, raw_order, allowed_fields)
        for clause in clauses_order:
            query = query.order_by(clause)

    # $top
    raw_top = get("$top") or get("top")
    if raw_top:
        try:
            top = int(raw_top)
            query = query.limit(top)
            meta["odata_top"] = top
        except ValueError:
            pass

    # $skip
    raw_skip = get("$skip") or get("skip")
    if raw_skip:
        try:
            skip = int(raw_skip)
            query = query.offset(skip)
            meta["odata_skip"] = skip
        except ValueError:
            pass

    # $select – return validated column names so the caller can project
    raw_select = get("$select") or get("select")
    if raw_select:
        requested = [s.strip() for s in raw_select.split(",")]
        validated = [
            f for f in requested
            if f not in _BLOCKED_FIELDS
            and (allowed_fields is None or f in allowed_fields)
            and hasattr(model, f)
        ]
        if validated:
            meta["odata_select"] = validated

    # $select – apply projection if the caller requests it
    if meta.get("odata_select"):
        cols = []
        for field_name in meta["odata_select"]:
            col = getattr(model, field_name, None)
            if col is not None:
                cols.append(col)
        if cols:
            query = query.with_entities(*cols)
            meta["odata_projected"] = True

    # $expand – informational only (caller must handle joins)
    raw_expand = get("$expand") or get("expand")
    if raw_expand:
        meta["odata_expand"] = [s.strip() for s in raw_expand.split(",")]

    return query, meta
