"""Aktionen der Belegmaske (BELEG-021): ein Aktionsweg auf den Kommandos von DocFlow und der Approval Engine.

Geprueft gegen die echte Datenbank, an den Referenzbelegen. Die Tests veraendern den Satz und laufen in der
Reihenfolge der Datei.
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
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.services import docflow_service
from testgrenze import ersetze_mandant

WURZEL = pathlib.Path(__file__).resolve().parent.parent

VERA = {"sub": "vera", "name": "v.kruse", "roles": ["SALES_BEARBEITEN"]}
LEO = {"sub": "leo", "name": "l.meyer", "roles": ["SALES_LESEN"]}
EVA = {"sub": "eva", "name": "e.harms", "roles": ["EINKAUF_BEARBEITEN"]}
EMIL = {"sub": "emil", "name": "e.tammen", "roles": ["EINKAUF_ADMIN"]}
BERND = {"sub": "bernd", "name": "b.dirks", "roles": ["FINANCE_BEARBEITEN"]}
CLARA = {"sub": "clara", "name": "c.onken", "roles": ["FINANCE_ADMIN"]}

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


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(scope="module")
def satz():
    mandant = f"ba-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "Belegaktionen Test")
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
def maske(satz):
    app = FastAPI()
    app.include_router(belege_endpunkt.router, prefix="/belege")
    ersetze_mandant(app, satz["mandant"])
    client = TestClient(app, raise_server_exceptions=False)

    def aktion(wer: dict | None, rolle: str, key: str, **rumpf) -> dict:
        app.dependency_overrides[get_current_user] = lambda: (wer or {"sub": "niemand", "roles": []})
        b = satz[rolle]
        antwort = client.post(f"/belege/{b['doc_type']}/{b['id']}/actions/{key}", json={"_mode": "execute", **rumpf})
        return {"http": antwort.status_code, **(antwort.json() if antwort.headers.get("content-type", "").startswith("application/json") else {})}

    def kopf(wer: dict, rolle: str) -> dict:
        app.dependency_overrides[get_current_user] = lambda: wer
        b = satz[rolle]
        return client.get(f"/belege/{b['doc_type']}/{b['id']}/kopf").json()

    return aktion, kopf


def _status(satz, rolle: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"), {"id": satz[rolle]["id"]}).scalar()


def _buchungen(satz) -> int:
    with SessionLocal() as db:
        return db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"), {"t": satz["mandant"]}).scalar()


def _nachfolger(satz, rolle: str, art: str) -> int:
    with SessionLocal() as db:
        return db.execute(text(
            "SELECT count(*) FROM domain_docflow.document_header_links k JOIN domain_docflow.document_headers z "
            "ON z.id = k.to_header_id WHERE k.from_header_id = :id AND z.doc_type = :art"),
            {"id": satz[rolle]["id"], "art": art}).scalar()


def test_der_trockenlauf_nennt_was_geht_und_was_nicht_und_schreibt_nichts(satz, maske):
    aktion, _ = maske
    vorher = (_buchungen(satz), _status(satz, "vk-rechnung-2"))
    geht = aktion(VERA, "vk-rechnung-2", "buchen", _mode="dryRun")
    assert geht["http"] == 200 and geht["success"] is True and geht["mode"] == "dryRun"
    gesperrt = aktion(EVA, "ek-rechnung-2", "buchen", _mode="dryRun")
    assert gesperrt["success"] is False and gesperrt["error"].startswith("Freigabe erforderlich (R3)")
    falscher_stand = aktion(VERA, "vk-rechnung-1", "buchen", _mode="dryRun")
    assert falscher_stand["success"] is False and "nicht möglich" in falscher_stand["error"]
    unbekannt = aktion(VERA, "vk-rechnung-2", "verschenken", _mode="dryRun")
    assert unbekannt["success"] is False
    assert (_buchungen(satz), _status(satz, "vk-rechnung-2")) == vorher


def test_ohne_recht_geschieht_nichts(satz, maske):
    aktion, _ = maske
    vorher = _buchungen(satz)
    assert aktion(None, "vk-rechnung-2", "buchen")["http"] == 403                # keine Rolle: der Beleg existiert fuer sie nicht
    assert aktion(EVA, "vk-rechnung-2", "buchen")["http"] == 403                 # Einkauf an einem Verkaufsbeleg
    nur_lesen = aktion(LEO, "vk-rechnung-2", "buchen")
    assert nur_lesen["success"] is False and nur_lesen["error"] == "Keine Berechtigung."
    assert _buchungen(satz) == vorher and _status(satz, "vk-rechnung-2") == "open"


def test_folgebeleg_aus_der_maske_genau_einmal(satz, maske):
    aktion, _ = maske
    vorher = _nachfolger(satz, "vk-rechnung-1", "sales_credit_memo")
    erster = aktion(VERA, "vk-rechnung-1", "umwandeln:sales_credit_memo")
    assert erster["success"] is True, erster
    assert "Gutschrift erstellt" in erster["summary"]
    assert _nachfolger(satz, "vk-rechnung-1", "sales_credit_memo") == vorher + 1
    with SessionLocal() as db:  # die neue Gutschrift fuer den Test der Ablehnung
        neu = db.execute(text(
            "SELECT z.id FROM domain_docflow.document_header_links k JOIN domain_docflow.document_headers z "
            "ON z.id = k.to_header_id WHERE k.from_header_id = :id AND z.doc_type = 'sales_credit_memo' "
            "AND z.status = 'open' ORDER BY z.created_at DESC LIMIT 1"), {"id": satz["vk-rechnung-1"]["id"]}).scalar()
    satz["neue-gutschrift"] = {"id": str(neu), "doc_type": "sales_credit_memo"}
    # Der zweite Klick: Der Rest ist uebernommen, es entsteht kein weiterer Beleg.
    zweiter = aktion(VERA, "vk-rechnung-1", "umwandeln:sales_credit_memo")
    assert zweiter["success"] is False and "bereits übernommen" in zweiter["error"]
    assert _nachfolger(satz, "vk-rechnung-1", "sales_credit_memo") == vorher + 1


def test_buchen_aus_der_maske_und_der_veraltete_stand_wird_abgewiesen(satz, maske):
    aktion, kopf = maske
    vorher = _buchungen(satz)
    alt = aktion(VERA, "vk-rechnung-2", "buchen", version=99)
    assert alt["success"] is False and "inzwischen geändert" in alt["error"]
    version = kopf(VERA, "vk-rechnung-2")["version"]
    gebucht = aktion(VERA, "vk-rechnung-2", "buchen", version=version, _idempotencyKey="klick-1")
    assert gebucht["success"] is True and "gebucht" in gebucht["summary"], gebucht
    assert _status(satz, "vk-rechnung-2") == "posted" and _buchungen(satz) == vorher + 1
    # Derselbe Klick noch einmal: dieselbe Antwort, keine zweite Buchung.
    nochmal = aktion(VERA, "vk-rechnung-2", "buchen", version=version, _idempotencyKey="klick-1")
    assert nochmal["success"] is True and _buchungen(satz) == vorher + 1
    # Ein neuer Klick am gebuchten Beleg: nichts mehr zu buchen.
    assert aktion(VERA, "vk-rechnung-2", "buchen")["success"] is False
    assert _buchungen(satz) == vorher + 1
    with SessionLocal() as db:
        akteur = db.execute(text(
            "SELECT actor FROM domain_docflow.document_status_history WHERE header_id = :id ORDER BY changed_at DESC LIMIT 1"),
            {"id": satz["vk-rechnung-2"]["id"]}).scalar()
    assert akteur == "vera"


def test_freigabe_anfragen_und_erteilen_aus_der_maske(satz, maske):
    aktion, kopf = maske
    vorher = _buchungen(satz)
    assert kopf(EVA, "ek-rechnung-2")["aktion_freigabe_anfordern_post"] is True
    angefragt = aktion(EVA, "ek-rechnung-2", "freigabe_anfordern:post")
    assert angefragt["success"] is True and "Freigabe angefragt (R3)" in angefragt["summary"], angefragt

    # Wer angefragt hat, sieht „erteilen" gesperrt — und der Server lehnt es mit demselben Grund ab.
    eigener = kopf(EVA | {"roles": ["EINKAUF_ADMIN"]}, "ek-rechnung-2")
    assert eigener["aktion_freigabe_erteilen_post"] is False and "Funktionstrennung" in eigener["aktionshinweis"]
    selbst = aktion(EVA | {"roles": ["EINKAUF_ADMIN"]}, "ek-rechnung-2", "freigabe_erteilen:post")
    assert selbst["success"] is False and "Funktionstrennung" in selbst["error"]
    ohne_recht = aktion(EVA | {"sub": "erik"}, "ek-rechnung-2", "freigabe_erteilen:post")  # Sachbearbeitung
    assert ohne_recht["success"] is False and ohne_recht["error"] == "Keine Berechtigung."
    assert aktion(EVA, "ek-rechnung-2", "buchen")["success"] is False and _buchungen(satz) == vorher

    assert kopf(EMIL, "ek-rechnung-2")["aktion_freigabe_erteilen_post"] is True
    erteilt = aktion(EMIL, "ek-rechnung-2", "freigabe_erteilen:post")
    assert erteilt["success"] is True and "Freigabe erteilt" in erteilt["summary"], erteilt
    danach = kopf(EVA, "ek-rechnung-2")
    assert danach["aktion_buchen"] is True and "aktion_freigabe_anfordern_post" not in danach
    gebucht = aktion(EVA, "ek-rechnung-2", "buchen")
    assert gebucht["success"] is True, gebucht
    assert _status(satz, "ek-rechnung-2") == "posted" and _buchungen(satz) == vorher + 1


def test_storno_aus_der_maske_braucht_grund_und_erhoehte_freigabe(satz, maske):
    aktion, _ = maske
    vorher = _buchungen(satz)
    ohne = aktion(BERND, "vk-rechnung-1", "stornieren", grund="Falscher Kunde")
    assert ohne["success"] is False and ohne["error"].startswith("Freigabe erforderlich (R4)")
    assert aktion(VERA, "vk-rechnung-1", "freigabe_anfordern:reverse")["success"] is False  # Sachbearbeitung fragt keinen Storno an
    assert aktion(BERND, "vk-rechnung-1", "freigabe_anfordern:reverse")["success"] is True
    assert aktion(BERND | {"sub": "britta"}, "vk-rechnung-1", "freigabe_erteilen:reverse")["success"] is False  # R4: nicht die Buchhaltung
    assert aktion(CLARA, "vk-rechnung-1", "freigabe_erteilen:reverse")["success"] is True
    ohne_grund = aktion(BERND, "vk-rechnung-1", "stornieren")
    assert ohne_grund["success"] is False and ohne_grund["validationErrors"][0]["field"] == "grund"
    assert _status(satz, "vk-rechnung-1") == "posted" and _buchungen(satz) == vorher
    storniert = aktion(BERND, "vk-rechnung-1", "stornieren", grund="Falscher Kunde")
    assert storniert["success"] is True and "storniert" in storniert["summary"], storniert
    assert _status(satz, "vk-rechnung-1") == "reversed" and _buchungen(satz) == vorher + 1


def test_eine_abgelehnte_freigabe_gilt_nicht(satz, maske):
    aktion, kopf = maske
    vorher = _buchungen(satz)
    # Jede Gutschrift braucht die zweite Person.
    assert aktion(VERA, "neue-gutschrift", "buchen")["error"].startswith("Freigabe erforderlich")
    assert aktion(VERA, "neue-gutschrift", "freigabe_anfordern:post")["success"] is True
    # Zusammen mit der ersten Gutschrift zur selben Rechnung liegt sie ueber 1.000 EUR: Es entscheidet die Leitung.
    assert aktion(BERND, "neue-gutschrift", "freigabe_ablehnen:post")["error"] == "Keine Berechtigung."
    abgelehnt = aktion(CLARA, "neue-gutschrift", "freigabe_ablehnen:post", grund="Betrag unklar")
    assert abgelehnt["success"] is True and "Freigabe abgelehnt" in abgelehnt["summary"], abgelehnt
    assert aktion(VERA, "neue-gutschrift", "buchen")["success"] is False and _buchungen(satz) == vorher
    # Nach der Ablehnung laesst sich neu anfragen; erteilen gibt es erst wieder mit einer offenen Anfrage.
    danach = kopf(VERA, "neue-gutschrift")
    assert danach["aktion_freigabe_anfordern_post"] is True and "aktion_freigabe_erteilen_post" not in danach
    assert aktion(CLARA, "neue-gutschrift", "freigabe_erteilen:post")["success"] is False


def test_wo_ein_sachgrund_sperrt_wird_keine_freigabe_angefragt(satz, maske):
    aktion, kopf = maske
    assert aktion(EVA, "ek-rechnung-ohne-schluessel", "freigabe_anfordern:post")["success"] is False
    assert kopf(BERND, "vk-rechnung-storno").get("aktion_stornieren") is None  # storniert: nichts mehr angeboten
