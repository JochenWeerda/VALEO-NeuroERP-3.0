"""Die Kunden-360-Maske findet ihren Kunden.

Gesucht wurde in ``domain_erp.business_partners``: Die Tabelle ist **leer** und
hat die abgefragten Spalten (`name`, `kunden_nr`) gar nicht. Der Spaltenfehler
lief in ein ``except``, die Suche kam leer zurueck — und **jedes** Register
antwortete „Kunde nicht gefunden", auch fuer Kunden, die es gibt. Die 360°-Sicht
ebenso.

Gefuehrt wird der Kunde in ``domain_crm.customers`` (operativer Stamm, traegt
die Kundennummer) und als Partner in ``domain_crm.business_partners``.

Listen und KIM reichen oft ``kunden_nr`` statt der Stamm-UUID. Dieselbe Suche
muss deshalb auch die Kundennummer treffen.

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

# Gewachsene DB: Boolean-Flags auf business_partners sind NOT NULL ohne DEFAULT.
# Gleiche Liste wie tests/test_meridian_beleg_systemweit.py (_BP_FLAGS).
_BP_FLAGS = (
    "is_customer",
    "is_supplier",
    "is_carrier",
    "is_employee",
    "is_service_provider",
    "blocked_for_delivery",
    "blocked_for_invoice",
    "bio_certified",
    "email_opt_in",
    "sms_opt_in",
    "whatsapp_opt_in",
    "newsletter_opt_in",
    "flyer_subscription",
    "privacy_policy_accepted",
    "data_processing_agreement_signed",
    "bank_connection_active",
    "wants_account_statement",
    "print_balance_on_invoice",
    "invoice_print_blocked",
    "delivery_note_print_blocked",
    "calculate_shipping_flat",
    "self_billing_customer",
    "auto_offset_enabled",
    "post_open_items_blocked",
    "market_price_evaluation",
    "webshop_customer",
    "fax_blocked",
    "proforma_invoice",
    "membership_terminated",
    "customer_card_flag",
    "edifact_invoic",
    "edifact_orders",
    "edifact_desadv",
)


@pytest.fixture(scope="module")
def client():
    from sqlalchemy import create_engine, text

    try:
        with create_engine(DB_URL, connect_args={"connect_timeout": 5}).connect() as conn:
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

    mandant = str(uuid.uuid4())
    kunden_id = str(uuid.uuid4())
    partner_id = str(uuid.uuid4())
    kunden_nr = f"KD-{uuid.uuid4().hex[:5].upper()}"
    partner_number = f"BP-{uuid.uuid4().hex[:5].upper()}"
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :domain, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": mandant, "domain": f"{mandant}.test"},
        )
        bp_spalten = ", ".join(_BP_FLAGS)
        bp_werte = ", ".join(
            "true" if spalte == "is_customer" else "false" for spalte in _BP_FLAGS
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partners "
                f"(partner_id, tenant_id, partner_number, name_1, status, {bp_spalten}) "
                f"VALUES (:id, :tid, :nr, :name, 'active', {bp_werte})"
            ),
            {
                "id": partner_id,
                "tid": mandant,
                "nr": partner_number,
                "name": "Testhof Sonnenacker",
            },
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.customers "
                "(id, tenant_id, customer_number, company_name, business_partner_id) "
                "VALUES (:id, :tid, :nr, :name, :pid)"
            ),
            {
                "id": kunden_id,
                "tid": mandant,
                "nr": kunden_nr,
                "name": "Testhof Sonnenacker",
                "pid": partner_id,
            },
        )
    try:
        yield {
            "id": kunden_id,
            "mandant": mandant,
            "kunden_nr": kunden_nr,
            "partner_id": partner_id,
            "partner_number": partner_number,
        }
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.customers WHERE id = :id"), {"id": kunden_id}
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partners WHERE partner_id = :id"),
                {"id": partner_id},
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


@pytest.mark.parametrize("register", ["contacts", "auftraege", "aktivitaeten", "dokumente", "praesente"])
@pytest.mark.parametrize("schluessel", ["id", "kunden_nr", "partner_number"])
def test_jedes_register_findet_den_kunden(client, kunde, register: str, schluessel: str) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde[schluessel]}/tabs/{register}",
        headers=kopf(kunde["mandant"]),
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["tab_key"] == register
    assert "items" in daten and "total" in daten


def test_die_360_sicht_findet_den_kunden(client, kunde) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['id']}/360", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["customer_id"] == kunde["id"]


def test_die_360_sicht_findet_den_kunden_per_nummer(client, kunde) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['kunden_nr']}/360", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["customer_id"] == kunde["id"]


def test_der_stamm_liefert_maskenfelder_per_nummer(client, kunde) -> None:
    """Native Object Page: GET /customers/{kunden_nr} mit firma/kunden_nr."""
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['kunden_nr']}", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["id"] == kunde["id"]
    assert daten["firma"] == "Testhof Sonnenacker"
    assert daten["kunden_nr"] == kunde["kunden_nr"]
    assert daten["company_name"] == "Testhof Sonnenacker"


def test_der_stamm_findet_den_kunden_per_partnernummer(client, kunde) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['partner_number']}", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["id"] == kunde["id"]
    assert daten["firma"] == "Testhof Sonnenacker"
    assert daten["kunden_nr"] == kunde["kunden_nr"]


def test_die_360_sicht_findet_den_kunden_per_partnernummer(client, kunde) -> None:
    antwort = client.get(
        f"/api/v1/crm/customers/{kunde['partner_number']}/360", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["customer_id"] == kunde["id"]


def test_ein_kunde_den_es_nicht_gibt_bleibt_ein_404(client, kunde) -> None:
    """Der 404 soll weiterhin etwas bedeuten."""
    antwort = client.get(
        f"/api/v1/crm/customers/{uuid.uuid4()}/tabs/contacts", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 404
