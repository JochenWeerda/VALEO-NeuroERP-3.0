"""Source catalog of native definitions and static evidence; never a live approval record."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.studio_release import definition_hash

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config/studio_screen_versions.json"
_VERSION = re.compile(r"[1-9][0-9]*\.[0-9]+\.[0-9]+\Z")
_REQUIRED_GATES = ("A", "B", "C", "E")


def _read_raw() -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        return {"schemaVersion": 1, "releaseVersion": "0.0.0", "screens": {}}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _entry_release_ready(entry: dict[str, Any]) -> bool:
    return entry.get("gates_passed") == list(_REQUIRED_GATES) and entry.get("studio_draft_clean") is True


def _validate_entry(screen_id: str, entry: dict[str, Any], definition: dict[str, Any] | None) -> None:
    if not isinstance(entry, dict):
        raise ValueError("studio_screen_entry_invalid")
    version = entry.get("version")
    if not isinstance(version, str) or not _VERSION.fullmatch(version):
        raise ValueError("studio_screen_version_invalid")
    stamp = entry.get("definition_hash")
    if not isinstance(stamp, str) or len(stamp) != 64:
        raise ValueError("studio_screen_hash_invalid")
    gates = entry.get("gates_passed")
    if not isinstance(gates, list) or not all(isinstance(g, str) and g in _REQUIRED_GATES for g in gates):
        raise ValueError("studio_screen_gates_invalid")
    if not isinstance(entry.get("studio_draft_clean"), bool):
        raise ValueError("studio_screen_draft_invalid")
    if definition is not None and definition_hash(definition) != stamp:
        raise ValueError("studio_screen_hash_changed")


def check_registry(registry: dict[str, Any], *, definitions: dict[str, dict[str, Any]] | None = None) -> None:
    try:
        if registry.get("schemaVersion") != 1:
            raise ValueError("studio_screen_registry_invalid")
        release = registry.get("releaseVersion")
        if not isinstance(release, str) or not _VERSION.fullmatch(release):
            raise ValueError("studio_screen_release_invalid")
        screens = registry.get("screens")
        if not isinstance(screens, dict):
            raise ValueError("studio_screen_registry_invalid")
        for screen_id, entry in screens.items():
            if not isinstance(screen_id, str) or screen_id.startswith("beleg/"):
                raise ValueError("studio_screen_id_invalid")
            definition = definitions.get(screen_id) if definitions else None
            _validate_entry(screen_id, entry, definition)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("studio_screen_registry_invalid") from error


@lru_cache(maxsize=2)
def _read_registry(path: str, modified: int, size: int) -> dict[str, Any]:
    registry = json.loads(Path(path).read_text(encoding="utf-8"))
    check_registry(registry)
    return registry


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        return {"schemaVersion": 1, "releaseVersion": "0.0.0", "screens": {}}
    stat = REGISTRY_PATH.stat()
    return _read_registry(str(REGISTRY_PATH), stat.st_mtime_ns, stat.st_size)


def released_screen_ids() -> frozenset[str]:
    registry = load_registry()
    return frozenset(
        screen_id for screen_id, entry in registry.get("screens", {}).items() if _entry_release_ready(entry)
    )


def release_entry(screen_id: str) -> dict[str, Any]:
    registry = load_registry()
    try:
        return dict(registry["screens"][screen_id])
    except KeyError as error:
        raise ValueError("studio_screen_version_unknown") from error


def catalog_summary() -> dict[str, Any]:
    registry = load_registry()
    return {
        "releaseVersion": registry.get("releaseVersion"),
        "count": len(registry.get("screens") or {}),
    }


def current_matches(registry: dict[str, Any], definitions: dict[str, dict[str, Any]]) -> bool:
    """True when every native ScreenDefinition is catalogued with the current builder hash."""
    native = {sid: definition for sid, definition in definitions.items() if not sid.startswith("beleg/")}
    try:
        check_registry(registry, definitions=native)
    except ValueError:
        return False
    screens = registry.get("screens") or {}
    if set(screens) != set(native):
        return False
    for screen_id, definition in native.items():
        if definition_hash(definition) != screens[screen_id]["definition_hash"]:
            return False
    return True


def build_catalog_entry(
    definition: dict[str, Any],
    *,
    version: str,
    gates_passed: list[str],
    studio_draft_clean: bool,
) -> dict[str, Any]:
    return {
        "version": version,
        "definition_hash": definition_hash(definition),
        "gates_passed": [g for g in _REQUIRED_GATES if g in set(gates_passed)],
        "studio_draft_clean": studio_draft_clean,
    }
