"""Lesende MCP-Werkzeuge fuer Belege und das Verzeichnis der Belegkommandos (BELEG-013).

Geprueft gegen die echte Datenbank, an den 17 Referenzbelegen: Der Agent liest denselben Beleg wie die Maske.
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
from app.core import belegvertrag as bv
from app.core.belegkommandos import BELEGKOMMANDOS, KEIN_BELEGKOMMANDO, RISIKOKLASSEN
from app.core.database import SessionLocal
from app.services import docflow_service
from app.services.mcp_execution_service import ToolExecutionRequest, execute_mcp_tool
from app.services.mcp_tool_registry_service import mcp_tool_registry_service
from testgrenze import ersetze_mandant, ersetze_nutzer

WURZEL = pathlib.Path(__file__).resolve().parent.parent
WERKZEUGE = ("beleg.arten", "beleg.suchen", "beleg.lesen")


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
    mandant = f"mb-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "MCP Belege Test")
        db.commit()
        angelegt = _modul("referenzbelege_anlegen").lege_an(db, mandant)
    yield {"mandant": mandant, **{b["rolle"]: b for b in angelegt}}
    patch.undo()
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


def _agent(mandant: str, *scopes: str) -> dict:
    # Rolle mit allen Rechten: Die Rechte je Rolle prueft tests/test_beleg_rechte.py.
    return {"sub": "agent-belegleser", "scopes": list(scopes or ("belege:read",)),
            "raw": {"tenant_id": mandant, "realm_access": {"roles": ["admin"]}}}


def _rufe(werkzeug: str, parameter: dict, nutzer: dict, modus: str = "dryRun") -> dict:
    with SessionLocal() as db:
        return execute_mcp_tool(db, ToolExecutionRequest(tool_name=werkzeug, parameters=parameter, mode=modus), nutzer, None)


def _stand(mandant: str) -> tuple:
    with SessionLocal() as db:
        return tuple(db.execute(text(
            "SELECT (SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t), "
            "(SELECT count(*) FROM domain_docflow.document_status_history WHERE tenant_id = :t), "
            "(SELECT count(*) FROM domain_docflow.document_command_log WHERE tenant_id = :t), "
            "(SELECT max(updated_at) FROM domain_docflow.document_headers WHERE tenant_id = :t), "
            "(SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t)"), {"t": mandant}).one())


# ── Verzeichnis der Belegkommandos ────────────────────────────────────────────

def _wege(router, praefix: str) -> set[tuple[str, str]]:
    return {(m, praefix + r.path) for r in router.routes for m in getattr(r, "methods", ()) if m != "HEAD"}


def test_jedes_kommando_hat_seinen_weg():
    vorhanden = _wege(docflow_endpunkt.router, "/docflow") | _wege(belege_endpunkt.router, "/belege")
    for kommando in BELEGKOMMANDOS.values():
        assert (kommando.methode, kommando.pfad) in vorhanden, kommando.name


def test_jeder_schreibende_docflow_weg_steht_im_verzeichnis():
    """Ein neuer schreibender Weg ohne Eintrag macht den Test rot."""
    schreibend = {w for w in _wege(docflow_endpunkt.router, "/docflow") if w[0] in {"POST", "PUT", "PATCH", "DELETE"}}
    im_verzeichnis = {(k.methode, k.pfad) for k in BELEGKOMMANDOS.values() if k.schreibend}
    assert schreibend == im_verzeichnis | set(KEIN_BELEGKOMMANDO)
    assert all(not k.schreibend for k in BELEGKOMMANDOS.values() if k.methode == "GET")


def test_risikoklassen_nach_mcp_write_freigabe_ab_r3_und_wiederholbar():
    for kommando in BELEGKOMMANDOS.values():
        assert kommando.risiko in RISIKOKLASSEN
        if kommando.freigabe_noetig:
            assert kommando.idempotent, kommando.name
    assert {k.name for k in BELEGKOMMANDOS.values() if not k.schreibend} == {"beleg.lesen"}
    assert {k.name: k.risiko for k in BELEGKOMMANDOS.values() if k.freigabe_noetig} == {
        "docflow.post": "R3", "docflow.reverse": "R4"}


# ── Registry ──────────────────────────────────────────────────────────────────

def test_die_belegwerkzeuge_sind_nur_lesend_registriert():
    for name in WERKZEUGE:
        werkzeug = mcp_tool_registry_service.get_tool(name)
        assert werkzeug["scope"] == "belege:read" and werkzeug["audit"] == "read"
        assert werkzeug["risk_class"] == "low" and werkzeug["idempotent"] is True
        assert werkzeug["human_approval_required"] is False
    # Entscheidung vom 13.10.2026: zuerst nur lesend — kein schreibendes Belegkommando hat ein MCP-Werkzeug.
    registriert = {t["tool_id"] for t in mcp_tool_registry_service.list_tools()}
    assert {n for n in registriert if n.startswith(("beleg.", "docflow."))} == set(WERKZEUGE)
    arten = mcp_tool_registry_service.get_tool("beleg.lesen")["input_schema"]["properties"]["belegart"]["enum"]
    assert set(arten) == set(bv.BELEGARTEN)


# ── Ausfuehrung ───────────────────────────────────────────────────────────────

def test_arten_nennt_varianten_und_kommandos(satz):
    antwort = _rufe("beleg.arten", {}, _agent(satz["mandant"]))
    assert {a["belegart"] for a in antwort["belegarten"]} == set(bv.BELEGARTEN)
    lieferschein = next(a for a in antwort["belegarten"] if a["belegart"] == "sales_delivery")
    assert lieferschein["mit_preisen"] is False and lieferschein["folgebelege"] == ["sales_invoice"]
    assert {k["name"] for k in antwort["kommandos"]} == set(BELEGKOMMANDOS)
    buchen = next(k for k in antwort["kommandos"] if k["name"] == "docflow.post")
    assert buchen == {
        "name": "docflow.post", "bezeichnung": "Beleg buchen", "methode": "POST",
        "pfad": "/api/v1/docflow/{doc_id}/post", "schreibend": True, "recht": "buchen", "risiko": "R3",
        "risiko_bezeichnung": "Geschäftlich verbindlich", "freigabe_noetig": True, "idempotent": True,
        "ueber_mcp": False,
    }
    # MCP-WRITE-014: Ueber MCP ist nur das Lesen erreichbar.
    assert [k["name"] for k in antwort["kommandos"] if k["ueber_mcp"]] == ["beleg.lesen"]


def test_agent_liest_denselben_beleg_wie_die_maske(satz):
    app = FastAPI()
    app.include_router(belege_endpunkt.router, prefix="/belege")
    ersetze_mandant(app, satz["mandant"])
    ersetze_nutzer(app, "admin")
    maske = TestClient(app)
    for rolle in (r for r in satz if r != "mandant"):
        b = satz[rolle]
        ueber_maske = maske.get(f"/belege/{b['doc_type']}/{b['id']}").json()
        ueber_mcp = _rufe("beleg.lesen", {"belegart": b["doc_type"], "beleg_id": b["id"]}, _agent(satz["mandant"]))
        assert ueber_mcp["beleg"] == ueber_maske, rolle
        beleg = bv.Beleg.model_validate(ueber_mcp["beleg"])
        assert bv.pruefe(beleg) == [], rolle
        # Jede Aktion nennt ein Kommando aus dem Verzeichnis; eine Freigabe braucht nur, was sie brauchen kann.
        for aktion in beleg.aktionen:
            assert aktion.kommando in BELEGKOMMANDOS, (rolle, aktion.key)
            assert not aktion.freigabe_noetig or BELEGKOMMANDOS[aktion.kommando].freigabe_noetig, (rolle, aktion.key)


def test_suchen_filtert_und_zeigt_ohne_preise_keinen_betrag(satz):
    agent = _agent(satz["mandant"])
    alle = _rufe("beleg.suchen", {"limit": 50}, agent)
    assert alle["count"] == 17
    rechnungen = _rufe("beleg.suchen", {"belegart": "sales_invoice"}, agent)["items"]
    assert len(rechnungen) == 4 and all(r["bezeichnung"] == "Rechnung" and r["brutto"] is not None for r in rechnungen)
    gebucht = _rufe("beleg.suchen", {"belegart": "sales_invoice", "status": "posted"}, agent)["items"]
    assert [r["beleg_nr"] for r in gebucht] == [satz["vk-rechnung-1"]["doc_number"]]
    lieferscheine = _rufe("beleg.suchen", {"belegart": "sales_delivery"}, agent)["items"]
    assert len(lieferscheine) == 2 and all(r["brutto"] is None and r["waehrung"] is None for r in lieferscheine)
    nach_nummer = _rufe("beleg.suchen", {"beleg_nr": "ref-ek-re"}, agent)["items"]
    assert {r["beleg_nr"] for r in nach_nummer} == {"REF-EK-RE-OHNE", "REF-EK-RE-STORNO"}
    lieferant = _rufe("beleg.suchen", {"partner_nr": "REF-LIEFERANT", "limit": 50}, agent)["items"]
    assert len(lieferant) == 8 and {r["partner_nr"] for r in lieferant} == {"REF-LIEFERANT"}
    assert _rufe("beleg.suchen", {"limit": 3}, agent)["count"] == 3


def test_ohne_scope_fremder_mandant_und_falsche_art(satz):
    rechnung = satz["vk-rechnung-1"]
    parameter = {"belegart": "sales_invoice", "beleg_id": rechnung["id"]}
    for werkzeug, p in (("beleg.arten", {}), ("beleg.suchen", {}), ("beleg.lesen", parameter)):
        with pytest.raises(HTTPException) as fehler:
            _rufe(werkzeug, p, _agent(satz["mandant"], "sales:read", "finance:read"))
        assert fehler.value.status_code == 403
    fremd = _agent("anderer-mandant")
    assert _rufe("beleg.suchen", {"limit": 50}, fremd)["count"] == 0
    with pytest.raises(HTTPException) as fehler:
        _rufe("beleg.lesen", parameter, fremd)
    assert fehler.value.status_code == 404
    with pytest.raises(HTTPException) as fehler:
        _rufe("beleg.lesen", {**parameter, "belegart": "sales_order"}, _agent(satz["mandant"]))
    assert fehler.value.status_code == 404


@pytest.mark.parametrize("werkzeug,parameter", [
    ("beleg.suchen", {"tenant_id": "anderer"}),
    ("beleg.suchen", {"belegart": "pos_receipt"}),
    ("beleg.suchen", {"limit": 500}),
    ("beleg.suchen", {"sql": "1=1"}),
    ("beleg.lesen", {"belegart": "sales_invoice"}),
    ("beleg.lesen", {"belegart": "frachtbrief", "beleg_id": "x"}),
    ("beleg.arten", {"belegart": "sales_invoice"}),
])
def test_ungueltige_eingaben_werden_abgelehnt(satz, werkzeug, parameter):
    with pytest.raises(HTTPException) as fehler:
        _rufe(werkzeug, parameter, _agent(satz["mandant"]))
    assert fehler.value.status_code == 422


def test_die_werkzeuge_schreiben_nichts_auch_nicht_im_modus_execute(satz):
    agent = _agent(satz["mandant"])
    vorher = _stand(satz["mandant"])
    rechnung = satz["vk-rechnung-2"]
    for modus in ("validate", "dryRun"):
        _rufe("beleg.arten", {}, agent, modus)
        _rufe("beleg.suchen", {}, agent, modus)
        _rufe("beleg.lesen", {"belegart": "sales_invoice", "beleg_id": rechnung["id"]}, agent, modus)
    with pytest.raises(HTTPException) as fehler:
        _rufe("beleg.lesen", {"belegart": "sales_invoice", "beleg_id": rechnung["id"]}, agent, "propose")
    assert fehler.value.status_code == 422
    assert _stand(satz["mandant"]) == vorher
