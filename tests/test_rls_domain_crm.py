"""RLS-Domain CRM: Geschaeftspartner, Details, Kontakte, Segmente, Chancen und Protokolle als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt). Die Tabellen der
Dienste unter services/* gehoeren nicht dazu.
"""

from __future__ import annotations

import asyncio
import importlib

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

PARTNERS = "domain_crm.business_partners"
CONSENTS, CONSENT_HISTORY = "domain_crm.crm_contact_consents", "domain_crm.crm_contact_consent_history"
SEGMENTS, SEGMENT_MEMBERS = "domain_crm.crm_segments", "domain_crm.crm_segment_members"
CONTACTS, FARM_PROFILES = "public.crm_contacts", "public.crm_betriebsprofile"
CANCEL_REASONS, OPPORTUNITY = "domain_crm.cancellation_reason", "domain_crm.opportunity"
SUPPLIER_TAX = "domain_crm.supplier_tax_profiles"
PARTNER_CHILDREN = tuple(f"domain_crm.business_partner_{name}" for name in (
    "addresses", "billing_configs", "community_members", "contacts", "cooperative_memberships", "cpd_accounts",
    "discount_items", "dispatch_media", "email_distributions", "instructions", "interest_settings",
    "interface_profiles", "price_agreements", "pricing_rules", "profiles"))
HEADS = (PARTNERS, "domain_crm.credit_limits", SEGMENTS, CANCEL_REASONS, OPPORTUNITY, CONTACTS,
         "public.crm_merge_log", "public.crm_ownership_log", "public.opportunities")
# Kind -> (Spalte, Eltern, Elternschluessel)
LINKS = {
    **{child: ("partner_id", PARTNERS, "partner_id") for child in PARTNER_CHILDREN},
    SUPPLIER_TAX: ("supplier_id", PARTNERS, "partner_id"),
    CONSENT_HISTORY: ("consent_id", CONSENTS, "id"),
    SEGMENT_MEMBERS: ("segment_id", SEGMENTS, "id"),
    FARM_PROFILES: ("contact_id", CONTACTS, "id"),
    OPPORTUNITY: ("cancel_reason_id", CANCEL_REASONS, "cancel_reason_id"),
}
ISOLATED = HEADS + PARTNER_CHILDREN + (CONSENT_HISTORY, SEGMENT_MEMBERS, FARM_PROFILES)
SEEDED = HEADS + tuple(t for t in LINKS if t not in HEADS)


def _link_values(rows: dict, table: str, tenant: str) -> dict:
    if table not in LINKS:
        return {}
    column, parent, key = LINKS[table]
    return {column: rows["full", parent, tenant][key]}


def _key(conn, table: str) -> str:
    return support.primary_key(conn, table)


def _fresh_link(conn, table: str, tenant: str) -> dict:
    """Neuer Elternsatz: mehrere Partnerdetails sind 1:1 (eindeutige partner_id)."""
    if table not in LINKS:
        return {}
    column, parent, key = LINKS[table]
    return {column: support.seed_row(conn, parent, tenant)[key]}


def _other_keys(rows: dict, table: str) -> dict:
    # Gemeinschaften sind mandantenlos (Klasse D); das Mitglied braucht eine bestehende.
    if table.endswith("community_members"):
        return {"community_id": rows["full", table, A]["community_id"]}
    return {}


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (CONSENTS, SUPPLIER_TAX, "domain_crm.business_partner_communities",
                                   "domain_crm.crm_consents", "domain_erp.offene_posten")) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            # Eltern zuerst, damit Kinder an den Zeilen desselben Mandanten haengen.
            for table in (PARTNERS, CONSENTS, SEGMENTS, CONTACTS, CANCEL_REASONS) + SEEDED:
                if (table, tenant) not in rows:
                    # Kontakte liest der Router als ORM mit Aufzaehlungstyp.
                    typed = {"type": "CUSTOMER"} if table == CONTACTS else {}
                    full = support.seed_row(conn, table, tenant, **_link_values(rows, table, tenant), **typed)
                    rows["full", table, tenant] = full
                    rows[table, tenant] = str(full[_key(conn, table)])
        for _column, parent, key in set(LINKS.values()):
            rows["spare", parent, B] = support.seed_row(conn, parent, B)[key]
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_policy_formen(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    key = _key(conn, table)

    def new_row(tenant):
        return support.insert_row(conn, table, tenant, key, **_fresh_link(conn, table, tenant),
                                  **_other_keys(rows, table))

    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM],
                                    key=key, new_row=new_row)


@pytest.mark.parametrize("child", list(LINKS))
def test_kein_kind_unter_fremdem_eltern(db, child):
    conn, rows = db
    column, parent, key = LINKS[child]
    foreign = rows["spare", parent, B]
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, child, A, _key(conn, child), **{column: foreign},
                                               **_other_keys(rows, child))
        assert constraint in message, message
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE {_key(conn, child)} = :i",
                                   {"p": foreign, "i": rows[child, A]})
        assert constraint in message, message


def test_kind_erbt_den_mandanten_vom_kontext(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        row = support.seed_row(conn, SEGMENT_MEMBERS, None, segment_id=rows[SEGMENTS, A])
        assert row["tenant_id"] == A
        row = support.seed_row(conn, "domain_crm.business_partner_addresses", None, partner_id=rows[PARTNERS, A])
        assert row["tenant_id"] == A


def test_eltern_mit_kindern_behaelt_seinen_mandanten(db):
    conn, rows = db
    for parent in (PARTNERS, SEGMENTS, CONTACTS, CONSENTS, CANCEL_REASONS):
        key = _key(conn, parent)
        message = support.as_owner_rejected(conn, f"UPDATE {parent} SET tenant_id = :b WHERE {key} = :i",
                                            {"b": B, "i": rows[parent, A]})
        assert "_tenant" in message, (parent, message)


def test_kontextwechsel_savepoint_hintergrund_pool(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, PARTNERS, rows[PARTNERS, A], rows[PARTNERS, B], "partner_id")
    support.assert_background_needs_explicit_context(conn, CONTACTS, rows[CONTACTS, A], rows[CONTACTS, B])
    support.assert_pool_reuse_keeps_no_tenant()


def test_fachkette_crm_router_nur_eigener_mandant(db):
    import app.infrastructure.models  # noqa: F401  # ORM-Fremdschluessel
    crm = importlib.import_module("app.crm.router")

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    run = asyncio.run
    try:
        with tenant_scope(A, "test"):
            assert {str(c.id) for c in run(crm.list_contacts(db=session, tenant_id=A))} == {rows[CONTACTS, A]}
            with pytest.raises(HTTPException) as exc:
                run(crm.get_contact(rows[CONTACTS, B], db=session, tenant_id=A))
            assert exc.value.status_code == 404
            export = run(crm.gdpr_data_export(rows[PARTNERS, A], db=session, tenant_id=A))
            assert export["business_partner"]["partner_id"] == rows[PARTNERS, A]
            with pytest.raises(HTTPException) as exc:
                run(crm.gdpr_data_export(rows[PARTNERS, B], db=session, tenant_id=A))
            assert exc.value.status_code == 404
    finally:
        session.close()


# --- ohne Datenbank -----------------------------------------------------------------------------

def test_crm_router_nimmt_den_mandanten_aus_dem_token():
    from app.core import tenant

    crm = importlib.import_module("app.crm.router")

    assert crm.get_tenant_id is tenant.get_tenant_id
    app = FastAPI()
    app.include_router(crm.router, prefix="/api/v1")
    app.dependency_overrides[crm.get_db] = lambda: None
    # Vorher galt der Kopf X-Tenant, ohne ihn der Mandant "default".
    antwort = TestClient(app).get("/api/v1/crm/contacts", headers={"X-Tenant": B})
    assert antwort.status_code in (401, 403), antwort.text


def test_dsgvo_kurzweg_meldet_keinen_schein_erfolg():
    crm = importlib.import_module("app.crm.router")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(crm.gdpr_anonymize("bp-1", reason="Antrag des Betroffenen", tenant_id=A))
    assert exc.value.status_code == 409
    assert "erasure-requests" in exc.value.detail


@pytest.mark.parametrize("service", ["crm_merge_service.CrmMergeService", "crm_ownership_service.CrmOwnershipService"])
@pytest.mark.parametrize("tenant", [None, ""])
def test_crm_dienste_ohne_standardmandant(service, tenant):
    module, cls = service.split(".")
    with pytest.raises(ValueError):
        getattr(importlib.import_module(f"app.services.{module}"), cls)(None, tenant)
