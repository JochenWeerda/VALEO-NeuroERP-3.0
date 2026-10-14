"""Lieferantengutschriften und der alte Rechnungsweg lesen und schreiben nur im eigenen Mandanten.

Bis 13.10.2026 lieferten die Lesewege die Belege aller Mandanten; die Freigabe zur Buchung, das Aendern und das
Loeschen trafen auch fremde Belege, und der Handelnde kam aus einem Kopf, den jeder setzen kann.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import credit_debit_memos, finance_invoices
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from testgrenze import ersetze_mandant

ANNA = {"sub": "anna", "name": "a.petersen", "roles": ["FINANCE_ADMIN", "EINKAUF_ADMIN", "SALES_ADMIN"]}
CLARA = {"sub": "clara", "name": "c.onken", "roles": ["FINANCE_ADMIN", "EINKAUF_ADMIN", "SALES_ADMIN"]}
LAGER = {"sub": "lars", "name": "l.janssen", "roles": ["LAGER_ADMIN"]}


@pytest.fixture
def haus(monkeypatch):
    mandant, anderer = f"lm-{uuid.uuid4().hex[:8]}", f"lm-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        for m in (mandant, anderer):
            db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": m})
        db.commit()
    monkeypatch.setattr(finance_invoices, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(credit_debit_memos.router)
    app.include_router(finance_invoices.router)
    ersetze_mandant(app, mandant)
    client = TestClient(app, raise_server_exceptions=False)
    herrenlos: list[str] = []

    def als(nutzer: dict, wo: str = mandant) -> TestClient:
        ersetze_mandant(app, wo)
        app.dependency_overrides[get_current_user] = lambda: nutzer
        return client

    yield {"mandant": mandant, "anderer": anderer, "als": als, "herrenlos": herrenlos}
    with SessionLocal() as db:
        for m in (mandant, anderer):
            db.execute(text("DELETE FROM documents WHERE CAST(data AS jsonb)->>'tenantId' = :t"), {"t": m})
            db.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": m})
        for nummer in herrenlos:
            db.execute(text("DELETE FROM documents WHERE doc_number = :n"), {"n": nummer})
        db.commit()


def _ohne_mandant(haus, art: str, daten: dict) -> str:
    """Ein Altbeleg, wie er vor dem 13.10.2026 entstand: ohne Mandant."""
    nummer = f"ALT-{uuid.uuid4().hex[:10]}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO documents (id, doc_type, doc_number, data) VALUES (:id, :a, :n, CAST(:d AS jsonb))"),
            {"id": str(uuid.uuid4()), "a": art, "n": nummer, "d": json.dumps({**daten, "number": nummer, "id": nummer})})
        db.commit()
    haus["herrenlos"].append(nummer)
    return nummer


def _beleg(nummer: str) -> dict | None:
    with SessionLocal() as db:
        roh = db.execute(text("SELECT data FROM documents WHERE doc_number = :n"), {"n": nummer}).scalar()
    return roh if roh is None or isinstance(roh, dict) else json.loads(roh)


# ── Lieferantengutschrift und -belastung ──────────────────────────────────────

MEMO = {"supplierId": "SUP-1", "memoDate": "2026-10-13", "reason": "Preisabweichung",
        "items": [{"productName": "Weizen", "quantity": 1, "unitPrice": 100, "netAmount": 100, "taxAmount": 19,
                   "grossAmount": 119}]}


def _memo(haus, wer: dict, wo: str, art: str = "credit-memos", **mehr) -> str:
    antwort = haus["als"](wer, wo).post(f"/einkauf/{art}", json={**MEMO, **mehr})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()["id"]


@pytest.mark.parametrize("art", ["credit-memos", "debit-memos"])
def test_die_liste_zeigt_nur_die_belege_des_eigenen_mandanten(haus, art):
    eigen = _memo(haus, ANNA, haus["mandant"], art)
    fremd = _memo(haus, CLARA, haus["anderer"], art)
    liste = haus["als"](ANNA).get(f"/einkauf/{art}", params={"limit": 500})
    assert liste.status_code == 200, liste.text
    kennungen = {m["id"] for m in liste.json()}
    assert eigen in kennungen and fremd not in kennungen
    assert {m["id"] for m in haus["als"](CLARA, haus["anderer"]).get(f"/einkauf/{art}").json()} == {fremd}


@pytest.mark.parametrize("art", ["credit-memos", "debit-memos"])
def test_ein_fremder_beleg_ist_nicht_abrufbar(haus, art):
    fremd = _memo(haus, CLARA, haus["anderer"], art)
    assert haus["als"](ANNA).get(f"/einkauf/{art}/{fremd}").status_code == 404
    assert haus["als"](CLARA, haus["anderer"]).get(f"/einkauf/{art}/{fremd}").json()["id"] == fremd


def test_lesen_braucht_das_recht_des_einkaufs(haus):
    eigen = _memo(haus, ANNA, haus["mandant"])
    assert haus["als"](LAGER).get("/einkauf/credit-memos").status_code == 403
    assert haus["als"](LAGER).get(f"/einkauf/credit-memos/{eigen}").status_code == 403
    assert haus["als"](LAGER).get("/einkauf/debit-memos").status_code == 403


def test_ein_altbeleg_ohne_mandant_wird_niemandem_ausgeliefert(haus):
    alt = _ohne_mandant(haus, "credit_memo", {**MEMO, "supplierName": "Alt", "netAmount": 100, "taxAmount": 19,
                                              "grossAmount": 119, "settled": False, "booked": False})
    assert alt not in {m["id"] for m in haus["als"](ANNA).get("/einkauf/credit-memos", params={"limit": 500}).json()}
    assert haus["als"](ANNA).get(f"/einkauf/credit-memos/{alt}").status_code == 404


@pytest.mark.parametrize("art", ["credit-memos", "debit-memos"])
def test_die_freigabe_zur_buchung_gilt_nur_im_eigenen_mandanten_und_nennt_die_anmeldung(haus, art):
    """Bis 13.10.2026 ohne Mandant und Rolle; der Freigebende kam aus dem Kopf ``X-User-ID``."""
    fremd = _memo(haus, CLARA, haus["anderer"], art, settlementId="SET-9")
    eigen = _memo(haus, ANNA, haus["mandant"], art, settlementId="SET-1")
    assert _beleg(eigen)["approvalStatus"] == "ENTWURF"
    assert haus["als"](ANNA).post(f"/einkauf/{art}/{fremd}/freigabe").status_code == 404
    assert _beleg(fremd)["approvalStatus"] == "ENTWURF"
    assert haus["als"](LAGER).post(f"/einkauf/{art}/{eigen}/freigabe").status_code == 403
    frei = haus["als"](ANNA).post(f"/einkauf/{art}/{eigen}/freigabe", headers={"X-User-ID": "jemand-anderes"})
    assert frei.status_code == 200, frei.text
    beleg = _beleg(eigen)
    assert (beleg["approvalStatus"], beleg["approvedBy"]) == ("FREIGEGEBEN", "anna")


def test_anlegen_und_buchen_nennen_die_anmeldung_nicht_einen_kopf(haus):
    antwort = haus["als"](ANNA).post("/einkauf/credit-memos", json=MEMO, headers={"X-User-ID": "jemand-anderes"})
    memo = antwort.json()["id"]
    beleg = _beleg(memo)
    assert (beleg["createdBy"], beleg["approvedBy"], beleg["tenantId"]) == ("anna", "anna", haus["mandant"])
    gebucht = haus["als"](ANNA).post(f"/einkauf/credit-memos/{memo}/buchung", headers={"X-User-ID": "jemand-anderes"})
    assert gebucht.status_code == 200, gebucht.text
    with SessionLocal() as db:
        wer = db.execute(text(
            "SELECT CAST(data AS jsonb)->>'bookedBy' FROM documents WHERE doc_type = 'ap_memo_booking' "
            "AND CAST(data AS jsonb)->>'memoId' = :m"), {"m": memo}).scalar()
        db.execute(text("DELETE FROM documents WHERE doc_type = 'ap_memo_booking' AND CAST(data AS jsonb)->>'memoId' = :m"),
                   {"m": memo})
        db.commit()
    assert wer == "anna"


# ── Alter Rechnungsweg ────────────────────────────────────────────────────────

def _rechnung(nummer: str, kunde: str = "kunde-1", **mehr) -> dict:
    return {"number": nummer, "date": "2026-10-13", "customerId": kunde, "dueDate": "2026-11-12", "status": "ENTWURF",
            "subtotalNet": 100.0, "totalTax": 19.0, "totalGross": 119.0, **mehr}


def _lege_an(haus, wer: dict, wo: str, **mehr) -> str:
    nummer = f"LM-{uuid.uuid4().hex[:10]}"
    antwort = haus["als"](wer, wo).post("/finance/invoices", json=_rechnung(nummer, **mehr))
    assert antwort.status_code == 200, antwort.text
    return nummer


def test_die_rechnung_traegt_ihren_mandanten_und_ist_nur_dort_lesbar(haus):
    eigen = _lege_an(haus, ANNA, haus["mandant"])
    fremd = _lege_an(haus, CLARA, haus["anderer"])
    assert _beleg(eigen)["tenantId"] == haus["mandant"] and _beleg(fremd)["tenantId"] == haus["anderer"]
    assert haus["als"](ANNA).get(f"/finance/invoices/{eigen}").json()["invoice"]["number"] == eigen
    assert haus["als"](ANNA).get(f"/finance/invoices/{fremd}").status_code == 404
    liste = haus["als"](ANNA).get("/finance/invoices", params={"limit": 1000}).json()
    assert [r["number"] for r in liste["invoices"]] == [eigen] and liste["total"] == 1


def test_eine_fremde_rechnung_wird_weder_geaendert_noch_geloescht(haus):
    fremd = _lege_an(haus, CLARA, haus["anderer"])
    vorher = _beleg(fremd)
    geaendert = haus["als"](ANNA).put(f"/finance/invoices/{fremd}", json=_rechnung(fremd, kunde="kunde-des-angreifers"))
    assert geaendert.status_code == 404
    assert haus["als"](ANNA).delete(f"/finance/invoices/{fremd}").status_code == 404
    assert _beleg(fremd) == vorher
    # Die eigene laesst sich aendern und behaelt ihren Mandanten.
    eigen = _lege_an(haus, ANNA, haus["mandant"])
    assert haus["als"](ANNA).put(f"/finance/invoices/{eigen}", json=_rechnung(eigen, kunde="kunde-2")).status_code == 200
    assert (_beleg(eigen)["customerId"], _beleg(eigen)["tenantId"]) == ("kunde-2", haus["mandant"])
    assert haus["als"](ANNA).delete(f"/finance/invoices/{eigen}").status_code == 204 and _beleg(eigen) is None


def test_eine_vergebene_nummer_ueberschreibt_nicht_die_rechnung_eines_anderen_mandanten(haus):
    """Die Nummer ist im Speicher systemweit eindeutig; das Anlegen ersetzte bis 13.10.2026 still den fremden Beleg."""
    fremd = _lege_an(haus, CLARA, haus["anderer"])
    vorher = _beleg(fremd)
    antwort = haus["als"](ANNA).post("/finance/invoices", json=_rechnung(fremd, kunde="kunde-des-angreifers"))
    assert antwort.status_code == 409 and "bereits vergeben" in antwort.text
    assert _beleg(fremd) == vorher


def test_eine_altrechnung_ohne_mandant_wird_niemandem_ausgeliefert(haus):
    alt = _ohne_mandant(haus, "sales_invoice", _rechnung("x"))
    assert haus["als"](ANNA).get(f"/finance/invoices/{alt}").status_code == 404
    assert alt not in [r["number"] for r in haus["als"](ANNA).get("/finance/invoices", params={"limit": 1000}).json()["invoices"]]
    assert haus["als"](ANNA).delete(f"/finance/invoices/{alt}").status_code == 404
    assert haus["als"](ANNA).post("/finance/invoices", json=_rechnung(alt)).status_code == 409
    assert "tenantId" not in _beleg(alt)


# ── Altbelege zuordnen ────────────────────────────────────────────────────────

def _offener_posten(mandant: str, nummer: str) -> None:
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr) VALUES (:id, :t, :n)"),
                   {"id": str(uuid.uuid4()), "t": mandant, "n": nummer})
        db.commit()


def test_ein_altbeleg_bekommt_seinen_mandanten_nur_wenn_die_buchung_ihn_eindeutig_nennt(haus):
    import importlib.util
    import pathlib

    pfad = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "belege_mandant_nachtragen.py"
    spec = importlib.util.spec_from_file_location("belege_mandant_nachtragen", pfad)
    skript = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(skript)

    eindeutig = _ohne_mandant(haus, "sales_invoice", _rechnung("x"))
    strittig = _ohne_mandant(haus, "sales_invoice", _rechnung("x"))
    ungebucht = _ohne_mandant(haus, "sales_invoice", _rechnung("x"))
    _offener_posten(haus["mandant"], eindeutig)
    _offener_posten(haus["mandant"], strittig)
    _offener_posten(haus["anderer"], strittig)
    try:
        def lauf(apply: bool) -> dict:
            with SessionLocal() as db:
                ergebnis = skript.ordne_zu(db, apply=apply)
                db.commit()
            mein = lambda liste: {e["nummer"] for e in liste} & {eindeutig, strittig, ungebucht}  # noqa: E731
            return {"zugeordnet": mein(ergebnis["zugeordnet"]), "offen": mein(ergebnis["offen"])}

        assert lauf(False) == {"zugeordnet": {eindeutig}, "offen": {strittig, ungebucht}}
        assert "tenantId" not in _beleg(eindeutig)                       # ohne --apply wird nur gezeigt
        assert lauf(True)["zugeordnet"] == {eindeutig}
        assert _beleg(eindeutig)["tenantId"] == haus["mandant"]
        assert "tenantId" not in _beleg(strittig) and "tenantId" not in _beleg(ungebucht)
        assert haus["als"](ANNA).get(f"/finance/invoices/{eindeutig}").status_code == 200
        assert haus["als"](CLARA, haus["anderer"]).get(f"/finance/invoices/{eindeutig}").status_code == 404
        assert lauf(True)["zugeordnet"] == set()                         # ein zweiter Lauf findet nichts mehr
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_erp.offene_posten WHERE rechnungsnr IN (:a, :b)"),
                       {"a": eindeutig, "b": strittig})
            db.commit()
