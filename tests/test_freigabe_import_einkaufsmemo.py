"""Massenimport von Buchungen und Lieferantengutschriften/-belastungen an der Approval Engine (APPROVAL-001).

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import approvals, bulk_journal_import, credit_debit_memos, kontrolle
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.finance.steuerschluessel import richte_skr03_ein
from app.services.finance_freigabe import importabdruck
from testgrenze import ersetze_mandant

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["FINANCE_ADMIN", "EINKAUF_BEARBEITEN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CLARA = {"sub": "clara", "name": "c.onken", "roles": ["FINANCE_ADMIN", "EINKAUF_ADMIN"]}
LAGER = {"sub": "lars", "name": "l.janssen", "roles": ["LAGER_ADMIN"]}
CARL = {"sub": "carl", "name": "c.boekhoff", "roles": ["controller"]}

AUFRAEUMEN = (
    "DELETE FROM domain_shared.blockchain_anchors WHERE tenant_id = :t",
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.control_findings WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approval_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approvals WHERE tenant_id = :t",
    "DELETE FROM documents WHERE CAST(data AS jsonb)->>'tenantId' = :t",
    "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


def _mandant() -> str:
    kennung = f"ie-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": kennung})
        richte_skr03_ein(db, kennung)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{kennung}-1400", "t": kennung})
        db.commit()
    return kennung


def _raeume(kennung: str) -> None:
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": kennung})
        db.commit()


@pytest.fixture
def haus(monkeypatch):
    mandant, anderer = _mandant(), _mandant()
    monkeypatch.setattr(bulk_journal_import, "log_fibu_audit", lambda *_a, **_k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(bulk_journal_import.router)
    app.include_router(credit_debit_memos.router)
    app.include_router(approvals.router, prefix="/approvals")
    app.include_router(kontrolle.router, prefix="/kontrolle")
    ersetze_mandant(app, mandant)
    client = TestClient(app, raise_server_exceptions=False)

    def als(nutzer: dict) -> TestClient:
        app.dependency_overrides[get_current_user] = lambda: nutzer
        return client

    yield {"mandant": mandant, "anderer": anderer, "als": als, "app": app}
    _raeume(mandant)
    _raeume(anderer)


def _buchungen(mandant: str) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"), {"t": mandant}).scalar()


CSV = ("entry_date,account_number,description,debit_amount,credit_amount,entry_number,reference\n"
       "2026-10-13,1400,Umbuchung,500.00,0,IMP-1,UMB-1\n"
       "2026-10-13,8400,Umbuchung,0,500.00,IMP-1,UMB-1\n")


def _import(haus, wer: dict, inhalt: str = CSV, **parameter):
    return haus["als"](wer).post(
        "/bulk-journal-import/csv", params={"period": "2026-10", **parameter},
        files={"file": ("buchungen.csv", inhalt.encode("utf-8"), "text/csv")})


# ── Massenimport ──────────────────────────────────────────────────────────────

def _korb(haus) -> list[tuple[str, str, str]]:
    antwort = haus["als"](CARL).get("/kontrolle/befunde")
    assert antwort.status_code == 200, antwort.text
    return sorted((b["subject_type"], b["code"], b["severity"]) for b in antwort.json())


def test_der_massenimport_bucht_und_steht_im_pruefkorb(haus):
    probe = _import(haus, ANNA, dry_run=True)
    assert probe.status_code == 200, probe.text
    abdruck = probe.json()["approval_subject"]
    assert abdruck == importabdruck(haus["mandant"], "2026-10", CSV.encode("utf-8"))
    assert _buchungen(haus["mandant"]) == 0 and _korb(haus) == []
    assert _import(haus, BERND).status_code == 403                 # der Import bleibt der Finanzleitung vorbehalten
    gebucht = _import(haus, ANNA)
    assert gebucht.status_code == 200, gebucht.text
    assert _buchungen(haus["mandant"]) == 1
    assert _korb(haus) == [("journal_import", "massenimport", "warnung")]


OHNE_NUMMER = ("entry_date,account_number,description,debit_amount,credit_amount\n"
               "2026-10-13,1400,Umbuchung,700.00,0\n"
               "2026-10-13,8400,Umbuchung,0,700.00\n")


def test_dieselbe_datei_ein_zweites_mal_ist_eine_dublette(haus):
    assert _import(haus, ANNA, OHNE_NUMMER).status_code == 200
    doppelt = _import(haus, ANNA, OHNE_NUMMER)
    assert doppelt.status_code == 409 and "bereits importiert" in doppelt.text
    assert _buchungen(haus["mandant"]) == 1
    # Eine andere Datei ist ein anderer Vorgang.
    assert _import(haus, ANNA, OHNE_NUMMER.replace("700.00", "600.00")).status_code == 200
    assert _buchungen(haus["mandant"]) == 2

    abdruck = importabdruck(haus["mandant"], "2026-10", OHNE_NUMMER.encode("utf-8"))
    weg = f"/approvals/journal_import/{abdruck}"
    assert haus["als"](BERND).post(weg, json={"action": "post"}).status_code == 403
    fid = haus["als"](ANNA).post(weg, json={"action": "post"}).json()["id"]
    assert haus["als"](ANNA).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 403   # Funktionstrennung
    assert haus["als"](BERND).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 403  # nicht Leitung
    assert haus["als"](CARL).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 200   # der Controller
    # Bewusst noch einmal, mit Freigabe: gebucht, und der kritische Befund steht im Pruefkorb.
    assert _import(haus, ANNA, OHNE_NUMMER).status_code == 200
    assert _buchungen(haus["mandant"]) == 3
    assert ("journal_import", "dublette", "kritisch") in _korb(haus)
    # Die Freigabe ist verbraucht.
    assert _import(haus, ANNA, OHNE_NUMMER).status_code == 409


def test_der_massenimport_bucht_nur_in_den_mandanten_der_anmeldung(haus):
    """Bis 13.10.2026 kam der Mandant aus der Anfrage: Wer importieren durfte, konnte in jeden Mandanten buchen."""
    assert _import(haus, ANNA, tenant_id=haus["anderer"]).status_code == 403
    assert _import(haus, ANNA, tenant_id=haus["anderer"], dry_run=True).status_code == 403
    assert _import(haus, ANNA, tenant_id=haus["mandant"], dry_run=True).status_code == 200
    assert _buchungen(haus["anderer"]) == 0 and _buchungen(haus["mandant"]) == 0


def test_ein_abdruck_der_keiner_ist_ist_kein_vorgang(haus):
    assert haus["als"](ANNA).post("/approvals/journal_import/irgendwas", json={"action": "post"}).status_code == 404


# ── Lieferantengutschrift und -belastung ──────────────────────────────────────

def _memo(haus, wer: dict, art: str = "credit-memos", brutto: float = 119, abrechnung: str | None = None) -> str:
    netto = round(brutto / 1.19, 2)
    rumpf = {"supplierId": "SUP-1", "memoDate": "2026-10-13", "reason": "Preisabweichung",
             "items": [{"productName": "Weizen", "quantity": 1, "unitPrice": netto, "netAmount": netto,
                        "taxAmount": round(brutto - netto, 2), "grossAmount": brutto}]}
    if abrechnung:
        rumpf["settlementId"] = abrechnung
    antwort = haus["als"](wer).post(f"/einkauf/{art}", json=rumpf)
    assert antwort.status_code == 200, antwort.text
    return antwort.json()["id"]


def _beleg(kennung: str) -> dict:
    import json
    with SessionLocal() as db:
        roh = db.execute(text("SELECT data FROM documents WHERE doc_number = :n"), {"n": kennung}).scalar()
    return roh if isinstance(roh, dict) else json.loads(roh)


@pytest.mark.parametrize("art", ["credit-memos", "debit-memos"])
def test_gutschrift_und_belastung_bucht_der_einkauf_selbst(haus, art):
    memo = _memo(haus, ANNA, art)
    beleg = _beleg(memo)
    assert (beleg["tenantId"], beleg["createdBy"]) == (haus["mandant"], "anna")  # aus der Anmeldung, nicht aus einem Kopf
    gebucht = haus["als"](ANNA).post(f"/einkauf/{art}/{memo}/buchung")
    assert gebucht.status_code == 200, gebucht.text
    assert _beleg(memo)["booked"] is True and _korb(haus) == []


def test_die_abrechnungskorrektur_der_ernte_ist_routine_ab_250_euro_sieht_sie_der_controller(haus):
    klein = _memo(haus, ANNA, brutto=119, abrechnung="SET-1")
    gross = _memo(haus, ANNA, brutto=357, abrechnung="SET-2")
    for memo in (klein, gross):
        assert haus["als"](ANNA).post(f"/einkauf/credit-memos/{memo}/freigabe").status_code == 200  # Freigabe des Moduls
        assert haus["als"](ANNA).post(f"/einkauf/credit-memos/{memo}/buchung").status_code == 200
    assert _korb(haus) == [("einkauf_credit_memo", "agrar_korrektur", "warnung")]


def test_buchen_und_verrechnen_brauchen_das_recht_des_einkaufs(haus):
    memo = _memo(haus, ANNA)
    rumpf = {"invoiceIds": ["RE-1"]}
    assert haus["als"](LAGER).post(f"/einkauf/credit-memos/{memo}/settle", json=rumpf).status_code == 403
    assert haus["als"](LAGER).post(f"/einkauf/credit-memos/{memo}/buchung").status_code == 403
    assert _beleg(memo)["booked"] is False and _beleg(memo)["settled"] is False


def test_grosse_gutschrift_wird_gebucht_und_gemeldet(haus):
    memo = _memo(haus, ANNA, brutto=2380)
    assert haus["als"](ANNA).post(f"/einkauf/credit-memos/{memo}/buchung").status_code == 200
    assert _korb(haus) == [("einkauf_credit_memo", "betrag", "warnung")]


def test_ein_beleg_eines_anderen_mandanten_wird_nicht_gebucht(haus):
    memo = _memo(haus, ANNA)
    ersetze_mandant(haus["app"], haus["anderer"])
    try:
        assert haus["als"](CLARA).post(f"/einkauf/credit-memos/{memo}/buchung").status_code == 404
        assert haus["als"](CLARA).post(f"/approvals/einkauf_credit_memo/{memo}", json={"action": "post"}).status_code == 404
    finally:
        ersetze_mandant(haus["app"], haus["mandant"])
    assert _beleg(memo)["booked"] is False


def test_ohne_recht_des_einkaufs_wird_keine_gutschrift_angelegt(haus):
    antwort = haus["als"](LAGER).post("/einkauf/credit-memos", json={
        "supplierId": "SUP-1", "memoDate": "2026-10-13", "reason": "Preisabweichung",
        "items": [{"productName": "Weizen", "quantity": 1, "unitPrice": 100, "netAmount": 100, "taxAmount": 19,
                   "grossAmount": 119}]})
    assert antwort.status_code == 403
