"""Lesender Belegweg (BELEG-011): DocFlow-Belege in der Form des Belegvertrags.

Geprueft gegen die echte Datenbank, an den 17 Referenzbelegen.
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
from app.core.database import SessionLocal
from app.services import docflow_service
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
    """Ein eingerichteter Mandant mit den Referenzbelegen: Rolle -> Beleg."""
    mandant = f"bl-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "Belege lesen Test")
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
def client():
    app = FastAPI()
    app.include_router(belege_endpunkt.router, prefix="/belege")
    ersetze_mandant(app)
    ersetze_nutzer(app, "sachbearbeitung")
    return TestClient(app)


def _lies(client, satz, rolle: str) -> dict:
    b = satz[rolle]
    antwort = client.get(f"/belege/{b['doc_type']}/{b['id']}", headers={"X-Tenant-ID": satz["mandant"]})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def _aktion(beleg: dict, key: str) -> dict | None:
    return next((a for a in beleg["aktionen"] if a["key"] == key), None)


def test_alle_referenzbelege_kommen_vertragsgerecht(client, satz):
    rollen = [r for r in satz if r != "mandant"]
    assert len(rollen) == 17
    for rolle in rollen:
        beleg = bv.Beleg.model_validate(_lies(client, satz, rolle))
        assert bv.pruefe(beleg) == [], rolle
        assert beleg.beleg_nr == satz[rolle]["doc_number"] and beleg.status == satz[rolle]["status"]
        assert beleg.historie and beleg.historie[-1].nach_status == beleg.status, rolle
        assert {h.akteur for h in beleg.historie} == {"referenzbelege"}, rolle


def test_gebuchte_rechnung_traegt_journal_kette_und_summen_je_steuerschluessel(client, satz):
    rechnung = _lies(client, satz, "vk-rechnung-1")
    assert rechnung["buchung"]["stand"] == "gebucht" and rechnung["buchung"]["journal_id"]
    assert rechnung["partner"] == {"rolle": "kunde", "nummer": "REF-KUNDE", "name": None}
    vor = [k for k in rechnung["kette"] if k["richtung"] == "vorgaenger"]
    nach = [k for k in rechnung["kette"] if k["richtung"] == "nachfolger"]
    assert [k["belegart"] for k in vor] == ["sales_delivery"]
    assert [(k["belegart"], k["beleg_nr"]) for k in nach] == [("sales_credit_memo", satz["vk-gutschrift"]["doc_number"])]
    gruppen = rechnung["summen"]["steuergruppen"]
    assert len(gruppen) == 2 and {g["steuerschluessel"] for g in gruppen} == {"2", "3"}
    assert _aktion(rechnung, "stornieren")["erlaubt"] is True
    assert _aktion(rechnung, "buchen") is None
    # Ein Teil ist gutgeschrieben; der Rest bleibt offen.
    assert any(float(p["menge_uebernommen"]) > 0 for p in rechnung["positionen"])
    assert _aktion(rechnung, "umwandeln:sales_credit_memo")["erlaubt"] is True


def test_lieferschein_und_wareneingang_liefern_keine_preise(client, satz):
    for rolle in ("vk-lieferschein-1", "ek-wareneingang-1"):
        beleg = _lies(client, satz, rolle)
        assert beleg["preise_sichtbar"] is False and beleg["summen"] is None
        assert beleg["positionen"], rolle
        for pos in beleg["positionen"]:
            assert all(pos[feld] is None for feld in bv.PREISFELDER), rolle
            assert float(pos["menge"]) > 0
        assert beleg["buchung"]["stand"] == "nicht_gebucht"
        assert _aktion(beleg, "buchen") is None


def test_beleg_ohne_steuerschluessel_steht_auf_pruefen_und_laesst_sich_nicht_buchen(client, satz):
    for rolle in ("vk-rechnung-ohne-schluessel", "ek-rechnung-ohne-schluessel"):
        beleg = _lies(client, satz, rolle)
        assert beleg["buchung"]["stand"] == "pruefen", rolle
        assert "prüfen" in beleg["buchung"]["grund"]
        buchen = _aktion(beleg, "buchen")
        assert buchen["erlaubt"] is False and buchen["grund"] == beleg["buchung"]["grund"]
        assert _aktion(beleg, "stornieren")["erlaubt"] is False


def test_offene_rechnung_ist_buchbar(client, satz):
    for rolle in ("vk-rechnung-2", "ek-rechnung-2"):
        beleg = _lies(client, satz, rolle)
        assert beleg["buchung"] == {"stand": "nicht_gebucht", "journal_id": None, "grund": None}
        buchen = _aktion(beleg, "buchen")
        assert buchen["erlaubt"] is True and buchen["kommando"] == "docflow.post" and buchen["freigabe_noetig"] is True


def test_stornierter_beleg_zeigt_die_stornierung_und_bietet_nichts_mehr_an(client, satz):
    for rolle in ("vk-rechnung-storno", "ek-rechnung-storno"):
        beleg = _lies(client, satz, rolle)
        assert beleg["status"] == "reversed" and beleg["buchung"]["stand"] == "storniert"
        assert beleg["buchung"]["journal_id"]
        assert [a["key"] for a in beleg["aktionen"] if a["erlaubt"]] == []
        assert [h["nach_status"] for h in beleg["historie"]][-2:] == ["posted", "reversed"]
        assert beleg["historie"][-1]["grund"]


def test_gebuchte_gutschrift_nennt_warum_sie_nicht_storniert_wird(client, satz):
    for rolle in ("vk-gutschrift", "ek-gutschrift"):
        storno = _aktion(_lies(client, satz, rolle), "stornieren")
        assert storno["erlaubt"] is False and "Gegenbuchung" in storno["grund"]


def test_auftrag_mit_lieferungen_wird_nicht_direkt_berechnet(client, satz):
    for rolle, lieferart, rechnungsart in (
        ("vk-auftrag", "sales_delivery", "sales_invoice"),
        ("ek-bestellung", "goods_receipt", "purchase_invoice"),
    ):
        beleg = _lies(client, satz, rolle)
        nach = [k["belegart"] for k in beleg["kette"] if k["richtung"] == "nachfolger"]
        assert nach == [lieferart, lieferart], rolle
        rest = sum(float(p["menge_offen"]) for p in beleg["positionen"])
        liefern = _aktion(beleg, f"umwandeln:{lieferart}")
        berechnen = _aktion(beleg, f"umwandeln:{rechnungsart}")
        assert liefern["erlaubt"] is (rest > 0)
        assert berechnen["erlaubt"] is False and berechnen["grund"]
        for pos in beleg["positionen"]:
            assert float(pos["menge_uebernommen"]) + float(pos["menge_offen"]) == float(pos["menge"])


def test_falsche_belegart_fremder_mandant_und_unbekanntes_ergeben_404(client, satz):
    rechnung = satz["vk-rechnung-1"]
    kopf = {"X-Tenant-ID": satz["mandant"]}
    assert client.get(f"/belege/sales_order/{rechnung['id']}", headers=kopf).status_code == 404
    assert client.get(f"/belege/frachtbrief/{rechnung['id']}", headers=kopf).status_code == 404
    assert client.get(f"/belege/sales_invoice/{uuid.uuid4()}", headers=kopf).status_code == 404
    assert client.get(f"/belege/sales_invoice/{rechnung['id']}", headers={"X-Tenant-ID": "anderer"}).status_code == 404


def test_lesen_schreibt_nichts(client, satz):
    def stand():
        with SessionLocal() as db:
            return tuple(db.execute(text(
                "SELECT (SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t), "
                "(SELECT count(*) FROM domain_docflow.document_status_history WHERE tenant_id = :t), "
                "(SELECT count(*) FROM domain_docflow.document_command_log WHERE tenant_id = :t), "
                "(SELECT max(updated_at) FROM domain_docflow.document_headers WHERE tenant_id = :t)"),
                {"t": satz["mandant"]}).one())
    vorher = stand()
    for rolle in (r for r in satz if r != "mandant"):
        _lies(client, satz, rolle)
    assert stand() == vorher
