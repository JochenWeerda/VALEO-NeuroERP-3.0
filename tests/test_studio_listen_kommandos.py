"""Zeilenaktionen der Einkaufslisten wirken nur im erlaubten Zustand (MASK-STUDIO-ROLLOUT-20261020, Welle 1).

Die handgebaute Liste rief ``/send`` ohne Lieferanten auf und loeschte Anfragen in jedem Status. Diese Vertraege
halten fest:

* ``loeschen`` entfernt einen Entwurf samt Positionen, verlangt eine Begruendung und schreibt Audit;
* eine freigegebene Anfrage oder eine Anfrage eines anderen Mandanten wird nicht geloescht;
* ``senden`` ohne Lieferanten wird abgewiesen, ohne den Status zu aendern;
* ``in_bestellung`` gilt nur fuer freigegebene Anfragen bzw. in der Angebotsphase;
* Angebote: pruefen/genehmigen/ablehnen nur aus den erlaubten Status, ablehnen mit Begruendung; ein bestelltes
  Angebot wird nicht zurueckgesetzt (der alte Statusweg setzte jeden Status);
* Anlieferavis: Liste und Objekt lesen die echten Spalten (vorher immer leer bzw. 404); stornieren mit Begruendung,
  nie ein erhaltenes Avis;
* Bestellungen: freigeben nur Entwuerfe, stornieren mit Begruendung und nie zweimal; der Import meldet ehrlich 501
  statt "Bestellungen werden angelegt";
* die Listen deklarieren jede Aktion mit diesem Kommandoweg und den Export.

Geprueft gegen eine frische Pruefstand-Datenbank (``TEST_DATABASE_URL``/``DATABASE_URL``).
"""
from __future__ import annotations

import os
import uuid

import pytest
from fastapi import Request  # Modulebene: FastAPI loest die Annotation hier auf

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

HAUS_A = f"anf-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"anf-b-{uuid.uuid4().hex[:6]}"
BEARBEITER = f"einkauf-{uuid.uuid4().hex[:8]}"
PFAD = "/api/v1/einkauf/anfragen/{id}/actions/{aktion}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM einkauf_anfragen LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text("DELETE FROM einkauf_anfragen_positionen WHERE anfrage_id IN "
                       "(SELECT id FROM einkauf_anfragen WHERE tenant_id = ANY(:h))"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_agrar.agrar_duenger WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM einkauf_angebote_positionen WHERE angebot_id IN "
                       "(SELECT id FROM einkauf_angebote WHERE tenant_id = ANY(:h))"), {"h": [HAUS_A, HAUS_B]})
        for tabelle in ("einkauf_anfragen", "einkauf_angebote", "einkauf_anlieferavis", "domain_crm.crm_action_audit_log", "public.outbox_events"):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                      {"id": haus, "n": f"Pruefbetrieb {haus}"})
    yield
    aufraeumen(engine)
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def leer(engine):
    aufraeumen(engine)
    yield


@pytest.fixture(autouse=True)
def gepruefte_person():
    from app.auth.deps import get_current_user
    from app.core.security import require_bearer_token
    from app.main import app
    from testgrenze import ALLE_FACHROLLEN, mandant_aus_kopf

    def geprueft(request: Request) -> str:
        tenant = mandant_aus_kopf(request)
        request.state.tenant_id = tenant
        request.state.tenant_verified = True
        request.state.token_claims = {"sub": BEARBEITER, "tenant_id": tenant, "roles": list(ALLE_FACHROLLEN)}
        return "pruefstand"

    app.dependency_overrides[require_bearer_token] = geprueft
    app.dependency_overrides[get_current_user] = lambda: {"sub": BEARBEITER, "name": BEARBEITER,
                                                          "roles": list(ALLE_FACHROLLEN)}
    yield
    app.dependency_overrides.pop(require_bearer_token, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def zeile(engine, sql: str, **parameter):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), parameter).mappings().first()


def anfrage(engine, status: str, haus: str = HAUS_A) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO einkauf_anfragen (id, anfrage_nummer, typ, anforderer, prioritaet, status, artikel, "
                       "menge, einheit, created_at, updated_at, tenant_id) VALUES (:id, :nr, 'BANF', 'Lager', "
                       "'normal', :s, 'Weizen', 25, 't', now(), now(), :h)"),
                  {"id": kennung, "nr": f"BANF-{kennung[:8]}", "s": status, "h": haus})
        v.execute(text("INSERT INTO einkauf_anfragen_positionen (id, anfrage_id, artikel, quantity, unit, created_at, "
                       "updated_at) VALUES (:p, :id, 'Weizen', 25, 't', now(), now())"),
                  {"p": str(uuid.uuid4()), "id": kennung})
    return kennung


def senden(client, kennung: str, aktion: str, body: dict, haus: str = HAUS_A) -> dict:
    antwort = client.post(PFAD.format(id=kennung, aktion=aktion), json=body, headers={"X-Tenant-ID": haus})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def test_loeschen_entfernt_entwurf_mit_positionen_und_audit(engine, client):
    kennung = anfrage(engine, "ENTWURF")
    ergebnis = senden(client, kennung, "loeschen", {"_auditReason": "Doppelt erfasst"})
    assert ergebnis["success"] is True, ergebnis
    assert zeile(engine, "SELECT id FROM einkauf_anfragen WHERE id = :id", id=kennung) is None
    assert zeile(engine, "SELECT COUNT(*) AS n FROM einkauf_anfragen_positionen WHERE anfrage_id = :id",
                 id=kennung)["n"] == 0
    assert zeile(engine, "SELECT COUNT(*) AS n FROM domain_crm.crm_action_audit_log WHERE tenant_id = :h "
                         "AND action_key = 'loeschen'", h=HAUS_A)["n"] == 1


@pytest.mark.parametrize("fall", ["ohne_grund", "freigegeben", "fremder_mandant"])
def test_loeschen_weist_ab_und_laesst_die_anfrage_stehen(engine, client, fall):
    kennung = anfrage(engine, "FREIGEGEBEN" if fall == "freigegeben" else "ENTWURF")
    body = {} if fall == "ohne_grund" else {"_auditReason": "Doppelt erfasst"}
    ergebnis = senden(client, kennung, "loeschen", body, haus=HAUS_B if fall == "fremder_mandant" else HAUS_A)
    assert ergebnis["success"] is False
    assert zeile(engine, "SELECT id FROM einkauf_anfragen WHERE id = :id", id=kennung) is not None


def test_senden_ohne_lieferanten_aendert_nichts(engine, client):
    kennung = anfrage(engine, "OFFEN")
    ergebnis = senden(client, kennung, "senden", {"lieferanten": []})
    assert ergebnis["success"] is False
    assert "Lieferanten" in (ergebnis.get("error") or "")
    assert zeile(engine, "SELECT status FROM einkauf_anfragen WHERE id = :id", id=kennung)["status"] == "OFFEN"


def test_in_bestellung_nur_freigegeben(engine, client):
    kennung = anfrage(engine, "OFFEN")
    ergebnis = senden(client, kennung, "in_bestellung", {})
    assert ergebnis["success"] is False
    assert "OFFEN" in (ergebnis.get("error") or "")


def test_liste_deklariert_kommandowege_und_export():
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("einkauf/anfragen")
    assert definition["mode"] == "list"
    zeilen = {a["key"]: a for a in definition["tables"][0]["rowActions"]}
    for aktion in ("senden", "in_bestellung", "loeschen"):
        assert zeilen[aktion]["commandEndpoint"] == PFAD.format(id="{entity_id}", aktion=aktion)
    assert zeilen["loeschen"]["auditReasonRequired"] is True
    assert {a["key"] for a in definition["actions"]} >= {"neu", "export"}


def angebot(engine, status: str) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO einkauf_angebote (id, tenant_id, angebotsnummer, lieferant_name, status, created_at, "
                       "updated_at) VALUES (:id, :h, :nr, 'Muehle Nord', :s, now(), now())"),
                  {"id": kennung, "h": HAUS_A, "nr": f"ANG-{kennung[:8]}", "s": status})
    return kennung


def angebot_status(engine, kennung: str) -> str:
    return zeile(engine, "SELECT status FROM einkauf_angebote WHERE id = :id", id=kennung)["status"]


def angebot_aktion(client, kennung: str, aktion: str, body: dict) -> dict:
    antwort = client.post(f"/api/v1/einkauf/angebote/{kennung}/actions/{aktion}", json=body,
                          headers={"X-Tenant-ID": HAUS_A})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def test_angebot_pruefen_und_genehmigen_der_reihe_nach(engine, client):
    kennung = angebot(engine, "ERFASST")
    assert angebot_aktion(client, kennung, "genehmigen", {})["success"] is False
    assert angebot_status(engine, kennung) == "ERFASST"
    assert angebot_aktion(client, kennung, "pruefen", {})["success"] is True
    assert angebot_aktion(client, kennung, "genehmigen", {})["success"] is True
    assert angebot_status(engine, kennung) == "GENEHMIGT"


def test_angebot_ablehnen_braucht_grund_und_trifft_kein_bestelltes(engine, client):
    offen = angebot(engine, "GEPRUEFT")
    assert angebot_aktion(client, offen, "ablehnen", {})["success"] is False
    assert angebot_aktion(client, offen, "ablehnen", {"_auditReason": "Preis ueber Marktniveau"})["success"] is True
    assert angebot_status(engine, offen) == "ABGELEHNT"
    bestellt = angebot(engine, "IN_BESTELLUNG")
    for aktion in ("pruefen", "ablehnen"):
        assert angebot_aktion(client, bestellt, aktion, {"_auditReason": "Versehentlich"})["success"] is False
    assert angebot_status(engine, bestellt) == "IN_BESTELLUNG"


def test_angebotsliste_deklariert_kommandowege():
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("einkauf/angebote")
    zeilen = {a["key"]: a for a in definition["tables"][0]["rowActions"]}
    for aktion in ("pruefen", "genehmigen", "bestellen", "ablehnen"):
        assert zeilen[aktion]["commandEndpoint"] == f"/api/v1/einkauf/angebote/{{entity_id}}/actions/{aktion}"
    assert zeilen["ablehnen"]["auditReasonRequired"] is True
    assert definition["tables"][0]["rowRouteTemplate"] == "/einkauf/angebot/{id}"


def avis(engine, status: str) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO einkauf_anlieferavis (id, tenant_id, lieferant_name, avis_nummer, bestell_nr, "
                       "erwartetes_datum, status) VALUES (:id, :h, 'Muehle Nord', :nr, 'PO-1', DATE '2026-10-22', :s)"),
                  {"id": kennung, "h": HAUS_A, "nr": f"AV-{kennung[:8]}", "s": status})
    return kennung


def test_avis_liste_und_objekt_lesen_die_echten_spalten(engine, client):
    kennung = avis(engine, "offen")
    liste = client.get("/api/v1/einkauf/anlieferavis", headers={"X-Tenant-ID": HAUS_A})
    assert liste.status_code == 200, liste.text
    eintrag = next(e for e in liste.json() if e["id"] == kennung)
    assert eintrag["bestellung"] == "PO-1"
    assert eintrag["geplantesAnlieferDatum"] == "2026-10-22"
    assert client.get(f"/api/v1/einkauf/anlieferavis/{kennung}", headers={"X-Tenant-ID": HAUS_A}).status_code == 200


def test_avis_statusgrenzen(engine, client):
    def aktion(kennung: str, schritt: str, body: dict) -> bool:
        antwort = client.post(f"/api/v1/einkauf/anlieferavis/{kennung}/actions/{schritt}", json=body,
                              headers={"X-Tenant-ID": HAUS_A})
        assert antwort.status_code == 200, antwort.text
        return antwort.json()["success"]

    kennung = avis(engine, "offen")
    assert aktion(kennung, "senden", {}) is True
    assert aktion(kennung, "bestaetigen", {}) is True
    assert aktion(kennung, "senden", {}) is False
    assert aktion(kennung, "stornieren", {}) is False
    assert aktion(kennung, "stornieren", {"_auditReason": "Lieferung abgesagt"}) is True
    erhalten = avis(engine, "ERHALTEN")
    assert aktion(erhalten, "stornieren", {"_auditReason": "Versehentlich"}) is False
    assert zeile(engine, "SELECT status FROM einkauf_anlieferavis WHERE id = :id", id=erhalten)["status"] == "ERHALTEN"


def test_ab_liste_nutzt_die_wege_der_objektmaske():
    from app.core.screen_definitions import get_screen_definition

    liste = get_screen_definition("einkauf/auftragsbestaetigungen")
    objekt = get_screen_definition("einkauf/auftragsbestaetigung")
    wege = {a["key"]: a["commandEndpoint"] for a in objekt["actions"]}
    for aktion in liste["tables"][0]["rowActions"]:
        assert aktion["commandEndpoint"] == wege[aktion["key"]]
    neu = next(a for a in liste["actions"] if a["key"] == "neu")
    assert neu["navigationRoute"] == "/einkauf/auftragsbestaetigung/neu" and objekt["creation"]["endpoint"]


def test_lieferantenliste_liest_die_quelle_der_objektmaske():
    from app.core.screen_definitions import get_screen_definition

    liste = get_screen_definition("einkauf/lieferanten")
    objekt = get_screen_definition("einkauf/supplier")
    quelle = next(d["endpoint"] for d in objekt["dataSources"] if d["key"] == "entity")
    assert quelle == liste["dataSources"][0]["endpoint"] + "/{entity_id}"
    assert liste["tables"][0]["rowRouteTemplate"] == "/einkauf/lieferanten/{id}"


def bestellung(engine, status: str) -> str:
    from sqlalchemy import text

    kennung, lieferant = str(uuid.uuid4()), str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:l, :h, :n, 'Muehle Nord')"), {"l": lieferant, "h": HAUS_A, "n": f"L-{lieferant[:6]}"})
        v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       "bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, :s)"),
                  {"i": kennung, "h": HAUS_A, "n": f"EK-{kennung[:8]}", "l": lieferant, "s": status})
    return kennung


def bestell_status(engine, kennung: str) -> str:
    return zeile(engine, "SELECT status FROM domain_einkauf.bestellungen WHERE id = CAST(:i AS uuid)", i=kennung)["status"]


def bestell_aktion(client, kennung: str, aktion: str, body: dict) -> dict:
    antwort = client.post(f"/api/v1/einkauf/bestellungen/{kennung}/actions/{aktion}", json=body,
                          headers={"X-Tenant-ID": HAUS_A})
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def test_bestellung_freigeben_nur_aus_dem_entwurf(engine, client):
    kennung = bestellung(engine, "entwurf")
    assert bestell_aktion(client, kennung, "freigeben", {})["success"] is True
    assert bestell_status(engine, kennung) == "freigegeben"
    assert bestell_aktion(client, kennung, "freigeben", {})["success"] is False


def test_bestellung_stornieren_mit_grund_und_nur_einmal(engine, client):
    kennung = bestellung(engine, "freigegeben")
    assert bestell_aktion(client, kennung, "stornieren", {})["success"] is False
    assert bestell_aktion(client, kennung, "stornieren", {"_auditReason": "Lieferant nicht lieferfaehig"})["success"]
    assert bestell_status(engine, kennung) == "storniert"
    assert bestell_aktion(client, kennung, "stornieren", {"_auditReason": "Noch einmal"})["success"] is False
    assert bestell_aktion(client, kennung, "versenden", {})["success"] is False


def test_bestellimport_meldet_keine_scheinwirkung(client):
    antwort = client.post("/api/v1/einkauf/bestellungen/import", headers={"X-Tenant-ID": HAUS_A},
                          files={"file": ("bestellungen.csv", b"nr;lieferant;1;Muehle", "text/csv")})
    assert antwort.status_code == 501, antwort.text


def test_bestellliste_liest_die_quelle_der_objektmaske():
    from app.core.screen_definitions import get_screen_definition

    liste = get_screen_definition("einkauf/bestellungen")
    objekt = get_screen_definition("einkauf/purchase-order")
    quelle = next(d["endpoint"] for d in objekt["dataSources"] if d["key"] == "entity")
    assert quelle == liste["dataSources"][0]["endpoint"] + "/{entity_id}"
    zeilen = {a["key"] for a in liste["tables"][0]["rowActions"]}
    assert zeilen == {"freigeben", "versenden", "stornieren"}


def test_saatgutliste_bleibt_in_der_grenze_des_dienstes():
    """Der Saatgut-Dienst erlaubt limit <= 200; die Liste laedt einmal bis zu ihrer pageSize."""
    from app.core.screen_definitions import get_screen_definition

    liste = get_screen_definition("agrar/saatgut-liste")
    assert liste["dataSources"][0]["pageSize"] <= 200
    assert liste["tables"][0]["rowRouteTemplate"] == "/agrar/saatgut/{id}"


def test_saatgutliste_antwortet_mit_der_ladegrenze(client):
    antwort = client.get("/api/v1/agrar/saatgut/", params={"limit": 200}, headers={"X-Tenant-ID": HAUS_A})
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["items"] == []


def test_duenger_deaktivieren_mit_grund_und_nur_einmal(engine, client):
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_agrar.agrar_duenger (id, tenant_id, artikelnummer, name, typ, ist_aktiv) "
                       "VALUES (:i, :h, :a, 'KAS 27', 'Mineralduenger', true)"),
                  {"i": kennung, "h": HAUS_A, "a": f"D-{kennung[:8]}"})

    def aktion(body: dict) -> bool:
        antwort = client.post(f"/api/v1/agrar/duenger/{kennung}/actions/deaktivieren", json=body,
                              headers={"X-Tenant-ID": HAUS_A})
        assert antwort.status_code == 200, antwort.text
        return antwort.json()["success"]

    assert aktion({}) is False
    assert aktion({"_auditReason": "Nicht mehr im Sortiment"}) is True
    assert zeile(engine, "SELECT ist_aktiv FROM domain_agrar.agrar_duenger WHERE id = :i", i=kennung)["ist_aktiv"] is False
    assert aktion({"_auditReason": "Noch einmal"}) is False
