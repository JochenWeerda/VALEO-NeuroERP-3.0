"""Eine Belegmaske, neun Varianten (BELEG-020): erzeugte ScreenDefinitions und die Wege, aus denen sie lesen.

Geprueft gegen die echte Datenbank, an den Referenzbelegen.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import belege as belege_endpunkt
from app.core import belegvertrag as bv
from app.core import screen_definitions_beleg as sdb
from app.core.belegkommandos import BELEGKOMMANDOS
from app.core.database import SessionLocal
from app.core.screen_governance import governance_errors, ux_lint
from app.services import docflow_service
from testgrenze import ersetze_mandant, ersetze_nutzer

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _spalten(definition: dict, reiter: str) -> list[str]:
    tab = next(t for t in definition["tabs"] if t["key"] == reiter)
    return [c["key"] for c in tab["tables"][0]["columns"]]


def _felder(definition: dict) -> list[str]:
    return [f["key"] for f in definition["tabs"][0]["fields"]]


# ── Die Definitionen (ohne Datenbank) ─────────────────────────────────────────

@pytest.mark.parametrize("belegart", sorted(bv.BELEGARTEN))
def test_jede_variante_besteht_die_regeln_der_masken(belegart):
    definition = sdb.build_beleg_screen_definition(belegart)
    assert governance_errors(definition) == []
    assert [f for f in ux_lint(definition)] == []
    assert [t["key"] for t in definition["tabs"]] == list(sdb.REITER)
    assert definition["title"] == bv.BELEGARTEN[belegart].bezeichnung
    assert definition["variant"]["belegart"] == belegart
    assert len([a for a in definition["actions"] if a["kind"] == "primary"]) == 1


def test_es_gibt_eine_quelle_und_neun_kennungen():
    alle = sdb.alle_beleg_screen_definitions()
    assert len(alle) == 9 and all(k == d["id"] and k.startswith("beleg/") for k, d in alle.items())
    # Das Geruest ist dasselbe: dieselben Reiter, dieselben Spalten in Kette, Dokumenten und Verlauf.
    for reiter in ("kette", "dokumente", "historie"):
        assert len({tuple(_spalten(d, reiter)) for d in alle.values()}) == 1


def test_preise_gibt_es_nur_in_varianten_mit_preisen():
    preisspalten = {"einzelpreis", "rabatt_prozent", "steuerschluessel", "netto", "aufwandskonto"}
    for belegart, variante in bv.BELEGARTEN.items():
        definition = sdb.build_beleg_screen_definition(belegart)
        spalten, felder = set(_spalten(definition, "positionen")), set(_felder(definition))
        if variante.mit_preisen:
            assert {"einzelpreis", "netto", "steuerschluessel"} <= spalten and {"netto", "steuer", "brutto"} <= felder
        else:
            assert not spalten & preisspalten and not felder & {"netto", "steuer", "brutto", "waehrung"}
            assert definition["agentContract"]["sensitiveFields"] == []
        assert ("aufwandskonto" in spalten) is (variante.mit_preisen and variante.richtung == "einkauf")
        assert ("menge_offen" in spalten) is bool(variante.folgebelege)
        assert ("buchungsstand" in felder) is variante.bucht
    lieferschein = sdb.build_beleg_screen_definition("sales_delivery")
    assert _spalten(lieferschein, "positionen") == ["pos_nr", "artikel_nr", "bezeichnung", "menge", "einheit", "charge", "menge_offen"]


def test_beschriftung_folgt_der_variante():
    rechnung = sdb.build_beleg_screen_definition("sales_invoice")
    eingang = sdb.build_beleg_screen_definition("purchase_invoice")
    kopf = lambda d: {f["key"]: f["label"] for f in d["tabs"][0]["fields"]}  # noqa: E731
    assert kopf(rechnung)["beleg_nr"] == "Rechnung Nr." and kopf(rechnung)["partner_name"] == "Kunde"
    assert kopf(rechnung)["steuer"] == "Umsatzsteuer"
    assert kopf(eingang)["beleg_nr"] == "Eingangsrechnung Nr." and kopf(eingang)["partner_name"] == "Lieferant"
    assert kopf(eingang)["steuer"] == "Vorsteuer"


@pytest.mark.parametrize("belegart", sorted(bv.BELEGARTEN))
def test_aktionen_kommen_aus_dem_verzeichnis_und_der_variante(belegart):
    variante = bv.BELEGARTEN[belegart]
    aktionen = {a["key"]: a for a in sdb.build_beleg_screen_definition(belegart)["actions"]}
    erwartet = {"freigeben", "stornieren"} | {f"umwandeln:{f}" for f in variante.folgebelege}
    assert set(aktionen) == erwartet | ({"buchen"} if variante.bucht else set())
    for aktion in aktionen.values():
        kommando = BELEGKOMMANDOS[aktion["kommando"]]
        assert aktion["commandEndpoint"] == f"/api/v1{kommando.pfad}".replace("{doc_id}", "{entity_id}")
        assert aktion["method"] == kommando.methode and aktion["permission"] == f"belege.{kommando.recht}"
        # Ab R3 bestaetigt der Mensch ausdruecklich.
        assert aktion["requiresConfirmation"] is kommando.freigabe_noetig
    assert aktionen["stornieren"]["dangerLevel"] == "critical"


# ── Die Wege, aus denen die Maske liest ───────────────────────────────────────

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
    mandant = f"sd-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "Belegmaske Test")
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
    app.include_router(belege_endpunkt.router, prefix="/api/v1/belege")
    ersetze_mandant(app, satz["mandant"])
    client = TestClient(app)

    def als(*rollen: str) -> TestClient:
        ersetze_nutzer(app, *rollen)
        return client

    return als


def test_jede_quelle_der_definition_antwortet_und_liefert_jedes_feld_und_jede_spalte(http, satz):
    """Die Definition verspricht nichts, was der Weg nicht liefert — fuer alle 17 Referenzbelege."""
    for rolle in (r for r in satz if r != "mandant"):
        b = satz[rolle]
        definition = sdb.build_beleg_screen_definition(b["doc_type"])
        quellen = {q["key"]: q["endpoint"].replace("{entity_id}", b["id"]) for q in definition["dataSources"]}
        kopf = http("admin").get(quellen["entity"])
        assert kopf.status_code == 200, (rolle, kopf.text)
        fehlend = [f for f in _felder(definition) if f not in kopf.json()]
        assert fehlend == [], (rolle, fehlend)
        assert kopf.json()[definition["identityField"]] == b["doc_number"]
        for reiter in sdb.REITER[1:]:
            seite = http("admin").get(quellen[reiter], params={"limit": 50})
            assert seite.status_code == 200, (rolle, reiter, seite.text)
            daten = seite.json()
            assert daten["tab_key"] == reiter and daten["total"] == len(daten["items"])
            for zeile in daten["items"]:
                assert set(_spalten(definition, reiter)) <= set(zeile), (rolle, reiter)
        positionen = http("admin").get(quellen["positionen"]).json()
        assert positionen["total"] > 0, rolle


def test_kopf_und_reiter_gelten_dieselben_rechte_wie_der_beleg(http, satz):
    rechnung = satz["vk-rechnung-1"]
    basis = f"/api/v1/belege/sales_invoice/{rechnung['id']}"
    for weg in ("/kopf", "/tabs/positionen", "/tabs/historie"):
        assert http("EINKAUF_ADMIN").get(basis + weg).status_code == 403
        assert http().get(basis + weg).status_code == 403
    # Das Lager sieht Mengen, aber an keiner Stelle einen Betrag.
    kopf = http("LAGER_LESEN").get(basis + "/kopf").json()
    assert kopf["preise_sichtbar"] is False and not {"netto", "steuer", "brutto"} & set(kopf)
    for zeile in http("LAGER_LESEN").get(basis + "/tabs/positionen").json()["items"]:
        assert all(zeile[feld] is None for feld in bv.PREISFELDER) and float(zeile["menge"]) > 0
    mit_preisen = http("SALES_LESEN").get(basis + "/kopf").json()
    assert float(mit_preisen["brutto"]) > 0
    assert all(a["erlaubt"] is False for a in mit_preisen["aktionen"])
    assert http("admin").get(basis + "/tabs/geheim").status_code == 404
    assert http("admin").get(f"/api/v1/belege/sales_order/{rechnung['id']}/kopf").status_code == 404


def test_kette_und_verlauf_sind_lesbar_beschriftet_und_blaettern(http, satz):
    auftrag = f"/api/v1/belege/sales_order/{satz['vk-auftrag']['id']}"
    kette = http("admin").get(auftrag + "/tabs/kette").json()["items"]
    assert {(k["richtung"], k["bezeichnung"]) for k in kette} == {("Vorgänger", "Angebot"), ("Nachfolger", "Lieferschein")}
    seite1 = http("admin").get(auftrag + "/tabs/kette", params={"limit": 2, "page": 1}).json()
    seite2 = http("admin").get(auftrag + "/tabs/kette", params={"limit": 2, "page": 2}).json()
    assert seite1["total"] == 3 and len(seite1["items"]) == 2 and len(seite2["items"]) == 1
    verlauf = http("admin").get(f"/api/v1/belege/sales_invoice/{satz['vk-rechnung-storno']['id']}/tabs/historie").json()
    assert [v["nach_status"] for v in verlauf["items"]][-2:] == ["posted", "reversed"]
