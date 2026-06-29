"""Shared helpers for Universal Mask Generator screen-summary payloads."""

from __future__ import annotations

from typing import Any


def _get_tab_columns(screen_id: str, tab_key: str) -> list[dict[str, Any]]:
    from app.core.screen_definitions import get_screen_definition  # lazy import

    definition = get_screen_definition(screen_id)
    if definition is None:
        return []
    for tab in definition.get("tabs", []):
        if tab.get("key") != tab_key:
            continue
        cols: list[dict[str, Any]] = []
        for table in tab.get("tables", []):
            cols.extend(table.get("columns", []))
        return cols
    return []


def get_sortable_columns(screen_id: str, tab_key: str) -> frozenset[str]:
    """Returns the set of sortable column keys for a tab from the ScreenDefinition."""
    return frozenset(col["key"] for col in _get_tab_columns(screen_id, tab_key) if col.get("sortable"))


def get_filterable_columns(screen_id: str, tab_key: str) -> frozenset[str]:
    """Returns the set of filterable column keys for a tab from the ScreenDefinition.

    FilterPlan keys are validated against this set — unknown columns are silently dropped.
    """
    return frozenset(col["key"] for col in _get_tab_columns(screen_id, tab_key) if col.get("filterable"))


def _apply_filter_plan(
    items: list[dict[str, Any]],
    filter_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    """Apply structured FilterPlan to items. Unknown operators are silently ignored."""
    result = items
    for col_key, spec in filter_plan.items():
        op = spec.get("op", "eq")
        val = spec.get("value")
        if val is None:
            continue
        if op == "eq":
            result = [r for r in result if r.get(col_key) == val]
        elif op == "neq":
            result = [r for r in result if r.get(col_key) != val]
        elif op == "contains":
            needle = str(val).casefold()
            result = [r for r in result if needle in str(r.get(col_key, "")).casefold()]
        elif op == "lt":
            result = [r for r in result if r.get(col_key) is not None and r.get(col_key) < val]
        elif op == "lte":
            result = [r for r in result if r.get(col_key) is not None and r.get(col_key) <= val]
        elif op == "gt":
            result = [r for r in result if r.get(col_key) is not None and r.get(col_key) > val]
        elif op == "gte":
            result = [r for r in result if r.get(col_key) is not None and r.get(col_key) >= val]
        elif op == "in":
            if isinstance(val, list):
                result = [r for r in result if r.get(col_key) in val]
        elif op == "between":
            if isinstance(val, list) and len(val) == 2:
                lo, hi = val
                result = [
                    r for r in result
                    if r.get(col_key) is not None and lo <= r.get(col_key) <= hi
                ]
    return result


def paginate_tab_items(
    items: list[dict[str, Any]],
    *,
    page: int = 1,
    limit: int = 25,
    q: str | None = None,
    sort: str | None = None,
    sort_dir: str | None = None,
    allowed_sort_columns: frozenset[str] | None = None,
    filter_plan: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    filtered = items
    if q:
        needle = q.casefold()
        filtered = [
            row
            for row in items
            if any(needle in str(value).casefold() for value in row.values())
        ]
    if filter_plan:
        filtered = _apply_filter_plan(filtered, filter_plan)
    # Sort — only against whitelisted columns
    if sort and (allowed_sort_columns is None or sort in allowed_sort_columns):
        reverse = (sort_dir or "asc") == "desc"
        filtered = sorted(
            filtered,
            key=lambda row: (row.get(sort) is None, row.get(sort)),
            reverse=reverse,
        )
    safe_limit = max(1, min(limit, 50))
    safe_page = max(1, page)
    start = (safe_page - 1) * safe_limit
    return filtered[start : start + safe_limit], len(filtered)


def format_optional_date(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def tab_endpoint(api_prefix: str, entity_id: str, tab_key: str) -> str:
    return f"{api_prefix.rstrip('/')}/{entity_id}/tabs/{tab_key}"


def build_screen_summary_payload(
    *,
    screen_id: str,
    entity_id: str,
    tenant_id: str,
    title: str,
    subtitle: str | None,
    summary: dict[str, Any],
    available_tabs: list[str],
    api_prefix: str,
    lazy_tab_keys: list[str] | None = None,
    actions: list[dict[str, str]] | None = None,
    initial_payload_budget_kb: int = 56,
    entity_key: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lazy_keys = lazy_tab_keys or [tab for tab in available_tabs if tab != "kopf"]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "screen_id": screen_id,
        entity_key or f"{screen_id.split('/')[-1]}_id": entity_id,
        "tenant_id": tenant_id,
        "title": title,
        "subtitle": subtitle,
        "summary": summary,
        "available_tabs": available_tabs,
        "tab_endpoints": {
            tab_key: tab_endpoint(api_prefix, entity_id, tab_key) for tab_key in lazy_keys
        },
        "actions": actions or [],
        "performance": {
            "initial_payload_budget_kb": initial_payload_budget_kb,
            "tabs_lazy": True,
            "lookup_min_chars": 2,
            "default_table_limit": 25,
        },
    }
    if extra:
        payload.update(extra)
    return payload


def build_tab_page(
    *,
    tab_key: str,
    table_key: str,
    items: list[dict[str, Any]],
    page: int,
    limit: int,
    q: str | None = None,
    sort: str | None = None,
    sort_dir: str | None = None,
    screen_id: str | None = None,
    filter_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    allowed_sort = get_sortable_columns(screen_id, tab_key) if screen_id else None
    # Restrict filterPlan to only filterable columns
    safe_filter_plan: dict[str, Any] | None = None
    if filter_plan and screen_id:
        allowed_filter = get_filterable_columns(screen_id, tab_key)
        if allowed_filter:
            safe_filter_plan = {k: v for k, v in filter_plan.items() if k in allowed_filter}
        else:
            safe_filter_plan = filter_plan  # no whitelist defined → pass through
    elif filter_plan:
        safe_filter_plan = filter_plan
    paged_items, total = paginate_tab_items(
        items, page=page, limit=limit, q=q,
        sort=sort, sort_dir=sort_dir, allowed_sort_columns=allowed_sort,
        filter_plan=safe_filter_plan,
    )
    return {
        "tab_key": tab_key,
        "table_key": table_key,
        "items": paged_items,
        "page": page,
        "limit": limit,
        "total": total,
    }
