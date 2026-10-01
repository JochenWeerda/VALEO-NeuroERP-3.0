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


@pytest.mark.parametrize("register", ["contacts", "auftraege", "aktivitaeten", "dokumente", "praesente", "angebote", "historie"])
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


def test_angebote_historie_und_aufgaben_liefern_echte_zeilen(client, kunde) -> None:
    """Die Register duerfen nicht leer bleiben, nur weil die Abfrage scheitert."""
    from sqlalchemy import create_engine, text

    chance = str(uuid.uuid4())
    pipeline_kunde = str(uuid.uuid4())
    aktivitaet = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.crm_customers "
                "(id, tenant_id, customer_number, company_name, last_name, street, postal_code, city) "
                "VALUES (:id, :tid, :nr, 'Testhof Sonnenacker', 'Meyer', 'Hofweg 1', '29525', 'Uelzen')"
            ),
            {"id": pipeline_kunde, "tid": kunde["mandant"], "nr": kunde["kunden_nr"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.crm_opportunities "
                "(id, customer_id, title, assigned_to, tenant_id, stage, estimated_value, probability) "
                "VALUES (:id, :cid, 'Weizen 2026', 'vertrieb', :tid, 'proposal', 12000, 40)"
            ),
            {"id": chance, "cid": pipeline_kunde, "tid": kunde["mandant"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.activities "
                "(id, type, title, customer, contact_person, date, status, assigned_to, tenant_id) "
                "VALUES (:id, 'task', 'Rueckruf', 'Testhof Sonnenacker', 'Meyer', NOW(), 'offen', 'vertrieb', :tid)"
            ),
            {"id": aktivitaet, "tid": kunde["mandant"]},
        )
    try:
        angebote = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/angebote", headers=kopf(kunde["mandant"])
        )
        assert angebote.status_code == 200, angebote.text
        assert any(zeile.get("title") == "Weizen 2026" for zeile in angebote.json()["items"])

        historie = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/historie", headers=kopf(kunde["mandant"])
        )
        assert historie.status_code == 200, historie.text
        assert any(zeile.get("subject") == "Rueckruf" for zeile in historie.json()["items"])

        aufgaben = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/aufgaben", headers=kopf(kunde["mandant"])
        )
        assert aufgaben.status_code == 200, aufgaben.text
        zeile = next(item for item in aufgaben.json()["items"] if item.get("titel") == "Rueckruf")
        assert zeile["art"] == "task"
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.crm_opportunities WHERE id = :id"), {"id": chance}
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.crm_customers WHERE id = :id"), {"id": pipeline_kunde}
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.activities WHERE id = :id"), {"id": aktivitaet}
            )


def test_offene_posten_erscheinen_in_dokumenten_und_im_kopf(client, kunde) -> None:
    """domain_erp.offene_posten fuehrt den Kunden als kunde_id, nicht als kunden_id."""
    from sqlalchemy import create_engine, text

    posten = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_erp.offene_posten "
                "(id, tenant_id, rechnungsnr, faelligkeit, betrag, offen, kunde_id, op_status) "
                "VALUES (:id, :tid, 'RE-100', CURRENT_DATE - 3, 250, 250, :cid, 'offen')"
            ),
            {"id": posten, "tid": kunde["mandant"], "cid": kunde["id"]},
        )
    try:
        dokumente = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/dokumente", headers=kopf(kunde["mandant"])
        )
        assert dokumente.status_code == 200, dokumente.text
        zeile = next(item for item in dokumente.json()["items"] if item.get("rechnungsnr") == "RE-100")
        assert zeile["amount"] == 250
        assert zeile["op_status"] == "offen"

        kopfzeile = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/screen-summary", headers=kopf(kunde["mandant"])
        )
        assert kopfzeile.status_code == 200, kopfzeile.text
        assert kopfzeile.json()["summary"]["open_items_total"] == 250
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_erp.offene_posten WHERE id = :id"), {"id": posten}
            )


def test_partnerfelder_kontakte_und_kontrakte_liegen_in_der_akte(client, kunde) -> None:
    """Steuern und Bank kommen vom Partner, Kontakte aus domain_crm.contacts, Kontrakte ueber party_id."""
    from sqlalchemy import create_engine, text

    kontakt = str(uuid.uuid4())
    kontrakt = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "UPDATE domain_crm.business_partners "
                "SET vat_id = 'DE123456789', iban = 'DE89370400440532013000' "
                "WHERE partner_id = :id"
            ),
            {"id": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.contacts "
                "(id, first_name, last_name, email, customer_id, position) "
                "VALUES (:id, 'Ada', 'Meyer', 'ada@sonnenacker.test', :cid, 'Geschaeftsfuehrung')"
            ),
            {"id": kontakt, "cid": kunde["id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_ops.kon_contract "
                "(contract_id, contract_no, contract_type, party_id, quantity_type, total_quantity, "
                "unit, allow_overdelivery, status, tenant_id) "
                "VALUES (:id, 'AK-1', 'purchase', :pid, 'weight', 1000, 'kg', false, 'active', :tid)"
            ),
            {"id": kontrakt, "pid": kunde["partner_id"], "tid": kunde["mandant"]},
        )
    try:
        stamm = client.get(
            f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        assert stamm.json()["ust_id"] == "DE123456789"
        assert stamm.json()["iban"] == "DE89370400440532013000"

        kontakte = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/contacts", headers=kopf(kunde["mandant"])
        )
        assert kontakte.status_code == 200, kontakte.text
        assert any(zeile.get("name") == "Meyer" for zeile in kontakte.json()["items"])

        kontrakte = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/kontrakte", headers=kopf(kunde["mandant"])
        )
        assert kontrakte.status_code == 200, kontrakte.text
        assert any(zeile.get("contract_no") == "AK-1" for zeile in kontrakte.json()["items"])
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(text("DELETE FROM domain_ops.kon_contract WHERE contract_id = :id"), {"id": kontrakt})
            verbindung.execute(text("DELETE FROM domain_crm.contacts WHERE id = :id"), {"id": kontakt})


def test_potenzial_kommt_aus_dem_juengsten_gap_snapshot(client, kunde) -> None:
    """Fachquelle: public.customer_potential_snapshot, juengstes GAP-Jahr."""
    from sqlalchemy import create_engine, text

    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO public.customer_potential_snapshot "
                "(ref_year, customer_id, potential_total_eur, potential_seed_eur, gap_estimated_area_ha, segment) "
                "VALUES (2024, CAST(:cid AS uuid), 1000, 200, 10, 'C'), "
                "(2026, CAST(:cid AS uuid), 48000, 12000, 42.5, 'A')"
            ),
            {"cid": kunde["id"]},
        )
    try:
        stamm = client.get(
            f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        koerper = stamm.json()
        assert koerper["gap_ref_year"] == 2026
        assert koerper["potential_total_eur"] == 48000
        assert koerper["potential_seed_eur"] == 12000
        assert koerper["gap_estimated_area_ha"] == 42.5
        assert koerper["potential_segment"] == "A"
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM public.customer_potential_snapshot WHERE customer_id = CAST(:cid AS uuid)"),
                {"cid": kunde["id"]},
            )


def test_ein_kunde_den_es_nicht_gibt_bleibt_ein_404(client, kunde) -> None:
    """Der 404 soll weiterhin etwas bedeuten."""
    antwort = client.get(
        f"/api/v1/crm/customers/{uuid.uuid4()}/tabs/contacts", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 404
