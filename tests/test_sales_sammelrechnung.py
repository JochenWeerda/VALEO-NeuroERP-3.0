"""Die Sammelrechnung kommt im Mengenmodell an.

Vorher schrieb sie in ``domain_finance.finance_invoices`` — eine Tabelle, die
es nicht gibt. Der Fehler wurde als 503 „Datenbankfehler" ausgeliefert; eine
Sammelrechnung war damit **nie** moeglich. Dieselbe Tabelle las die
Kreditpruefung, um offene Forderungen zu summieren: Das Ergebnis war immer
null, also galt jeder Kunde als unbelastet.

Beides zeigt jetzt auf den echten Beleg (``domain_sales.sales_invoices``), und
die Sammelrechnung entsteht ueber denselben Dienst wie die Einzelrechnung —
Position fuer Position, Menge fuer Menge zugeordnet.

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


def lieferschein(client, kopf, menge: str, preis: str = "25.00") -> str:
    antwort = client.post(
        "/api/v1/sales/delivery-notes",
        headers=kopf,
        json={
            "customer_id": "K-SAMMEL",
            "delivery_date": "2026-09-17",
            "positionen": [
                {
                    "pos_nr": 1,
                    "artikel_id": "ART-WEIZEN",
                    "artikel_nr": "10001",
                    "bezeichnung": "Weizen A",
                    "menge": menge,
                    "einheit": "dt",
                    "netto_preis": preis,
                    "mwst_prozent": "7",
                }
            ],
        },
    )
    assert antwort.status_code == 201, antwort.text
    ls_id = antwort.json()["id"]
    gebucht = client.post(f"/api/v1/sales/delivery-notes/{ls_id}/post", headers=kopf)
    assert gebucht.status_code == 200, gebucht.text
    return ls_id


def sammelrechnung(client, kopf, *ls_ids: str):
    return client.post(
        "/api/v1/sales/collective-documents/collective-invoice",
        headers=kopf,
        json={
            "customer_id": "K-SAMMEL",
            "delivery_note_ids": list(ls_ids),
            "invoice_date": "2026-09-17",
        },
    )


def test_sammelrechnung_entsteht_mit_positionen_und_herkunft(client, kopf) -> None:
    """Zwei Lieferscheine, eine Rechnung — und jede Position weiss, woher sie kommt."""
    erster = lieferschein(client, kopf, "100")
    zweiter = lieferschein(client, kopf, "40")

    angelegt = sammelrechnung(client, kopf, erster, zweiter)
    assert angelegt.status_code == 201, angelegt.text
    daten = angelegt.json()
    # 140 dt zu 25,00 = 3.500 netto, dazu 7 % — die Rechnung fuehrt brutto.
    assert daten["total_amount"] == pytest.approx(3745.0, abs=0.01)

    gelesen = client.get(f"/api/v1/sales/invoices/{daten['id']}", headers=kopf)
    assert gelesen.status_code == 200, gelesen.text
    beleg = gelesen.json()
    assert [z["quantity"] for z in beleg["lines"]] == ["100", "40"]
    quellen = {z["origins"][0]["source_document_id"] for z in beleg["lines"]}
    assert quellen == {erster, zweiter}


def test_quell_lieferscheine_gelten_danach_als_berechnet(client, kopf) -> None:
    ls_id = lieferschein(client, kopf, "100")
    assert sammelrechnung(client, kopf, ls_id).status_code == 201

    gelesen = client.get(f"/api/v1/sales/delivery-notes/{ls_id}", headers=kopf)
    assert gelesen.status_code == 200
    assert gelesen.json()["status"] == "BERECHNET"


def test_zweimal_sammeln_wird_abgewiesen(client, kopf) -> None:
    """Der Beleg ist berechnet — ein zweiter Lauf ist eine Lage, kein Absturz."""
    ls_id = lieferschein(client, kopf, "100")
    assert sammelrechnung(client, kopf, ls_id).status_code == 201

    zweite = sammelrechnung(client, kopf, ls_id)
    assert zweite.status_code == 409
    assert "bereits berechnet" in zweite.json()["detail"]


def test_entwurf_wird_nicht_abgerechnet(client, kopf) -> None:
    antwort = client.post(
        "/api/v1/sales/delivery-notes",
        headers=kopf,
        json={
            "customer_id": "K-SAMMEL",
            "delivery_date": "2026-09-17",
            "positionen": [
                {
                    "pos_nr": 1,
                    "artikel_id": "ART-WEIZEN",
                    "artikel_nr": "10001",
                    "bezeichnung": "Weizen A",
                    "menge": "10",
                    "einheit": "dt",
                    "netto_preis": "25.00",
                    "mwst_prozent": "7",
                }
            ],
        },
    )
    entwurf = antwort.json()["id"]

    abgewiesen = sammelrechnung(client, kopf, entwurf)
    assert abgewiesen.status_code == 422
    assert "herausgegebener Beleg" in abgewiesen.json()["detail"]


def test_gelesene_sammelrechnung_nennt_ihre_quellbelege(client, kopf) -> None:
    erster = lieferschein(client, kopf, "100")
    zweiter = lieferschein(client, kopf, "40")
    rechnungs_id = sammelrechnung(client, kopf, erster, zweiter).json()["id"]

    gelesen = client.get(
        f"/api/v1/sales/collective-documents/collective-invoice/{rechnungs_id}",
        headers=kopf,
    )
    assert gelesen.status_code == 200, gelesen.text
    # Die Quellbelege stehen nicht mehr als JSON-Liste am Kopf, sondern
    # ergeben sich aus den Mengenzuordnungen.
    assert set(gelesen.json()["source_document_ids"]) == {erster, zweiter}


def test_kreditpruefung_sieht_die_offene_forderung(client, kopf) -> None:
    """Der Fehler, der niemandem auffiel: Die Summe war immer null.

    Gelesen wurde eine Tabelle, die es nicht gibt — jeder Kunde galt als
    unbelastet, egal wie viel offen war.
    """
    from sqlalchemy import create_engine, text

    ls_id = lieferschein(client, kopf, "100")
    rechnungs_id = sammelrechnung(client, kopf, ls_id).json()["id"]

    # Die Rechnung entsteht als Entwurf. Ein Entwurf ist keine Forderung ...
    vorher = client.get(
        "/api/v1/sales/credit-management/customers/K-SAMMEL/credit-status", headers=kopf
    )
    if vorher.status_code == 404:
        pytest.skip("Kreditpruefung nicht unter diesem Pfad erreichbar")
    assert vorher.status_code == 200, vorher.text
    # `current_exposure` ist die Summe aus offenen Rechnungen und offenen
    # Auftraegen. Ein Entwurf zaehlt in keiner der beiden.
    assert float(vorher.json()["current_exposure"]) == 0.0

    # ... eine gebuchte Rechnung schon.
    with create_engine(DB_URL).begin() as verbindung:
        verbindung.execute(
            text("UPDATE domain_sales.sales_invoices SET status = 'gebucht' WHERE id = :id"),
            {"id": rechnungs_id},
        )

    nachher = client.get(
        "/api/v1/sales/credit-management/customers/K-SAMMEL/credit-status", headers=kopf
    )
    assert nachher.status_code == 200
    assert float(nachher.json()["current_exposure"]) == pytest.approx(2675.0, abs=0.01)
