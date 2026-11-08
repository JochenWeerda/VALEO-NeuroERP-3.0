"""Gemeinsame Buchungsvorlagen: lesbar und anwendbar fuer alle Mandanten, nicht aenderbar.

Nutzerentscheidung 27.10.2026; Migration rls_booking_templates_shared_20261027.
Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt; valeo_app).
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from decimal import Decimal

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, ROOT, SYSTEM

pytestmark = pytest.mark.integration

TEMPLATES = "domain_erp.booking_templates"
ACCOUNTS = "domain_erp.chart_of_accounts"
SCHEMAS = ("domain_erp", "domain_finance", "domain_shared")
LINES = [
    {"account_number": "9810", "debit_percentage": "100", "credit_percentage": "0", "line_number": 1},
    {"account_number": "9820", "debit_percentage": "0", "credit_percentage": "100", "line_number": 2},
]


def _template(conn, tenant: str, name: str) -> str:
    return support.insert_row(conn, TEMPLATES, tenant, name=name, category="GENERAL", trigger_type="MANUAL",
                              lines=json.dumps(LINES), currency="EUR", active=True, default_amount=100)


def _account(conn, tenant: str, number: str) -> str:
    return support.insert_row(conn, ACCOUNTS, tenant, account_number=number, account_name=f"Konto {number}",
                              account_type="asset", is_active=True)


@pytest.fixture(scope="module")
def probe():
    with support.probe((TEMPLATES, ACCOUNTS)) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        for schema in SCHEMAS:
            conn.execute(sa.text(f"GRANT USAGE ON SCHEMA {schema} TO valeo_app"))
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {schema} TO valeo_app"))
        rows = {
            "shared": _template(conn, SYSTEM, "RLS gemeinsame Vorlage"),
            "own": _template(conn, A, "RLS eigene Vorlage"),
            "foreign": _template(conn, B, "RLS fremde Vorlage"),
            # Gemeinsamer Kontenrahmen fuer beide Konten, Mandant A hat 9810 zusaetzlich selbst.
            "system_9810": _account(conn, SYSTEM, "9810"),
            "system_9820": _account(conn, SYSTEM, "9820"),
            "a_9810": _account(conn, A, "9810"),
        }
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_freigabe_ist_begruendet_und_form_stimmt(db):
    conn, _ = db
    exceptions = json.loads((ROOT / "docs" / "admin" / "rls-exceptions.json").read_text(encoding="utf-8"))
    assert TEMPLATES in exceptions["system_lesbar"]
    assert support.shape(conn, TEMPLATES) == ("getrennt_system", "")


def test_gemeinsame_vorlagen_lesbar_aber_nicht_aenderbar(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        assert {rows["own"], rows["shared"]} <= support.keys(conn, TEMPLATES)
        assert rows["foreign"] not in support.keys(conn, TEMPLATES)
        for sql, params in (
            (f"UPDATE {TEMPLATES} SET name = 'x' WHERE id = :i", {}),
            (f"UPDATE {TEMPLATES} SET tenant_id = :a WHERE id = :i", {"a": A}),
            (f"DELETE FROM {TEMPLATES} WHERE id = :i", {}),
        ):
            assert support.affected(conn, sql, {"i": rows["shared"], **params}) == 0
        assert "row-level security" in support.rejected_insert_with(
            conn, TEMPLATES, SYSTEM, name="neu", category="GENERAL", trigger_type="MANUAL",
            lines=json.dumps(LINES), currency="EUR", active=True)
        assert "row-level security" in support.rejected(
            conn, f"UPDATE {TEMPLATES} SET tenant_id = 'system' WHERE id = :i", {"i": rows["own"]})
    with tenant_scope(B, "test"):
        assert rows["shared"] in support.keys(conn, TEMPLATES)
        assert rows["own"] not in support.keys(conn, TEMPLATES)
    assert support.keys(conn, TEMPLATES) == set()  # ohne Mandant auch keine gemeinsamen
    assert support.as_owner(conn, f"SELECT name, tenant_id FROM {TEMPLATES} WHERE id = :i",
                            {"i": rows["shared"]}) == [("RLS gemeinsame Vorlage", SYSTEM)]


def test_fachkette_gemeinsame_vorlage_anwenden(db):
    from app.api.v1.endpoints import booking_templates as ep

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    run = asyncio.run
    try:
        with tenant_scope(A, "test"):
            listed = {t.id: t for t in run(ep.list_booking_templates(None, True, tenant_id=A, db=session))}
            assert listed[rows["shared"]].shared and not listed[rows["own"]].shared
            assert rows["foreign"] not in listed
            applied = run(ep.apply_booking_template(
                rows["shared"], ep.ApplyTemplateRequest(entry_date=date(2026, 10, 27), amount=Decimal("250")),
                tenant_id=A, db=session, http_request=None))
            entry = conn.execute(sa.text("SELECT tenant_id, total_debit FROM domain_erp.journal_entries WHERE id = :i"),
                                 {"i": applied.journal_entry_id}).one()
            assert entry.tenant_id == A and Decimal(str(entry.total_debit)) == Decimal("250")
            accounts = {r.line_number: str(r.account_id) for r in conn.execute(sa.text(
                "SELECT line_number, account_id FROM domain_erp.journal_entry_lines WHERE journal_entry_id = :i "
                "AND tenant_id = :a"), {"i": applied.journal_entry_id, "a": A})}
            # eigenes Konto vor dem gemeinsamen Kontenrahmen
            assert accounts == {1: rows["a_9810"], 2: rows["system_9820"]}
            for call in (
                lambda: ep.update_booking_template(rows["shared"], ep.BookingTemplateUpdate(name="x"),
                                                   tenant_id=A, db=session),
                lambda: ep.delete_booking_template(rows["shared"], tenant_id=A, db=session),
            ):
                with pytest.raises(HTTPException) as exc:
                    run(call())
                assert exc.value.status_code == 403
        with tenant_scope(B, "test"):
            for call in (
                lambda: ep.get_booking_template(rows["own"], tenant_id=B, db=session),
                lambda: ep.update_booking_template(rows["own"], ep.BookingTemplateUpdate(name="x"),
                                                   tenant_id=B, db=session),
                lambda: ep.delete_booking_template(rows["own"], tenant_id=B, db=session),
            ):
                with pytest.raises(HTTPException) as exc:
                    run(call())
                assert exc.value.status_code == 404
            assert run(ep.get_booking_template(rows["shared"], tenant_id=B, db=session)).shared
    finally:
        session.close()
