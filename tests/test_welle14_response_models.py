"""SPEC-P1-06 Welle 14: TypedObjectOut drain — weak response_models → 0."""

from __future__ import annotations

import pytest

from app.api.v1.endpoints import kaeufergruppe as kaeufergruppe_module
from app.api.v1.endpoints import mobile_sync as mobile_sync_module
from app.api.v1.endpoints import process_map as process_map_module
from app.api.v1.schemas.base import TypedObjectOut

pytestmark = pytest.mark.unit

SAMPLE_MODULES = [kaeufergruppe_module, mobile_sync_module, process_map_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in getattr(route, "methods", []) or []:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = getattr(route, "response_model", None)
    return out


def test_typed_object_out_accepts_extra_keys_without_field_loss():
    payload = {
        "status": "ok",
        "count": 3,
        "nested": {"a": 1},
        "items": [{"id": "x"}],
        "unexpected_extra": True,
    }
    model = TypedObjectOut.model_validate(payload)
    dumped = model.model_dump()
    fehlend = [key for key in payload if key not in dumped]
    assert not fehlend, f"Feldverlust: {fehlend}"
    assert dumped["unexpected_extra"] is True
    assert dumped["nested"] == {"a": 1}


def test_weak_response_model_gate_is_zero():
    from scripts.check_weak_response_models import count_all

    total, _by_file, compat = count_all(include_compat_flex=True)
    assert total == 0, f"erwartete 0 schwache Typen, gefunden {total}"
    assert compat == 0, f"erwartete 0 CompatFlexOut, gefunden {compat}"


@pytest.mark.parametrize(
    "module", SAMPLE_MODULES, ids=lambda m: m.__name__.rsplit(".", 1)[-1]
)
def test_sample_modules_have_no_weak_response_models(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        if model is None:
            continue
        # Unwrap list[TypedObjectOut] / TypedObjectOut
        origin = getattr(model, "__origin__", None)
        args = getattr(model, "__args__", ())
        inner = args[0] if origin is list and args else model
        if model in (dict, list) or inner in (dict, list):
            schwach.append(f"{method} {path}: {model}")
            continue
        text = str(model)
        if "dict[str, Any]" in text or "Dict[str, Any]" in text or text in (
            "dict",
            "list",
        ):
            schwach.append(f"{method} {path}: {text}")
    assert not schwach, f"noch schwach typisiert: {schwach}"
