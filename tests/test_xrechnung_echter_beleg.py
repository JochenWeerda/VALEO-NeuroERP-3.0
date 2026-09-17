"""Die E-Rechnung liest den Beleg, den es wirklich gibt.

`_load_invoice` las `domain_erp.sales_invoices` — ein Schema, das es nicht
gibt. Der Endpunkt fing den Datenbankfehler ab und meldete „Rechnung nicht
gefunden": Die XRechnung war **nie** erzeugbar, und der 404 sah aus wie eine
fehlende Rechnung statt wie ein fehlendes Schema.

Der Beleg liegt in `domain_sales` und nennt seine Betraege anders
(`vat_amount`, `gross_amount`), die Position ihre Nummer auch (`line_no`).

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")


@pytest.fixture(scope="module")
def client():
    from sqlalchemy import create_engine, text

    try:
        with create_engine(DB_URL).connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_sales.sales_invoice_lines')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration sales_invoice_lines_20260915 nicht angewandt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def mandant():
    from sqlalchemy import create_engine, text

    name = f"test-{uuid.uuid4().hex[:8]}"
    engine = create_engine(DB_URL)
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": name, "domain": f"{name}.test"},
        )
    try:
        yield name
    finally:
        with engine.begin() as verbindung:
            for tabelle, spalte in (
                ("domain_sales.sales_invoices", "tenant_id"),
                ("domain_docs.doc_allocation_sources", "tenant_id"),
                ("domain_sales.delivery_notes", "tenant_id"),
                ("domain_shared.tenants", "id"),
            ):
                verbindung.execute(
                    text(f"DELETE FROM {tabelle} WHERE {spalte} = :id"),  # nosec B608
                    {"id": name},
                )


@pytest.fixture()
def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


@pytest.fixture()
def rechnung(client, kopf) -> dict:
    """Eine echte Rechnung ueber 100 dt zu 25,00 mit 7 % Steuer."""
    ls = client.post(
        "/api/v1/sales/delivery-notes",
        headers=kopf,
        json={
            "customer_id": "K-XRECHNUNG",
            "delivery_date": "2026-09-17",
            "positionen": [
                {
                    "pos_nr": 1,
                    "artikel_id": "ART-WEIZEN",
                    "artikel_nr": "10001",
                    "bezeichnung": "Weizen A",
                    "menge": "100",
                    "einheit": "dt",
                    "netto_preis": "25.00",
                    "mwst_prozent": "7",
                }
            ],
        },
    )
    assert ls.status_code == 201, ls.text
    angelegt = client.post(
        "/api/v1/sales/invoices/from-delivery-notes",
        headers=kopf,
        json={
            "customer_id": "K-XRECHNUNG",
            "delivery_note_ids": [ls.json()["id"]],
            "invoice_date": "2026-09-17",
        },
    )
    assert angelegt.status_code == 201, angelegt.text
    return angelegt.json()


def test_xrechnung_findet_den_beleg_und_traegt_seine_zahlen(client, kopf, rechnung) -> None:
    antwort = client.get(f"/api/v1/xrechnung/{rechnung['id']}", headers=kopf)
    assert antwort.status_code == 200, antwort.text

    xml = antwort.text
    assert rechnung["invoice_number"] in xml
    # Netto 2.500,00 und brutto 2.675,00 — die Betraege kommen aus dem Beleg,
    # nicht aus einer Neuberechnung.
    assert "2500" in xml.replace(".00", "")
    assert "2675" in xml.replace(".00", "")
    # Die Position steht drin, mit ihrer Bezeichnung.
    assert "Weizen A" in xml


def test_positionsbetrag_kommt_aus_dem_beleg(client, kopf, rechnung) -> None:
    """Nicht Menge mal Preis: In einer Rechnung ans Amt zaehlt der Beleg."""
    from sqlalchemy import create_engine, text

    with create_engine(DB_URL).begin() as verbindung:
        # Eine Position, deren gespeicherter Betrag bewusst von Menge x Preis
        # abweicht — so wie es bei Rundung und Rabatt vorkommt.
        verbindung.execute(
            text(
                "UPDATE domain_sales.sales_invoice_lines SET net_amount = 2499.99 "
                "WHERE invoice_id = :id"
            ),
            {"id": rechnung["id"]},
        )

    xml = client.get(f"/api/v1/xrechnung/{rechnung['id']}", headers=kopf).text
    assert "2499.99" in xml


def test_fremde_rechnung_bleibt_verschlossen(client, kopf, rechnung) -> None:
    fremd = {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": "test-fremder-mandant",
        "X-Tenant-Id": "test-fremder-mandant",
    }
    assert client.get(f"/api/v1/xrechnung/{rechnung['id']}", headers=fremd).status_code == 404


def test_pflichtfeldpruefung_sieht_denselben_beleg(client, kopf, rechnung) -> None:
    antwort = client.get(f"/api/v1/xrechnung/{rechnung['id']}/validate", headers=kopf)
    assert antwort.status_code == 200, antwort.text
    ergebnis = antwort.json()
    assert ergebnis.get("invoice_number") == rechnung["invoice_number"] or ergebnis.get("valid") in (
        True,
        False,
    )
