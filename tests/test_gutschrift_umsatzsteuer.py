"""Verkaufsgutschrift in DocFlow: Umsatzsteuer je Position, Erloes netto, Steuer getrennt, Forderung brutto.

Fachliche Entscheidung vom 12.10.2026 (unveraendert):
1. Steuersatz je Position ueber den Steuerschluessel, nicht pauschal je Gutschrift.
2. Netto, Umsatzsteuer und Brutto getrennt fuehren.
3. Das Erloeskonto wird nur netto belastet, die Umsatzsteuer auf ihrem Konto berichtigt.
4. Keine stillschweigende Steuerannahme: fehlt eine Angabe, wird nicht gebucht, sondern zur Pruefung vorgelegt.

Seit 09.11.2026 (BELEG-052) liegt die Gutschrift in DocFlow (Belegart ``sales_credit_memo``); der Altspeicher
``domain_sales.sales_credit_notes`` und seine Maske ``sales/gutschrift`` entfielen. Die Agentenwerkzeuge
``sales.gutschrift.*`` arbeiten auf der DocFlow-Gutschrift: Entwurf, Vorschlag, Freigabe durch einen Menschen,
genau eine Buchung. Geprueft gegen die echte Datenbank.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import gutschrift_vorschlaege
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.finance.steuerschluessel import richte_skr03_ein
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = pytest.mark.integration

AUFRAEUMEN = (
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
    "DELETE FROM public.agent_proposals WHERE tenant_id = :t",
    "DELETE FROM public.mcp_tool_executions WHERE tenant_id = :t",
)


@pytest.fixture
def haus():
    from test_belege_lesen import AUFRAEUMEN as BELEGE

    lauf = uuid.uuid4().hex[:6]
    mandant, kunde = f"gu-{lauf}", str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": mandant})
        richte_skr03_ein(db, mandant)  # Schluessel 2 (7 %), 3 (19 %) mit Erloes- und Steuerkonto
        # Finance bucht nur auf eigene Konten des Mandanten: das Forderungskonto dazu (wie test_freigabe).
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            "is_active) VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        for code, name, satz, ust, erloes, rc in (("1", "Steuerfrei (Test)", 0, None, "8400", False),
                                                  ("94", "Reverse Charge", 0, None, "8400", True)):
            db.execute(text(
                "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, gueltig_von, "
                " credit_account, revenue_account, reverse_charge, par_24_ustg) "
                "VALUES (:id, :t, :code, :name, :satz, DATE '2021-01-01', :ust, :erloes, :rc, false)"),
                {"id": f"gu-{lauf}-sk{code}", "t": mandant, "code": code, "name": name, "satz": satz, "ust": ust,
                 "erloes": erloes, "rc": rc})
        db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                        "VALUES (:id, :t, 'kunde-1', 'Hof Gutschrift')"), {"id": kunde, "t": mandant})
        db.execute(text(
            "INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr, konto_typ, kunde_id, betrag, offen, "
            "op_status) VALUES (:id, :t, :re, 'debitoren', :k, 1500, 1500, 'offen')"),
            {"id": f"gu-{lauf}-op1", "t": mandant, "re": f"RE-{lauf}-1", "k": kunde})
        db.commit()
    _rechnung(mandant, kunde, f"RE-{lauf}-1")
    try:
        yield {"lauf": lauf, "mandant": mandant, "kunde": kunde}
    finally:
        with SessionLocal() as db:
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            # Mandant und Kunde bleiben (Kundenstamm loescht nicht hart); der Mandant ist je Lauf eindeutig.
            for sql in (*AUFRAEUMEN, *(sql for sql in BELEGE if "domain_shared.tenants" not in sql),
                        "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _rechnung(mandant: str, kunde: str, nummer: str) -> str:
    """Bezugsrechnung als DocFlow-Beleg (nur fuer die Verknuepfung Rechnung -> Gutschrift)."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    with SessionLocal() as db:
        return DocflowService(db, mandant, "pruefer").create_document(DocflowCreateRequest(
            doc_type="sales_invoice", doc_number=nummer, customer_id=kunde, items=[
                DocflowLineInput(article_number="W", quantity=1, unit_price=1260.5, tax_code="3")]))


def _gutschrift(haus, positionen: list[tuple[str | None, float]], *, mit_rechnung: bool = True) -> str:
    """``positionen`` = (Steuerschluessel, Netto); legt den DocFlow-Entwurf an wie das Werkzeug."""
    from app.services.gutschrift_docflow import lege_entwurf_an

    with SessionLocal() as db:
        beleg = lege_entwurf_an(
            db, haus["mandant"], nummer=f"GS-{haus['lauf']}-{uuid.uuid4().hex[:4]}", kunde="kunde-1",
            rechnung=f"RE-{haus['lauf']}-1" if mit_rechnung else None, akteur="pruefer",
            zeilen=[{"description": "Position", "quantity": 1, "unit_price": netto, "tax_code": code}
                    for code, netto in positionen])
        db.commit()
    return beleg


def _buchung(mandant: str) -> list[tuple[str, float, float]]:
    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT k.account_number, l.debit, l.credit FROM domain_erp.journal_entry_lines l "
            "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id "
            "JOIN domain_erp.journal_entries e ON e.id = l.journal_entry_id "
            "WHERE e.tenant_id = :t ORDER BY l.line_number"), {"t": mandant}).fetchall()
    return [(z[0], float(z[1]), float(z[2])) for z in zeilen]


def _status(beleg: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"),
                          {"id": beleg}).scalar()


def _buche(haus, beleg: str) -> None:
    from app.services.gutschrift_docflow import buche

    with SessionLocal() as db:
        buche(db, haus["mandant"], beleg, akteur="buchhaltung-1", idempotenz=f"buchen-{beleg}")
        db.commit()


def _vorschau(haus, beleg: str) -> dict:
    from app.services.gutschrift_docflow import vorschau

    with SessionLocal() as db:
        return vorschau(db, haus["mandant"], beleg)


def _pruefgrund(haus, beleg: str) -> str:
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as fehler:
        _vorschau(haus, beleg)
    assert fehler.value.status_code == 409
    return str(fehler.value.detail)


# --- Der Regelfall --------------------------------------------------------------------------


def test_1190_brutto_mit_19_prozent_und_offener_posten_gemindert(haus):
    beleg = _gutschrift(haus, [("3", 1000)])
    plan = _vorschau(haus, beleg)
    assert (plan["netto"], plan["steuer"], plan["brutto"]) == (Decimal("1000.00"), Decimal("190.00"), Decimal("1190.00"))
    _buche(haus, beleg)
    assert _buchung(haus["mandant"]) == [("8400", 1000.0, 0.0), ("1776", 190.0, 0.0), ("1400", 0.0, 1190.0)]
    assert _status(beleg) == "posted"
    with SessionLocal() as db:
        offen = db.execute(text("SELECT offen FROM domain_erp.offene_posten WHERE tenant_id = :t"),
                           {"t": haus["mandant"]}).scalar()
    assert float(offen) == pytest.approx(310.0)  # 1.500 - 1.190


def test_gemischte_saetze_werden_je_steuerschluessel_gebucht(haus):
    beleg = _gutschrift(haus, [("3", 100), ("2", 100)])
    plan = _vorschau(haus, beleg)
    assert (plan["steuer"], plan["brutto"]) == (Decimal("26.00"), Decimal("226.00"))  # 19 + 7
    assert {z["code"] for z in plan["zeilen"] if z["code"]} == {"2", "3"}


def test_steuerfreie_gutschrift_bucht_keine_umsatzsteuer(haus):
    beleg = _gutschrift(haus, [("1", 100)])
    _buche(haus, beleg)
    assert _buchung(haus["mandant"]) == [("8400", 100.0, 0.0), ("1400", 0.0, 100.0)]


def test_ohne_steuerschluessel_wird_nicht_gebucht(haus):
    beleg = _gutschrift(haus, [(None, 100)])
    assert "nicht gebucht, bitte prüfen" in _pruefgrund(haus, beleg)
    assert _buchung(haus["mandant"]) == [] and _status(beleg) == "draft"


def test_unbekannter_steuerschluessel_wird_gar_nicht_erst_angelegt(haus):
    """DocFlow prueft den Schluessel schon beim Anlegen (strenger als der Altspeicher, der erst beim Buchen pruefte)."""
    from app.core.exceptions import ValidationFailedError

    with pytest.raises(ValidationFailedError, match="Steuerschl"):
        _gutschrift(haus, [("77", 100)])


def test_reverse_charge_wird_nicht_automatisch_gebucht(haus):
    beleg = _gutschrift(haus, [("94", 100)])
    assert "nicht gebucht, bitte prüfen" in _pruefgrund(haus, beleg)


def test_doppelte_gutschriftnummer_wird_abgelehnt(haus):
    from fastapi import HTTPException

    from app.services.gutschrift_docflow import lege_entwurf_an

    nummer = f"GS-{haus['lauf']}-DOPPELT"
    with SessionLocal() as db:
        lege_entwurf_an(db, haus["mandant"], nummer=nummer, kunde="kunde-1", rechnung=None, akteur="p",
                        zeilen=[{"description": "x", "quantity": 1, "unit_price": 10, "tax_code": "3"}])
        db.commit()
        with pytest.raises(HTTPException) as fehler:
            lege_entwurf_an(db, haus["mandant"], nummer=nummer, kunde="kunde-1", rechnung=None, akteur="p",
                            zeilen=[{"description": "x", "quantity": 1, "unit_price": 10, "tax_code": "3"}])
    assert fehler.value.status_code == 409


def test_die_alte_maske_und_der_altspeicher_sind_weg():
    from app.core.screen_definitions import get_screen_definition
    from app.main import app

    assert get_screen_definition("sales/gutschrift") is None
    pfade = {getattr(r, "path", "") for r in app.routes}
    assert "/api/v1/sales/credit-notes" not in pfade and "/api/v1/sales/credit-notes/{cn_id}/post" not in pfade
    assert "/api/v1/sales/credit-notes/buchungsvorschlaege" in pfade


# --- MCP: Agent legt an und schlaegt vor, ein Mensch gibt frei, der Agent bucht genau einmal --------------------


@pytest.fixture
def mcp(haus):
    from app.api.v1.endpoints.mcp_tool_registry import get_current_user as mcp_nutzer
    from app.api.v1.endpoints.mcp_tool_registry import get_db as mcp_get_db
    from app.api.v1.endpoints.mcp_tool_registry import router as mcp_router

    werkzeuge = FastAPI()
    werkzeuge.include_router(mcp_router)
    scopes = ["sales:write"]
    werkzeuge.dependency_overrides[mcp_nutzer] = lambda: {
        "sub": "agent-7", "scopes": list(scopes), "raw": {"tenant_id": haus["mandant"]}}

    def _db():
        with SessionLocal() as db:
            yield db

    werkzeuge.dependency_overrides[mcp_get_db] = _db
    menschen = FastAPI()
    register_domain_exception_handlers(menschen)
    menschen.include_router(gutschrift_vorschlaege.router)
    ersetze_mandant(menschen, haus["mandant"])
    ersetze_nutzer(menschen, "admin")
    with TestClient(werkzeuge, raise_server_exceptions=False) as client, \
            TestClient(menschen, raise_server_exceptions=False) as mensch:
        yield {**haus, "mcp": client, "client": mensch, "scopes": scopes}


def _auftrag(mcp, **zusatz) -> dict:
    return {
        "tool_name": "sales.gutschrift.speichern",
        "parameters": {
            "credit_note_number": f"GS-{mcp['lauf']}-A", "customer_id": "kunde-1", "grund": "Retoure",
            "lines": [{"description": "Weizen", "quantity": 2, "unit_price": 500, "tax_code": "3"}],
            "reason": "Retoure laut Kundenmeldung",
        },
        **zusatz,
    }


def _gutschriften(mandant: str) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t "
                               "AND doc_type = 'sales_credit_memo'"), {"t": mandant}).scalar()


def _werkzeug(mcp, name: str, parameter: dict, **zusatz):
    return mcp["mcp"].post("/mcp/tools/call", json={"tool_name": name, "parameters": parameter, **zusatz})


def _vorschlag(mcp, beleg: str) -> str:
    antwort = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": beleg}, mode="propose",
                        idempotency_key=f"vorschlag-{beleg}")
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["approval_status"] == "pending"
    return antwort.json()["entwurf_id"]


def _als_mensch(mcp, kennung: str = "buchhaltung-1") -> None:
    from app.auth.deps import get_current_user

    mcp["client"].app.dependency_overrides[get_current_user] = lambda: {
        "sub": kennung, "name": kennung, "roles": ["FINANCE_BEARBEITEN"]}


def _stand(vorschlag: str) -> tuple:
    with SessionLocal() as db:
        return tuple(db.execute(text(
            "SELECT approval_status, reviewed_by, execution_result IS NOT NULL FROM public.agent_proposals "
            "WHERE proposal_id = :id"), {"id": vorschlag}).fetchone())


def test_mcp_trockenlauf_zeigt_die_betraege_und_schreibt_nichts(mcp):
    antwort = mcp["mcp"].post("/mcp/tools/call", json=_auftrag(mcp))
    assert antwort.status_code == 200, antwort.text
    vorschlag = antwort.json()["proposedChanges"]
    assert (vorschlag["netto"], vorschlag["steuer"], vorschlag["brutto"], vorschlag["pruefgrund"]) == (
        1000.0, 190.0, 1190.0, None)
    assert _gutschriften(mcp["mandant"]) == 0


def test_mcp_trockenlauf_nennt_den_pruefgrund_statt_einen_satz_anzunehmen(mcp):
    auftrag = _auftrag(mcp)
    del auftrag["parameters"]["lines"][0]["tax_code"]
    vorschlag = mcp["mcp"].post("/mcp/tools/call", json=auftrag).json()["proposedChanges"]
    assert (vorschlag["steuer"], vorschlag["brutto"]) == (None, None)
    assert "keinen Steuerschlüssel" in vorschlag["pruefgrund"]


def test_mcp_legt_den_docflow_entwurf_einmal_an_und_bucht_nicht(mcp):
    assert mcp["mcp"].post("/mcp/tools/call", json=_auftrag(mcp, mode="execute")).status_code == 422
    auftrag = _auftrag(mcp, mode="execute", idempotency_key=f"mcp-{mcp['lauf']}")
    erste = mcp["mcp"].post("/mcp/tools/call", json=auftrag)
    assert erste.status_code == 200, erste.text
    ergebnis = erste.json()
    assert ergebnis["success"] is True and ergebnis["auditEntryId"] and ergebnis["brutto"] == 1190.0
    assert mcp["mcp"].post("/mcp/tools/call", json=auftrag).json()["credit_note_id"] == ergebnis["credit_note_id"]
    assert _gutschriften(mcp["mandant"]) == 1
    assert _status(ergebnis["credit_note_id"]) == "draft" and _buchung(mcp["mandant"]) == []


def test_mcp_weist_mandantenangabe_und_fehlendes_recht_ab(mcp):
    fremd = _auftrag(mcp)
    fremd["parameters"]["tenant_id"] = "anderes-haus"
    assert mcp["mcp"].post("/mcp/tools/call", json=fremd).status_code == 422
    mcp["scopes"][:] = ["sales:read"]
    assert mcp["mcp"].post("/mcp/tools/call", json=_auftrag(mcp)).status_code == 403
    assert _gutschriften(mcp["mandant"]) == 0


def test_kein_vorschlag_fuer_eine_gutschrift_die_sich_nicht_buchen_laesst(mcp):
    beleg = _gutschrift(mcp, [(None, 100)])
    antwort = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": beleg}, mode="propose",
                        idempotency_key=f"vorschlag-{beleg}")
    assert antwort.status_code == 409 and "bitte prüfen" in antwort.text


def test_ohne_freigabe_bucht_der_agent_nicht(mcp):
    beleg = _gutschrift(mcp, [("3", 1000)])
    vorschlag = _vorschlag(mcp, beleg)
    antwort = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                        idempotency_key=f"buchen-{beleg}")
    assert antwort.status_code == 409 and "not approved" in antwort.text
    assert _buchung(mcp["mandant"]) == [] and _status(beleg) == "draft"


def test_mensch_gibt_frei_und_der_agent_bucht_genau_einmal(mcp):
    beleg = _gutschrift(mcp, [("3", 1000)])
    vorschau = _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": beleg}).json()
    assert [(z["soll"], z["haben"]) for z in vorschau["buchungszeilen"]] == [(1000.0, 0.0), (190.0, 0.0), (0.0, 1190.0)]
    vorschlag = _vorschlag(mcp, beleg)
    assert _werkzeug(mcp, "sales.gutschrift.propose", {"credit_note_id": beleg}, mode="propose",
                     idempotency_key=f"vorschlag-{beleg}-2").status_code == 409  # einer offen genuegt

    _als_mensch(mcp)
    liste = mcp["client"].get("/sales/credit-notes/buchungsvorschlaege", params={"status": "pending"}).json()
    assert [(v["proposal_id"], v["vorgeschlagen_von"], Decimal(v["brutto"])) for v in liste] == [
        (vorschlag, "agent-7", Decimal("1190.00"))]
    weg = f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben"
    freigabe = mcp["client"].post(weg, json={"_mode": "execute", "_idempotencyKey": f"frei-{vorschlag}"}).json()
    assert freigabe["success"] is True, freigabe
    assert _stand(vorschlag) == ("approved", "buchhaltung-1", False) and _buchung(mcp["mandant"]) == []

    auftrag = {"mode": "execute", "idempotency_key": f"buchen-{beleg}"}
    gebucht = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, **auftrag)
    assert gebucht.status_code == 200, gebucht.text
    assert gebucht.json()["posted"] is True and gebucht.json()["approved_by"] == "buchhaltung-1"
    erwartet = [("8400", 1000.0, 0.0), ("1776", 190.0, 0.0), ("1400", 0.0, 1190.0)]
    assert _buchung(mcp["mandant"]) == erwartet and _status(beleg) == "posted"
    assert _stand(vorschlag) == ("approved", "buchhaltung-1", True)
    assert _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, **auftrag).json()["replayed"] is True
    assert _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                     idempotency_key=f"buchen-{beleg}-2").status_code == 409
    assert _buchung(mcp["mandant"]) == erwartet


def test_wer_vorschlaegt_gibt_nicht_selbst_frei(mcp):
    vorschlag = _vorschlag(mcp, _gutschrift(mcp, [("3", 1000)]))
    _als_mensch(mcp, kennung="agent-7")
    ergebnis = mcp["client"].post(
        f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben", json={"_mode": "execute"}).json()
    assert ergebnis["success"] is False and "nicht selbst prüfen" in ergebnis["error"]
    assert _stand(vorschlag)[0] == "pending"


def test_ablehnung_braucht_einen_grund_und_sperrt_die_buchung(mcp):
    beleg = _gutschrift(mcp, [("3", 1000)])
    vorschlag = _vorschlag(mcp, beleg)
    _als_mensch(mcp)
    weg = f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/ablehnen"
    assert mcp["client"].post(weg, json={"_mode": "execute"}).json()["success"] is False
    mit = mcp["client"].post(weg, json={"_mode": "execute", "_auditReason": "Menge stimmt nicht"}).json()
    assert mit["success"] is True, mit
    assert _stand(vorschlag)[:2] == ("rejected", "buchhaltung-1")
    assert _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                     idempotency_key=f"buchen-{beleg}").status_code == 409
    assert _buchung(mcp["mandant"]) == [] and _status(beleg) == "draft"


def test_gebucht_wird_was_freigegeben_wurde(mcp):
    """Aendert sich die Gutschrift nach der Freigabe, bucht der Agent nicht - es braucht einen neuen Vorschlag."""
    beleg = _gutschrift(mcp, [("3", 1000)])
    vorschlag = _vorschlag(mcp, beleg)
    _als_mensch(mcp)
    assert mcp["client"].post(f"/sales/credit-notes/buchungsvorschlaege/{vorschlag}/actions/freigeben",
                              json={"_mode": "execute"}).json()["success"] is True
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_docflow.document_items SET unit_price = 2000, line_total_net = 2000, "
                        "line_total_tax = 380 WHERE header_id = :id"), {"id": beleg})
        db.commit()
    antwort = _werkzeug(mcp, "sales.gutschrift.buchen", {"proposal_id": vorschlag}, mode="execute",
                        idempotency_key=f"buchen-{beleg}")
    assert antwort.status_code == 409 and "changed after approval" in antwort.text
    assert _buchung(mcp["mandant"]) == [] and _status(beleg) == "draft"
