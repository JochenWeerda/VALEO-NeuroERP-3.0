"""Regression guards for the 2026-06-25 runtime API error sweep
(RUNTIME-API-SWEEP-001).

Covers the response_model dict→list fixes (same bug class as the tapi bridge)
and the ``cached_read_model`` decorator signature-resolution fix that had broken
the entire OpenAPI/Swagger generation.
"""
from typing import Optional, get_origin

import pytest

pytestmark = pytest.mark.unit


def _list_response_routes(module_path: str):
    import importlib

    mod = importlib.import_module(module_path)
    return mod.router.routes


def _route_by_suffix(routes, suffix: str, method: str = "GET"):
    for r in routes:
        if getattr(r, "path", "").endswith(suffix) and method in getattr(r, "methods", set()):
            return r
    return None


def test_agri_silo_list_endpoints_return_list_response_model():
    routes = _list_response_routes("app.api.v1.endpoints.agri_silo_material_flow")
    for suffix in ("/silo-systems", "/silo-cells", "/material-flow/nodes", "/material-flow/edges"):
        route = _route_by_suffix(routes, suffix)
        assert route is not None, f"GET {suffix} nicht gefunden"
        assert get_origin(route.response_model) is list, (
            f"{suffix} muss list-response_model haben (gibt eine Liste zurück)"
        )


def test_warehouse_wms_list_endpoints_return_list_response_model():
    routes = _list_response_routes("app.api.v1.endpoints.warehouse_wms")
    for suffix in ("/bins", "/stock-valuation"):
        route = _route_by_suffix(routes, suffix)
        assert route is not None, f"GET {suffix} nicht gefunden"
        assert get_origin(route.response_model) is list, (
            f"{suffix} muss list-response_model haben (gibt eine Liste zurück)"
        )


def test_cached_read_model_resolves_string_annotations():
    """The decorator must expose a signature with *resolved* annotations so
    FastAPI does not try to evaluate forward refs against the decorator module's
    globals (which broke OpenAPI generation for Optional[...] params)."""
    import inspect

    from app.core.read_model_cache import cached_read_model

    @cached_read_model("test_prefix", ttl=1)
    def handler(flag: Optional[bool] = None, tenant_id: str = "x"):
        return []

    sig = inspect.signature(handler)
    flag_annotation = sig.parameters["flag"].annotation
    # Must be the real typing object, never the unresolved string "Optional[bool]".
    assert flag_annotation is Optional[bool]
    assert not isinstance(flag_annotation, str)
