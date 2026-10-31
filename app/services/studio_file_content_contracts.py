"""Pure validation of bounded local UTF-8 file-content field declarations.

This metadata describes a browser input only. Domain commands must independently
validate their payloads; a valid declaration grants no upload or write permission.
Fields without a fileContent declaration retain their existing behavior.
"""
from __future__ import annotations

from typing import Any

MAX_FILE_CONTENT_BYTES = 1_048_576
_KEYS = frozenset({"encoding", "maxBytes", "accept"})
_EXTENSIONS = frozenset({".csv", ".txt"})


def _objects(value: Any):
    """Visit every JSON object, including nested action and table inputs."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects(child)


def validate_file_content_contracts(definition: Any) -> list[str]:
    """Reject malformed declarations without modifying their containing metadata."""
    violations: list[str] = []
    for node in _objects(definition):
        if "fileContent" not in node:
            continue
        contract = node["fileContent"]
        valid = (
            node.get("type") == "file"
            and isinstance(contract, dict)
            and set(contract) == _KEYS
            and contract["encoding"] == "utf-8"
            and type(contract["maxBytes"]) is int
            and 1 <= contract["maxBytes"] <= MAX_FILE_CONTENT_BYTES
            and isinstance(contract["accept"], list)
            and 1 <= len(contract["accept"]) <= len(_EXTENSIONS)
            and all(isinstance(item, str) and item in _EXTENSIONS for item in contract["accept"])
            and len(set(contract["accept"])) == len(contract["accept"])
        )
        if not valid:
            violations.append("fileContent is invalid")
    return violations
