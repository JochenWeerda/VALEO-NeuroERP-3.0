"""Produktionsleitstand: Maskenaktionen als Kommando-Weg; Schreibwege mit Rolle und Urheber aus dem Token.

Bis zum 19.10.2026 hatte der Router keine Rollenpruefung (jede angemeldete Person schaltete Vorgaenge weiter)
und nahm den Urheber aus ``X-User-ID``. Gegen die Pruefstand-Datenbank.
"""
from __future__ import annotations

import pytest

from maskenkommando_pruefstand import Pruefstand, registriere

pytestmark = pytest.mark.integration

PS = Pruefstand(
    "pct",
    tabellen=("domain_ops.production_operation_audit", "domain_ops.production_operations"),
    probe_sql="SELECT 1 FROM domain_ops.production_operations LIMIT 0",
)
registriere(PS, globals())

MEISTER = ("meister-sub", "LAGER_BEARBEITEN")


def vorgang(client) -> str:
    PS.identitaet.als(*MEISTER)
    antwort = PS.post(client, "/api/v1/production-control/operations", operation_type="mill_run",
                      source_type="test", source_ref=f"M-{PS.haus_a}", source_number="M-1",
                      reason="Muehlenlauf im Test")
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


def aktion(client, kennung: str, key: str, haus: str | None = None, **extra):
    return PS.post(client, f"/api/v1/production-control/operations/{kennung}/actions/{key}", haus=haus,
                   **PS.auftrag(**extra))


def status(engine, kennung: str) -> str:
    return PS.wert(engine, "SELECT status FROM domain_ops.production_operations WHERE id = :id", id=kennung)


def test_lebenslauf_und_urheber(client, engine) -> None:
    kennung = vorgang(client)
    for key, ziel in (("release", "released"), ("start", "running"), ("mark_rework", "rework"), ("complete", "completed")):
        antwort = aktion(client, kennung, key).json()
        assert antwort["success"] is True, (key, antwort)
        assert status(engine, kennung) == ziel
    akteure = set(PS.wert(engine, "SELECT string_agg(DISTINCT actor, ',') FROM domain_ops.production_operation_audit "
                                  "WHERE operation_id = :id", id=kennung).split(","))
    assert akteure == {"meister-sub"}


def test_ohne_bearbeitungsrolle_kein_schreiben(client, engine) -> None:
    kennung = vorgang(client)
    PS.identitaet.als("leser-sub", "LAGER_LESEN")
    assert aktion(client, kennung, "release").status_code == 403
    assert PS.post(client, f"/api/v1/production-control/operations/{kennung}/transition",
                   target="released", reason="Ohne Rolle im Test").status_code == 403
    assert status(engine, kennung) == "queued"


def test_unerlaubter_uebergang_trockenlauf_fremder_mandant(client, engine) -> None:
    kennung = vorgang(client)
    assert aktion(client, kennung, "complete").json()["success"] is False
    trocken = aktion(client, kennung, "release", _mode="dryRun")
    assert trocken.json()["success"] is True and status(engine, kennung) == "queued"
    assert aktion(client, kennung, "release", haus=PS.haus_b).json()["success"] is False
    assert status(engine, kennung) == "queued"
