"""Hilfsfunktionen für API-Responses."""

from __future__ import annotations

from typing import Any, Dict


def build_response(data: Any, *, source: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    base_meta = {"source": source}
    if meta:
        base_meta.update(meta)
    return {"data": data, "meta": base_meta}


