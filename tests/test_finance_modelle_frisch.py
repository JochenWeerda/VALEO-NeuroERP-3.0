"""Jedes Finanzmodell hat seine Tabelle auf einer frisch migrierten Datenbank (M3, 23.11.2026).

``app/finance/router.py`` fuehrte Wechselkurse, Buchungsschemata, Kostenstellen, Abschlusschecklisten,
Intercompany und die Nebenbuch-Abstimmung auf Tabellen, die keine Migration anlegte - nur ``create_all`` in der
gewachsenen Entwicklungsdatenbank. Auf einer frischen Installation scheiterte jeder dieser Wege. Die Altwege sind
entfernt, die Abstimmung hat ihre Migration; diese Pruefung haelt den Zustand.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

ENTFERNT = ("/api/v1/finance/wechselkurse", "/api/v1/finance/buchungsschemata", "/api/v1/finance/kostenstellen",
            "/api/v1/finance/checklisten", "/api/v1/finance/intercompany")


@pytest.mark.integration
def test_jedes_finanzmodell_hat_seine_tabelle_auf_dem_pruefstand():
    import app.finance.models as modelle
    from app.core.database import SessionLocal

    tabellen = {
        klasse.__table__.fullname
        for klasse in vars(modelle).values()
        if isinstance(klasse, type) and hasattr(klasse, "__table__") and klasse.__module__ == modelle.__name__
    }
    assert "nebenbuch_abstimmungen" in tabellen
    with SessionLocal() as db:
        fehlend = sorted(
            name for name in tabellen
            if not db.execute(text("SELECT to_regclass(:n)"), {"n": name if "." in name else f"public.{name}"}).scalar()
        )
    assert not fehlend, f"Modelle ohne Tabelle auf frischer Datenbank (Migration fehlt): {fehlend}"


def test_altwege_sind_nicht_mehr_eingebunden():
    from app.finance.router import router

    pfade = {route.path for route in router.routes}
    assert not [p for p in pfade for alt in ENTFERNT if p.startswith(alt.removeprefix("/api/v1"))]
    assert "/finance/abstimmung/nebenbuch/{id}/ausfuehren" in pfade
