"""Deterministic screenshot filenames for Benutzerhandbuch routes."""

from __future__ import annotations

import re

ADMIN_PREFIXES = ("admin", "admin-suite", "api-docs", "mcp")
PLACEHOLDER = "demo-1"


def resolve_route_path(path: str) -> str:
    """Replace :param segments with demo placeholder for capture."""
    return re.sub(r":\w+|\{[^}]+\}", PLACEHOLDER, path or "")


def normalize_route_path(path: str) -> str:
    """Canonical path key (lowercase, no trailing slash)."""
    p = (path or "").strip().strip("/")
    return p.lower()


def route_to_img_slug(path: str) -> str:
    resolved = resolve_route_path(path)
    if not resolved:
        return "start-dashboard"
    slug = resolved.lower().replace("/", "__")
    slug = re.sub(r"[^a-z0-9_-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:140] or "route"


def is_admin_route(path: str) -> bool:
    p = normalize_route_path(path)
    return any(p == prefix or p.startswith(f"{prefix}/") for prefix in ADMIN_PREFIXES)


def is_capture_route(path: str) -> bool:
    if is_admin_route(path):
        return False
    # OIDC callback duplicates add no handbook value
    if normalize_route_path(path) in {"auth/callback", "auth/login"}:
        return False
    return True
