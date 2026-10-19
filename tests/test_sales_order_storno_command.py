"""Auftrag stornieren als Kommando-Weg (Studio-Katalog ``stornieren``, MASK-COMMANDS-ROLLOUT-20261019).

Der Studio-Katalog versprach ``/sales/orders/{id}/actions/stornieren``; den Weg gab es nicht. Jetzt: derselbe
Zustandswechsel wie ``/cancel``, mit Verkaufsrolle, Begruendung, Trockenlauf und Wiederholungsschutz.
Gegen die Pruefstand-Datenbank.
"""
from __future__ import annotations

import uuid

import pytest

from maskenkommando_pruefstand import Pruefstand, registriere

pytestmark = pytest.mark.integration

PS = Pruefstand(
    "sot",
    tabellen=("domain_crm.sales_orders", "domain_crm.customers"),
    probe_sql="SELECT 1 FROM domain_crm.sales_orders LIMIT 0",
)
registriere(PS, globals())


def auftrag(engine, status: str = "confirmed") -> str:
    kunde, kennung = str(uuid.uuid4()), str(uuid.uuid4())
    PS.ausfuehren(engine, "INSERT INTO domain_crm.customers (id, tenant_id, customer_number) VALUES (:id, :h, :nr)",
                  id=kunde, h=PS.haus_a, nr=f"K-{kunde[:8]}")
    PS.ausfuehren(engine, "INSERT INTO domain_crm.sales_orders (id, tenant_id, customer_id, order_number, subject, "
                          "description, total_amount, currency, status, version) VALUES (:id, :h, :k, :nr, 'Test', 'Test', "
                          "0, 'EUR', :s, 1)", id=kennung, h=PS.haus_a, k=kunde, nr=f"A-{kennung[:8]}", s=status)
    return kennung


def status(engine, kennung: str) -> str:
    return PS.wert(engine, "SELECT status FROM domain_crm.sales_orders WHERE id = :id", id=kennung)


def test_stornieren_mit_rolle_begruendung_und_wiederholung(client, engine) -> None:
    kennung = auftrag(engine)
    pfad = f"/api/v1/sales/orders/{kennung}/actions/stornieren"
    PS.identitaet.als("einkauf-sub", "EINKAUF_BEARBEITEN")
    assert PS.post(client, pfad, **PS.auftrag()).status_code == 403
    PS.identitaet.als("verkauf-sub", "SALES_BEARBEITEN")
    assert PS.post(client, pfad, _idempotencyKey=str(uuid.uuid4())).json()["success"] is False  # ohne Begruendung
    assert PS.post(client, pfad, _mode="dryRun", _auditReason="Nur pruefen bitte").json()["success"] is True
    assert status(engine, kennung) == "confirmed"
    befehl = PS.auftrag("Kunde hat abbestellt")
    assert PS.post(client, pfad, **befehl).json()["success"] is True
    assert PS.post(client, pfad, **befehl).json()["success"] is True  # Wiederholung, keine zweite Wirkung
    assert status(engine, kennung) == "cancelled"
    assert PS.spuren(engine, PS.haus_a, "stornieren") == 1
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is False  # schon storniert


def test_abgeschlossen_und_fremder_mandant(client, engine) -> None:
    fertig = auftrag(engine, status="completed")
    offen = auftrag(engine)
    PS.identitaet.als("verkauf-sub", "SALES_BEARBEITEN")
    assert PS.post(client, f"/api/v1/sales/orders/{fertig}/actions/stornieren", **PS.auftrag()).json()["success"] is False
    fremd = PS.post(client, f"/api/v1/sales/orders/{offen}/actions/stornieren", haus=PS.haus_b, **PS.auftrag()).json()
    assert fremd["success"] is False
    assert status(engine, offen) == "confirmed"
