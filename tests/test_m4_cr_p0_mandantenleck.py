"""M4-CR-P0: Mandantenlecks an public.kunden / KIM / Lookup / Merge / 360-Fallback.

Gegen den gemeinsamen Pruefstand (TEST_DATABASE_URL / valeo_probe). Eigene Testdaten
werden angelegt und am Ende geloescht — kein Probe-Reset.
"""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")
os.environ.setdefault("PGAPPNAME", "agent:cursor-m4-cr-p0")

HAUS_A = f"m4cr-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"m4cr-b-{uuid.uuid4().hex[:6]}"

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


def _kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="module")
def engine():
    try:
        eng = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        with eng.connect() as conn:
            conn.execute(text("SELECT 1 FROM public.kunden LIMIT 0"))
            conn.execute(text("SELECT 1 FROM domain_crm.business_partners LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Pruefstand nicht erreichbar: {fehler}")
    return eng


@pytest.fixture()
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    # Context-Manager: Lifespan sauber beenden (sonst hängt der Suite-Abschluss).
    with TestClient(app, raise_server_exceptions=False) as tc:
        yield tc


@pytest.fixture()
def zwei_mandanten(engine):
    """Je Mandant ein Partner + public.kunden + domain_crm.customers."""
    partner_a = str(uuid.uuid4())
    partner_b = str(uuid.uuid4())
    cust_a = str(uuid.uuid4())
    cust_b = str(uuid.uuid4())
    nr_a = f"A-{uuid.uuid4().hex[:6].upper()}"
    nr_b = f"B-{uuid.uuid4().hex[:6].upper()}"
    andere_flags = [f for f in _BP_FLAGS if f != "is_customer"]
    bp_cols = ", ".join(["partner_id", "tenant_id", "partner_number", "name_1", "status", "is_customer", *andere_flags])
    bp_vals = ", ".join(
        [":pid", ":tid", ":pn", ":name", "'active'", "TRUE", *("FALSE" for _ in andere_flags)]
    )

    with engine.begin() as v:
        for haus, name in ((HAUS_A, "Haus A"), (HAUS_B, "Haus B")):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "n": name},
            )
        for partner_id, haus, nr, name, cust_id in (
            (partner_a, HAUS_A, nr_a, "Kunde A", cust_a),
            (partner_b, HAUS_B, nr_b, "Kunde B", cust_b),
        ):
            v.execute(
                text(
                    f"INSERT INTO domain_crm.business_partners ({bp_cols}) "
                    f"VALUES ({bp_vals})"
                ),
                {"pid": partner_id, "tid": haus, "pn": f"BP-{nr}", "name": name},
            )
            v.execute(
                text(
                    "INSERT INTO public.kunden (kunden_nr, name1, strasse, plz, ort, land, tel, business_partner_id) "
                    "VALUES (:nr, :name, 'Weg 1', '12345', 'Ort', 'DE', '040-1', :pid)"
                ),
                {"nr": nr, "name": name, "pid": partner_id},
            )
            v.execute(
                text(
                    "INSERT INTO domain_crm.customers "
                    "(id, tenant_id, customer_number, company_name, is_active, business_partner_id) "
                    "VALUES (:id, :tid, :nr, :name, TRUE, :pid)"
                ),
                {"id": cust_id, "tid": haus, "nr": nr, "name": name, "pid": partner_id},
            )

    yield {"nr_a": nr_a, "nr_b": nr_b, "partner_a": partner_a, "partner_b": partner_b}

    with engine.begin() as v:
        for nr in (nr_a, nr_b):
            v.execute(text("DELETE FROM public.kunden_ansprechpartner WHERE kunden_nr = :n"), {"n": nr})
            v.execute(text("DELETE FROM public.kunden_crm360 WHERE kunden_nr = :n"), {"n": nr})
            v.execute(text("DELETE FROM public.kunden WHERE kunden_nr = :n"), {"n": nr})
        v.execute(
            text("DELETE FROM domain_crm.customers WHERE tenant_id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )
        v.execute(
            text("DELETE FROM domain_crm.business_partners WHERE tenant_id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )


def test_lookup_zeigt_nur_eigenen_mandanten(client, zwei_mandanten):
    eigen = client.get(
        "/api/v1/crm/customers/lookup?limit=200", headers=_kopf(HAUS_A)
    )
    assert eigen.status_code == 200, eigen.text
    nrs = {row.get("kunden_nr") for row in eigen.json()}
    assert zwei_mandanten["nr_a"] in nrs
    assert zwei_mandanten["nr_b"] not in nrs


def test_kim_liste_und_fremder_kunde_404(client, zwei_mandanten):
    liste = client.get("/api/v1/crm/kim/customers?limit=200", headers=_kopf(HAUS_A))
    assert liste.status_code == 200, liste.text
    ids = {row.get("id") for row in liste.json()}
    assert zwei_mandanten["nr_a"] in ids
    assert zwei_mandanten["nr_b"] not in ids

    fremd = client.get(
        f"/api/v1/crm/kim/customers/{zwei_mandanten['nr_b']}", headers=_kopf(HAUS_A)
    )
    assert fremd.status_code in (200, 404)
    if fremd.status_code == 200:
        assert fremd.json() is None or fremd.json() == {}


def test_kim_update_und_kontakt_fremder_mandant_404(client, zwei_mandanten):
    put = client.put(
        f"/api/v1/crm/kim/customers/{zwei_mandanten['nr_b']}",
        headers=_kopf(HAUS_A),
        json={"street": "Hackstrasse"},
    )
    assert put.status_code == 404, put.text

    kontakte = client.get(
        f"/api/v1/crm/kim/customers/{zwei_mandanten['nr_b']}/contacts",
        headers=_kopf(HAUS_A),
    )
    assert kontakte.status_code == 404, kontakte.text

    anlegen = client.post(
        f"/api/v1/crm/kim/customers/{zwei_mandanten['nr_b']}/contacts",
        headers=_kopf(HAUS_A),
        json={"name": "Fremd", "firstName": "X"},
    )
    assert anlegen.status_code == 404, anlegen.text


def test_kunde_finden_ohne_mandant_und_fremd(engine, zwei_mandanten):
    from sqlalchemy.orm import sessionmaker

    from app.api.v1.endpoints.crm_360_sql import _kunde_finden

    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        assert _kunde_finden(db, zwei_mandanten["nr_a"], HAUS_A) is not None
        assert _kunde_finden(db, zwei_mandanten["nr_b"], HAUS_A) is None
        assert _kunde_finden(db, zwei_mandanten["nr_a"], None) is None
    finally:
        db.close()


def test_merge_fremder_mandant_scheitert(engine, zwei_mandanten):
    from sqlalchemy.orm import sessionmaker

    from app.services.crm_merge_service import CrmMergeService, MergeError

    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        svc = CrmMergeService(db, HAUS_A)
        with pytest.raises(MergeError):
            svc.preview(zwei_mandanten["nr_a"], zwei_mandanten["nr_b"])
    finally:
        db.close()


def test_unverbundener_bestandskunde_ist_404(client, engine):
    """public.kunden ohne Partner/Customers-Bezug ist kein Mandantenobjekt mehr."""
    nummer = f"ORPH-{uuid.uuid4().hex[:6].upper()}"
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO public.kunden (kunden_nr, name1, strasse, plz, ort, land, tel) "
                "VALUES (:nr, 'Waise', 'Dorf 1', '11111', 'X', 'DE', '000')"
            ),
            {"nr": nummer},
        )
    try:
        antwort = client.get(f"/api/v1/crm/customers/{nummer}", headers=_kopf(HAUS_A))
        assert antwort.status_code == 404, antwort.text
    finally:
        with engine.begin() as v:
            v.execute(text("DELETE FROM public.kunden WHERE kunden_nr = :n"), {"n": nummer})
