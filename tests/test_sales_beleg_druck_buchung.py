"""Drucken und Buchen fuer Auftrag und Angebot.

Beide Masken riefen diesen Weg seit jeher — es gab ihn nicht. Der 404 landete
im ``catch`` und wurde als „Fehler beim Drucken" gemeldet, ohne zu sagen, dass
der Endpunkt selbst fehlt.

Geprueft wird die fachliche Aussage, nicht die Technik:

- Der **zweite** Druck ist ein eigener Vorgang und wird gezaehlt, nicht
  ueberschrieben — und er verlangt eine Begruendung.
- **Zweimal buchen ist kein Fehler.** Die Maske druckt und bucht in einem Zug;
  wer ein zweites Exemplar druckt, bucht dabei erneut.
- Ein **stornierter** Auftrag laesst sich nicht buchen, und ein abgelehntes
  Angebot faellt nicht auf „versendet" zurueck.

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
            spalten = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='domain_crm' AND table_name='sales_orders'"
                )
            ).fetchall()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if "print_count" not in {r[0] for r in spalten}:
        pytest.skip("Migration sales_beleg_druck_buchung_20260917 nicht angewandt")

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
            for tabelle in (
                "domain_crm.sales_order_items",
                "domain_crm.sales_orders",
                "domain_crm.sales_offer_items",
                "domain_crm.sales_offers",
            ):
                verbindung.execute(
                    text(f"DELETE FROM {tabelle} WHERE tenant_id = :id"),  # nosec B608
                    {"id": name},
                )
            verbindung.execute(
                text("DELETE FROM domain_shared.tenants WHERE id = :id"), {"id": name}
            )


@pytest.fixture()
def kunde(mandant: str) -> str:
    """Ein echter Kunde — der Auftrag prueft die Kennung gegen den Stamm."""
    from sqlalchemy import create_engine, text

    kunden_id = str(uuid.uuid4())
    with create_engine(DB_URL).begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                "VALUES (:id, :tid, :nr, :name)"
            ),
            {
                "id": kunden_id,
                "tid": mandant,
                "nr": f"K-{uuid.uuid4().hex[:6].upper()}",
                "name": "Testkunde Drucktest",
            },
        )
    try:
        yield kunden_id
    finally:
        with create_engine(DB_URL).begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.customers WHERE id = :id"), {"id": kunden_id}
            )


@pytest.fixture()
def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


def auftrag(client, kopf, kunde) -> str:
    antwort = client.post(
        "/api/v1/sales/orders/",
        headers=kopf,
        json={
            "customer_id": kunde,
            "customer_name": "Testkunde",
            "subject": "Drucktest",
            "total_amount": 100,
            "currency": "EUR",
            "items": [
                {
                    "line_number": 1,
                    "article_number": "10001",
                    "description": "Weizen A",
                    "quantity": 1,
                    "unit_price": 100,
                    "discount_percent": 0,
                }
            ],
        },
    )
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


def angebot(client, kopf, kunde) -> str:
    antwort = client.post(
        "/api/v1/sales/offers/",
        headers=kopf,
        json={
            "offer_number": f"AN-{uuid.uuid4().hex[:6].upper()}",
            "customer_id": kunde,
            "customer_name": "Testkunde",
            "subject": "Drucktest",
            "total_amount": 100,
            "currency": "EUR",
            "status": "entwurf",
            "items": [
                {
                    "line_number": 1,
                    "article_number": "10001",
                    "description": "Weizen A",
                    "quantity": 1,
                    "unit_price": 100,
                    "discount_percent": 0,
                }
            ],
        },
    )
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


# ── Auftrag ────────────────────────────────────────────────────────────────


def test_auftrag_drucken_zaehlt_die_exemplare(client, kopf, kunde) -> None:
    auftrags_id = auftrag(client, kopf, kunde)

    erste = client.post(
        f"/api/v1/sales/orders/{auftrags_id}/print",
        headers=kopf,
        params={"template": "standard", "copies": 2},
    )
    assert erste.status_code == 200, erste.text
    assert erste.json()["print_count"] == 2
    assert erste.json()["printed_at"]


def test_wiederholungsdruck_verlangt_eine_begruendung(client, kopf, kunde) -> None:
    """Wer einen gedruckten Beleg erneut ausgibt, soll sagen warum."""
    auftrags_id = auftrag(client, kopf, kunde)
    assert client.post(f"/api/v1/sales/orders/{auftrags_id}/print", headers=kopf).status_code == 200

    ohne_grund = client.post(f"/api/v1/sales/orders/{auftrags_id}/print", headers=kopf)
    assert ohne_grund.status_code == 400
    assert "Begruendung" in ohne_grund.json()["detail"]

    mit_grund = client.post(
        f"/api/v1/sales/orders/{auftrags_id}/print",
        headers=kopf,
        params={"attestation": "Kunde hat das erste Exemplar nicht erhalten"},
    )
    assert mit_grund.status_code == 200
    assert mit_grund.json()["print_count"] == 2


def test_auftrag_buchen_macht_aus_offen_bestaetigt(client, kopf, kunde) -> None:
    auftrags_id = auftrag(client, kopf, kunde)
    gebucht = client.post(f"/api/v1/sales/orders/{auftrags_id}/post", headers=kopf)
    assert gebucht.status_code == 200, gebucht.text
    assert gebucht.json()["status"] == "confirmed"


def test_zweimal_buchen_ist_kein_fehler(client, kopf, kunde) -> None:
    """Die Maske druckt und bucht in einem Zug — auch beim zweiten Exemplar."""
    auftrags_id = auftrag(client, kopf, kunde)
    assert client.post(f"/api/v1/sales/orders/{auftrags_id}/post", headers=kopf).status_code == 200
    zweite = client.post(f"/api/v1/sales/orders/{auftrags_id}/post", headers=kopf)
    assert zweite.status_code == 200
    assert zweite.json()["status"] == "confirmed"


def test_stornierter_auftrag_wird_nicht_gebucht(client, kopf, kunde) -> None:
    auftrags_id = auftrag(client, kopf, kunde)
    assert client.post(f"/api/v1/sales/orders/{auftrags_id}/cancel", headers=kopf).status_code == 200

    gebucht = client.post(f"/api/v1/sales/orders/{auftrags_id}/post", headers=kopf)
    assert gebucht.status_code == 400
    assert "storniert" in gebucht.json()["detail"]


def test_fremder_auftrag_bleibt_unberuehrt(client, kopf, kunde) -> None:
    auftrags_id = auftrag(client, kopf, kunde)
    fremd = {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": "test-fremder-mandant",
        "X-Tenant-Id": "test-fremder-mandant",
    }
    assert client.post(f"/api/v1/sales/orders/{auftrags_id}/print", headers=fremd).status_code == 404
    assert client.post(f"/api/v1/sales/orders/{auftrags_id}/post", headers=fremd).status_code == 404


# ── Angebot ────────────────────────────────────────────────────────────────


def test_angebot_drucken_und_buchen(client, kopf, kunde) -> None:
    angebots_id = angebot(client, kopf, kunde)

    gedruckt = client.post(
        f"/api/v1/sales/offers/{angebots_id}/print",
        headers=kopf,
        params={"copies": 1},
    )
    assert gedruckt.status_code == 200, gedruckt.text
    assert gedruckt.json()["print_count"] == 1

    gebucht = client.post(f"/api/v1/sales/offers/{angebots_id}/post", headers=kopf)
    assert gebucht.status_code == 200, gebucht.text
    assert gebucht.json()["status"] == "versendet"


def test_angenommenes_angebot_faellt_nicht_auf_versendet_zurueck(client, kopf, kunde) -> None:
    """Der spaetere Stand bleibt stehen — Buchen ist kein Rueckwaertsgang."""
    from sqlalchemy import create_engine, text

    angebots_id = angebot(client, kopf, kunde)
    with create_engine(DB_URL).begin() as verbindung:
        verbindung.execute(
            text("UPDATE domain_crm.sales_offers SET status = 'angenommen' WHERE id = :id"),
            {"id": angebots_id},
        )

    gebucht = client.post(f"/api/v1/sales/offers/{angebots_id}/post", headers=kopf)
    assert gebucht.status_code == 200
    assert gebucht.json()["status"] == "angenommen"
