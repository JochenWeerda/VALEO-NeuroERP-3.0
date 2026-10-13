"""Freigabe fuer Buchen und Stornieren (APPROVAL-001): Matrix, Funktionstrennung, Bindung an den Inhalt.

Die Matrix ohne Datenbank; die Engine gegen die echte Datenbank ueber die DocFlow-Wege und den Dienst.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import docflow
from app.core.database import SessionLocal
from app.core.exceptions import ConflictError
from app.core.freigabe import STANDARDGRENZEN, anforderung, wirksame_grenze
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from app.services.docflow_service import DocflowService
from testgrenze import ersetze_mandant

D = Decimal


# ── Die Matrix (ohne Datenbank) ───────────────────────────────────────────────

@pytest.mark.parametrize("belegart,brutto,risiko", [
    ("sales_invoice", "10000.00", "R2"), ("sales_invoice", "10000.01", "R3"),
    ("purchase_invoice", "5000.00", "R2"), ("purchase_invoice", "5000.01", "R3"),
    ("sales_credit_memo", "0.01", "R3"), ("sales_credit_memo", "1000.00", "R3"), ("sales_credit_memo", "1000.01", "R4"),
    ("purchase_credit_memo", "1000.00", "R3"), ("purchase_credit_memo", "2500.00", "R4"),
    ("sales_order", "999999", "R2"), ("sales_delivery", "999999", "R2"), ("pos_receipt", "999999", "R2"),
])
def test_buchen_nach_betrag(belegart, brutto, risiko):
    assert anforderung(belegart, "post", brutto=D(brutto), gebucht=False).risiko == risiko


def test_stornieren_gebuchtes_ist_immer_r4_ungebuchtes_rollenrecht():
    for art in ("sales_invoice", "purchase_invoice"):
        assert anforderung(art, "reverse", brutto=D("1"), gebucht=True).risiko == "R4"
        assert anforderung(art, "reverse", brutto=D("99999"), gebucht=False).risiko == "R2"
    assert anforderung("sales_order", "reverse", brutto=D("99999"), gebucht=True).risiko == "R2"


def test_eingangsrechnung_ohne_abgleich_und_stueckelung_brauchen_die_zweite_person():
    ohne = anforderung("purchase_invoice", "post", brutto=D("10"), gebucht=False, abgleich_in_ordnung=False,
                       abgleich_hinweis="Position 1: Preis 12 weicht von 10 ab")
    assert ohne.risiko == "R3" and "Preis 12 weicht von 10 ab" in ohne.grund
    # Zwei Gutschriften zu 600 EUR aus derselben Rechnung zaehlen wie 1.200 EUR.
    assert anforderung("sales_credit_memo", "post", brutto=D("600"), gebucht=False, brutto_des_vorgangs=D("1200")).risiko == "R4"
    assert anforderung("sales_invoice", "post", brutto=D("6000"), gebucht=False, brutto_des_vorgangs=D("12000")).risiko == "R3"
    assert anforderung("sales_invoice", "post", brutto=D("6000"), gebucht=False, brutto_des_vorgangs=D("6000")).risiko == "R2"


def test_der_mandant_setzt_die_grenze_nur_enger():
    assert wirksame_grenze("ausgangsrechnung", None) == STANDARDGRENZEN["ausgangsrechnung"] == D("10000")
    assert wirksame_grenze("ausgangsrechnung", D("2500")) == D("2500")
    assert wirksame_grenze("ausgangsrechnung", D("1000000")) == D("10000")
    assert wirksame_grenze("gutschrift", D("-1")) == D("1000")


# ── Die Engine ────────────────────────────────────────────────────────────────

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["SALES_BEARBEITEN", "EINKAUF_BEARBEITEN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CLARA = {"sub": "clara", "name": "c.onken", "roles": ["FINANCE_ADMIN"]}
ADMIN = {"sub": "anna", "name": "a.petersen", "roles": ["admin"]}  # dieselbe Person, andere Rolle
LAGER = {"sub": "lars", "name": "l.janssen", "roles": ["LAGER_ADMIN", "SALES_BEARBEITEN"]}
DIENST = {"sub": "svc-1", "name": "service-account-erp", "roles": ["admin"],
          "raw": {"preferred_username": "service-account-erp"}}

AUFRAEUMEN = (
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
)


@pytest.fixture
def haus(monkeypatch):
    mandant = f"fg-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        richte_skr03_ein(db, mandant)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    app.include_router(docflow.router, prefix="/docflow")
    ersetze_mandant(app, mandant)
    client = TestClient(app, raise_server_exceptions=False)

    def als(nutzer: dict) -> TestClient:
        app.dependency_overrides[docflow.get_current_user] = lambda: nutzer
        return client

    yield {"mandant": mandant, "als": als}
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


def _beleg(haus, wer: dict, doc_type: str, preis: float, *, status: str = "open", menge: float = 1) -> dict:
    einkauf = doc_type.startswith("purchase")
    rumpf = {"doc_type": doc_type, "doc_number": f"F-{uuid.uuid4().hex[:8]}", "status": status,
             "supplier_id" if einkauf else "customer_id": "partner-1",
             "items": [{"article_number": "A-1", "quantity": menge, "unit_price": preis, "tax_code": "9" if einkauf else "3"}]}
    antwort = haus["als"](wer).post("/docflow/", json=rumpf)
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def _buche(haus, wer: dict, doc_id: str):
    return haus["als"](wer).post(f"/docflow/{doc_id}/post", json={"idempotency_key": f"buchen-{uuid.uuid4().hex}"})


def _storniere(haus, wer: dict, doc_id: str):
    return haus["als"](wer).post(f"/docflow/{doc_id}/reverse",
                                 json={"idempotency_key": f"storno-{uuid.uuid4().hex}", "reason": "Falscher Kunde"})


def _frage(haus, wer: dict, doc_id: str, aktion: str = "post"):
    return haus["als"](wer).post(f"/docflow/{doc_id}/approvals", json={"action": aktion, "reason": "bitte freigeben"})


def _entscheide(haus, wer: dict, doc_id: str, freigabe_id: str, erteilt: bool = True):
    return haus["als"](wer).post(f"/docflow/{doc_id}/approvals/{freigabe_id}/decision", json={"granted": erteilt})


def _buchungen(haus) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"),
                          {"t": haus["mandant"]}).scalar()


def _status(doc_id: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"), {"id": doc_id}).scalar()


def _protokoll(doc_id: str) -> list[tuple[str, str]]:
    with SessionLocal() as db:
        return [tuple(z) for z in db.execute(text(
            "SELECT command, actor FROM domain_docflow.document_command_log WHERE header_id = :id AND command LIKE 'approval%' "
            "ORDER BY logged_at, id"), {"id": doc_id}).fetchall()]


def test_unter_der_grenze_bucht_das_rollenrecht(haus):
    rechnung = _beleg(haus, ANNA, "sales_invoice", 8000)  # 9.520 EUR brutto
    assert _buche(haus, ANNA, rechnung["id"]).status_code == 200
    assert _frage(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 100)["id"]).status_code == 409


def test_ueber_der_grenze_bucht_erst_die_freigabe_einer_zweiten_person(haus):
    rechnung = _beleg(haus, ANNA, "sales_invoice", 9000)  # 10.710 EUR brutto
    doc = rechnung["id"]
    ohne = _buche(haus, ANNA, doc)
    assert ohne.status_code == 409 and "Freigabe erforderlich (R3)" in ohne.json()["detail"]
    assert _buchungen(haus) == 0 and _status(doc) == "open"

    anfrage = _frage(haus, ANNA, doc)
    assert anfrage.status_code == 200, anfrage.text
    fid = anfrage.json()["id"]
    assert (anfrage.json()["status"], anfrage.json()["risk"], anfrage.json()["requested_by"]) == ("requested", "R3", "anna")
    # Eine zweite Anfrage ist dieselbe.
    assert _frage(haus, ANNA, doc).json()["id"] == fid
    # Angefragt ist nicht freigegeben.
    assert _buche(haus, ANNA, doc).status_code == 409

    # Funktionstrennung: nicht die Antragstellerin, auch nicht als Administratorin; kein Dienstkonto; keine Rolle ohne Recht.
    for wer in (ANNA, ADMIN, DIENST, LAGER):
        nein = _entscheide(haus, wer, doc, fid)
        assert nein.status_code == 403, (wer["roles"], nein.text)
    assert "Funktionstrennung" in _entscheide(haus, ADMIN, doc, fid).json()["detail"]
    assert _buche(haus, ANNA, doc).status_code == 409

    ja = _entscheide(haus, BERND, doc, fid)
    assert ja.status_code == 200 and (ja.json()["status"], ja.json()["decided_by"]) == ("granted", "bernd")
    assert _buche(haus, ANNA, doc).status_code == 200
    assert _status(doc) == "posted" and _buchungen(haus) == 1
    freigaben = haus["als"](ANNA).get(f"/docflow/{doc}/approvals").json()
    assert [f["status"] for f in freigaben] == ["consumed"]
    befehle = _protokoll(doc)
    assert befehle[0] == ("approval_request", "anna") and befehle[-2:] == [("approval_grant", "bernd"), ("approval_consume", "anna")]
    assert [b for b in befehle if b[0] == "approval_refused"] and len(befehle) >= 7


def test_eine_aenderung_nach_der_freigabe_macht_sie_ungueltig(haus):
    rechnung = _beleg(haus, ANNA, "sales_invoice", 9000, status="draft")
    doc = rechnung["id"]
    fid = _frage(haus, ANNA, doc).json()["id"]
    assert _entscheide(haus, BERND, doc, fid).status_code == 200
    geaendert = haus["als"](ANNA).put(f"/docflow/{doc}", json={
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 9500, "tax_code": "3"}]})
    assert geaendert.status_code == 200, geaendert.text
    antwort = _buche(haus, ANNA, doc)
    assert antwort.status_code == 409 and "Freigabe erforderlich" in antwort.json()["detail"]
    assert _buchungen(haus) == 0
    # Die alte Anfrage laesst sich auch nicht mehr fuer den neuen Inhalt benutzen.
    neu = _frage(haus, ANNA, doc).json()
    assert neu["id"] != fid and float(neu["amount"]) == 11305.0
    stand = {f["id"]: f["status"] for f in haus["als"](ANNA).get(f"/docflow/{doc}/approvals").json()}
    assert stand == {fid: "invalidated", neu["id"]: "requested"}


def test_eine_freigabe_laeuft_ab_und_eine_abgelehnte_gilt_nicht(haus):
    doc = _beleg(haus, ANNA, "sales_invoice", 9000)["id"]
    fid = _frage(haus, ANNA, doc).json()["id"]
    assert _entscheide(haus, BERND, doc, fid).status_code == 200
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_docflow.approvals SET expires_at = now() - interval '1 minute' WHERE id = :id"), {"id": fid})
        db.commit()
    assert _buche(haus, ANNA, doc).status_code == 409 and _buchungen(haus) == 0

    zweite = _beleg(haus, ANNA, "sales_invoice", 9000)["id"]
    fid2 = _frage(haus, ANNA, zweite).json()["id"]
    assert _entscheide(haus, BERND, zweite, fid2, erteilt=False).json()["status"] == "denied"
    assert _buche(haus, ANNA, zweite).status_code == 409
    assert _entscheide(haus, CLARA, zweite, fid2).status_code == 409  # entschieden ist entschieden


def test_wer_den_beleg_angelegt_hat_gibt_ihn_nicht_frei(haus):
    doc = _beleg(haus, BERND | {"roles": ["admin"]}, "sales_invoice", 9000)["id"]  # Bernd legt an
    fid = _frage(haus, ANNA, doc).json()["id"]                                      # Anna fragt an
    nein = _entscheide(haus, BERND, doc, fid)
    assert nein.status_code == 403 and "Funktionstrennung" in nein.json()["detail"]
    assert _entscheide(haus, CLARA, doc, fid).status_code == 200


def test_gutschrift_braucht_immer_die_zweite_person_ueber_1000_die_erhoehte(haus):
    klein = _beleg(haus, ANNA, "sales_credit_memo", 100)["id"]
    assert "Freigabe erforderlich (R3)" in _buche(haus, ANNA, klein).json()["detail"]
    fid = _frage(haus, ANNA, klein).json()["id"]
    assert _entscheide(haus, BERND, klein, fid).status_code == 200
    assert _buche(haus, ANNA, klein).status_code == 200

    gross = _beleg(haus, ANNA, "sales_credit_memo", 2000, menge=1)["id"]
    anfrage = _frage(haus, ANNA, gross).json()
    assert anfrage["risk"] == "R4"
    nein = _entscheide(haus, BERND, gross, anfrage["id"])  # Buchhaltung ohne erhoehte Berechtigung
    assert nein.status_code == 403 and "R4" in nein.json()["detail"]
    assert _entscheide(haus, CLARA, gross, anfrage["id"]).status_code == 200
    assert _buche(haus, ANNA, gross).status_code == 200


def test_stueckelung_unter_die_grenze_zaehlt_wie_der_gesamtbetrag(haus):
    rechnung = _beleg(haus, ANNA, "sales_invoice", 2000, menge=1)
    assert _buche(haus, ANNA, rechnung["id"]).status_code == 200
    pos = rechnung["items"][0]["id"]

    def gutschrift(menge: float) -> str:
        antwort = haus["als"](ANNA).post(f"/docflow/{rechnung['id']}/convert", json={
            "target_doc_type": "sales_credit_memo", "idempotency_key": f"gs-{uuid.uuid4().hex}",
            "quantities_by_source_item_id": {pos: menge}})
        assert antwort.status_code == 200, antwort.text
        return antwort.json()["target_doc_id"]

    erste = gutschrift(0.3)   # 714 EUR brutto
    assert _frage(haus, ANNA, erste).json()["risk"] == "R3"
    zweite = gutschrift(0.3)  # zusammen 1.428 EUR
    anfrage = _frage(haus, ANNA, zweite).json()
    assert anfrage["risk"] == "R4"


def test_storno_eines_gebuchten_belegs_braucht_die_erhoehte_freigabe(haus):
    doc = _beleg(haus, ANNA, "sales_invoice", 100)["id"]
    assert _buche(haus, ANNA, doc).status_code == 200
    ohne = _storniere(haus, CLARA, doc)
    assert ohne.status_code == 409 and "Freigabe erforderlich (R4)" in ohne.json()["detail"]
    assert _status(doc) == "posted" and _buchungen(haus) == 1
    assert _frage(haus, ANNA, doc, "reverse").status_code == 403  # Sachbearbeitung fragt keinen Storno an
    fid = _frage(haus, BERND, doc, "reverse").json()["id"]
    assert _entscheide(haus, BERND, doc, fid).status_code == 403
    assert _entscheide(haus, CLARA, doc, fid).status_code == 200
    # Die Freigabe gilt fuer den Storno, nicht fuer etwas anderes.
    assert _storniere(haus, BERND, doc).status_code == 200
    assert _status(doc) == "reversed" and _buchungen(haus) == 2


def test_eingangsrechnung_ohne_bestellung_oder_mit_preisabweichung_braucht_die_zweite_person(haus):
    frei = _beleg(haus, ANNA, "purchase_invoice", 100)["id"]
    ohne = _buche(haus, ANNA, frei)
    assert ohne.status_code == 409 and "ohne Bestellung oder Wareneingang" in ohne.json()["detail"]

    bestellung = _beleg(haus, ANNA, "purchase_order", 100, menge=10)

    def rechnung(menge: float) -> str:
        antwort = haus["als"](ANNA).post(f"/docflow/{bestellung['id']}/convert", json={
            "target_doc_type": "purchase_invoice", "idempotency_key": f"er-{uuid.uuid4().hex}",
            "quantities_by_source_item_id": {bestellung["items"][0]["id"]: menge}})
        assert antwort.status_code == 200, antwort.text
        return antwort.json()["target_doc_id"]

    passend = rechnung(4)
    assert _buche(haus, ANNA, passend).status_code == 200  # 476 EUR, Preis und Menge wie bestellt
    abweichend = rechnung(4)
    with SessionLocal() as db:  # Der Lieferant berechnet mehr als bestellt.
        db.execute(text("UPDATE domain_docflow.document_items SET unit_price = 112 WHERE header_id = :id"), {"id": abweichend})
        db.commit()
    antwort = _buche(haus, ANNA, abweichend)
    assert antwort.status_code == 409 and "Preis 112" in antwort.json()["detail"]
    assert _buchungen(haus) == 1


def test_die_grenze_des_mandanten_gilt_nur_wenn_sie_enger_ist(haus):
    def setze(wert: str) -> None:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_shared.system_properties WHERE tenant_id = :t AND property_key = :k"),
                       {"t": haus["mandant"], "k": "freigabe.grenze.ausgangsrechnung"})
            db.execute(text(
                "INSERT INTO domain_shared.system_properties (id, tenant_id, property_key, property_value) "
                "VALUES (:id, :t, 'freigabe.grenze.ausgangsrechnung', :w)"),
                {"id": str(uuid.uuid4()), "t": haus["mandant"], "w": wert})
            db.commit()

    setze("500")
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 1000)["id"]).status_code == 409
    setze("1000000")
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 9000)["id"]).status_code == 409
    setze("unlesbar")
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 9000)["id"]).status_code == 409
    assert _buchungen(haus) == 0


def test_die_freigabe_gilt_in_jedem_zugang_auch_im_dienst_selbst(haus):
    """Ein Skript oder ein kuenftiges MCP-Werkzeug, das den Dienst direkt ruft, kommt nicht an der Freigabe vorbei."""
    doc = _beleg(haus, ANNA, "sales_invoice", 9000)["id"]
    with SessionLocal() as db:
        with pytest.raises(ConflictError) as fehler:
            DocflowService(db, haus["mandant"], "skript").post_document(
                doc, docflow.DocflowPostRequest(idempotency_key=f"direkt-{uuid.uuid4().hex}"))
        db.rollback()
    assert "Freigabe erforderlich (R3)" in str(fehler.value.detail)
    assert _buchungen(haus) == 0 and _status(doc) == "open"


def test_freigaben_eines_anderen_mandanten_gibt_es_nicht(haus):
    doc = _beleg(haus, ANNA, "sales_invoice", 9000)["id"]
    fid = _frage(haus, ANNA, doc).json()["id"]
    from app.services.docflow_freigabe import DocflowFreigabe
    from app.core.exceptions import EntityNotFoundError
    with SessionLocal() as db:
        with pytest.raises(EntityNotFoundError):
            DocflowFreigabe(db, "anderer-mandant").entscheide(doc, fid, CLARA, True)
        db.rollback()
    assert haus["als"](ANNA).get(f"/docflow/{uuid.uuid4()}/approvals").status_code == 404
