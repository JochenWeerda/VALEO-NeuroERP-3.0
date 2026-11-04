"""Vertrag: Auswahloptionen der Masken entsprechen den Wertelisten der Kommandowege (Literal / ^(a|b)$)."""
from __future__ import annotations

from typing import Literal

import pytest
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.core.wertelisten_abgleich import abweichungen

pytestmark = pytest.mark.unit
#: Stand 02.11.2026: so viele Auswahlfelder vergleicht der Abgleich; sinkt sie, trifft er weniger Masken.
VERGLICHEN_MINDESTENS = 9


class _ProbeEingabe(BaseModel):
    """Modulebene: mit postponed annotations loest FastAPI lokale Klassen nicht auf."""
    art: Literal["post", "email"]
    kanal: str = Field(pattern=r"^(edi|fax)$")


def test_muster_selbsttest():
    """Der Abgleich findet beide Richtungen: Option ohne Serverwert und Serverwert ohne Option."""
    app = FastAPI()

    @app.post("/api/v1/probe")
    def probe(eingabe: _ProbeEingabe) -> None:  # pragma: no cover - nur Route
        return None

    definition = {"actions": [{"key": "senden", "commandEndpoint": "/api/v1/probe", "method": "POST", "inputFields": [
        {"key": "art", "type": "select", "options": [{"value": "post"}, {"value": "brief"}]},
        {"key": "kanal", "type": "select", "options": [{"value": "edi"}, {"value": "fax"}]},
    ]}]}
    funde = abweichungen(app, {"probe/maske": definition})
    assert funde == [{"screen": "probe/maske", "aktion": "senden", "feld": "art",
                      "nicht_erlaubt": ["brief"], "nicht_waehlbar": ["email"]}]


@pytest.fixture(scope="module")
def registrierte():
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

    ensure_stamm_screen_registry()
    return {sid: get_screen_definition(sid) or {} for sid in list(SCREEN_DEFINITION_BUILDERS)}


def test_masken_bieten_nur_serverwerte_an(registrierte):
    from main import app

    funde = abweichungen(app, registrierte)
    assert not funde, f"Auswahl weicht vom Kommandoweg ab: {funde}"


def test_abgleich_trifft_masken(registrierte, monkeypatch):
    """Zaehlt die verglichenen Felder ueber einen Fund je Feld (jede Option als fremd markiert)."""
    from main import app

    verfaelscht = {}
    for sid, d in registrierte.items():
        kopie = {**d, "actions": [{**a, "inputFields": [
            {**f, "options": [*(f.get("options") or []), {"value": "__probe__"}]} for f in a.get("inputFields") or []]}
            for a in d.get("actions") or []],
            "fields": [{**f, "options": [*(f.get("options") or []), {"value": "__probe__"}]} if f.get("options") else f
                       for f in d.get("fields") or []]}
        verfaelscht[sid] = kopie
    assert len(abweichungen(app, verfaelscht)) >= VERGLICHEN_MINDESTENS
