"""Referenzbelege fuer die Sichtpruefung: vollstaendig, echt gebucht und wiederholbar (Phase 0.7).

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid
from collections import Counter

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service


def _skript():
    pfad = pathlib.Path(__file__).resolve().parent.parent / "scripts/referenzbelege_anlegen.py"
    spec = importlib.util.spec_from_file_location("referenzbelege_anlegen", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture
def mandant(monkeypatch):
    kennung = f"rb-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": kennung})
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    yield kennung
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in (
            "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
            "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
            "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
            "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.create_request_idempotency WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_links WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
            "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
            "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
            "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
            "DELETE FROM domain_shared.tenants WHERE id = :t",
        ):
            db.execute(text(sql), {"t": kennung})
        db.commit()


def _einrichten(kennung: str) -> None:
    with SessionLocal() as db:
        richte_skr03_ein(db, kennung)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{kennung}-1400", "t": kennung})
        db.commit()


def _zaehle(kennung: str) -> dict:
    with SessionLocal() as db:
        return {
            "belege": db.execute(text(
                "SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t"), {"t": kennung}).scalar(),
            "buchungen": db.execute(text(
                "SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"), {"t": kennung}).scalar(),
            "posten": db.execute(text(
                "SELECT count(*) FROM domain_erp.offene_posten WHERE tenant_id = :t"), {"t": kennung}).scalar(),
        }


def test_ohne_voraussetzungen_wird_nichts_angelegt(mandant):
    skript = _skript()
    with SessionLocal() as db:
        fehlt = skript.fehlende_voraussetzungen(db, mandant)
        assert "Steuerschluessel 3" in fehlt and "Konto 1400 (Forderungen)" in fehlt
        with pytest.raises(RuntimeError, match="Voraussetzungen fehlen"):
            skript.lege_an(db, mandant)
    assert _zaehle(mandant) == {"belege": 0, "buchungen": 0, "posten": 0}


def test_der_satz_ist_vollstaendig_und_echt_gebucht(mandant):
    _einrichten(mandant)
    skript = _skript()
    with SessionLocal() as db:
        assert skript.fehlende_voraussetzungen(db, mandant) == []
        belege = {b["rolle"]: b for b in skript.lege_an(db, mandant)}
    assert Counter(b["doc_type"] for b in belege.values()) == Counter({
        "sales_offer": 1, "sales_order": 1, "sales_delivery": 2, "sales_invoice": 4, "sales_credit_memo": 1,
        "purchase_order": 1, "goods_receipt": 2, "purchase_invoice": 4, "purchase_credit_memo": 1,
    })
    # Unterschiedliche Staende: Entwurf, offen, gebucht, storniert.
    assert {rolle: b["status"] for rolle, b in belege.items() if "rechnung" in rolle or "gutschrift" in rolle} == {
        "vk-rechnung-1": "posted", "vk-gutschrift": "posted", "vk-rechnung-2": "open",
        "vk-rechnung-ohne-schluessel": "draft", "vk-rechnung-storno": "reversed",
        "ek-rechnung-1": "posted", "ek-gutschrift": "posted", "ek-rechnung-2": "open",
        "ek-rechnung-ohne-schluessel": "open", "ek-rechnung-storno": "reversed",
    }
    # Sechs Buchungen (zwei Rechnungen, zwei Gutschriften, zwei stornierte Rechnungen) plus zwei Stornobuchungen.
    assert _zaehle(mandant) == {"belege": 17, "buchungen": 8, "posten": 4}
    with SessionLocal() as db:
        akteure = {z[0] for z in db.execute(text(
            "SELECT DISTINCT actor FROM domain_docflow.document_status_history WHERE tenant_id = :t"), {"t": mandant})}
    assert akteure == {"referenzbelege"}


def test_ein_zweiter_lauf_verdoppelt_nichts(mandant):
    _einrichten(mandant)
    skript = _skript()
    with SessionLocal() as db:
        erste = sorted((b["rolle"], b["id"], b["status"]) for b in skript.lege_an(db, mandant))
    stand = _zaehle(mandant)
    with SessionLocal() as db:
        zweite = sorted((b["rolle"], b["id"], b["status"]) for b in skript.lege_an(db, mandant))
    assert zweite == erste
    assert _zaehle(mandant) == stand
