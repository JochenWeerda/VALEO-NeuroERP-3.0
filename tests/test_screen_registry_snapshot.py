"""Das Abbild der ScreenDefinition-Registry fuer das Frontend ist aktuell.

``packages/frontend-web/src/masks/screen-registry.snapshot.json`` kommt aus der Python-Registry — der einen
Quelle. Der Frontend-Test ``capture-screens-sync.test.ts`` vergleicht die von Hand kopierten Definitionen
damit. Aendert jemand eine ScreenDefinition, ohne das Abbild neu zu erzeugen, wird es hier rot.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _modul():
    pfad = WURZEL / "scripts/generate_screen_registry_snapshot.py"
    spec = importlib.util.spec_from_file_location("generate_screen_registry_snapshot", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_das_abbild_ist_aktuell():
    modul = _modul()
    aktuell = modul.ZIEL.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert aktuell == modul.abbild(), "python scripts/generate_screen_registry_snapshot.py ausfuehren"


def test_das_abbild_traegt_keinen_agentenvertrag_und_jede_kennung_ist_registriert():
    from app.core.screen_definitions import _SCREEN_DEFINITIONS

    modul = _modul()
    daten = json.loads(modul.abbild())
    assert set(daten["exports"].values()) == set(daten["screens"])
    assert set(daten["screens"]) <= set(_SCREEN_DEFINITIONS)
    assert not [k for k, sd in daten["screens"].items() if "agentContract" in sd]
