"""Der Mandant fuer die Sichtpruefung laesst sich wiederholbar einrichten und traegt danach die Referenzbelege.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services import docflow_service

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture
def kennung(monkeypatch):
    mandant = f"sp-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    yield mandant
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in (
            "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
            "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
            "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
            "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.approval_log WHERE tenant_id = :t",
            "DELETE FROM domain_docflow.approvals WHERE tenant_id = :t",
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
            db.execute(text(sql), {"t": mandant})
        db.commit()


def test_einrichten_ist_wiederholbar_und_reicht_fuer_die_referenzbelege(kennung):
    einrichten = _modul("sichtpruefung_mandant_einrichten")
    belege = _modul("referenzbelege_anlegen")
    with SessionLocal() as db:
        erster = einrichten.richte_ein(db, kennung, "Sichtpruefung Test")
        db.commit()
        assert erster["mandant"] is True and erster["konto_1400"] is True
        assert erster["steuerschluessel"] == ["2", "3", "8", "9"]
        zweiter = einrichten.richte_ein(db, kennung, "Sichtpruefung Test")
        db.commit()
        # Ein zweiter Lauf legt nichts mehr an.
        assert (zweiter["mandant"], zweiter["konto_1400"], zweiter["steuerschluessel"], zweiter["konten"]) == (
            False, False, [], [])
        assert belege.fehlende_voraussetzungen(db, kennung) == []
        assert len(belege.lege_an(db, kennung)) == 17


def test_ohne_apply_bleibt_nichts_zurueck(kennung):
    einrichten = _modul("sichtpruefung_mandant_einrichten")
    with SessionLocal() as db:
        einrichten.richte_ein(db, kennung, "Sichtpruefung Test")
        db.rollback()
        assert db.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id = :t"), {"t": kennung}).scalar() == 0
