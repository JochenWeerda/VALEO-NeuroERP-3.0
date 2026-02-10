"""
OData v4 query adapter for FastAPI / SQLAlchemy.

Maps standard OData query parameters ($filter, $select, $top, $skip,
$orderby, $expand) to SQLAlchemy query modifiers.

Usage:
    from app.middleware.odata_adapter import apply_odata

    @router.get("/items")
    async def list_items(request: Request, db: Session = Depends(get_db)):
        q = db.query(ItemModel)
        q, meta = apply_odata(q, ItemModel, request.query_params)
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


def _parse_filter(model: Any, raw: str) -> list:
    """Parse a simple $filter expression into SQLAlchemy filter clauses.

    Supports:  field eq value, field ne value, etc.
    Does NOT support nested any()/all() – those require a full OData parser.
    """
    clauses = []
    # Split on ' and ' (case-insensitive)
    parts = raw.split(" and ")
    for part in parts:
        part = part.strip()
        tokens = part.split()
        if len(tokens) < 3:
            continue
        field_name, op_str, *value_parts = tokens
        value_raw = " ".join(value_parts).strip("'\"")
        op_func = _OPS.get(op_str.lower())
        if op_func is None:
            continue
        col = getattr(model, field_name, None)
        if col is None:
            continue
        # Attempt numeric conversion
        try:
            value: Any = int(value_raw)
        except ValueError:
            try:
                value = float(value_raw)
            except ValueError:
                value = value_raw
        clauses.append(op_func(col, value))
    return clauses


def _parse_orderby(model: Any, raw: str) -> list:
    """Parse $orderby into SQLAlchemy order_by clauses."""
    clauses = []
    for segment in raw.split(","):
        segment = segment.strip()
        parts = segment.split()
        field_name = parts[0]
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
) -> tuple[SAQuery, dict[str, Any]]:
    """Apply OData v4 query parameters to a SQLAlchemy query.

    Returns (modified_query, metadata_dict).
    metadata_dict contains keys like 'odata_top', 'odata_skip' for the caller.
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
        clauses = _parse_filter(model, raw_filter)
        for clause in clauses:
            query = query.filter(clause)

    # $orderby
    raw_order = get("$orderby") or get("orderby")
    if raw_order:
        clauses_order = _parse_orderby(model, raw_order)
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

    # $select – we return the column names so the caller can project
    raw_select = get("$select") or get("select")
    if raw_select:
        meta["odata_select"] = [s.strip() for s in raw_select.split(",")]

    # $expand – informational only (caller must handle joins)
    raw_expand = get("$expand") or get("expand")
    if raw_expand:
        meta["odata_expand"] = [s.strip() for s in raw_expand.split(",")]

    return query, meta
