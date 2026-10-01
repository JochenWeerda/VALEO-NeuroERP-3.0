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
    aktivitaet = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.crm_customers "
                "(id, tenant_id, customer_number, company_name, last_name, street, postal_code, city) "
                "VALUES (:id, :tid, :nr, 'Testhof Sonnenacker', 'Meyer', 'Hofweg 1', '29525', 'Uelzen')"
            ),
            {"id": kunde["id"], "tid": kunde["mandant"], "nr": kunde["kunden_nr"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.crm_opportunities "
                "(id, customer_id, title, assigned_to, tenant_id, stage, estimated_value, probability) "
                "VALUES (:id, :cid, 'Weizen 2026', 'vertrieb', :tid, 'proposal', 12000, 40)"
            ),
            {"id": chance, "cid": kunde["id"], "tid": kunde["mandant"]},
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
                text("DELETE FROM domain_crm.crm_customers WHERE id = :id"), {"id": kunde["id"]}
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.activities WHERE id = :id"), {"id": aktivitaet}
            )


def test_angelegte_aktivitaet_erscheint_in_der_historie(client, kunde) -> None:
    """create_activity schreibt in domain_crm.activities, nicht in eine Tabelle ohne Migration."""
    from sqlalchemy import create_engine, text

    antwort = client.post(
        f"/api/v1/crm/customers/{kunde['id']}/actions/create_activity",
        headers=kopf(kunde["mandant"]),
        json={"betreff": "Hofbesuch", "typ": "Besuch", "_mode": "execute", "_auditReason": "Termin"},
    )
    assert antwort.status_code == 200, antwort.text
    koerper = antwort.json()
    assert koerper["success"] is True
    aktivitaet = koerper["affectedIds"][0]
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    try:
        historie = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/historie", headers=kopf(kunde["mandant"])
        )
        assert historie.status_code == 200, historie.text
        assert any(zeile.get("subject") == "Hofbesuch" for zeile in historie.json()["items"])
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(text("DELETE FROM domain_crm.activities WHERE id = :id"), {"id": aktivitaet})
            verbindung.execute(
                text(
                    "DELETE FROM domain_crm.crm_action_audit_log "
                    "WHERE entity_id = :cid AND action_key = 'create_activity'"
                ),
                {"cid": kunde["id"]},
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
    """Steuern und Bank kommen vom Partner, Kontakte aus business_partner_contacts, Kontrakte ueber party_id."""
    from sqlalchemy import create_engine, text

    kontakt = str(uuid.uuid4())
    kontrakt = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "UPDATE domain_crm.business_partners "
                "SET vat_id = 'DE123456789', iban = 'DE89370400440532013000', "
                "marketing_segment = 'A-Kunde' "
                "WHERE partner_id = :id"
            ),
            {"id": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_contacts "
                "(id, partner_id, priority, first_name, last_name, email, position, contact_type, "
                "invoice_email_recipient, reminder_email_recipient, is_data_protection_officer) "
                "VALUES (:id, :pid, 0, 'Ada', 'Meyer', 'ada@sonnenacker.test', 'Geschaeftsfuehrung', "
                "'other', false, false, false)"
            ),
            {"id": kontakt, "pid": kunde["partner_id"]},
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
        assert stamm.json()["segment"] == "A-Kunde"
        assert stamm.json()["marketing_segment"] == "A-Kunde"

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
            verbindung.execute(text("DELETE FROM domain_crm.business_partner_contacts WHERE id = :id"), {"id": kontakt})


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


def test_pflege_register_liegen_in_der_akte(client, kunde) -> None:
    """Tab 21, 23, 24 und 25: Anweisungen, Anschriften, Kontoauszug, CPD."""
    from sqlalchemy import create_engine, text

    anweisung = str(uuid.uuid4())
    anschrift = str(uuid.uuid4())
    abrechnung = str(uuid.uuid4())
    cpd = str(uuid.uuid4())
    cpd_nr = f"CPD-{uuid.uuid4().hex[:6].upper()}"
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_instructions "
                "(id, partner_id, instruction_text, instruction_priority) "
                "VALUES (:id, :pid, 'Nur nach Absprache liefern', 'high')"
            ),
            {"id": anweisung, "pid": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_addresses "
                "(id, partner_id, address_type, name_1, city, is_default) "
                "VALUES (:id, :pid, 'shipping', 'Lagerhof', 'Kiel', false)"
            ),
            {"id": anschrift, "pid": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_billing_configs "
                "(id, partner_id, customer_group, account_balance, "
                "account_statement_print, account_statement_separate, account_statement_reprint, "
                "print_ad_text, shipping_expenses_enabled, bonus_eligible, "
                "self_billing_sales, self_billing_purchase, remarkable_claim, vat_optimizer) "
                "VALUES (:id, :pid, 'LAND', 1250.50, true, false, false, false, false, true, "
                "false, false, false, false)"
            ),
            {"id": abrechnung, "pid": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_cpd_accounts "
                "(id, partner_id, cpd_customer_number, name_1, debtor_account, collective_invoice) "
                "VALUES (:id, :pid, :nr, 'CPD Hof', '1400', false)"
            ),
            {"id": cpd, "pid": kunde["partner_id"], "nr": cpd_nr},
        )
    try:
        anweisungen = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/chefanweisungen",
            headers=kopf(kunde["mandant"]),
        )
        assert anweisungen.status_code == 200, anweisungen.text
        assert any(
            zeile.get("instruction_text") == "Nur nach Absprache liefern"
            for zeile in anweisungen.json()["items"]
        )

        anschriften = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/anschriften",
            headers=kopf(kunde["mandant"]),
        )
        assert anschriften.status_code == 200, anschriften.text
        assert any(zeile.get("name_1") == "Lagerhof" for zeile in anschriften.json()["items"])

        konten = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/cpd",
            headers=kopf(kunde["mandant"]),
        )
        assert konten.status_code == 200, konten.text
        assert any(zeile.get("cpd_customer_number") == cpd_nr for zeile in konten.json()["items"])

        stamm = client.get(
            f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        assert stamm.json()["billing_customer_group"] == "LAND"
        assert stamm.json()["account_balance"] == 1250.5
        assert stamm.json()["bonus_eligible"] is True
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_cpd_accounts WHERE id = :id"),
                {"id": cpd},
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_billing_configs WHERE id = :id"),
                {"id": abrechnung},
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_addresses WHERE id = :id"),
                {"id": anschrift},
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_instructions WHERE id = :id"),
                {"id": anweisung},
            )


def test_rabatte_preise_und_sepa_liegen_in_der_akte(client, kunde) -> None:
    """Rabatt- und Preislisten des Partners plus SEPA-Mandat an der Bank."""
    from sqlalchemy import create_engine, text

    rabatt = str(uuid.uuid4())
    preis = str(uuid.uuid4())
    kontakt = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "UPDATE domain_crm.business_partners "
                "SET sepa_mandate_reference = 'MANDAT-1', "
                "sepa_mandate_signed_at = '2026-03-01' "
                "WHERE partner_id = :id"
            ),
            {"id": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_discount_items "
                "(id, partner_id, article_number, description, discount_percent) "
                "VALUES (:id, :pid, 'SAAT-1', 'Winterweizen', 12.5)"
            ),
            {"id": rabatt, "pid": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_price_agreements "
                "(id, partner_id, article_number, description, price_net, price_unit, discount_allowed) "
                "VALUES (:id, :pid, 'SAAT-1', 'Winterweizen', 18.40, 'kg', true)"
            ),
            {"id": preis, "pid": kunde["partner_id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.business_partner_contacts "
                "(id, partner_id, priority, last_name, email, contact_type, "
                "invoice_email_recipient, reminder_email_recipient, is_data_protection_officer) "
                "VALUES (:id, :pid, 0, 'Berger', 'berger@sonnenacker.test', 'other', false, false, false)"
            ),
            {"id": kontakt, "pid": kunde["partner_id"]},
        )
    try:
        rabatte = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/rabatte", headers=kopf(kunde["mandant"])
        )
        assert rabatte.status_code == 200, rabatte.text
        zeile = next(item for item in rabatte.json()["items"] if item.get("article_number") == "SAAT-1")
        assert zeile["discount_percent"] == 12.5

        preise = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/preise", headers=kopf(kunde["mandant"])
        )
        assert preise.status_code == 200, preise.text
        vereinbarung = next(item for item in preise.json()["items"] if item.get("article_number") == "SAAT-1")
        assert vereinbarung["price_net"] == 18.4

        kontakte = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/contacts", headers=kopf(kunde["mandant"])
        )
        assert kontakte.status_code == 200, kontakte.text
        assert any(zeile.get("name") == "Berger" for zeile in kontakte.json()["items"])

        stamm = client.get(
            f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        assert stamm.json()["sepa_mandat_ref"] == "MANDAT-1"
        assert stamm.json()["sepa_mandat_datum"] == "2026-03-01"
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_contacts WHERE id = :id"), {"id": kontakt}
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_price_agreements WHERE id = :id"), {"id": preis}
            )
            verbindung.execute(
                text("DELETE FROM domain_crm.business_partner_discount_items WHERE id = :id"), {"id": rabatt}
            )


def test_annahme_und_kreditlimit_in_der_360_sicht(client, kunde) -> None:
    """Annahmeschein und Kreditausnahme treffen die Spalten der Migration."""
    from sqlalchemy import create_engine, text

    annahme = str(uuid.uuid4())
    annahme_nr = f"AN-{uuid.uuid4().hex[:6].upper()}"
    limit_id = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_inventory.harvest_acceptances "
                "(id, acceptance_number, tenant_id, delivery_date, operator_id, customer_id, "
                "is_sustainable_biomass, release_status, pricing_mode, "
                "print_remarks_on_acceptance_note, print_remarks_on_settlement) "
                "VALUES (:id, :nr, :tid, CURRENT_DATE, 'bedienung', :cid, "
                "false, 'draft', 'spot_daily', false, false)"
            ),
            {"id": annahme, "nr": annahme_nr, "tid": kunde["mandant"], "cid": kunde["id"]},
        )
        verbindung.execute(
            text(
                "UPDATE domain_crm.customers SET credit_limit = 1000 WHERE id = :id"
            ),
            {"id": kunde["id"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_crm.credit_limits "
                "(id, tenant_id, customer_id, credit_limit_eur) "
                "VALUES (:id, :tid, :cid, 5000)"
            ),
            {"id": limit_id, "tid": kunde["mandant"], "cid": kunde["id"]},
        )
    try:
        sicht = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/360", headers=kopf(kunde["mandant"])
        )
        assert sicht.status_code == 200, sicht.text
        koerper = sicht.json()
        eingang = koerper["last_goods_receipt"]
        assert eingang["reference_number"] == annahme_nr
        assert eingang["source"] == "harvest_acceptances"
        assert koerper["credit_limit_status"]["credit_limit"] == 5000
        assert koerper["credit_limit_status"]["source"] == "ausnahme"
        stamm = client.get(
            f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        assert stamm.json()["kreditlimit"] == 5000
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.credit_limits WHERE id = :id"), {"id": limit_id}
            )
            verbindung.execute(
                text("DELETE FROM domain_inventory.harvest_acceptances WHERE id = :id"),
                {"id": annahme},
            )


def test_warenzugang_ohne_annahmeschein_haengt_am_partner(client, kunde) -> None:
    """Lagerbewegung zaehlt ueber owner_partner_id, nicht ueber einen Notiztext."""
    from sqlalchemy import create_engine, text

    bewegung = str(uuid.uuid4())
    artikel = str(uuid.uuid4())
    lager = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_inventory.warehouses "
                "(id, tenant_id, warehouse_code, name, address, city, postal_code) "
                "VALUES (:id, :tid, :code, 'Prueflager Akte', 'Kai 1', 'Bremen', '28195')"
            ),
            {"id": lager, "tid": kunde["mandant"], "code": f"L-{uuid.uuid4().hex[:4]}"},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_inventory.articles "
                "(id, tenant_id, article_number, name, mhd_erforderlich, lagerartikel, "
                "lagerorte, chargenpflicht, qs_pruefung_erforderlich, bio_kennzeichnung, "
                "gmp_plus_relevanz, unit, category, sales_price) "
                "VALUES (:id, :tid, :nr, 'Weizen Akte', false, true, '[]'::jsonb, false, "
                "false, false, false, 't', 'Getreide', 0)"
            ),
            {"id": artikel, "tid": kunde["mandant"], "nr": f"A-{uuid.uuid4().hex[:6]}"},
        )
        verbindung.execute(
            text(
                "INSERT INTO domain_inventory.inventory_stock_movements "
                "(id, article_id, warehouse_id, movement_type, quantity, reference_number, "
                "owner_partner_id, ownership_type, auto_created, storage_fee_relevant, "
                "previous_stock, new_stock, tenant_id) "
                "VALUES (:id, :artikel, :lager, 'in', 12, 'WE-1', :pid, 'owned', false, false, "
                "0, 12, :tid)"
            ),
            {
                "id": bewegung,
                "artikel": artikel,
                "lager": lager,
                "pid": kunde["partner_id"],
                "tid": kunde["mandant"],
            },
        )
    try:
        sicht = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/360", headers=kopf(kunde["mandant"])
        )
        assert sicht.status_code == 200, sicht.text
        eingang = sicht.json()["last_goods_receipt"]
        assert eingang["reference_number"] == "WE-1"
        assert eingang["quantity_kg"] == 12
        assert eingang["source"] == "inventory_stock_movements"
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_inventory.inventory_stock_movements WHERE id = :id"),
                {"id": bewegung},
            )
            verbindung.execute(
                text("DELETE FROM domain_inventory.articles WHERE id = :id"),
                {"id": artikel},
            )
            verbindung.execute(
                text("DELETE FROM domain_inventory.warehouses WHERE id = :id"),
                {"id": lager},
            )


def test_agrarkontrakt_haengt_am_partner_nicht_nur_an_der_kunden_id(client, kunde) -> None:
    """Die 360-Liste trifft Kontrakte, deren partner_id der Geschaeftspartner ist."""
    from sqlalchemy import create_engine, text

    kontrakt = str(uuid.uuid4())
    nummer = f"AK-{uuid.uuid4().hex[:6].upper()}"
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO domain_inventory.agrar_contracts "
                "(id, tenant_id, contract_number, contract_type, harvest_year, partner_id, "
                "article_id, pricing_model, total_quantity_kg, remaining_quantity_kg, status, "
                "fixed_price) "
                "VALUES (:id, :tid, :nr, 'purchase', 2026, :pid, :artikel, 'fixed', "
                "1000, 1000, 'open', 200)"
            ),
            {
                "id": kontrakt,
                "tid": kunde["mandant"],
                "nr": nummer,
                "pid": kunde["partner_id"],
                "artikel": str(uuid.uuid4()),
            },
        )
    try:
        sicht = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/360", headers=kopf(kunde["mandant"])
        )
        assert sicht.status_code == 200, sicht.text
        nummern = [zeile.get("contract_number") for zeile in sicht.json()["active_contracts"]]
        assert nummer in nummern
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_inventory.agrar_contracts WHERE id = :id"),
                {"id": kontrakt},
            )


def test_jahresumsatz_zaehlt_die_geschriebenen_auftragsstatus(client, kunde) -> None:
    """Offene Auftraege zaehlen nicht. completed und geliefert zaehlen."""
    from sqlalchemy import create_engine, text

    abgeschlossen = str(uuid.uuid4())
    geliefert = str(uuid.uuid4())
    offen = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        for auftrag, nummer, status, betrag in (
            (abgeschlossen, f"VA-{uuid.uuid4().hex[:6]}", "completed", 1500),
            (geliefert, f"VA-{uuid.uuid4().hex[:6]}", "geliefert", 250),
            (offen, f"VA-{uuid.uuid4().hex[:6]}", "open", 999),
        ):
            verbindung.execute(
                text(
                    "INSERT INTO domain_crm.sales_orders "
                    "(id, tenant_id, customer_id, order_number, subject, total_amount, status) "
                    "VALUES (:id, :tid, :cid, :nr, 'Akte', :betrag, :status)"
                ),
                {
                    "id": auftrag,
                    "tid": kunde["mandant"],
                    "cid": kunde["id"],
                    "nr": nummer,
                    "betrag": betrag,
                    "status": status,
                },
            )
    try:
        sicht = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/360", headers=kopf(kunde["mandant"])
        )
        assert sicht.status_code == 200, sicht.text
        koerper = sicht.json()
        assert koerper["jahresumsatz_eur"] == 1750
        nummern = {zeile.get("order_number") for zeile in koerper["recent_orders"]}
        assert len(nummern) == 3
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM domain_crm.sales_orders WHERE id IN (:a, :b, :c)"),
                {"a": abgeschlossen, "b": geliefert, "c": offen},
            )


def test_postfach_und_geo_kommen_aus_dem_migrierten_stamm(client, kunde) -> None:
    """Postfach aus public.kunden, Koordinaten aus public.kunden_geo."""
    from sqlalchemy import create_engine, text

    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO public.kunden (kunden_nr, name1, postfach, postfach_plz, postfach_ort) "
                "VALUES (:nr, 'Testhof Sonnenacker', '12', '28195', 'Bremen')"
            ),
            {"nr": kunde["kunden_nr"]},
        )
        verbindung.execute(
            text(
                "INSERT INTO public.kunden_geo (kunden_nr, lat, lon, \"precision\", source) "
                "VALUES (:nr, 53.0793, 8.8017, 'address', 'manuell')"
            ),
            {"nr": kunde["kunden_nr"]},
        )
    try:
        stamm = client.get(
            f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        daten = stamm.json()
        assert daten["postfach"] == "12"
        assert daten["postfach_plz"] == "28195"
        assert daten["postfach_ort"] == "Bremen"
        assert float(daten["breitengrad"]) == 53.0793
        assert float(daten["laengengrad"]) == 8.8017
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM public.kunden_geo WHERE kunden_nr = :nr"),
                {"nr": kunde["kunden_nr"]},
            )
            verbindung.execute(
                text("DELETE FROM public.kunden WHERE kunden_nr = :nr"),
                {"nr": kunde["kunden_nr"]},
            )


def test_ein_reiner_bestandskunde_oeffnet_die_akte(client, kunde) -> None:
    """public.kunden fuehrt name1 und tel. Daraus wird die Akte, auch ohne CRM-Satz."""
    from sqlalchemy import create_engine, text

    nummer = f"KD-{uuid.uuid4().hex[:6].upper()}"
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO public.kunden (kunden_nr, name1, strasse, plz, ort, land, tel) "
                "VALUES (:nr, 'Hof Altbestand', 'Dorfstr. 4', '29439', 'Luechow', 'DE', '05841-100')"
            ),
            {"nr": nummer},
        )
    try:
        stamm = client.get(
            f"/api/v1/crm/customers/{nummer}", headers=kopf(kunde["mandant"])
        )
        assert stamm.status_code == 200, stamm.text
        daten = stamm.json()
        assert daten["firma"] == "Hof Altbestand"
        assert daten["kunden_nr"] == nummer
        assert daten["strasse"] == "Dorfstr. 4"
        assert daten["telefon"] == "05841-100"
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM public.kunden WHERE kunden_nr = :nr"),
                {"nr": nummer},
            )


def test_adresse_und_branche_kommen_aus_dem_kundenstamm(client, kunde) -> None:
    """Ort, PLZ, Land und Branche liegen auf domain_crm.customers, das Fax am Partner."""
    from sqlalchemy import create_engine, text

    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "UPDATE domain_crm.customers "
                "SET address = 'Dorfstr. 4', postal_code = '29439', city = 'Luechow', "
                "country = 'DE', industry = 'Ackerbau', phone = '05841-100' "
                "WHERE id = :id"
            ),
            {"id": kunde["id"]},
        )
        verbindung.execute(
            text(
                "UPDATE domain_crm.business_partners SET fax = '05841-200' "
                "WHERE partner_id = :id"
            ),
            {"id": kunde["partner_id"]},
        )
    stamm = client.get(
        f"/api/v1/crm/customers/{kunde['id']}", headers=kopf(kunde["mandant"])
    )
    assert stamm.status_code == 200, stamm.text
    daten = stamm.json()
    assert daten["strasse"] == "Dorfstr. 4"
    assert daten["plz"] == "29439"
    assert daten["ort"] == "Luechow"
    assert daten["land"] == "DE"
    assert daten["branche"] == "Ackerbau"
    assert daten["telefon"] == "05841-100"
    assert daten["fax"] == "05841-200"


def test_praesent_erscheint_im_register(client, kunde) -> None:
    """Präsente liegen in public.crm_gifts und werden ueber die Kundennummer gelesen."""
    from sqlalchemy import create_engine, text

    geschenk = str(uuid.uuid4())
    engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
    with engine.begin() as verbindung:
        verbindung.execute(
            text(
                "INSERT INTO public.crm_gifts "
                "(id, tenant_id, kunden_nr, year, gift_name, occasion, quantity) "
                "VALUES (:id, :tid, :nr, 2026, 'Weihnachtspaket', 'Weihnachten', 1)"
            ),
            {"id": geschenk, "tid": kunde["mandant"], "nr": kunde["kunden_nr"]},
        )
    try:
        register = client.get(
            f"/api/v1/crm/customers/{kunde['id']}/tabs/praesente",
            headers=kopf(kunde["mandant"]),
        )
        assert register.status_code == 200, register.text
        zeilen = register.json()["items"]
        assert any(zeile.get("gift_name") == "Weihnachtspaket" for zeile in zeilen)
    finally:
        with engine.begin() as verbindung:
            verbindung.execute(
                text("DELETE FROM public.crm_gifts WHERE id = :id"),
                {"id": geschenk},
            )


def test_ein_kunde_den_es_nicht_gibt_bleibt_ein_404(client, kunde) -> None:
    """Der 404 soll weiterhin etwas bedeuten."""
    antwort = client.get(
        f"/api/v1/crm/customers/{uuid.uuid4()}/tabs/contacts", headers=kopf(kunde["mandant"])
    )
    assert antwort.status_code == 404
