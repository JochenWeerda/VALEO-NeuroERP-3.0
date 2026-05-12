"""
Fast Track Classifier + Router — NC-E1/E2
Deterministischer Bypass fuer Standard-CRUD ohne AI-Overhead.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

FAST_TRACK_WHITELIST: set[str] = {
    "/api/v1/articles",
    "/api/v1/warehouses",
    "/api/v1/crm/customers",
    "/api/v1/crm/contacts",
    "/api/v1/crm/business-partners",
    "/api/v1/finance/chart-of-accounts",
    "/api/v1/compliance/registers",
    "/api/v1/config",
}

FAST_TRACK_PATTERNS: list[re.Pattern] = [
    re.compile(r"^/api/v1/articles/[^/]+$"),
    re.compile(r"^/api/v1/warehouses/[^/]+$"),
    re.compile(r"^/api/v1/crm/customers/[^/]+$"),
    re.compile(r"^/api/v1/crm/contacts/[^/]+$"),
]

NEVER_FAST_TRACK: set[str] = {
    "/api/v1/neuro/",
    "/api/v1/audit/",
    "/api/v1/finance/closing",
    "/api/v1/agrar/settlements",
}


def is_fast_track(method: str, path: str) -> bool:
    if method.upper() == "GET":
        if path in FAST_TRACK_WHITELIST:
            return True
        for pattern in FAST_TRACK_PATTERNS:
            if pattern.match(path):
                return True

    for blocked in NEVER_FAST_TRACK:
        if path.startswith(blocked):
            return False

    if method.upper() in ("POST", "PUT", "PATCH") and path in FAST_TRACK_WHITELIST:
        return True

    return False


def classify_request(method: str, path: str, has_ai_context: bool = False) -> dict:
    if has_ai_context:
        return {"route": "neuro-core", "reason": "AI context present"}

    if is_fast_track(method, path):
        return {"route": "fast-track", "reason": "Standard CRUD — kein AI-Overhead"}

    return {"route": "neuro-core", "reason": "Nicht in Fast-Track-Whitelist"}
