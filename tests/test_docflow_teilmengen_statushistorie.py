"""DocFlow Phase 0.2 und 0.3: Teilmengen ueber mehrere Folgebelege, verbindliche Statushistorie.

Bedingungen (Auftraggeber und Codex, 13.10.2026):

* Teilmengen werden ausdruecklich angefordert; ein blosser Wiederholungsaufruf erzeugt keinen weiteren Folgebeleg.
* Derselbe Idempotenzschluessel mit gleichem Inhalt liefert denselben Beleg, mit anderem Inhalt eine Abweisung.
* Folgebeleg, Mengenbezug und Restmenge entstehen in einer Transaktion; parallele Aufrufe uebernehmen nie mehr
  als verfuegbar.
* Statushistorie und Protokoll sind verbindlich: Scheitert der Eintrag, scheitert die Aenderung. Der Akteur
  kommt aus der geprueften Anmeldung.

Bis dahin liess DocFlow je Quelle und Folgeart genau einen Folgebeleg zu, der Status wurde ueberschrieben, und
das Protokoll hiess ``best_effort_audit``.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import threading
import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.api.v1.endpoints import docflow
from app.core.database import SessionLocal
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from app.services.docflow_service import DocflowService
from testgrenze import ersetze_mandant, ersetze_nutzer


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"dt-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        richte_skr03_ein(db, mandant)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    app.include_router(docflow.router, prefix="/docflow")
    # testgrenze: angemeldet als 5f0c2a9e, im Mandanten dieses Laufs (DocFlow bindet ihn an die Anmeldung).
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"lauf": lauf, "mandant": mandant, "client": client, "t": {"tenant_id": mandant}}
    finally:
        with SessionLocal() as db:
            # Historie und Protokoll sind unveraenderlich; nur der Wartungsschalter erlaubt das Aufraeumen.
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            koepfe = "(SELECT id FROM domain_docflow.document_headers WHERE tenant_id = :t)"
            for sql in (
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_links WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_items WHERE header_id IN " + koepfe,  # noqa: S608 — fester Text
                "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
                "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _auftrag(haus, mengen=(10, 4), doc_type="sales_order") -> dict:
    antwort = haus["client"].post("/docflow/", params=haus["t"], json={
        "doc_type": doc_type, "doc_number": f"AU-{haus['lauf']}-{uuid.uuid4().hex[:4]}", "status": "open",
        "customer_id": "kunde-1",
        "items": [{"article_number": f"A-{nr}", "quantity": menge, "unit_price": 100, "tax_code": "3"}
                  for nr, menge in enumerate(mengen, 1)]})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def _wandle(haus, doc_id: str, ziel="sales_delivery", mengen=None, schluessel=None):
    rumpf = {"target_doc_type": ziel, "idempotency_key": schluessel or f"wandeln-{uuid.uuid4().hex}"}
    if mengen is not None:
        rumpf["quantities_by_source_item_id"] = mengen
    return haus["client"].post(f"/docflow/{doc_id}/convert", params=haus["t"], json=rumpf)


def _folgebelege(haus, doc_id: str) -> list[tuple[str, Decimal]]:
    """Je Folgebeleg die Menge der ersten Quellposition, in Reihenfolge der Entstehung."""
    with SessionLocal() as db:
        return [(z[0], Decimal(str(z[1]))) for z in db.execute(text(
            "SELECT h.doc_type, COALESCE(SUM(l.quantity_linked), 0) FROM domain_docflow.document_header_links k "
            "JOIN domain_docflow.document_headers h ON h.id = k.to_header_id "
            "LEFT JOIN domain_docflow.document_links l ON l.to_header_id = h.id "
            "WHERE k.tenant_id = :t AND k.from_header_id = :f GROUP BY h.id, h.doc_type, h.created_at ORDER BY h.created_at"),
            {"t": haus["mandant"], "f": doc_id}).fetchall()]


def _historie(haus, doc_id: str) -> list[tuple]:
    antwort = haus["client"].get(f"/docflow/{doc_id}/status-history", params=haus["t"])
    assert antwort.status_code == 200, antwort.text
    return [(z["from_status"], z["to_status"], z["command"], z["actor"]) for z in antwort.json()]


# --- 0.2 Teilmengen ---------------------------------------------------------------------------

def test_ein_auftrag_drei_teillieferscheine_dann_ist_schluss(haus):
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    for menge in (4, 3, 3):
        antwort = _wandle(haus, auftrag["id"], mengen={pos: menge})
        assert antwort.status_code == 200, antwort.text
    assert _folgebelege(haus, auftrag["id"]) == [
        ("sales_delivery", Decimal("4")), ("sales_delivery", Decimal("3")), ("sales_delivery", Decimal("3"))]
    # Die Menge ist verbraucht: Ein vierter Lieferschein entsteht nicht.
    voll = _wandle(haus, auftrag["id"], mengen={pos: 1})
    assert voll.status_code == 400 and "übersteigt die Restmenge 0" in voll.json()["detail"]
    assert len(_folgebelege(haus, auftrag["id"])) == 3


def test_ueberlieferung_wird_abgelehnt_und_nennt_die_restmenge(haus):
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    assert _wandle(haus, auftrag["id"], mengen={pos: 6}).status_code == 200
    antwort = _wandle(haus, auftrag["id"], mengen={pos: 5})
    assert antwort.status_code == 400
    assert "Menge 5 übersteigt die Restmenge 4 (Beleg 10, bereits umgewandelt 6)" in antwort.json()["detail"]
    assert len(_folgebelege(haus, auftrag["id"])) == 1


def test_ein_blosser_wiederholungsaufruf_erzeugt_keinen_weiteren_folgebeleg(haus):
    """Teilmengen werden ausdruecklich verlangt — auch wenn noch Restmenge da waere."""
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    assert _wandle(haus, auftrag["id"], mengen={pos: 4}).status_code == 200
    ohne_mengen = _wandle(haus, auftrag["id"])
    assert ohne_mengen.status_code == 409 and "Mengen je Position ausdrücklich angeben" in ohne_mengen.json()["detail"]
    assert len(_folgebelege(haus, auftrag["id"])) == 1


def test_vollstaendige_umwandlung_ohne_mengen_und_keine_zweite(haus):
    auftrag = _auftrag(haus, mengen=(10, 4))
    erste = _wandle(haus, auftrag["id"])
    assert erste.status_code == 200 and erste.json()["payload"]["item_count"] == 2
    # Ein neuer Schluessel ist ein neuer Auftrag — es gibt aber nichts mehr umzuwandeln.
    zweite = _wandle(haus, auftrag["id"])
    assert zweite.status_code == 409
    assert len(_folgebelege(haus, auftrag["id"])) == 1


def test_teilrechnungen_aus_dem_lieferschein_bis_zur_gelieferten_menge(haus):
    """Geliefert 10: zwei Teilrechnungen zu 6 und 4, eine dritte nicht.

    Berechnet wird aus dem Lieferschein — ein Auftrag mit Lieferung laesst sich nicht zusaetzlich direkt
    berechnen (``test_docflow_einkauf_gutschrift.py``).
    """
    auftrag = _auftrag(haus, mengen=(10,))
    lieferschein = _wandle(haus, auftrag["id"], ziel="sales_delivery").json()["target_doc_id"]
    with SessionLocal() as db:
        pos = db.execute(text(
            "SELECT id FROM domain_docflow.document_items WHERE header_id = :h"), {"h": lieferschein}).scalar()
    assert _wandle(haus, lieferschein, ziel="sales_invoice", mengen={pos: 6}).status_code == 200
    assert _wandle(haus, lieferschein, ziel="sales_invoice", mengen={pos: 4}).status_code == 200
    assert _wandle(haus, lieferschein, ziel="sales_invoice", mengen={pos: 1}).status_code == 400
    assert _folgebelege(haus, lieferschein) == [("sales_invoice", Decimal("6")), ("sales_invoice", Decimal("4"))]


# --- Idempotenz ---------------------------------------------------------------------------------

def test_gleicher_schluessel_gleicher_inhalt_liefert_denselben_beleg(haus):
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    erste = _wandle(haus, auftrag["id"], mengen={pos: 4}, schluessel="wandeln-fest-0001").json()
    zweite = _wandle(haus, auftrag["id"], mengen={pos: 4}, schluessel="wandeln-fest-0001").json()
    assert zweite["target_doc_id"] == erste["target_doc_id"] and zweite.get("idempotent_hit") is True
    assert len(_folgebelege(haus, auftrag["id"])) == 1


def test_gleicher_schluessel_anderer_inhalt_wird_abgewiesen(haus):
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    assert _wandle(haus, auftrag["id"], mengen={pos: 4}, schluessel="wandeln-fest-0002").status_code == 200
    antwort = _wandle(haus, auftrag["id"], mengen={pos: 5}, schluessel="wandeln-fest-0002")
    assert antwort.status_code == 409 and "mit anderem Inhalt" in antwort.json()["detail"]
    andere_art = _wandle(haus, auftrag["id"], ziel="sales_invoice", mengen={pos: 4}, schluessel="wandeln-fest-0002")
    assert andere_art.status_code == 409
    assert _folgebelege(haus, auftrag["id"]) == [("sales_delivery", Decimal("4"))]


# --- Parallelzugriff ----------------------------------------------------------------------------

def test_parallele_aufrufe_uebernehmen_nie_mehr_als_verfuegbar(haus):
    """Acht gleichzeitige Teillieferungen zu je 3 aus 10: hoechstens drei gelingen."""
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    ergebnisse: list[int] = []
    start = threading.Barrier(8)

    def lauf() -> None:
        start.wait()
        ergebnisse.append(_wandle(haus, auftrag["id"], mengen={pos: 3}).status_code)

    faeden = [threading.Thread(target=lauf) for _ in range(8)]
    for f in faeden:
        f.start()
    for f in faeden:
        f.join()
    assert sorted(ergebnisse) == [200, 200, 200, 400, 400, 400, 400, 400], ergebnisse
    belege = _folgebelege(haus, auftrag["id"])
    assert len(belege) == 3 and sum(menge for _art, menge in belege) == Decimal("9")


def test_parallele_wiederholungen_desselben_auftrags_erzeugen_einen_beleg(haus):
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    antworten: list[dict] = []
    start = threading.Barrier(6)

    def lauf() -> None:
        start.wait()
        antworten.append(_wandle(haus, auftrag["id"], mengen={pos: 4}, schluessel="wandeln-parallel-01").json())

    faeden = [threading.Thread(target=lauf) for _ in range(6)]
    for f in faeden:
        f.start()
    for f in faeden:
        f.join()
    assert len({a["target_doc_id"] for a in antworten}) == 1, antworten
    assert _folgebelege(haus, auftrag["id"]) == [("sales_delivery", Decimal("4"))]


# --- Storno gibt die Menge frei -----------------------------------------------------------------

def test_stornierte_rechnung_gibt_ihre_menge_wieder_frei(haus):
    auftrag = _auftrag(haus, mengen=(10,))
    pos = auftrag["items"][0]["id"]
    rechnung = _wandle(haus, auftrag["id"], ziel="sales_invoice", mengen={pos: 10}).json()["target_doc_id"]
    assert _wandle(haus, auftrag["id"], ziel="sales_invoice", mengen={pos: 1}).status_code == 400
    assert haus["client"].post(f"/docflow/{rechnung}/post", params=haus["t"],
                               json={"idempotency_key": f"buchen-{rechnung}"}).status_code == 200
    storno = haus["client"].post(f"/docflow/{rechnung}/reverse", params=haus["t"],
                                 json={"idempotency_key": f"storno-{rechnung}", "reason": "Falsche Menge"})
    assert storno.status_code == 200, storno.text
    # Nach dem Storno ist die Menge wieder fakturierbar.
    assert _wandle(haus, auftrag["id"], ziel="sales_invoice", mengen={pos: 10}).status_code == 200
    assert _historie(haus, rechnung) == [
        (None, "open", "convert", "5f0c2a9e"), ("open", "posted", "post", "5f0c2a9e"),
        ("posted", "reversed", "reverse", "5f0c2a9e")]
    with SessionLocal() as db:
        grund = db.execute(text(
            "SELECT reason FROM domain_docflow.document_status_history WHERE header_id = :id AND to_status = 'reversed'"),
            {"id": rechnung}).scalar()
    assert grund == "Falsche Menge"


# --- 0.3 Statushistorie und Protokoll -----------------------------------------------------------

def test_jeder_statuswechsel_steht_in_der_historie_mit_dem_angemeldeten_benutzer(haus):
    angelegt = haus["client"].post("/docflow/", params=haus["t"], json={
        "doc_type": "sales_invoice", "doc_number": f"RE-{haus['lauf']}-1", "status": "draft", "customer_id": "kunde-1",
        # Die Anfrage nennt jemand anderen; es zaehlt die Anmeldung.
        "created_by": "jemand-anderes",
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 100, "tax_code": "3"}]}).json()
    doc_id = angelegt["id"]
    assert haus["client"].post(f"/docflow/{doc_id}/release", params=haus["t"], json={
        "idempotency_key": f"frei-{doc_id}", "released_by": "jemand-anderes"}).status_code == 200
    assert haus["client"].post(f"/docflow/{doc_id}/post", params=haus["t"], json={
        "idempotency_key": f"buchen-{doc_id}", "posted_by": "jemand-anderes"}).status_code == 200
    assert _historie(haus, doc_id) == [
        (None, "draft", "create", "5f0c2a9e"), ("draft", "open", "release", "5f0c2a9e"),
        ("open", "posted", "post", "5f0c2a9e")]
    with SessionLocal() as db:
        protokoll = db.execute(text(
            "SELECT command, actor FROM domain_docflow.document_command_log WHERE header_id = :id ORDER BY logged_at"),
            {"id": doc_id}).fetchall()
    assert [tuple(z) for z in protokoll] == [("create", "5f0c2a9e"), ("release", "5f0c2a9e"), ("post", "5f0c2a9e")]


def test_auch_ein_statuswechsel_am_dienst_vorbei_wird_festgehalten(haus):
    """Die Historie schreibt die Datenbank: Kein Weg kann sie vergessen."""
    auftrag = _auftrag(haus)
    with SessionLocal() as db:
        db.execute(text(
            "UPDATE domain_docflow.document_headers SET status = 'completed', updated_by = 'rohes-sql' WHERE id = :id"),
            {"id": auftrag["id"]})
        db.commit()
    assert _historie(haus, auftrag["id"])[-1] == ("open", "completed", None, "rohes-sql")


def test_die_historie_laesst_sich_nicht_aendern_oder_loeschen(haus):
    auftrag = _auftrag(haus)
    for sql in (
        "UPDATE domain_docflow.document_status_history SET actor = 'niemand' WHERE header_id = :id",
        "DELETE FROM domain_docflow.document_status_history WHERE header_id = :id",
        "UPDATE domain_docflow.document_command_log SET actor = 'niemand' WHERE header_id = :id",
        "DELETE FROM domain_docflow.document_command_log WHERE header_id = :id",
    ):
        with SessionLocal() as db:
            with pytest.raises(DBAPIError, match="nicht geaendert oder geloescht"):
                db.execute(text(sql), {"id": auftrag["id"]})
            db.rollback()
    assert _historie(haus, auftrag["id"]) == [(None, "open", "create", "5f0c2a9e")]


def test_scheitert_das_protokoll_scheitert_die_aenderung(haus, monkeypatch):
    """Rollback: kein Folgebeleg, kein Statuswechsel, keine Buchung ohne Protokoll."""
    auftrag = _auftrag(haus, mengen=(10,))
    rechnung = _wandle(haus, auftrag["id"], ziel="sales_invoice").json()["target_doc_id"]

    def faellt_aus(self, *_a, **_k):
        raise RuntimeError("Protokoll nicht erreichbar")

    monkeypatch.setattr(DocflowService, "_protokolliere", faellt_aus)
    assert _wandle(haus, auftrag["id"], ziel="sales_delivery").status_code == 500
    assert haus["client"].post(f"/docflow/{rechnung}/post", params=haus["t"],
                               json={"idempotency_key": f"buchen-{rechnung}"}).status_code == 500
    monkeypatch.undo()
    assert [art for art, _m in _folgebelege(haus, auftrag["id"])] == ["sales_invoice"]
    assert _historie(haus, rechnung) == [(None, "open", "convert", "5f0c2a9e")]
    with SessionLocal() as db:
        assert db.execute(text(
            "SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"), {"t": haus["mandant"]}).scalar() == 0


def test_scheitert_die_historie_scheitert_der_statuswechsel(haus):
    """Der Trigger ist Teil der Transaktion: Ohne Eintrag gibt es keinen Wechsel."""
    auftrag = _auftrag(haus)
    with SessionLocal() as db:
        # Ein Status, den die Historie nicht fassen kann (laenger als ihr Feld), darf nicht durchgehen.
        with pytest.raises(DBAPIError):
            db.execute(text(
                "UPDATE domain_docflow.document_headers SET status = 'open', deleted_at = NOW(), "
                "updated_by = :wer WHERE id = :id"), {"id": auftrag["id"], "wer": "x" * 200})
        db.rollback()
    assert _historie(haus, auftrag["id"]) == [(None, "open", "create", "5f0c2a9e")]


@pytest.mark.parametrize("status", ["posted", "reversed", "cancelled"])
def test_ein_beleg_wird_nicht_als_gebucht_oder_storniert_angelegt(haus, status):
    antwort = haus["client"].post("/docflow/", params=haus["t"], json={
        "doc_type": "sales_invoice", "doc_number": f"RE-{haus['lauf']}-x", "status": status, "customer_id": "kunde-1",
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 100, "tax_code": "3"}]})
    assert antwort.status_code in (400, 422), antwort.text
    assert "über die Kommandos" in antwort.text


def test_gebucht_wird_nicht_durch_aendern_gesetzt(haus):
    auftrag = _auftrag(haus, doc_type="sales_invoice")
    antwort = haus["client"].put(f"/docflow/{auftrag['id']}", params=haus["t"], json={"status": "posted"})
    assert antwort.status_code in (400, 409, 422) and "entsteht durch Buchen" in antwort.text, antwort.text
    assert _historie(haus, auftrag["id"]) == [(None, "open", "create", "5f0c2a9e")]
