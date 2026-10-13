"""Massenimport von Buchungen und Lieferantengutschriften/-belastungen an der Approval Engine (APPROVAL-001).

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import approvals, bulk_journal_import, credit_debit_memos
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

AUFRAEUMEN = (
    "DELETE FROM domain_shared.blockchain_anchors WHERE tenant_id = :t",
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
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

def test_der_massenimport_bucht_erst_mit_der_freigabe_fuer_genau_diese_datei(haus):
    probe = _import(haus, ANNA, dry_run=True)
    assert probe.status_code == 200, probe.text
    abdruck = probe.json()["approval_subject"]
    assert abdruck == importabdruck(haus["mandant"], "2026-10", CSV.encode("utf-8")) and _buchungen(haus["mandant"]) == 0

    ohne = _import(haus, ANNA)
    assert ohne.status_code == 409 and "Freigabe erforderlich (R3)" in ohne.text
    assert _buchungen(haus["mandant"]) == 0

    weg = f"/approvals/journal_import/{abdruck}"
    assert haus["als"](BERND).post(weg, json={"action": "post"}).status_code == 403  # nur die Finanzleitung fragt an
    fid = haus["als"](ANNA).post(weg, json={"action": "post"}).json()["id"]
    assert haus["als"](ANNA).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 403   # Funktionstrennung
    assert haus["als"](BERND).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 403  # nicht Leitung
    assert haus["als"](CLARA).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 200

    # Eine andere Datei ist ein anderer Vorgang: Die Freigabe gilt fuer sie nicht.
    andere = _import(haus, ANNA, CSV.replace("500.00", "5000.00"))
    assert andere.status_code == 409 and _buchungen(haus["mandant"]) == 0

    gebucht = _import(haus, ANNA)
    assert gebucht.status_code == 200, gebucht.text
    assert _buchungen(haus["mandant"]) == 1
    # Die Freigabe ist verbraucht: dieselbe Datei ein zweites Mal braucht eine neue.
    assert _import(haus, ANNA).status_code == 409 and _buchungen(haus["mandant"]) == 1


def test_der_massenimport_bucht_nur_in_den_mandanten_der_anmeldung(haus):
    """Bis 13.10.2026 kam der Mandant aus der Anfrage: Wer importieren durfte, konnte in jeden Mandanten buchen."""
    fremd = _import(haus, ANNA, tenant_id=haus["anderer"])
    assert fremd.status_code == 403
    assert _import(haus, ANNA, tenant_id=haus["anderer"], dry_run=True).status_code == 403
    assert _import(haus, ANNA, tenant_id=haus["mandant"], dry_run=True).status_code == 200
    assert _buchungen(haus["anderer"]) == 0 and _buchungen(haus["mandant"]) == 0


def test_ein_abdruck_der_keiner_ist_ist_kein_vorgang(haus):
    assert haus["als"](ANNA).post("/approvals/journal_import/irgendwas", json={"action": "post"}).status_code == 404


# ── Lieferantengutschrift und -belastung ──────────────────────────────────────

def _memo(haus, wer: dict, art: str = "credit-memos", brutto: float = 119) -> str:
    netto = round(brutto / 1.19, 2)
    antwort = haus["als"](wer).post(f"/einkauf/{art}", json={
        "supplierId": "SUP-1", "memoDate": "2026-10-13", "reason": "Preisabweichung",
        "items": [{"productName": "Weizen", "quantity": 1, "unitPrice": netto, "netAmount": netto,
                   "taxAmount": round(brutto - netto, 2), "grossAmount": brutto}]})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()["id"]


def _beleg(kennung: str) -> dict:
    import json
    with SessionLocal() as db:
        roh = db.execute(text("SELECT data FROM documents WHERE doc_number = :n"), {"n": kennung}).scalar()
    return roh if isinstance(roh, dict) else json.loads(roh)


@pytest.mark.parametrize("art,subjekt", [("credit-memos", "einkauf_credit_memo"), ("debit-memos", "einkauf_debit_memo")])
def test_gutschrift_und_belastung_buchen_erst_mit_der_zweiten_person(haus, art, subjekt):
    memo = _memo(haus, ANNA, art)
    beleg = _beleg(memo)
    assert (beleg["tenantId"], beleg["createdBy"]) == (haus["mandant"], "anna")  # aus der Anmeldung, nicht aus einem Kopf

    ohne = haus["als"](ANNA).post(f"/einkauf/{art}/{memo}/buchung")
    assert ohne.status_code == 409 and "Freigabe erforderlich (R3)" in ohne.text
    assert _beleg(memo)["booked"] is False

    weg = f"/approvals/{subjekt}/{memo}"
    fid = haus["als"](ANNA).post(weg, json={"action": "post"}).json()["id"]
    assert haus["als"](ANNA).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 403
    assert haus["als"](LAGER).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 403
    assert haus["als"](CLARA).post(f"{weg}/{fid}/decision", json={"granted": True}).status_code == 200
    gebucht = haus["als"](ANNA).post(f"/einkauf/{art}/{memo}/buchung")
    assert gebucht.status_code == 200, gebucht.text
    assert _beleg(memo)["booked"] is True
    assert [f["status"] for f in haus["als"](CLARA).get(weg).json()] == ["consumed"]


def test_verrechnen_braucht_dieselbe_freigabe_und_das_recht_des_einkaufs(haus):
    memo = _memo(haus, ANNA)
    rumpf = {"invoiceIds": ["RE-1"]}
    assert haus["als"](LAGER).post(f"/einkauf/credit-memos/{memo}/settle", json=rumpf).status_code == 403
    assert haus["als"](LAGER).post(f"/einkauf/credit-memos/{memo}/buchung").status_code == 403
    ohne = haus["als"](ANNA).post(f"/einkauf/credit-memos/{memo}/settle", json=rumpf)
    assert ohne.status_code == 409 and "Freigabe erforderlich" in ohne.text
    assert _beleg(memo)["settled"] is False


def test_gutschrift_ueber_1000_braucht_die_erhoehte_berechtigung(haus):
    memo = _memo(haus, ANNA, brutto=2380)
    anfrage = haus["als"](ANNA).post(f"/approvals/einkauf_credit_memo/{memo}", json={"action": "post"}).json()
    assert anfrage["risk"] == "R4"
    weg = f"/approvals/einkauf_credit_memo/{memo}/{anfrage['id']}/decision"
    assert haus["als"](BERND).post(weg, json={"granted": True}).status_code == 403
    assert haus["als"](CLARA).post(weg, json={"granted": True}).status_code == 200


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
