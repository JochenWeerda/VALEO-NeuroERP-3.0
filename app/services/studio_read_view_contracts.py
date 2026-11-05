"""Strict contracts for declarative related-row reads; grants no write access."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PATH = re.compile(r"^/api/v1/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\})(?:/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\}))*/?$")
_IDENTITY = re.compile(r"(?:^|_)(?:tenant|mandant|actor|user|agent)(?:_|$)", re.I)
_KINDS = {"text", "number", "currency", "date", "datetime", "status", "boolean", "quantity", "percentage"}


@lru_cache(maxsize=1)
def _openapi() -> dict:
    path = Path(__file__).resolve().parents[2] / "docs/schnittstellen/openapi.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _shape(path: str) -> str:
    return re.sub(r"\{[^{}]+\}", "{}", path.rstrip("/"))


def _row_fields(endpoint: str) -> set[str]:
    spec = _openapi()
    matches = [v.get("get") for k, v in spec.get("paths", {}).items() if _shape(k) == _shape(endpoint) and isinstance(v, dict) and "get" in v]
    if len(matches) != 1 or not isinstance(matches[0], dict):
        return set()
    schema = matches[0].get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema", {})
    if schema.get("type") != "array":
        return set()
    item = schema.get("items", {})
    ref = item.get("$ref", "")
    prefix = "#/components/schemas/"
    if ref.startswith(prefix):
        item = spec.get("components", {}).get("schemas", {}).get(ref[len(prefix):], {})
    return set(item.get("properties", {})) if isinstance(item, dict) else set()


def validate_read_view(action: dict[str, Any]) -> list[str]:
    if "readView" not in action:
        return []
    errors: list[str] = []
    view = action["readView"]
    if not isinstance(view, dict) or set(view) != {"endpoint", "columns"}:
        return ["readView_ungueltig"]
    endpoint, columns = view.get("endpoint"), view.get("columns")
    if (not isinstance(endpoint, str) or not _PATH.fullmatch(endpoint)
            or len(re.findall(r"\{([^{}]+)\}", endpoint)) > 1
            or any(_IDENTITY.search(p) for p in re.findall(r"\{([^{}]+)\}", endpoint))):
        errors.append("readView_endpoint_ungueltig")
        fields = set()
    else:
        fields = _row_fields(endpoint)
        if not fields:
            errors.append("readView_endpoint_nicht_registriert")
    if action.get("localEffect") != "view" or any(k in action for k in ("commandEndpoint", "download", "inputFlow", "commandBinding", "command")) or action.get("method", "GET") != "GET":
        errors.append("readView_aktionsvertrag_ungueltig")
    if not isinstance(columns, list) or not columns:
        return errors + ["readView_spalten_ungueltig"]
    keys = []
    for col in columns:
        if (not isinstance(col, dict) or not {"key", "label"} <= set(col) or set(col) - {"key", "label", "renderKind"}
                or not isinstance(col.get("key"), str) or not _IDENTIFIER.fullmatch(col["key"])
                or not isinstance(col.get("label"), str) or not col["label"].strip()
                or ("renderKind" in col and (not isinstance(col["renderKind"], str) or col["renderKind"] not in _KINDS))):
            errors.append("readView_spalte_ungueltig")
            continue
        keys.append(col["key"])
        if col["key"] not in fields:
            errors.append("readView_spalte_nicht_im_schema:" + col["key"])
    if len(keys) != len(set(keys)):
        errors.append("readView_spalte_doppelt")
    return errors
