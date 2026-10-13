"""Rechte an Belegen (BELEG-012): Belegweg, DocFlow-Kommandos und MCP-Werkzeuge pruefen die Rolle der Anmeldung.

Geprueft gegen die echte Datenbank, an den 17 Referenzbelegen.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import belege as belege_endpunkt
from app.api.v1.endpoints import docflow as docflow_endpunkt
from app.auth.beleg_roles import RECHTE, darf, rollen_fuer
from app.core import belegvertrag as bv
from app.core.belegkommandos import BELEGKOMMANDOS
from app.core.database import SessionLocal
from app.services import docflow_service
from app.services.mcp_execution_service import ToolExecutionRequest, execute_mcp_tool
from freigabehilfe import sichere_freigabe
from testgrenze import ersetze_mandant, ersetze_nutzer

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


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


@pytest.fixture(scope="module")
def satz():
    mandant = f"br-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "Belegrechte Test")
        db.commit()
        angelegt = _modul("referenzbelege_anlegen").lege_an(db, mandant)
    yield {"mandant": mandant, **{b["rolle"]: b for b in angelegt}}
    patch.undo()
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


@pytest.fixture(scope="module")
def http(satz):
    app = FastAPI()
    app.include_router(belege_endpunkt.router, prefix="/belege")
    app.include_router(docflow_endpunkt.router, prefix="/docflow")
    ersetze_mandant(app, satz["mandant"])
    client = TestClient(app)

    def als(*rollen: str) -> TestClient:
        ersetze_nutzer(app, *rollen)
        return client

    return als


def _beleg(http, satz, rolle: str, *rollen: str):
    b = satz[rolle]
    return http(*rollen).get(f"/belege/{b['doc_type']}/{b['id']}")


def _aktion(beleg: dict, key: str) -> dict:
    return next(a for a in beleg["aktionen"] if a["key"] == key)


def _status(satz, rolle: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"),
                          {"id": satz[rolle]["id"]}).scalar()


def _buchungen(satz) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"),
                          {"t": satz["mandant"]}).scalar()


# ── Rollen je Recht (ohne Datenbank) ──────────────────────────────────────────

def test_jedes_kommando_nennt_ein_bekanntes_recht():
    assert {k.recht for k in BELEGKOMMANDOS.values()} <= set(RECHTE)
    assert {k.name: k.recht for k in BELEGKOMMANDOS.values() if k.freigabe_noetig} == {
        "docflow.post": "buchen", "docflow.reverse": "stornieren"}


def test_der_beleg_gehoert_seinem_bereich():
    assert darf({"roles": ["SALES_BEARBEITEN"]}, "bearbeiten", "sales_invoice")
    assert not darf({"roles": ["SALES_BEARBEITEN"]}, "lesen", "purchase_invoice")
    assert darf({"roles": ["EINKAUF_BEARBEITEN"]}, "buchen", "purchase_invoice")
    assert not darf({"roles": ["EINKAUF_ADMIN"]}, "lesen", "sales_order")
    # Die Buchhaltung liest und bucht beide Richtungen, bearbeitet aber keinen Beleg des Verkaufs.
    assert darf({"roles": ["FINANCE_BEARBEITEN"]}, "buchen", "sales_invoice")
    assert darf({"roles": ["FINANCE_LESEN"]}, "preise", "purchase_order")
    assert not darf({"roles": ["FINANCE_ADMIN"]}, "bearbeiten", "sales_invoice")
    assert not darf({"roles": []}, "lesen", "sales_invoice")
    assert not darf({"roles": ["admin"]}, "lesen", "pos_receipt")


def test_das_lager_liest_ohne_preise_und_bearbeitet_nur_lieferschein_und_wareneingang():
    for art in bv.BELEGARTEN:
        assert darf({"roles": ["LAGER_LESEN"]}, "lesen", art)
        assert not darf({"roles": ["LAGER_ADMIN"]}, "preise", art)
        assert not darf({"roles": ["LAGER_ADMIN"]}, "buchen", art)
        assert darf({"roles": ["LAGER_BEARBEITEN"]}, "bearbeiten", art) is (art in {"sales_delivery", "goods_receipt"})


def test_gebuchtes_storniert_nur_buchhaltung_und_bereichsleitung():
    assert rollen_fuer("stornieren", "sales_invoice") == {"admin", "SALES_ADMIN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN"}
    assert rollen_fuer("stornieren", "purchase_credit_memo") == {
        "admin", "EINKAUF_ADMIN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN"}
    # Was Finance nicht bucht, nimmt zurueck, wer es bearbeiten darf.
    assert rollen_fuer("stornieren", "sales_order") == rollen_fuer("bearbeiten", "sales_order")
    assert "manager" not in rollen_fuer("stornieren", "sales_invoice")


# ── Belegweg ──────────────────────────────────────────────────────────────────

def test_ohne_rolle_und_mit_rolle_des_anderen_bereichs_gibt_es_den_beleg_nicht(http, satz):
    assert _beleg(http, satz, "vk-rechnung-1").status_code == 403
    assert _beleg(http, satz, "vk-rechnung-1", "sachbearbeitung").status_code == 403
    assert _beleg(http, satz, "vk-rechnung-1", "EINKAUF_ADMIN").status_code == 403
    assert _beleg(http, satz, "ek-rechnung-1", "SALES_ADMIN", "CRM_ADMIN").status_code == 403
    # Auch ein Beleg, den es nicht gibt, verraet sich nicht: erst das Recht, dann die Suche.
    assert http("EINKAUF_LESEN").get(f"/belege/sales_invoice/{uuid.uuid4()}").status_code == 403


def test_das_lager_bekommt_die_rechnung_ohne_preise_und_ohne_aktion(http, satz):
    antwort = _beleg(http, satz, "vk-rechnung-2", "LAGER_LESEN")
    assert antwort.status_code == 200
    roh = antwort.json()
    beleg = bv.Beleg.model_validate(roh)
    assert bv.pruefe(beleg) == []
    assert roh["preise_sichtbar"] is False and roh["summen"] is None
    assert all(pos[feld] is None for pos in roh["positionen"] for feld in bv.PREISFELDER)
    assert all(float(pos["menge"]) > 0 for pos in roh["positionen"])
    # Kein Betrag an irgendeiner Stelle der Antwort.
    assert "100" not in {str(v) for pos in roh["positionen"] for k, v in pos.items() if k in bv.PREISFELDER}
    assert roh["aktionen"] and all(a["erlaubt"] is False and a["grund"] for a in roh["aktionen"])


def test_lesen_mit_preisen_aber_ohne_aktion(http, satz):
    roh = _beleg(http, satz, "vk-rechnung-2", "SALES_LESEN").json()
    assert roh["preise_sichtbar"] is True and roh["summen"]["brutto"]
    assert all(a["erlaubt"] is False for a in roh["aktionen"])
    assert _aktion(roh, "buchen")["grund"] == "Keine Berechtigung."


def test_sachbearbeitung_bucht_aber_storniert_nichts_gebuchtes(http, satz):
    offen = _beleg(http, satz, "vk-rechnung-2", "SALES_BEARBEITEN").json()
    assert _aktion(offen, "buchen")["erlaubt"] is True
    gebucht = _beleg(http, satz, "vk-rechnung-1", "SALES_BEARBEITEN").json()
    # Einen gebuchten Beleg storniert die Buchhaltung oder die Leitung des Bereichs (FIN-CONTROL-001), nicht die
    # Sachbearbeitung.
    assert _aktion(gebucht, "stornieren")["grund"] == "Keine Berechtigung."
    assert _aktion(gebucht, "umwandeln:sales_credit_memo")["erlaubt"] is True
    for rollen in (("FINANCE_BEARBEITEN",), ("SALES_ADMIN",)):
        assert _aktion(_beleg(http, satz, "vk-rechnung-1", *rollen).json(), "stornieren")["erlaubt"] is True
    # Die Buchhaltung bucht, erstellt aber keine Gutschrift des Verkaufs.
    finanz = _beleg(http, satz, "vk-rechnung-1", "FINANCE_BEARBEITEN").json()
    assert _aktion(finanz, "umwandeln:sales_credit_memo")["grund"] == "Keine Berechtigung."


def test_der_sachliche_sperrgrund_bleibt_vor_dem_recht_sichtbar(http, satz):
    roh = _beleg(http, satz, "vk-rechnung-ohne-schluessel", "SALES_LESEN").json()
    assert "prüfen" in _aktion(roh, "buchen")["grund"]


# ── DocFlow-Kommandos ─────────────────────────────────────────────────────────

def test_docflow_liefert_preise_nur_mit_preisrecht(http, satz):
    rechnung, bestellung = satz["vk-rechnung-1"]["id"], satz["ek-bestellung"]["id"]
    assert http("LAGER_ADMIN").get(f"/docflow/{rechnung}").status_code == 403
    assert http("EINKAUF_LESEN").get(f"/docflow/{rechnung}").status_code == 403
    assert http("SALES_LESEN").get(f"/docflow/{rechnung}").status_code == 200
    assert http("LAGER_LESEN").get(f"/docflow/{rechnung}/status-history").status_code == 200
    assert http().get(f"/docflow/{rechnung}/status-history").status_code == 403
    assert http("SALES_LESEN").get(f"/docflow/{bestellung}").status_code == 403
    liste = http("EINKAUF_LESEN").get("/docflow/", params={"limit": 200})
    assert liste.status_code == 200
    assert {b["doc_type"] for b in liste.json()} == {
        "purchase_order", "goods_receipt", "purchase_invoice", "purchase_credit_memo"}
    assert http("LAGER_LESEN").get("/docflow/", params={"limit": 200}).json() == []
    assert http("EINKAUF_LESEN").get("/docflow/", params={"doc_type": "sales_invoice"}).status_code == 403


def test_ohne_recht_wird_nichts_gebucht_storniert_angelegt_oder_umgewandelt(http, satz):
    vorher = _buchungen(satz)
    offen, gebucht = satz["vk-rechnung-2"]["id"], satz["vk-rechnung-1"]["id"]
    for rollen in ((), ("SALES_LESEN",), ("LAGER_ADMIN",), ("EINKAUF_ADMIN",)):
        antwort = http(*rollen).post(f"/docflow/{offen}/post", json={"idempotency_key": f"recht-{uuid.uuid4()}"})
        assert antwort.status_code == 403, rollen
    for rollen in (("SALES_BEARBEITEN",), ("manager",), ("EINKAUF_ADMIN",)):
        antwort = http(*rollen).post(f"/docflow/{gebucht}/reverse",
                                     json={"idempotency_key": f"recht-{uuid.uuid4()}", "reason": "ohne Recht"})
        assert antwort.status_code == 403, rollen
    neu = {"doc_type": "sales_invoice", "doc_number": f"RECHT-{uuid.uuid4().hex[:8]}", "customer_id": "REF-KUNDE",
           "idempotency_key": f"recht-{uuid.uuid4()}", "items": []}
    assert http("LAGER_BEARBEITEN").post("/docflow/", json=neu).status_code == 403
    assert http("FINANCE_ADMIN").post("/docflow/", json=neu).status_code == 403
    wandeln = {"target_doc_type": "sales_credit_memo", "idempotency_key": f"recht-{uuid.uuid4()}"}
    assert http("FINANCE_BEARBEITEN").post(f"/docflow/{gebucht}/convert", json=wandeln).status_code == 403
    assert http("SALES_LESEN").post(f"/docflow/{offen}/release", json={"idempotency_key": "recht-freigeben"}).status_code == 403
    assert http("SALES_LESEN").delete(f"/docflow/{offen}").status_code == 403
    assert http("SALES_LESEN").put(f"/docflow/{offen}", json={}).status_code == 403
    assert (_status(satz, "vk-rechnung-2"), _status(satz, "vk-rechnung-1")) == ("open", "posted")
    assert _buchungen(satz) == vorher


# ── MCP-Werkzeuge ─────────────────────────────────────────────────────────────

def _mcp(satz, werkzeug: str, parameter: dict, *rollen: str) -> dict:
    nutzer = {"sub": "agent-belegleser", "scopes": ["belege:read"],
              "raw": {"tenant_id": satz["mandant"], "realm_access": {"roles": list(rollen)}}}
    with SessionLocal() as db:
        return execute_mcp_tool(db, ToolExecutionRequest(tool_name=werkzeug, parameters=parameter), nutzer, None)


def test_der_scope_allein_zeigt_dem_agenten_keinen_beleg(satz):
    rechnung = {"belegart": "sales_invoice", "beleg_id": satz["vk-rechnung-1"]["id"]}
    assert _mcp(satz, "beleg.suchen", {"limit": 50})["count"] == 0
    for rollen in ((), ("EINKAUF_ADMIN",)):
        with pytest.raises(HTTPException) as fehler:
            _mcp(satz, "beleg.lesen", rechnung, *rollen)
        assert fehler.value.status_code == 403
    with pytest.raises(HTTPException) as fehler:
        _mcp(satz, "beleg.suchen", {"belegart": "purchase_invoice"}, "SALES_ADMIN")
    assert fehler.value.status_code == 403


def test_der_agent_sieht_was_seine_rolle_sieht(satz):
    rechnung = {"belegart": "sales_invoice", "beleg_id": satz["vk-rechnung-1"]["id"]}
    verkauf = _mcp(satz, "beleg.suchen", {"limit": 50}, "SALES_LESEN")["items"]
    assert len(verkauf) == 9 and all(v["belegart"].startswith("sales_") for v in verkauf)
    lager = _mcp(satz, "beleg.suchen", {"limit": 50}, "LAGER_LESEN")["items"]
    assert len(lager) == 17 and all(v["brutto"] is None and v["waehrung"] is None for v in lager)
    ohne_preise = _mcp(satz, "beleg.lesen", rechnung, "LAGER_LESEN")["beleg"]
    assert ohne_preise["summen"] is None and ohne_preise["preise_sichtbar"] is False
    mit_preisen = _mcp(satz, "beleg.lesen", rechnung, "SALES_LESEN")["beleg"]
    assert mit_preisen["summen"]["brutto"] and all(a["erlaubt"] is False for a in mit_preisen["aktionen"])


# ── Mit Recht geht es (veraendert den Satz, deshalb zuletzt) ──────────────────

def test_buchhaltung_bucht_und_storniert(http, satz):
    offen = satz["vk-rechnung-2"]["id"]
    gebucht = http("FINANCE_BEARBEITEN").post(f"/docflow/{offen}/post", json={"idempotency_key": "recht-buchen"})
    assert gebucht.status_code == 200, gebucht.text
    assert _status(satz, "vk-rechnung-2") == "posted"
    # Ein regelkonformer Storno: die Buchhaltung entscheidet und begruendet, ohne zweite Person.
    storno = http("FINANCE_BEARBEITEN").post(
        f"/docflow/{offen}/reverse", json={"idempotency_key": "recht-storno", "reason": "Test der Rechte"})
    assert storno.status_code == 200, storno.text
    assert _status(satz, "vk-rechnung-2") == "reversed"
    with SessionLocal() as db:
        akteure = db.execute(text(
            "SELECT actor FROM domain_docflow.document_status_history WHERE header_id = :id ORDER BY changed_at DESC LIMIT 2"),
            {"id": offen}).scalars().all()
    assert akteure == ["5f0c2a9e", "5f0c2a9e"]
