"""Manuelle Hauptbuchbuchung und Zahlungslauf an der Approval Engine (APPROVAL-001).

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import approvals, docflow, journal_entries, payment_runs
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.exceptions import ConflictError, register_domain_exception_handlers
from app.core.freigabe import anforderung
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from app.services.finance_freigabe import HauptbuchFreigabe, ZahlungslaufFreigabe
from app.services.finance_transaction_service import FinanceTransactionService
from testgrenze import ersetze_mandant

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["FINANCE_ADMIN", "SALES_BEARBEITEN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CLARA = {"sub": "clara", "name": "c.onken", "roles": ["FINANCE_ADMIN"]}
VERKAUF = {"sub": "vera", "name": "v.kruse", "roles": ["SALES_ADMIN"]}

AUFRAEUMEN = (
    "DELETE FROM domain_shared.blockchain_anchors WHERE tenant_id = :t",
    "DELETE FROM domain_erp.payment_run_items WHERE tenant_id = :t",
    "DELETE FROM domain_erp.payment_runs WHERE tenant_id = :t",
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approval_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approvals WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
    "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


class _Buchungen:
    """Der Buchungsweg der Hauptbuch-Endpunkte, ohne den Abhaengigkeitsbehaelter der Anwendung."""

    def __init__(self, mandant: str) -> None:
        self.mandant = mandant

    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        with SessionLocal() as db:
            FinanceTransactionService(db, tenant_id).post(entry_id)
        return True

    async def reverse_entry(self, entry_id: str, reason: str, tenant_id: str):
        with SessionLocal() as db:
            _, storno = FinanceTransactionService(db, tenant_id).reverse(entry_id, reason)
            db.refresh(storno)
            return storno

    async def get_by_id(self, entry_id: str, tenant_id: str):
        with SessionLocal() as db:
            from app.infrastructure.models import JournalEntry
            eintrag = db.get(JournalEntry, entry_id)
            _ = eintrag.lines
            db.expunge_all()
            return eintrag


@pytest.fixture
def haus(monkeypatch):
    mandant = f"hz-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        richte_skr03_ein(db, mandant)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    monkeypatch.setattr(journal_entries.container, "resolve", lambda _art: _Buchungen(mandant))
    monkeypatch.setattr(journal_entries, "log_fibu_audit", lambda *_a, **_k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(journal_entries.router, prefix="/journal-entries")
    app.include_router(payment_runs.router)
    app.include_router(docflow.router, prefix="/docflow")
    app.include_router(approvals.router, prefix="/approvals")
    ersetze_mandant(app, mandant)
    client = TestClient(app, raise_server_exceptions=False)

    def als(nutzer: dict) -> TestClient:
        app.dependency_overrides[get_current_user] = lambda: nutzer
        return client

    yield {"mandant": mandant, "als": als}
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


def _konto(mandant: str, nummer: str) -> str:
    with SessionLocal() as db:
        return str(db.execute(text(
            "SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id = :t AND account_number = :n"),
            {"t": mandant, "n": nummer}).scalar())


def _buchung(haus, betrag: str = "250.00") -> str:
    """Eine manuelle Buchung im Entwurf."""
    with SessionLocal() as db:
        eintrag = FinanceTransactionService(db, haus["mandant"]).create(
            entry_number=f"MB-{uuid.uuid4().hex[:8]}", description="Umbuchung", entry_date=datetime(2026, 10, 13),
            reference=f"UMB-{uuid.uuid4().hex[:6]}", source="manual",
            lines=[{"account_id": _konto(haus["mandant"], "1400"), "debit_amount": Decimal(betrag), "credit_amount": Decimal("0")},
                   {"account_id": _konto(haus["mandant"], "8400"), "debit_amount": Decimal("0"), "credit_amount": Decimal(betrag)}])
        return str(eintrag.id)


def _stand(tabelle: str, kennung: str) -> str:
    with SessionLocal() as db:
        return db.execute(text(f"SELECT status FROM domain_erp.{tabelle} WHERE id = :id"), {"id": kennung}).scalar()  # nosec B608


def _frage(haus, wer: dict, subjekt: str, kennung: str, aktion: str = "post"):
    return haus["als"](wer).post(f"/approvals/{subjekt}/{kennung}", json={"action": aktion})


def _entscheide(haus, wer: dict, subjekt: str, kennung: str, fid: str):
    return haus["als"](wer).post(f"/approvals/{subjekt}/{kennung}/{fid}/decision", json={"granted": True})


# ── Matrix ────────────────────────────────────────────────────────────────────

def test_hauptbuch_und_zahlung_in_der_matrix():
    assert anforderung("manual_journal", "post", brutto=Decimal("0.01"), gebucht=False).risiko == "R3"
    assert anforderung("manual_journal", "reverse", brutto=Decimal("1"), gebucht=True).risiko == "R4"
    assert anforderung("manual_journal", "reverse", brutto=Decimal("1"), gebucht=False).risiko == "R2"
    assert anforderung("payment_run", "post", brutto=Decimal("1"), gebucht=False).risiko == "R4"


# ── Manuelle Hauptbuchbuchung ─────────────────────────────────────────────────

def test_die_manuelle_buchung_bucht_erst_mit_der_zweiten_person(haus):
    eintrag = _buchung(haus)
    ohne = haus["als"](ANNA).post(f"/journal-entries/{eintrag}/post")
    assert ohne.status_code == 409 and "Freigabe erforderlich (R3)" in ohne.text and "Manuelle Hauptbuchbuchung" in ohne.text
    assert _stand("journal_entries", eintrag) == "draft"

    assert _frage(haus, VERKAUF, "journal_entry", eintrag).status_code == 403  # der Verkauf fragt keine Hauptbuchbuchung an
    fid = _frage(haus, ANNA, "journal_entry", eintrag).json()["id"]
    assert _entscheide(haus, ANNA, "journal_entry", eintrag, fid).status_code == 403   # Funktionstrennung
    assert _entscheide(haus, VERKAUF, "journal_entry", eintrag, fid).status_code == 403  # keine Finanzrolle
    assert _entscheide(haus, BERND, "journal_entry", eintrag, fid).status_code == 200
    gebucht = haus["als"](ANNA).post(f"/journal-entries/{eintrag}/post")
    assert gebucht.status_code == 200, gebucht.text
    assert _stand("journal_entries", eintrag) == "posted"


def test_storno_einer_gebuchten_buchung_braucht_die_erhoehte_freigabe(haus):
    eintrag = _buchung(haus)
    fid = _frage(haus, ANNA, "journal_entry", eintrag).json()["id"]
    assert _entscheide(haus, BERND, "journal_entry", eintrag, fid).status_code == 200
    assert haus["als"](ANNA).post(f"/journal-entries/{eintrag}/post").status_code == 200

    ohne = haus["als"](CLARA).post(f"/journal-entries/{eintrag}/reverse", params={"reason": "Falsches Konto"})
    assert ohne.status_code == 409 and "Freigabe erforderlich (R4)" in ohne.text
    assert _stand("journal_entries", eintrag) == "posted"
    fid = _frage(haus, ANNA, "journal_entry", eintrag, "reverse").json()["id"]
    assert _entscheide(haus, BERND, "journal_entry", eintrag, fid).status_code == 403  # R4: nur die Finanzleitung
    assert _entscheide(haus, CLARA, "journal_entry", eintrag, fid).status_code == 200
    storno = haus["als"](ANNA).post(f"/journal-entries/{eintrag}/reverse", params={"reason": "Falsches Konto"})
    assert storno.status_code == 200, storno.text
    assert _stand("journal_entries", eintrag) == "reversed"


def test_eine_geaenderte_buchung_verliert_ihre_freigabe(haus):
    eintrag = _buchung(haus)
    fid = _frage(haus, ANNA, "journal_entry", eintrag).json()["id"]
    assert _entscheide(haus, BERND, "journal_entry", eintrag, fid).status_code == 200
    with SessionLocal() as db:  # Betrag nach der Freigabe geaendert
        db.execute(text("UPDATE domain_erp.journal_entry_lines SET debit_amount = debit_amount * 4, credit_amount = credit_amount * 4 "
                        "WHERE journal_entry_id = :id"), {"id": eintrag})
        db.commit()
    antwort = haus["als"](ANNA).post(f"/journal-entries/{eintrag}/post")
    assert antwort.status_code == 409 and "Freigabe erforderlich" in antwort.text
    assert _stand("journal_entries", eintrag) == "draft"


def test_die_buchung_eines_belegs_wird_nicht_ueber_das_hauptbuch_storniert(haus):
    """Sonst bliebe der Beleg „gebucht", waehrend seine Buchung zurueckgenommen ist — an Beleg und Freigabe vorbei."""
    nummer = f"DF-{uuid.uuid4().hex[:8]}"
    beleg = haus["als"](ANNA).post("/docflow/", json={
        "doc_type": "sales_invoice", "doc_number": nummer, "status": "open", "customer_id": "kunde-1",
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 100, "tax_code": "3"}]})
    assert beleg.status_code == 200, beleg.text
    assert haus["als"](ANNA).post(f"/docflow/{beleg.json()['id']}/post",
                                  json={"idempotency_key": f"b-{uuid.uuid4().hex}"}).status_code == 200
    with SessionLocal() as db:
        buchung = str(db.execute(text(
            "SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t AND (reference = :n OR document_number = :n)"),
            {"t": haus["mandant"], "n": nummer}).scalar())
    antwort = haus["als"](CLARA).post(f"/journal-entries/{buchung}/reverse", params={"reason": "am Beleg vorbei"})
    assert antwort.status_code == 409 and "Belegweg" in antwort.text
    assert _stand("journal_entries", buchung) == "posted"


# ── Zahlungslauf ──────────────────────────────────────────────────────────────

def _zahlungslauf(haus, ersteller: str = "anna") -> str:
    lauf = f"zl-{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.payment_runs (id, tenant_id, run_number, execution_date, initiator_name, initiator_iban, "
            "total_amount, payment_count, status, created_by, created_at, updated_at) "
            "VALUES (:id, :t, :nr, DATE '2026-10-20', 'Testhaus', 'DE02120300000000202051', 1500, 1, 'draft', :wer, NOW(), NOW())"),
            {"id": lauf, "t": haus["mandant"], "nr": lauf.upper(), "wer": ersteller})
        db.execute(text(
            "INSERT INTO domain_erp.payment_run_items (id, tenant_id, payment_run_id, creditor_id, creditor_name, iban, amount, "
            "purpose, invoice_number, status, created_at, updated_at) "
            "VALUES (:id, :t, :lauf, 'lieferant-1', 'Lieferant', 'DE89370400440532013000', 1500, 'RE-1', 'RE-1', 'pending', NOW(), NOW())"),
            {"id": f"{lauf}-1", "t": haus["mandant"], "lauf": lauf})
        db.commit()
    return lauf


def test_die_zahlungsfreigabe_ist_eine_freigabe_der_engine(haus):
    lauf = _zahlungslauf(haus, ersteller="anna")
    selbst = haus["als"](ANNA).post(f"/payment-runs/{lauf}/approve")
    assert selbst.status_code == 409 and "Vier-Augen" in selbst.text
    frei = haus["als"](CLARA).post(f"/payment-runs/{lauf}/approve")
    assert frei.status_code == 200, frei.text
    assert _stand("payment_runs", lauf) == "approved"
    freigaben = haus["als"](CLARA).get(f"/approvals/payment_run/{lauf}").json()
    assert [(f["risk"], f["status"], f["requested_by"], f["decided_by"]) for f in freigaben] == [("R4", "granted", "anna", "clara")]

    # Aendert sich nach der Freigabe ein Empfaenger, gilt sie nicht mehr.
    with SessionLocal() as db:
        engine = ZahlungslaufFreigabe(db, haus["mandant"])
        assert engine.gueltige_fuer(engine.vorgang(lauf, "post"), "post") is not None
        db.execute(text("UPDATE domain_erp.payment_run_items SET iban = 'DE75512108001245126199' WHERE payment_run_id = :l"), {"l": lauf})
        db.commit()
        with pytest.raises(ConflictError) as fehler:
            engine.verlange_fuer(engine.vorgang(lauf, "post"), "post", "clara")
        db.rollback()
    assert "Freigabe erforderlich (R4)" in str(fehler.value.detail)
    ausfuehren = haus["als"](CLARA).post(f"/payment-runs/{lauf}/execute", json={"executed_by": "x"})
    assert ausfuehren.status_code == 409 and "Freigabe erforderlich (R4)" in ausfuehren.text
    assert _stand("payment_runs", lauf) == "approved"


def test_ein_lauf_der_nur_den_status_traegt_wird_nicht_ausgefuehrt(haus):
    """Wer den Status an der Engine vorbei auf freigegeben setzt, hat keine Zahlungsfreigabe."""
    lauf = _zahlungslauf(haus)
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_erp.payment_runs SET status = 'approved', approved_by = 'irgendwer' WHERE id = :l"), {"l": lauf})
        db.commit()
    antwort = haus["als"](CLARA).post(f"/payment-runs/{lauf}/execute", json={"executed_by": "x"})
    assert antwort.status_code == 409 and "Freigabe erforderlich (R4)" in antwort.text


def test_nur_die_finanzleitung_gibt_zahlungen_frei_und_nur_finanzrollen_sehen_sie(haus):
    lauf = _zahlungslauf(haus)
    with SessionLocal() as db:
        engine = ZahlungslaufFreigabe(db, haus["mandant"])
        v = engine.vorgang(lauf, "post")
        assert engine.freigaberollen(v, "R4") == {"FINANCE_ADMIN", "admin"}
        haupt = HauptbuchFreigabe(db, haus["mandant"])
        assert "FINANCE_BEARBEITEN" in haupt.freigaberollen(v, "R3") and "FINANCE_BEARBEITEN" not in haupt.freigaberollen(v, "R4")
        db.rollback()
    assert haus["als"](VERKAUF).get(f"/approvals/payment_run/{lauf}").status_code == 403
    assert haus["als"](BERND).get(f"/approvals/payment_run/{lauf}").status_code == 200
