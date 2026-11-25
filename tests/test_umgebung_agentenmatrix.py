"""Umgebung und Agentenmatrix (M5, Nutzerentscheid 25.11.2026)."""
from __future__ import annotations

import pytest

from app.core.umgebung import Umgebung, agenten_autonom, aktuelle_umgebung

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(("wert", "erwartet", "autonom"), [
    (None, Umgebung.PRODUCTION, False),          # nicht gesetzt: geschlossen
    ("", Umgebung.PRODUCTION, False),
    ("prod", Umgebung.PRODUCTION, False),        # unbekannt: geschlossen
    ("development", Umgebung.PRODUCTION, False),  # APP_ENV-Werte gelten hier nicht
    ("production", Umgebung.PRODUCTION, False),
    ("staging", Umgebung.STAGING, False),        # Spiegelbetrieb: Freigabe je Aktion
    ("local", Umgebung.LOCAL, True),
    ("LOCAL", Umgebung.LOCAL, True),
    ("ci", Umgebung.CI, True),
])
def test_umgebung_und_autonomie(monkeypatch, wert, erwartet, autonom):
    if wert is None:
        monkeypatch.delenv("VALEO_UMGEBUNG", raising=False)
    else:
        monkeypatch.setenv("VALEO_UMGEBUNG", wert)

    assert (aktuelle_umgebung(), agenten_autonom()) == (erwartet, autonom)


def test_agentenweg_folgt_der_umgebung(monkeypatch):
    from app.services import mcp_write_capability
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service

    monkeypatch.setattr(mcp_tool_registry_service, "get_tool", lambda _: {"write_capabilities": []})
    argumente = ("admin.rolle.anlegen.v1", "/api/v1/admin/rollen", "admin/rollen-verwaltung", "anlegen")

    monkeypatch.setenv("VALEO_UMGEBUNG", "local")
    lokal = mcp_write_capability.capability_enabled(*argumente)
    monkeypatch.setenv("VALEO_UMGEBUNG", "staging")
    staging = mcp_write_capability.capability_enabled(*argumente)
    monkeypatch.delenv("VALEO_UMGEBUNG", raising=False)
    ohne = mcp_write_capability.capability_enabled(*argumente)

    assert (lokal, staging, ohne) == (True, False, False)
