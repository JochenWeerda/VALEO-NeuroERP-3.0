"""Canonical router mounts retain their paths and contracts exactly once."""
from collections import defaultdict
from importlib import import_module

import pytest
from fastapi.routing import APIRoute

from app.core.config import settings
from main import app

MOUNTS = [
    ("app.api.v1.endpoints.credit_debit_memos", ""),
    ("app.finance.router", ""),
    ("app.domains.inventory.api", "/inventory"),
    ("app.domains.agrar.api", "/agrar"),
    ("app.api.v1.endpoints.audit", "/audit"),
    ("app.api.v1.endpoints.gdpr", "/gdpr"),
    ("app.api.v1.endpoints.kontrakte", ""),
    ("app.api.v1.endpoints.quality_evidence", ""),
]


def dependency_calls(dependant):
    calls = set()
    for child in dependant.dependencies:
        calls.add(child.call)
        calls.update(dependency_calls(child))
    return calls


@pytest.mark.parametrize("module,prefix", MOUNTS)
def test_all_canonical_endpoints_keep_their_contract(module, prefix):
    expected = [r for r in import_module(module).router.routes if isinstance(r, APIRoute)]
    assert expected
    for route in expected:
        path = settings.API_V1_STR + prefix + route.path
        for method in route.methods:
            matches = [r for r in app.routes if isinstance(r, APIRoute)
                       and r.path == path and method in r.methods]
            assert len(matches) == 1, (method, path, len(matches))
            actual = matches[0]
            assert actual.endpoint is route.endpoint, (method, path)
            assert actual.response_model == route.response_model, (method, path)
            assert actual.status_code == route.status_code, (method, path)
            assert dependency_calls(route.dependant) <= dependency_calls(actual.dependant), (method, path)


def test_affected_modules_have_no_duplicate_method_paths():
    modules = {r.endpoint.__module__ for module, _ in MOUNTS
               for r in import_module(module).router.routes if isinstance(r, APIRoute)}
    grouped = defaultdict(list)
    for route in app.routes:
        if isinstance(route, APIRoute) and route.endpoint.__module__ in modules:
            for method in route.methods:
                grouped[(method, route.path)].append(route.endpoint.__qualname__)
    duplicates = {key: handlers for key, handlers in grouped.items() if len(handlers) > 1}
    assert duplicates == {}, duplicates
