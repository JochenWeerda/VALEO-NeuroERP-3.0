"""Shared helpers for Universal Mask Generator screen-summary payloads."""

from __future__ import annotations

from typing import Any


def paginate_tab_items(
    items: list[dict[str, Any]],
    *,
    page: int = 1,
    limit: int = 25,
    q: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    filtered = items
    if q:
        needle = q.casefold()
        filtered = [
            row
            for row in items
            if any(needle in str(value).casefold() for value in row.values())
        ]
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
) -> dict[str, Any]:
    paged_items, total = paginate_tab_items(items, page=page, limit=limit, q=q)
    return {
        "tab_key": tab_key,
        "table_key": table_key,
        "items": paged_items,
        "page": page,
        "limit": limit,
        "total": total,
    }
