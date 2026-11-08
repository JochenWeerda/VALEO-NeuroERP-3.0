"""Bound native ScreenDefinition list payloads by their published API limits."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from app.core.screen_definitions_listen import LISTEN_SCREEN_BUILDERS


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = REPO_ROOT / "docs" / "schnittstellen" / "openapi.json"
PAGINATION_QUERY_KEYS = {"limit", "page_size", "pagesize", "per_page", "take"}


def _openapi_path_for(paths: dict, endpoint_path: str) -> str | None:
    if endpoint_path in paths:
        return endpoint_path
    matching = [
        path
        for path in paths
        if re.fullmatch(re.sub(r"\{[^}]+\}", r"[^/]+", path), endpoint_path)
    ]
    return matching[0] if len(matching) == 1 else None


def test_registered_list_page_sizes_respect_published_openapi_maxima():
    """A registered list may not request more rows than its GET contract allows."""
    openapi = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
    paths = openapi["paths"]
    violations = []
    checked = set()

    for screen_id, builder in LISTEN_SCREEN_BUILDERS.items():
        screen = builder()
        for source in screen.get("dataSources", []):
            endpoint = source.get("endpoint", "")
            endpoint_path = urlsplit(endpoint).path
            api_path = _openapi_path_for(paths, endpoint_path)
            if api_path is None:
                continue
            operation = paths[api_path].get("get")
            if operation is None:
                continue

            page_size = source.get("pageSize")
            if not isinstance(page_size, int):
                continue

            for parameter in operation.get("parameters", []):
                if parameter.get("in") != "query" or parameter.get("name", "").lower() not in PAGINATION_QUERY_KEYS:
                    continue
                schema = parameter.get("schema", {})
                if "anyOf" in schema:
                    schema = next(
                        (option for option in schema["anyOf"] if option.get("type") == "integer"),
                        schema,
                    )
                maximum = schema.get("maximum")
                if isinstance(maximum, int):
                    checked.add((screen_id, source.get("key"), parameter["name"]))
                if isinstance(maximum, int) and page_size > maximum:
                    violations.append(
                        f"{screen_id}: {endpoint} pageSize={page_size} exceeds "
                        f"OpenAPI {parameter['name']} maximum={maximum}"
                    )

    assert len(checked) >= 15, "Expected declared API bounds were not checked"
    assert not violations, "\n".join(violations)
