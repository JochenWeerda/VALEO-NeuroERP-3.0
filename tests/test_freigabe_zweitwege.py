"""Die Buchungswege neben DocFlow gehen durch dieselbe Kontroll-Engine (FIN-CONTROL-001).

Routine bucht die Buchhaltung selbst; Auffaelliges steht im Pruefkorb; nur ein kritischer Befund sperrt.

Geprueft gegen die echte Datenbank: Eingangsrechnung der Finanzbuchhaltung, Verkaufsgutschrift, alter Rechnungsweg
und der gemeinsame Freigabeweg ``/approvals``.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import (
    ap_approval_workflow, ap_invoices, approvals, docflow, finance_invoices, kontrolle, sales_credit_notes,
)
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from app.services.finance_freigabe import SUBJEKTE, engine_fuer
from testgrenze import ersetze_mandant

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["FINANCE_ADMIN", "SALES_BEARBEITEN", "EINKAUF_BEARBEITEN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CLARA = {"sub": "clara", "name": "c.onken", "roles": ["FINANCE_ADMIN"]}
LESER = {"sub": "lea", "name": "l.meyer", "roles": ["LAGER_LESEN"]}
CARL = {"sub": "carl", "name": "c.boekhoff", "roles": ["controller"]}

AUFRAEUMEN = (
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.control_findings WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approval_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approvals WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
    # Archivstuecke des alten Rechnungswegs lassen sich nicht loeschen; ihr Kopf bleibt stehen.
    "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t AND source_system <> 'gobd_artifact'",
    "DELETE FROM domain_sales.sales_credit_note_lines WHERE credit_note_id IN "
    "(SELECT id FROM domain_sales.sales_credit_notes WHERE tenant_id = :t)",
    "DELETE FROM domain_sales.sales_credit_notes WHERE tenant_id = :t",
    "DELETE FROM documents WHERE CAST(data AS jsonb)->>'tenantId' = :t",
    "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


@pytest.fixture
def haus(monkeypatch):
    mandant = f"zw-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        richte_skr03_ein(db, mandant)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        db.commit()

    async def freigegeben(*_a, **_k):  # Der Freigabeablauf des AP-Moduls ist hier nicht Gegenstand.
        return SimpleNamespace(can_post=True, status="approved", required_approvals=1, current_approvals=1)

    monkeypatch.setattr(ap_approval_workflow, "get_approval_status", freigegeben)
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    monkeypatch.setattr(sales_credit_notes, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    monkeypatch.setattr(finance_invoices, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(ap_invoices.router)
    app.include_router(sales_credit_notes.router)
    app.include_router(finance_invoices.router)
    app.include_router(docflow.router, prefix="/docflow")
    app.include_router(approvals.router, prefix="/approvals")
    app.include_router(kontrolle.router, prefix="/kontrolle")
    ersetze_mandant(app, mandant)
    aktuell: dict = {}

    @app.middleware("http")
    async def _claims(request, call_next):  # noqa: ANN001, ANN202
        # Wie die echte Bearer-Pruefung: die gepruefte Identitaet liegt im Request (FiBu-Audit liest sie dort).
        if aktuell:
            request.state.token_claims = {"sub": aktuell["sub"], "preferred_username": aktuell.get("name"),
                                          "roles": list(aktuell.get("roles") or [])}
        return await call_next(request)

    client = TestClient(app, raise_server_exceptions=False)

    def als(nutzer: dict) -> TestClient:
        aktuell.clear()
        aktuell.update(nutzer)
        app.dependency_overrides[get_current_user] = lambda: nutzer
        return client

    yield {"mandant": mandant, "als": als}
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


def _buchungen(haus) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"),
                          {"t": haus["mandant"]}).scalar()


def _log(haus, subjekt: str, kennung: str) -> list[tuple[str, str]]:
    with SessionLocal() as db:
        return [tuple(z) for z in db.execute(text(
            "SELECT event, actor FROM domain_docflow.approval_log WHERE tenant_id = :t AND subject_type = :s "
            "AND subject_id = :id ORDER BY logged_at, id"), {"t": haus["mandant"], "s": subjekt, "id": kennung}).fetchall()]


def _frage(haus, wer: dict, subjekt: str, kennung: str, aktion: str = "post"):
    return haus["als"](wer).post(f"/approvals/{subjekt}/{kennung}", json={"action": aktion})


def _entscheide(haus, wer: dict, subjekt: str, kennung: str, fid: str):
    return haus["als"](wer).post(f"/approvals/{subjekt}/{kennung}/{fid}/decision", json={"granted": True})


# ── Eingangsrechnung der Finanzbuchhaltung ────────────────────────────────────

def _korb(haus) -> list[tuple[str, str, str]]:
    antwort = haus["als"](CARL).get("/kontrolle/befunde")
    assert antwort.status_code == 200, antwort.text
    return sorted((b["subject_type"], b["code"], b["severity"]) for b in antwort.json())


def _eingangsrechnung(haus, wer: dict, preis: float = 100, datum: str = "2026-10-13") -> str:
    nummer = f"ER-{uuid.uuid4().hex[:8]}"
    antwort = haus["als"](wer).post("/ap/invoices/", json={
        "number": nummer, "date": datum, "customerId": "lieferant-1", "dueDate": "2026-11-12",
        "lines": [{"article": "Miete", "qty": 1, "price": preis, "taxCode": "9"}]})
    assert antwort.status_code == 201, antwort.text
    with SessionLocal() as db:
        # Das Anlegen setzt das Tagesdatum; fuer die Tests zaehlt das angegebene.
        db.execute(text(
            "UPDATE documents SET data = jsonb_set(jsonb_set(CAST(data AS jsonb), '{status}', '\"FREIGEGEBEN\"'), "
            "'{date}', to_jsonb(CAST(:d AS text))) WHERE doc_type = 'ap_invoice' AND doc_number = :n"),
            {"n": nummer, "d": datum})
        db.commit()
    return nummer


def _buche_er(haus, wer: dict, nummer: str):
    return haus["als"](wer).post(f"/ap/invoices/{nummer}/post", params={"posted_by": "x"})


def test_als_buchender_steht_wer_angemeldet_ist_nicht_wer_in_der_anfrage_steht(haus):
    nummer = _eingangsrechnung(haus, ANNA)
    assert haus["als"](ANNA).post(f"/ap/invoices/{nummer}/post", params={"posted_by": "jemand-anderes"}).status_code == 200
    assert haus["als"](ANNA).post(f"/ap/invoices/{_eingangsrechnung(haus, ANNA, 70)}/post").status_code == 200  # ohne Angabe
    with SessionLocal() as db:
        wer = db.execute(text("SELECT CAST(data AS jsonb)->>'postedBy' FROM documents WHERE doc_number = :n"),
                         {"n": nummer}).scalar()
    assert wer == "anna"


def test_die_wiederkehrende_finanzrechnung_bucht_die_buchhaltung_selbst(haus):
    for monat in ("2026-08-13", "2026-09-13", "2026-10-13"):
        assert _buche_er(haus, ANNA, _eingangsrechnung(haus, ANNA, 1000, monat)).status_code == 200
    assert _buchungen(haus) == 3 and _korb(haus) == []
    # Mehr als 10 % ueber dem ueblichen Betrag: gebucht, aber der Controller sieht es.
    teurer = _eingangsrechnung(haus, ANNA, 1150, "2026-11-13")
    assert _buche_er(haus, ANNA, teurer).status_code == 200
    assert _korb(haus) == [("finance_ap_invoice", "abweichung_ueblich", "warnung")]
    # Innerhalb von 10 % faellt nichts auf.
    assert _buche_er(haus, ANNA, _eingangsrechnung(haus, ANNA, 1050, "2026-12-13")).status_code == 200
    assert len(_korb(haus)) == 1 and _buchungen(haus) == 5


def test_die_doppelte_finanzrechnung_sperrt_bis_zur_unabhaengigen_freigabe(haus):
    assert _buche_er(haus, ANNA, _eingangsrechnung(haus, ANNA, 500)).status_code == 200
    doppelt = _eingangsrechnung(haus, ANNA, 500)                     # derselbe Lieferant, Betrag und Tag
    gesperrt = _buche_er(haus, ANNA, doppelt)
    assert gesperrt.status_code == 409 and "Mögliche Dublette" in gesperrt.text
    assert _buchungen(haus) == 1

    fid = _frage(haus, ANNA, "finance_ap_invoice", doppelt).json()["id"]
    selbst = _entscheide(haus, ANNA, "finance_ap_invoice", doppelt, fid)   # angelegt und angefragt
    assert selbst.status_code == 403 and "Funktionstrennung" in selbst.text
    assert _entscheide(haus, LESER, "finance_ap_invoice", doppelt, fid).status_code == 403
    assert _entscheide(haus, CARL, "finance_ap_invoice", doppelt, fid).status_code == 200   # der Controller
    assert _buche_er(haus, ANNA, doppelt).status_code == 200
    assert _buchungen(haus) == 2
    assert ("finance_ap_invoice", "dublette", "kritisch") in _korb(haus)
    ereignisse = _log(haus, "finance_ap_invoice", doppelt)
    assert ereignisse[0] == ("approval_request", "anna") and ereignisse[-2:] == [("approval_grant", "carl"), ("approval_consume", "anna")]


def test_auch_der_kernel_bucht_routine_und_sperrt_die_dublette(haus):
    from app.services.ap_invoice_kernel_posting import post_ap_invoice_kernel_sync

    erste = _eingangsrechnung(haus, ANNA, 700)
    with SessionLocal() as db:
        post_ap_invoice_kernel_sync(db, invoice_id=erste, tenant_id=haus["mandant"], posted_by="kernel")
    assert _buchungen(haus) == 1
    doppelt = _eingangsrechnung(haus, ANNA, 700)
    with SessionLocal() as db:
        post_ap_invoice_kernel_sync(db, invoice_id=doppelt, tenant_id=haus["mandant"], posted_by="kernel")
    assert _buchungen(haus) == 1


# ── Verkaufsgutschrift ────────────────────────────────────────────────────────

def _gutschrift(haus, netto: float, rechnung: str | None = "RE-1") -> str:
    gs = f"gu-{uuid.uuid4().hex[:8]}"
    brutto = round(netto * 1.19, 2)
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_sales.sales_credit_notes "
            "(id, tenant_id, credit_note_number, customer_id, invoice_reference, reason, total_amount, status, correction_type) "
            "VALUES (:id, :t, :nr, 'kunde-1', :re, 'Retoure', :total, 'draft', 'rechnungskorrektur')"),
            {"id": gs, "t": haus["mandant"], "nr": gs.upper(), "re": rechnung, "total": brutto})
        db.execute(text(
            "INSERT INTO domain_sales.sales_credit_note_lines "
            "(id, credit_note_id, line_number, description, quantity, unit_price, tax_code, tax_rate, line_total) "
            "VALUES (:id, :gs, 1, 'Position', 1, :netto, '3', 19, :netto)"), {"id": f"{gs}-1", "gs": gs, "netto": netto})
        db.commit()
    return gs


def test_die_gutschrift_mit_rechnungsbezug_ist_routine_auf_beiden_buchungswegen(haus):
    assert haus["als"](ANNA).post(f"/sales/credit-notes/{_gutschrift(haus, 100)}/post").status_code == 200
    kommando = haus["als"](ANNA).post(f"/sales/credit-notes/{_gutschrift(haus, 100, 'RE-2')}/actions/buchen", json={"_mode": "execute"})
    assert kommando.json().get("success") is True, kommando.text
    assert _buchungen(haus) == 2 and _korb(haus) == []


def test_grosse_und_gestueckelte_gutschriften_sieht_der_controller(haus):
    assert haus["als"](ANNA).post(f"/sales/credit-notes/{_gutschrift(haus, 1000, 'RE-A')}/post").status_code == 200  # 1.190 EUR
    _gutschrift(haus, 500, "RE-B")
    assert haus["als"](ANNA).post(f"/sales/credit-notes/{_gutschrift(haus, 500, 'RE-B')}/post").status_code == 200   # zusammen 1.190
    assert _korb(haus) == [("sales_credit_note", "betrag", "warnung"), ("sales_credit_note", "stueckelung", "warnung")]


def test_die_gutschrift_ohne_rechnungsbezug_ueber_der_schwelle_ist_gesperrt(haus):
    ohne = _gutschrift(haus, 1000, None)
    gesperrt = haus["als"](ANNA).post(f"/sales/credit-notes/{ohne}/post")
    assert gesperrt.status_code == 409 and "ohne Bezugsrechnung" in gesperrt.text
    assert _buchungen(haus) == 0
    fid = _frage(haus, ANNA, "sales_credit_note", ohne).json()["id"]
    assert _entscheide(haus, ANNA, "sales_credit_note", ohne, fid).status_code == 403
    assert _entscheide(haus, BERND, "sales_credit_note", ohne, fid).status_code == 200
    assert haus["als"](ANNA).post(f"/sales/credit-notes/{ohne}/post").status_code == 200
    # Klein und ohne Bezug: Routine.
    assert haus["als"](ANNA).post(f"/sales/credit-notes/{_gutschrift(haus, 100, None)}/post").status_code == 200


# ── Alter Rechnungsweg ────────────────────────────────────────────────────────

def _alte_rechnung(nummer: str, preis: float, status: str = "VERSENDET") -> dict:
    return {"number": nummer, "date": "2026-10-13", "customerId": "kunde-1", "dueDate": "2026-11-12", "status": status,
            "lines": [{"article": "Weizen", "qty": 1, "price": preis, "taxCode": "3"}]}


def test_der_alte_rechnungsweg_bucht_und_storniert_mit_rollenrecht(haus):
    klein, gross = f"AR-{uuid.uuid4().hex[:8]}", f"AR-{uuid.uuid4().hex[:8]}"
    assert haus["als"](ANNA).post("/finance/invoices", json=_alte_rechnung(klein, 100)).status_code == 200
    assert haus["als"](ANNA).post("/finance/invoices", json=_alte_rechnung(gross, 9000)).status_code == 200  # 10.710 EUR
    assert _buchungen(haus) == 2
    # Ein regelkonformer Storno: ohne zweite Person.
    storno = haus["als"](ANNA).post(f"/finance/invoices/{klein}/storno")
    assert storno.status_code == 200, storno.text
    assert _buchungen(haus) == 3


def test_der_alte_weg_storniert_keine_docflow_rechnung(haus):
    """Bis 13.10.2026 fand er ihre Buchung ueber die Nummer und nahm sie ohne Beleg zurueck."""
    nummer = f"DF-{uuid.uuid4().hex[:8]}"
    beleg = haus["als"](ANNA).post("/docflow/", json={
        "doc_type": "sales_invoice", "doc_number": nummer, "status": "open", "customer_id": "kunde-1",
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 100, "tax_code": "3"}]})
    assert beleg.status_code == 200, beleg.text
    doc = beleg.json()["id"]
    assert haus["als"](ANNA).post(f"/docflow/{doc}/post", json={"idempotency_key": f"b-{uuid.uuid4().hex}"}).status_code == 200
    antwort = haus["als"](CLARA).post(f"/finance/invoices/{nummer}/storno")
    assert antwort.status_code == 409 and "DocFlow-Beleg" in antwort.text
    with SessionLocal() as db:
        assert db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"), {"id": doc}).scalar() == "posted"
    assert _buchungen(haus) == 1


# ── Gemeinsamer Freigabeweg ───────────────────────────────────────────────────

def test_der_gemeinsame_weg_kennt_jeden_bereich_und_nur_den_eigenen_mandanten(haus):
    engine_fuer("docflow_document", None, "x")
    assert set(SUBJEKTE) == {"docflow_document", "finance_ap_invoice", "sales_credit_note", "finance_sales_invoice",
                             "journal_entry", "payment_run", "journal_import", "einkauf_credit_memo",
                             "einkauf_debit_memo"}
    nummer = _eingangsrechnung(haus, ANNA)
    assert haus["als"](ANNA).get("/approvals/lohnabrechnung/x").status_code == 404
    assert haus["als"](ANNA).get(f"/approvals/finance_ap_invoice/{uuid.uuid4().hex}").status_code == 404
    assert haus["als"](LESER).get(f"/approvals/finance_ap_invoice/{nummer}").status_code == 200
    assert _frage(haus, LESER, "finance_ap_invoice", nummer).status_code == 403  # Lesen ist nicht Buchen
    assert _frage(haus, ANNA, "finance_ap_invoice", nummer).status_code == 409   # Routine: nichts freizugeben
    with SessionLocal() as db:
        from app.core.exceptions import EntityNotFoundError
        with pytest.raises(EntityNotFoundError):
            engine_fuer("finance_ap_invoice", db, "anderer-mandant").vorgang(nummer, "post")
        db.rollback()
