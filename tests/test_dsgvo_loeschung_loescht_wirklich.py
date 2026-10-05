"""Ein Loeschantrag nach Art. 17 DSGVO loescht wirklich — oder bleibt offen.

Jede einzelne Anweisung der Loeschroutine zeigte auf Tabellen oder Spalten,
die es nicht gibt:

- ``domain_crm.crm_customers`` hat kein `name`, `telefon`, `adresse` — und ist
  ausserdem leer; gefuehrt werden die Kunden in ``domain_crm.customers``.
- ``domain_crm.contacts`` hat kein `tenant_id`.
- ``domain_crm.activities`` hat weder `customer_id` noch `lead_id`.
- ``domain_hr.employees`` gibt es nicht.

Jeder Fehlschlag landete im Protokoll — und der Antrag wurde **trotzdem** auf
ABGESCHLOSSEN gesetzt. Eine gesetzliche Pflicht galt damit als erfuellt,
waehrend kein einziger Datensatz angefasst worden war. Das ist der
gefaehrlichste Fall dieses Musters: nicht eine leere Liste, sondern eine
falsche Zusage.

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
        with create_engine(DB_URL).connect() as verbindung:
            vorhanden = verbindung.execute(
                text("SELECT to_regclass('domain_compliance.data_erasure_requests')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Tabelle domain_compliance.data_erasure_requests fehlt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def kunde_mit_spuren():
    """Ein Kunde, eine Aktivitaet unter seinem Namen, ein eigener Mandant."""
    from sqlalchemy import create_engine, text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    kunden_id = str(uuid.uuid4())
    aktivitaet_id = str(uuid.uuid4())
    name = f"Hof Testmann {uuid.uuid4().hex[:5]}"

    engine = create_engine(DB_URL)
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": mandant, "domain": f"{mandant}.test"},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.customers "
                "(id, tenant_id, customer_number, company_name, email, phone, city) "
                "VALUES (:id, :tid, :nr, :name, :mail, '0123456789', 'Testdorf')"
            ),
            {
                "id": kunden_id,
                "tid": mandant,
                "nr": f"KD-{uuid.uuid4().hex[:5].upper()}",
                "name": name,
                "mail": "kunde@example.invalid",
            },
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.activities "
                "(id, type, title, customer, contact_person, date, status, "
                " assigned_to, tenant_id) "
                "VALUES (:id, 'call', 'Telefonat', :kunde, :kunde, NOW(), "
                "        'completed', 'tester', :tid)"
            ),
            {"id": aktivitaet_id, "kunde": name, "tid": mandant},
        )
    try:
        yield {
            "id": kunden_id,
            "mandant": mandant,
            "name": name,
            "aktivitaet": aktivitaet_id,
        }
    finally:
        with engine.begin() as verbindung:
            for sql, params in (
                ("DELETE FROM domain_crm.activities WHERE id = :id", {"id": aktivitaet_id}),
                ("DELETE FROM domain_crm.customers WHERE id = :id", {"id": kunden_id}),
                (
                    "DELETE FROM domain_compliance.data_erasure_requests "
                    "WHERE tenant_id = :tid",
                    {"tid": mandant},
                ),
                ("DELETE FROM domain_shared.tenants WHERE id = :tid", {"tid": mandant}),
            ):
                verbindung.execute(text(sql), params)


def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


def antrag_stellen(client, betroffener: dict, typ: str = "CUSTOMER") -> str:
    antwort = client.post(
        "/api/v1/compliance/dsgvo/erasure-requests",
        headers=kopf(betroffener["mandant"]),
        json={
            "requester_name": "Betroffener",
            "requester_email": "betroffener@example.invalid",
            "subject_id": betroffener["id"],
            "subject_type": typ,
        },
    )
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


def test_der_kunde_ist_danach_anonym(client, kunde_mit_spuren) -> None:
    from sqlalchemy import create_engine, text

    antrag = antrag_stellen(client, kunde_mit_spuren)
    antwort = client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag}/process",
        headers=kopf(kunde_mit_spuren["mandant"]),
        json={"deletion_notes": "Testlauf"},
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["status"] == "ABGESCHLOSSEN"

    with create_engine(DB_URL).connect() as verbindung:
        zeile = verbindung.execute(
            text(
                "SELECT company_name, email, phone, city FROM domain_crm.customers "
                "WHERE id::text = :id"
            ),
            {"id": kunde_mit_spuren["id"]},
        ).first()
    assert zeile is not None, "Der Kunde wurde geloescht statt anonymisiert"
    assert kunde_mit_spuren["name"] not in (zeile[0] or ""), "Der Name steht noch da"
    assert zeile[1] == "geloescht@dsgvo.invalid"
    assert zeile[2] is None and zeile[3] is None


def test_die_aktivitaet_unter_seinem_namen_ist_weg(client, kunde_mit_spuren) -> None:
    """Die Aktivitaet kennt den Kunden nur beim Namen — deshalb blieb sie liegen."""
    from sqlalchemy import create_engine, text

    antrag = antrag_stellen(client, kunde_mit_spuren)
    client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag}/process",
        headers=kopf(kunde_mit_spuren["mandant"]),
        json={},
    )
    with create_engine(DB_URL).connect() as verbindung:
        uebrig = verbindung.execute(
            text("SELECT count(*) FROM domain_crm.activities WHERE id::text = :id"),
            {"id": kunde_mit_spuren["aktivitaet"]},
        ).scalar()
    assert uebrig == 0, "Die Aktivitaet mit dem Klarnamen liegt noch in der Datenbank"


def test_das_protokoll_weist_die_angefassten_zeilen_aus(client, kunde_mit_spuren) -> None:
    antrag = antrag_stellen(client, kunde_mit_spuren)
    antwort = client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag}/process",
        headers=kopf(kunde_mit_spuren["mandant"]),
        json={},
    )
    protokoll = antwort.json()["deletion_log"]
    assert not any(e.get("error") for e in protokoll), protokoll
    angefasst = sum(e.get("rows_affected", 0) for e in protokoll)
    assert angefasst >= 2, f"Zu wenig angefasst — Kunde und Aktivitaet fehlen: {protokoll}"


def test_ohne_datenbestand_bleibt_der_antrag_offen(client, kunde_mit_spuren) -> None:
    """Einen Personalstamm gibt es nicht — das darf nicht wie erledigt aussehen."""
    antrag = antrag_stellen(client, kunde_mit_spuren, typ="EMPLOYEE")
    antwort = client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag}/process",
        headers=kopf(kunde_mit_spuren["mandant"]),
        json={},
    )
    assert antwort.status_code == 422, antwort.text

    gelesen = client.get(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag}",
        headers=kopf(kunde_mit_spuren["mandant"]),
    )
    assert gelesen.json()["status"] != "ABGESCHLOSSEN"
