"""Die Rechnungsendpunkte — der Weg, den die Maske geht.

Die Auskunft, auf die es ankommt, steht am Ende in `GET /sales/invoices/{id}`:
je Position die Menge **und ihre Herkunft**. Ohne sie steht in einer Rechnung
eine Zahl ohne Nachweis.

Die Sammelrechnung ist hier kein Sonderfall: Zwei Lieferscheine sind nur eine
laengere Quellenliste.

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


def lieferschein(client, kopf, menge: str = "100", preis: str = "25.00") -> str:
    antwort = client.post(
        "/api/v1/sales/delivery-notes",
        headers=kopf,
        json={
            "customer_id": "K-100",
            "delivery_date": "2026-09-15",
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
    return antwort.json()["id"]


def rechnung(client, kopf, *ls_ids: str):
    return client.post(
        "/api/v1/sales/invoices/from-delivery-notes",
        headers=kopf,
        json={
            "customer_id": "K-100",
            "delivery_note_ids": list(ls_ids),
            "invoice_date": "2026-09-15",
        },
    )


def test_rechnung_bekommt_positionen_und_die_position_ihre_herkunft(client, kopf) -> None:
    """Der Kern des Slices in einem Durchlauf."""
    ls_id = lieferschein(client, kopf)

    angelegt = rechnung(client, kopf, ls_id)
    assert angelegt.status_code == 201, angelegt.text
    assert angelegt.json()["lines"][0]["quantity"] == "100"

    gelesen = client.get(f"/api/v1/sales/invoices/{angelegt.json()['id']}", headers=kopf)
    assert gelesen.status_code == 200
    position = gelesen.json()["lines"][0]

    assert position["quantity"] == "100"
    assert position["unit"] == "dt"
    assert position["net_amount"] == "2500"
    herkunft = position["origins"][0]
    assert herkunft["source_document_type"] == "delivery_note"
    assert herkunft["source_document_id"] == ls_id
    assert herkunft["source_line_id"] == "1"
    assert herkunft["quantity"] == "100"


def test_sammelrechnung_ist_nur_eine_laengere_quellenliste(client, kopf) -> None:
    erster = lieferschein(client, kopf, "100")
    zweiter = lieferschein(client, kopf, "40")

    angelegt = rechnung(client, kopf, erster, zweiter)
    assert angelegt.status_code == 201, angelegt.text

    gelesen = client.get(f"/api/v1/sales/invoices/{angelegt.json()['id']}", headers=kopf).json()
    assert [z["quantity"] for z in gelesen["lines"]] == ["100", "40"]
    # Jede Position zeigt auf ihren eigenen Lieferschein.
    quellen = {z["origins"][0]["source_document_id"] for z in gelesen["lines"]}
    assert quellen == {erster, zweiter}
    assert gelesen["net_amount"] == "3500"


def test_zweimal_berechnen_wird_abgewiesen_statt_doppelt_gebucht(client, kopf) -> None:
    """Der Fehler, den ohne Restmengenfuehrung niemand bemerkt haette.

    Der Betrag der zweiten Rechnung waere fuer sich genommen richtig gewesen.
    """
    ls_id = lieferschein(client, kopf)
    assert rechnung(client, kopf, ls_id).status_code == 201

    zweite = rechnung(client, kopf, ls_id)
    assert zweite.status_code == 409
    assert "bereits vollstaendig berechnet" in zweite.json()["detail"]


def test_fremder_lieferschein_wird_nicht_berechnet(client, kopf) -> None:
    antwort = rechnung(client, kopf, "gibt-es-nicht")
    assert antwort.status_code == 404


def test_unbekannte_rechnung_meldet_404(client, kopf) -> None:
    assert client.get("/api/v1/sales/invoices/gibt-es-nicht", headers=kopf).status_code == 404


def test_liste_findet_die_rechnung_und_zaehlt_ihre_positionen(client, kopf) -> None:
    """Ohne Liste ist die Maske nur ueber eine Kennung erreichbar, die niemand hat."""
    ls_id = lieferschein(client, kopf)
    angelegt = rechnung(client, kopf, ls_id).json()

    antwort = client.get("/api/v1/sales/invoices", headers=kopf)
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()

    treffer = [z for z in daten["items"] if z["id"] == angelegt["id"]]
    assert len(treffer) == 1
    zeile = treffer[0]
    assert zeile["invoice_number"] == angelegt["invoice_number"]
    assert zeile["customer_id"] == "K-100"
    assert zeile["status"] == "entwurf"
    # Die Positionszahl beantwortet "sieht der Beleg leer aus", ohne ihn zu oeffnen.
    assert zeile["line_count"] == 1
    assert daten["total"] >= 1


def test_liste_zeigt_nur_die_rechnungen_des_eigenen_mandanten(client) -> None:
    """Mandantentrennung an der Liste — hier faellt sie am ehesten auf."""
    import uuid as _uuid

    from sqlalchemy import create_engine, text

    fremd = f"test-{_uuid.uuid4().hex[:8]}"
    engine = create_engine(DB_URL)
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": fremd, "domain": f"{fremd}.test"},
        )
    fremd_kopf = {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": fremd,
        "X-Tenant-Id": fremd,
    }
    try:
        ls_id = lieferschein(client, fremd_kopf)
        fremde = rechnung(client, fremd_kopf, ls_id).json()

        eigener = f"test-{_uuid.uuid4().hex[:8]}"
        with engine.begin() as verbindung:
            verbindung.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                    "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
                ),
                {"id": eigener, "domain": f"{eigener}.test"},
            )
        eigen_kopf = {
            "Authorization": "Bearer dev-token",
            "X-Tenant-ID": eigener,
            "X-Tenant-Id": eigener,
        }
        gelesen = client.get("/api/v1/sales/invoices", headers=eigen_kopf).json()
        assert fremde["id"] not in {z["id"] for z in gelesen["items"]}
        # Und einzeln ist sie auch nicht lesbar.
        assert client.get(
            f"/api/v1/sales/invoices/{fremde['id']}", headers=eigen_kopf
        ).status_code == 404
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
                    {"id": fremd},
                )


def test_liste_filtert_nach_nummer_status_und_zeitraum(client, kopf) -> None:
    ls_id = lieferschein(client, kopf)
    angelegt = rechnung(client, kopf, ls_id).json()
    nummer = angelegt["invoice_number"]

    # Teiltreffer, weil in der Praxis die letzten Stellen gesucht werden.
    gefunden = client.get(
        "/api/v1/sales/invoices", headers=kopf, params={"invoice_number": nummer[-4:]}
    ).json()
    assert angelegt["id"] in {z["id"] for z in gefunden["items"]}

    # Ein Status, den es hier nicht gibt, ergibt eine leere Liste — keinen Fehler.
    gebucht = client.get(
        "/api/v1/sales/invoices", headers=kopf, params={"status": "bezahlt"}
    ).json()
    assert angelegt["id"] not in {z["id"] for z in gebucht["items"]}

    # Zeitraum vor dem Rechnungsdatum: der Beleg faellt heraus.
    davor = client.get(
        "/api/v1/sales/invoices", headers=kopf, params={"date_to": "2026-09-14"}
    ).json()
    assert angelegt["id"] not in {z["id"] for z in davor["items"]}

    passend = client.get(
        "/api/v1/sales/invoices",
        headers=kopf,
        params={"date_from": "2026-09-15", "date_to": "2026-09-15"},
    ).json()
    assert angelegt["id"] in {z["id"] for z in passend["items"]}
