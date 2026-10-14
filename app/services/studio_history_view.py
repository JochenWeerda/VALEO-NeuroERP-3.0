"""Read-only, type-preserving comparison of immutable Studio snapshots."""
import json

_MISSING = object()


def definition_diff(before, after, path=""):
    if isinstance(before, dict) and isinstance(after, dict):
        rows = []
        for key in sorted(before.keys() | after.keys()):
            rows.extend(definition_diff(before.get(key, _MISSING), after.get(key, _MISSING),
                                        path + "/" + key.replace("~", "~0").replace("/", "~1")))
        return rows
    encode = lambda value: "Nicht vorhanden" if value is _MISSING else json.dumps(value, sort_keys=True, ensure_ascii=False)
    old, new = encode(before), encode(after)
    return [] if old == new else [{"id": path or "/", "path": path or "/", "before": old, "after": new}]
