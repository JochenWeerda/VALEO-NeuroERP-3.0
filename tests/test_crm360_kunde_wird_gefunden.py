"""Die Kunden-360-Maske findet ihren Kunden.

Gesucht wurde in ``domain_erp.business_partners``: Die Tabelle ist **leer** und
hat die abgefragten Spalten (`name`, `kunden_nr`) gar nicht. Der Spaltenfehler
lief in ein ``except``, die Suche kam leer zurueck — und **jedes** Register
antwortete „Kunde nicht gefunden", auch fuer Kunden, die es gibt. Die 360°-Sicht
ebenso.

Gefuehrt wird der Kunde in ``domain_crm.customers`` (operativer Stamm, traegt
die Kundennummer) und als Partner in ``domain_crm.business_partners``.

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
            conn.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def kunde():
    """Ein Kunde im operativen Stamm, mit eigenem Mandanten."""
    from sqlalchemy import create_engine, text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    kunden_id = str(uuid.uuid4())
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
                "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                "VALUES (:id, :tid, :nr, :name)"
            ),
            {
                "id": kunden_id,
                "tid": mandant,
                "nr": f"KD-{uuid.uuid4().hex[:5].upper()}",
                "name": "Testhof Sonnenacker",
            },
        )
    try:
        yield {"id": kunden_id, "mandant": mandant}
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.customers WHERE id = :id"), {"id": kunden_id}
            )
            verbindung.execute(
                text("DELETE FROM domain_shared.tenants WHERE id = :id"), {"id": mandant}
            )


def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
    }


@pytest.mark.parametrize("register", ["contacts", "auftraege", "aktivitaeten", "dokumente"])
def test_jedes_register_findet_den_kunden(client, kunde, register: str) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['id']}/tabs/{register}",
        headers=kopf(kunde["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["tab_key"] == register
    # Leer ist in Ordnung — „nicht gefunden" war es nicht.
    assert "items" in daten and "total" in daten


def test_die_360_sicht_findet_den_kunden(client, kunde) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['id']}/360", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["customer_id"] == kunde["id"]


def test_ein_kunde_den_es_nicht_gibt_bleibt_ein_404(client, kunde) -> None:
    """Der 404 soll weiterhin etwas bedeuten."""
    antwort = client.get(
        f"/api/v1/crm/customers/{uuid.uuid4()}/tabs/contacts", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 404
