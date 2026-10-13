"""Kontroll-Engine der Finanzbuchhaltung (FIN-CONTROL-001) an DocFlow-Belegen.

„Der Finanzbuchhalter hat den Hut auf. Der Controller ueberwacht die Ausnahmen." Routine laeuft mit Rollenrecht;
was auffaellt, geht in den Pruefkorb; nur ein kritischer Befund sperrt bis zur unabhaengigen Freigabe.

Die Regel ohne Datenbank; die Engine gegen die echte Datenbank ueber die DocFlow-Wege und den Dienst.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import docflow, kontrolle
from app.core.database import SessionLocal
from app.core.exceptions import ConflictError
from app.core.freigabe import STANDARDGRENZEN, Befund, anforderung, wirksame_grenze
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from app.services.docflow_service import DocflowService
from testgrenze import ersetze_mandant

D = Decimal


# ── Die Regel (ohne Datenbank) ────────────────────────────────────────────────

@pytest.mark.parametrize("belegart,brutto,code", [
    ("sales_invoice", "10000.00", None), ("sales_invoice", "10000.01", "betrag"),
    ("purchase_invoice", "5000.00", None), ("purchase_invoice", "5000.01", "betrag"),
    ("sales_credit_memo", "1000.00", None), ("sales_credit_memo", "1000.01", "betrag"),
    ("purchase_credit_memo", "2500.00", "betrag"),
    ("manual_journal", "9999.99", None), ("manual_journal", "10000.00", "betrag"),
    ("sales_order", "999999", None), ("sales_delivery", "999999", None), ("pos_receipt", "999999", None),
])
def test_der_betrag_allein_sperrt_nicht_er_warnt(belegart, brutto, code):
    bedarf = anforderung(belegart, "post", brutto=D(brutto), gebucht=False)
    assert bedarf.risiko == "R2" and bedarf.zweitfreigabe is False
    assert [b.code for b in bedarf.befunde] == ([code] if code else [])
    assert all(b.schwere == "warnung" for b in bedarf.befunde)


def test_regelkonformer_storno_braucht_keine_zweite_person():
    for art in ("sales_invoice", "purchase_invoice", "manual_journal"):
        assert anforderung(art, "reverse", brutto=D("99999"), gebucht=True).risiko == "R2"


def test_ein_kritischer_befund_sperrt_unabhaengig_vom_betrag():
    dublette = Befund("dublette", "kritisch", "Mögliche Dublette der Eingangsrechnung PIV-1.")
    bedarf = anforderung("purchase_invoice", "post", brutto=D("0.01"), gebucht=False, befunde=[dublette])
    assert bedarf.risiko == "R3" and bedarf.zweitfreigabe and "Mögliche Dublette" in bedarf.grund
    # Eine Warnung des Bereichs sperrt nicht.
    warnung = Befund("storno_haeufung", "warnung", "…")
    assert anforderung("sales_invoice", "reverse", brutto=D("1"), gebucht=True, befunde=[warnung]).risiko == "R2"


def test_stueckelung_warnt_und_der_zahlungslauf_braucht_immer_die_freigabe():
    gestueckelt = anforderung("sales_credit_memo", "post", brutto=D("600"), gebucht=False, brutto_des_vorgangs=D("1200"))
    assert gestueckelt.risiko == "R2" and [b.code for b in gestueckelt.befunde] == ["stueckelung"]
    assert anforderung("payment_run", "post", brutto=D("1"), gebucht=False).risiko == "R4"


def test_die_schwelle_stellt_der_mandant_ein():
    assert wirksame_grenze("ausgangsrechnung", None) == STANDARDGRENZEN["ausgangsrechnung"] == D("10000")
    assert wirksame_grenze("ausgangsrechnung", D("2500")) == D("2500")
    assert wirksame_grenze("ausgangsrechnung", D("1000000")) == D("1000000")
    assert wirksame_grenze("gutschrift", D("-1")) == D("1000")


# ── Die Engine ────────────────────────────────────────────────────────────────

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["SALES_BEARBEITEN", "EINKAUF_BEARBEITEN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CARL = {"sub": "carl", "name": "c.boekhoff", "roles": ["controller"]}
ADMIN = {"sub": "anna", "name": "a.petersen", "roles": ["admin"]}  # dieselbe Person, andere Rolle
LAGER = {"sub": "lars", "name": "l.janssen", "roles": ["LAGER_ADMIN", "SALES_BEARBEITEN", "EINKAUF_BEARBEITEN"]}
DIENST = {"sub": "svc-1", "name": "service-account-erp", "roles": ["admin"],
          "raw": {"preferred_username": "service-account-erp"}}

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
    app.include_router(kontrolle.router, prefix="/kontrolle")
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


def _beleg(haus, wer: dict, doc_type: str, preis: float, *, status: str = "open", menge: float = 1, **kopf) -> dict:
    einkauf = doc_type.startswith("purchase")
    rumpf = {"doc_type": doc_type, "doc_number": f"F-{uuid.uuid4().hex[:8]}", "status": status,
             "supplier_id" if einkauf else "customer_id": "partner-1",
             "items": [{"article_number": "A-1", "quantity": menge, "unit_price": preis, "tax_code": "9" if einkauf else "3"}],
             **kopf}
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


def _korb(haus, wer: dict = CARL, status: str = "offen") -> list[dict]:
    antwort = haus["als"](wer).get("/kontrolle/befunde", params={"status": status})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def _buchungen(haus) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"),
                          {"t": haus["mandant"]}).scalar()


def _status(doc_id: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"), {"id": doc_id}).scalar()


def _doppelte_eingangsrechnung(haus, *, status: str = "open") -> tuple[str, str]:
    """Zwei Eingangsrechnungen desselben Lieferanten mit derselben Fremdnummer."""
    nummer = f"LR-{uuid.uuid4().hex[:6]}"
    erste = _beleg(haus, ANNA, "purchase_invoice", 100, source_ref=nummer)["id"]
    zweite = _beleg(haus, ANNA, "purchase_invoice", 150, source_ref=nummer, status=status)["id"]
    return erste, zweite


# ── Routine und Pruefkorb ─────────────────────────────────────────────────────

def test_routine_bucht_die_sachbearbeitung_ohne_zweite_person(haus):
    klein = _beleg(haus, ANNA, "sales_invoice", 8000)["id"]            # 9.520 EUR
    frei = _beleg(haus, ANNA, "purchase_invoice", 100)["id"]           # frei erfasste Eingangsrechnung
    gutschrift = _beleg(haus, ANNA, "sales_credit_memo", 100)["id"]    # 119 EUR
    for doc in (klein, frei, gutschrift):
        assert _buche(haus, ANNA, doc).status_code == 200
    assert _buchungen(haus) == 3 and _korb(haus) == []
    # Ein regelkonformer Storno: die Buchhaltung entscheidet und begruendet.
    assert _storniere(haus, BERND, klein).status_code == 200
    assert _status(klein) == "reversed" and _korb(haus) == []
    assert _frage(haus, ANNA, frei).status_code == 409  # nichts, wofuer eine Freigabe anzufragen waere


def test_ueber_der_schwelle_wird_gebucht_und_der_controller_sieht_es(haus):
    gross = _beleg(haus, ANNA, "sales_invoice", 9000)["id"]  # 10.710 EUR
    assert _buche(haus, ANNA, gross).status_code == 200
    assert _status(gross) == "posted" and _buchungen(haus) == 1

    korb = _korb(haus)
    assert len(korb) == 1
    befund = korb[0]
    assert (befund["subject_id"], befund["code"], befund["severity"], befund["actor"], befund["status"]) == (
        gross, "betrag", "warnung", "anna", "offen")
    assert "10710" in befund["text"] and float(befund["amount"]) == 10710.0

    weg = f"/kontrolle/befunde/{befund['id']}/pruefung"
    # Wer gebucht hat, prueft nicht selbst; ohne Kontrollrolle auch nicht; ein Dienstkonto nie.
    for wer in (ADMIN, BERND, LAGER, DIENST):
        assert haus["als"](wer).post(weg, json={"note": "in Ordnung"}).status_code == 403, wer["roles"]
    assert haus["als"](CARL).post(weg, json={"note": "x"}).status_code == 422  # eine Bewertung, kein Haken
    geprueft = haus["als"](CARL).post(weg, json={"note": "Grosskunde, Lieferung laut Kontrakt"})
    assert geprueft.status_code == 200 and (geprueft.json()["status"], geprueft.json()["reviewed_by"]) == ("geprueft", "carl")
    assert haus["als"](CARL).post(weg, json={"note": "nochmal"}).status_code == 409
    assert _korb(haus) == [] and len(_korb(haus, status="geprueft")) == 1
    # Die Buchhaltung sieht den Korb, die Sachbearbeitung des Verkaufs nicht.
    assert haus["als"](BERND).get("/kontrolle/befunde").status_code == 200
    assert haus["als"](ANNA).get("/kontrolle/befunde").status_code == 403


def test_die_schwelle_des_mandanten_gilt(haus):
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
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 1000)["id"]).status_code == 200
    assert [b["code"] for b in _korb(haus)] == ["betrag"]
    setze("1000000")
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 9000)["id"]).status_code == 200
    assert len(_korb(haus)) == 1
    setze("unlesbar")  # ein unlesbarer Wert: es gilt der Startwert
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 9500)["id"]).status_code == 200
    assert len(_korb(haus)) == 2


def test_gutschrift_mit_bezug_ist_routine_ohne_bezug_ueber_der_schwelle_gesperrt(haus):
    rechnung = _beleg(haus, ANNA, "sales_invoice", 5000)
    assert _buche(haus, ANNA, rechnung["id"]).status_code == 200
    pos = rechnung["items"][0]["id"]

    def gutschrift(menge: float) -> str:
        antwort = haus["als"](ANNA).post(f"/docflow/{rechnung['id']}/convert", json={
            "target_doc_type": "sales_credit_memo", "idempotency_key": f"gs-{uuid.uuid4().hex}",
            "quantities_by_source_item_id": {pos: menge}})
        assert antwort.status_code == 200, antwort.text
        return antwort.json()["target_doc_id"]

    # Mit Bezugsrechnung: Routine, ueber 1.000 EUR und gestueckelt eine Warnung.
    assert _buche(haus, ANNA, gutschrift(0.1)).status_code == 200            # 595 EUR
    assert _korb(haus) == []
    assert _buche(haus, ANNA, gutschrift(0.1)).status_code == 200            # zusammen 1.190 EUR
    assert _buche(haus, ANNA, gutschrift(0.5)).status_code == 200            # 2.975 EUR
    assert sorted(b["code"] for b in _korb(haus)) == ["betrag", "stueckelung"]

    # Ohne Bezugsrechnung ueber der Schwelle: Forderungsverzicht ohne Beleg.
    frei = _beleg(haus, ANNA, "sales_credit_memo", 2000)["id"]
    gesperrt = _buche(haus, ANNA, frei)
    assert gesperrt.status_code == 409 and "ohne Bezugsrechnung" in gesperrt.json()["detail"]
    assert _status(frei) == "open"
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_credit_memo", 100)["id"]).status_code == 200


def test_gehaeufte_stornos_eines_partners_fallen_auf(haus):
    belege = [_beleg(haus, ANNA, "sales_invoice", 100 + n)["id"] for n in range(3)]
    for doc in belege:
        assert _buche(haus, ANNA, doc).status_code == 200
    assert _storniere(haus, BERND, belege[0]).status_code == 200
    assert _storniere(haus, BERND, belege[1]).status_code == 200
    assert _korb(haus) == []
    assert _storniere(haus, BERND, belege[2]).status_code == 200   # der dritte Storno desselben Kunden
    korb = _korb(haus)
    assert [(b["code"], b["action"], b["subject_id"]) for b in korb] == [("storno_haeufung", "reverse", belege[2])]


# ── Kritische Befunde ─────────────────────────────────────────────────────────

def test_eine_moegliche_dublette_sperrt_bis_zur_unabhaengigen_freigabe(haus):
    erste, zweite = _doppelte_eingangsrechnung(haus)
    assert _buche(haus, ANNA, erste).status_code == 409  # jede der beiden ist die Dublette der anderen
    gesperrt = _buche(haus, ANNA, zweite)
    assert gesperrt.status_code == 409 and "Mögliche Dublette" in gesperrt.json()["detail"]
    assert _buchungen(haus) == 0 and _korb(haus) == []

    anfrage = _frage(haus, ANNA, zweite)
    assert anfrage.status_code == 200, anfrage.text
    fid = anfrage.json()["id"]
    assert (anfrage.json()["status"], anfrage.json()["risk"], anfrage.json()["requested_by"]) == ("requested", "R3", "anna")
    assert _frage(haus, ANNA, zweite).json()["id"] == fid
    assert _buche(haus, ANNA, zweite).status_code == 409            # angefragt ist nicht freigegeben

    # Funktionstrennung: nicht die Antragstellerin, auch nicht als Administratorin; kein Dienstkonto; keine Rolle ohne Recht.
    for wer in (ANNA, ADMIN, DIENST, LAGER):
        assert _entscheide(haus, wer, zweite, fid).status_code == 403, wer["roles"]
    assert "Funktionstrennung" in _entscheide(haus, ADMIN, zweite, fid).json()["detail"]

    ja = _entscheide(haus, CARL, zweite, fid)                       # der Controller gibt frei
    assert ja.status_code == 200 and (ja.json()["status"], ja.json()["decided_by"]) == ("granted", "carl")
    assert _buche(haus, ANNA, zweite).status_code == 200
    assert _status(zweite) == "posted" and _buchungen(haus) == 1
    assert [f["status"] for f in haus["als"](ANNA).get(f"/docflow/{zweite}/approvals").json()] == ["consumed"]
    # Auch der freigegebene kritische Befund steht im Pruefkorb, mit seiner Freigabe.
    korb = _korb(haus)
    assert [(b["code"], b["severity"], b["approval_id"]) for b in korb] == [("dublette", "kritisch", fid)]
    with SessionLocal() as db:
        befehle = [tuple(z) for z in db.execute(text(
            "SELECT command, actor FROM domain_docflow.document_command_log WHERE header_id = :id AND command LIKE 'approval%' "
            "ORDER BY logged_at, id"), {"id": zweite}).fetchall()]
    assert befehle[0] == ("approval_request", "anna") and befehle[-2:] == [("approval_grant", "carl"), ("approval_consume", "anna")]


def test_dieselbe_summe_am_selben_tag_ist_auch_ohne_fremdnummer_eine_dublette(haus):
    erste = _beleg(haus, ANNA, "purchase_invoice", 300)["id"]
    assert _buche(haus, ANNA, erste).status_code == 200
    zweite = _beleg(haus, ANNA, "purchase_invoice", 300)["id"]
    assert "Mögliche Dublette" in _buche(haus, ANNA, zweite).json()["detail"]
    # Ein anderer Betrag ist keine.
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "purchase_invoice", 301)["id"]).status_code == 200
    # Ausgangsrechnungen gleichen Betrags sind Alltag.
    for _ in range(2):
        assert _buche(haus, ANNA, _beleg(haus, ANNA, "sales_invoice", 300)["id"]).status_code == 200


def test_abweichung_von_der_bestellung_sperrt_die_frei_erfasste_rechnung_nicht(haus):
    bestellung = _beleg(haus, ANNA, "purchase_order", 100, menge=10)

    def rechnung(menge: float) -> str:
        antwort = haus["als"](ANNA).post(f"/docflow/{bestellung['id']}/convert", json={
            "target_doc_type": "purchase_invoice", "idempotency_key": f"er-{uuid.uuid4().hex}",
            "quantities_by_source_item_id": {bestellung["items"][0]["id"]: menge}})
        assert antwort.status_code == 200, antwort.text
        return antwort.json()["target_doc_id"]

    assert _buche(haus, ANNA, rechnung(4)).status_code == 200       # Preis und Menge wie bestellt
    abweichend = rechnung(3)
    with SessionLocal() as db:  # Der Lieferant berechnet mehr als bestellt.
        db.execute(text("UPDATE domain_docflow.document_items SET unit_price = 112 WHERE header_id = :id"), {"id": abweichend})
        db.commit()
    antwort = _buche(haus, ANNA, abweichend)
    assert antwort.status_code == 409 and "Preis 112" in antwort.json()["detail"] and "weicht" in antwort.json()["detail"]
    assert _buche(haus, ANNA, _beleg(haus, ANNA, "purchase_invoice", 777)["id"]).status_code == 200
    assert _buchungen(haus) == 2


def test_eine_aenderung_nach_der_freigabe_macht_sie_ungueltig(haus):
    _erste, zweite = _doppelte_eingangsrechnung(haus, status="draft")
    fid = _frage(haus, ANNA, zweite).json()["id"]
    assert _entscheide(haus, CARL, zweite, fid).status_code == 200
    geaendert = haus["als"](ANNA).put(f"/docflow/{zweite}", json={
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 950, "tax_code": "9"}]})
    assert geaendert.status_code == 200, geaendert.text
    antwort = _buche(haus, ANNA, zweite)
    assert antwort.status_code == 409 and "Freigabe erforderlich" in antwort.json()["detail"]
    assert _buchungen(haus) == 0
    neu = _frage(haus, ANNA, zweite).json()
    assert neu["id"] != fid and float(neu["amount"]) == 1130.5
    stand = {f["id"]: f["status"] for f in haus["als"](ANNA).get(f"/docflow/{zweite}/approvals").json()}
    assert stand == {fid: "invalidated", neu["id"]: "requested"}


def test_eine_freigabe_laeuft_ab_und_eine_abgelehnte_gilt_nicht(haus):
    _e, doc = _doppelte_eingangsrechnung(haus)
    fid = _frage(haus, ANNA, doc).json()["id"]
    assert _entscheide(haus, CARL, doc, fid).status_code == 200
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_docflow.approvals SET expires_at = now() - interval '1 minute' WHERE id = :id"), {"id": fid})
        db.commit()
    assert _buche(haus, ANNA, doc).status_code == 409 and _buchungen(haus) == 0

    _e2, zweite = _doppelte_eingangsrechnung(haus)
    fid2 = _frage(haus, ANNA, zweite).json()["id"]
    assert _entscheide(haus, CARL, zweite, fid2, erteilt=False).json()["status"] == "denied"
    assert _buche(haus, ANNA, zweite).status_code == 409
    assert _entscheide(haus, BERND, zweite, fid2).status_code == 409  # entschieden ist entschieden


def test_wer_den_beleg_angelegt_hat_gibt_ihn_nicht_frei(haus):
    nummer = f"LR-{uuid.uuid4().hex[:6]}"
    _beleg(haus, ANNA, "purchase_invoice", 100, source_ref=nummer)
    doc = _beleg(haus, CARL | {"roles": ["admin"]}, "purchase_invoice", 150, source_ref=nummer)["id"]  # Carl legt an
    fid = _frage(haus, ANNA, doc).json()["id"]                                                          # Anna fragt an
    nein = _entscheide(haus, CARL, doc, fid)
    assert nein.status_code == 403 and "Funktionstrennung" in nein.json()["detail"]
    assert _entscheide(haus, BERND, doc, fid).status_code == 200


def test_die_sperre_gilt_in_jedem_zugang_auch_im_dienst_selbst(haus):
    """Ein Skript oder ein kuenftiges MCP-Werkzeug, das den Dienst direkt ruft, kommt nicht an der Sperre vorbei."""
    _e, doc = _doppelte_eingangsrechnung(haus)
    with SessionLocal() as db:
        with pytest.raises(ConflictError) as fehler:
            DocflowService(db, haus["mandant"], "skript").post_document(
                doc, docflow.DocflowPostRequest(idempotency_key=f"direkt-{uuid.uuid4().hex}"))
        db.rollback()
    assert "Freigabe erforderlich (R3)" in str(fehler.value.detail)
    assert _buchungen(haus) == 0 and _status(doc) == "open"


def test_freigaben_und_befunde_eines_anderen_mandanten_gibt_es_nicht(haus):
    _e, doc = _doppelte_eingangsrechnung(haus)
    fid = _frage(haus, ANNA, doc).json()["id"]
    from app.core.exceptions import EntityNotFoundError
    from app.services.docflow_freigabe import DocflowFreigabe
    from app.services.freigabe_engine import pruefkorb
    with SessionLocal() as db:
        with pytest.raises(EntityNotFoundError):
            DocflowFreigabe(db, "anderer-mandant").entscheide(doc, fid, CARL, True)
        assert pruefkorb(db, "anderer-mandant", None) == []
        db.rollback()
    assert haus["als"](ANNA).get(f"/docflow/{uuid.uuid4()}/approvals").status_code == 404
    assert haus["als"](CARL).post(f"/kontrolle/befunde/{uuid.uuid4()}/pruefung", json={"note": "nichts da"}).status_code == 404
