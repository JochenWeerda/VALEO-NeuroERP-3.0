"""Read-only, type-preserving comparison of immutable Studio snapshots."""
import json

_MISSING = object()


def _encode(value):
    return "Nicht vorhanden" if value is _MISSING else json.dumps(value, sort_keys=True, ensure_ascii=False)


def definition_diff(before, after, path=""):
    # New/removed nonempty containers are expanded; an empty container remains a real value.
    if before is _MISSING and isinstance(after, (dict, list)) and after:
        before = {} if isinstance(after, dict) else []
    if after is _MISSING and isinstance(before, (dict, list)) and before:
        after = {} if isinstance(before, dict) else []
    if isinstance(before, dict) and isinstance(after, dict):
        rows = []
        for key in sorted(before.keys() | after.keys()):
            rows.extend(definition_diff(before.get(key, _MISSING), after.get(key, _MISSING),
                                        path + "/" + key.replace("~", "~0").replace("/", "~1")))
        return rows
    if isinstance(before, list) and isinstance(after, list):
        rows = []
        for index in range(max(len(before), len(after))):
            rows.extend(definition_diff(before[index] if index < len(before) else _MISSING,
                                        after[index] if index < len(after) else _MISSING,
                                        path + "/" + str(index)))
        return rows
    old, new = _encode(before), _encode(after)
    return [] if old == new else [{"id": path or "/", "path": path or "/", "before": old, "after": new}]
