"""Regressionstests fuer die Paginierung neu begrenzter Listen (QG-GREEN-20260909).

Der Pagination-Ratchet in `scripts/check_pagination.py` zaehlt Dateien, nicht
Endpunkte: sobald irgendwo im Modul `skip`/`limit` vorkommt, gilt die Datei als
sauber. Diese Tests binden den Vertrag an die konkreten Endpunkte, damit die
Begrenzung nicht wieder still verschwindet und der Ratchet es nicht merkt.
"""
from __future__ import annotations

import pytest
from fastapi.routing import APIRoute

from main import app

pytestmark = pytest.mark.unit

# Pfad -> erwartete Obergrenze der Standard-Seitengroesse
PAGINIERTE_LISTEN = {
    "/api/v1/kostenrechnung/kostenstellen": 100,
    "/api/v1/kostenrechnung/kostenarten": 100,
    "/api/v1/kostenrechnung/buchungen": 100,
    "/api/v1/admin/devices": 100,
    "/api/v1/admin/device-mappings": 100,
    "/api/v1/admin/output-templates": 100,
    "/api/v1/admin/output-templates/{template_id}/versions": 100,
    "/api/v1/admin/output-profiles": 100,
}


def _get_route(pfad: str) -> APIRoute:
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == pfad and "GET" in route.methods:
            return route
    raise AssertionError(f"GET-Route nicht gefunden: {pfad}")


@pytest.mark.parametrize("pfad", sorted(PAGINIERTE_LISTEN))
def test_liste_bietet_limit_und_skip(pfad):
    namen = {p.name for p in _get_route(pfad).dependant.query_params}
    assert {"limit", "skip"} <= namen, f"{pfad} ohne Paginierungsparameter: {sorted(namen)}"


@pytest.mark.parametrize("pfad,standard", sorted(PAGINIERTE_LISTEN.items()))
def test_limit_hat_standard_und_obergrenze(pfad, standard):
    limit = next(p for p in _get_route(pfad).dependant.query_params if p.name == "limit")
    assert limit.default == standard
    # le=1000 verhindert, dass ein Aufrufer die Begrenzung praktisch aushebelt.
    obergrenzen = [m.le for m in limit.field_info.metadata if getattr(m, "le", None) is not None]
    assert obergrenzen == [1000], f"{pfad}: erwartet le=1000, gefunden {obergrenzen}"


@pytest.mark.parametrize("pfad", sorted(PAGINIERTE_LISTEN))
def test_skip_ist_nicht_negativ(pfad):
    skip = next(p for p in _get_route(pfad).dependant.query_params if p.name == "skip")
    assert skip.default == 0
    untergrenzen = [m.ge for m in skip.field_info.metadata if getattr(m, "ge", None) is not None]
    assert untergrenzen == [0], f"{pfad}: erwartet ge=0, gefunden {untergrenzen}"
