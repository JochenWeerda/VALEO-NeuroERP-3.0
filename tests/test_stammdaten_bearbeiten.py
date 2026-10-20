"""Bearbeiten der Objektmasken wirkt — ueber den bestehenden Aenderungsweg (STAMMDATEN-BEARBEITEN-20261019).

Elf Objektmasken hatten einen Bearbeiten-Knopf ohne Wirkung. Diese Vertraege halten fest:

* ``execute`` aendert das Objekt in der Datenbank und schreibt Audit und Ereignis in **einem** Commit;
* ``dryRun`` prueft gegen die Datenbank und schreibt nichts;
* nur die deklarierten Felder zaehlen — die Maske schickt den ganzen Objektkontext mit;
* ein Vollersatz-Fachweg (Mischfuttermittel) leert keine nicht gesendeten Felder;
* Objekte eines anderen Mandanten und gesperrte Zustaende werden abgewiesen;
* jede Maske deklariert die Aktion mit diesem Kommandoweg.

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

HAUS_A = f"stb-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"stb-b-{uuid.uuid4().hex[:6]}"
BEARBEITER = f"bearb-{uuid.uuid4().hex[:8]}"

TABELLEN = ("domain_crm.crm_action_audit_log", "public.outbox_events", "domain_ops.ops_bankkonten",
            "domain_shared.futtermittel_mischfutter", "public.crm_leads", "public.einkauf_auftragsbestaetigungen",
            "domain_ops.reklamationen", "domain_einkauf.bestellungen",
            "domain_einkauf.lieferanten")


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_ops.ops_bankkonten LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        # Positionen tragen keinen Mandanten; sie haengen an der Bestellung.
        v.execute(text("DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
                       "(SELECT id FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h))"), {"h": [HAUS_A, HAUS_B]})
        for tabelle in TABELLEN:
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


def kopf(haus: str = HAUS_A) -> dict[str, str]:
    return {"X-Tenant-ID": haus}


def zeile(engine, sql: str, **parameter):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), parameter).mappings().first()


def ausfuehren(engine, sql: str, **parameter) -> None:
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text(sql), parameter)


def audit_zahl(engine, haus: str, aktion: str) -> int:
    return zeile(engine, "SELECT COUNT(*) AS n FROM domain_crm.crm_action_audit_log "
                         "WHERE tenant_id = :h AND action_key = :a", h=haus, a=aktion)["n"]


def bankkonto(engine, haus: str = HAUS_A) -> str:
    kennung = str(uuid.uuid4())
    ausfuehren(engine, "INSERT INTO domain_ops.ops_bankkonten (id, tenant_id, iban, bic, bank, kontoart, saldo, "
                       "waehrung, status, ist_aktiv) VALUES (:id, :h, 'DE02120300000000202051', 'BYLADEM1001', "
                       "'Alte Bank', 'giro', 1000, 'EUR', 'aktiv', TRUE)", id=kennung, h=haus)
    return kennung


def mischfutter(engine) -> str:
    kennung = str(uuid.uuid4())
    ausfuehren(engine, "INSERT INTO domain_shared.futtermittel_mischfutter (id, tenant_id, produkt_code, name, "
                       "tierart, protein, beschreibung, aktiv) VALUES (:id, :h, :code, 'Milchleistung 18', 'rind', "
                       "18.0, 'Bleibt erhalten', TRUE)", id=kennung, h=HAUS_A, code=f"MF-{kennung[:6]}")
    return kennung


def lead(engine) -> str:
    kennung = str(uuid.uuid4())
    ausfuehren(engine, "INSERT INTO public.crm_leads (id, company, status, tenant_id) VALUES (:id, 'Hof Alt', 'new', :h)",
               id=kennung, h=HAUS_A)
    return kennung


# --------------------------------------------------------------------------- Wirkung

def test_bankkonto_aendert_nur_deklarierte_felder_mit_begruendung(client, engine):
    kennung = bankkonto(engine)
    pfad = f"/api/v1/banken/konten/{kennung}/actions/bearbeiten"
    # Die Maske schickt den ganzen Objektkontext; Saldo und IBAN sind keine Eingabefelder.
    kontext = {"id": kennung, "bank": "Neue Bank", "saldo": 0, "iban": "DE00000000000000000000"}

    ohne_grund = client.post(pfad, json=kontext, headers=kopf())
    assert ohne_grund.json()["success"] is False

    antwort = client.post(pfad, json={**kontext, "_auditReason": "Bankfusion zum 01.10."}, headers=kopf())
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["success"] is True, antwort.json()
    konto = zeile(engine, "SELECT bank, saldo, iban FROM domain_ops.ops_bankkonten WHERE id = :id", id=kennung)
    assert konto["bank"] == "Neue Bank"
    assert float(konto["saldo"]) == 1000.0
    assert konto["iban"] == "DE02120300000000202051"
    assert audit_zahl(engine, HAUS_A, "bearbeiten") == 1


def test_trockenlauf_schreibt_nichts(client, engine):
    kennung = bankkonto(engine)
    antwort = client.post(f"/api/v1/banken/konten/{kennung}/actions/bearbeiten",
                          json={"bank": "Probe", "_mode": "dryRun", "_auditReason": "nur pruefen bitte"},
                          headers=kopf())
    assert antwort.json()["success"] is True
    assert zeile(engine, "SELECT bank FROM domain_ops.ops_bankkonten WHERE id = :id", id=kennung)["bank"] == "Alte Bank"
    assert audit_zahl(engine, HAUS_A, "bearbeiten") == 0


def test_fremder_mandant_wird_abgewiesen(client, engine):
    kennung = bankkonto(engine, HAUS_B)
    antwort = client.post(f"/api/v1/banken/konten/{kennung}/actions/bearbeiten",
                          json={"bank": "Uebernahme", "_auditReason": "fremdes Konto aendern"}, headers=kopf(HAUS_A))
    assert antwort.json()["success"] is False
    assert zeile(engine, "SELECT bank FROM domain_ops.ops_bankkonten WHERE id = :id", id=kennung)["bank"] == "Alte Bank"


def test_ohne_aenderung_keine_ausfuehrung(client, engine):
    kennung = bankkonto(engine)
    antwort = client.post(f"/api/v1/banken/konten/{kennung}/actions/bearbeiten",
                          json={"saldo": 5, "_auditReason": "nur Kontext gesendet"}, headers=kopf())
    assert antwort.json()["success"] is False
    assert "Keine Aenderung" in antwort.json()["error"]


def test_mischfutter_vollersatz_leert_nichts(client, engine):
    kennung = mischfutter(engine)
    antwort = client.post(f"/api/v1/futter/mischfuttermittel/{kennung}/actions/bearbeiten",
                          json={"protein": 19.5}, headers=kopf())
    assert antwort.json()["success"] is True, antwort.json()
    futter = zeile(engine, "SELECT protein, beschreibung, name FROM domain_shared.futtermittel_mischfutter "
                           "WHERE id = :id", id=kennung)
    assert float(futter["protein"]) == 19.5
    assert futter["beschreibung"] == "Bleibt erhalten"
    assert futter["name"] == "Milchleistung 18"


def test_lead_bearbeiten(client, engine):
    kennung = lead(engine)
    antwort = client.post(f"/api/v1/crm/leads/{kennung}/actions/bearbeiten",
                          json={"company_name": "Hof Neu", "phone": "04941 123"}, headers=kopf())
    assert antwort.json()["success"] is True, antwort.json()
    assert zeile(engine, "SELECT company FROM public.crm_leads WHERE id = :id", id=kennung)["company"] == "Hof Neu"


def test_reklamation_zustaendigkeit_mit_audit_und_sperre_wenn_geschlossen(client, engine):
    angelegt = client.post("/api/v1/reklamationen", json={
        "lieferant_id": "LF-1", "typ": "qualitaet", "positionen": [], "zustaendiger": "alt",
        "frist_datum": "2026-11-30"}, headers=kopf())
    assert angelegt.status_code == 201, angelegt.text
    kennung = angelegt.json()["reklamation_id"]
    pfad = f"/api/v1/reklamationen/{kennung}/actions/bearbeiten"

    antwort = client.post(pfad, json={"zustaendiger": "neu", "frist_datum": "2026-12-15"}, headers=kopf())
    assert antwort.json()["success"] is True, antwort.json()
    rek = zeile(engine, "SELECT zustaendiger, frist_datum, audit_trail FROM domain_ops.reklamationen "
                        "WHERE reklamation_id = :id", id=kennung)
    assert rek["zustaendiger"] == "neu"
    assert str(rek["frist_datum"]) == "2026-12-15"
    eintrag = rek["audit_trail"][-1]
    assert eintrag["aktion"] == "bearbeitet"
    assert eintrag["aktor_id"] == BEARBEITER  # aus dem Token, nicht aus dem Anfragekoerper

    ausfuehren(engine, "UPDATE domain_ops.reklamationen SET status = 'geschlossen' WHERE reklamation_id = :id",
               id=kennung)
    gesperrt = client.post(pfad, json={"zustaendiger": "spaeter"}, headers=kopf())
    assert gesperrt.json()["success"] is False


def test_auftragsbestaetigung_pruefen_und_bestaetigen(client, engine):
    kennung = str(uuid.uuid4())
    ausfuehren(engine, "INSERT INTO public.einkauf_auftragsbestaetigungen (id, tenant_id, ab_nummer, bestell_nr, "
                       "lieferant_name, status, created_at) VALUES (:id, :h, :nr, 'B-1', 'Lieferant', 'OFFEN', now())",
               id=kennung, h=HAUS_A, nr=f"AB-{kennung[:6]}")
    gelesen = client.get(f"/api/v1/einkauf/auftragsbestaetigungen/{kennung}", headers=kopf())
    assert gelesen.status_code == 200, gelesen.text  # bis 19.10.2026 immer 404 (falsche Spaltennamen)

    geprueft = client.post(f"/api/v1/einkauf/auftragsbestaetigungen/{kennung}/actions/pruefen", json={},
                           headers=kopf())
    assert geprueft.json()["success"] is True, geprueft.json()
    assert zeile(engine, "SELECT status FROM public.einkauf_auftragsbestaetigungen WHERE id = :id",
                 id=kennung)["status"] == "GEPRUEFT"
    nochmal = client.post(f"/api/v1/einkauf/auftragsbestaetigungen/{kennung}/actions/pruefen", json={},
                          headers=kopf())
    assert nochmal.json()["success"] is False
    assert client.post(f"/api/v1/einkauf/auftragsbestaetigungen/{kennung}/actions/bestaetigen", json={},
                       headers=kopf()).json()["success"] is True
    assert zeile(engine, "SELECT status FROM public.einkauf_auftragsbestaetigungen WHERE id = :id",
                 id=kennung)["status"] == "BESTAETIGT"


# --------------------------------------------------------------------------- Deklaration

ERWARTET = {
    "sales/sales-order": "/api/v1/sales/orders/{entity_id}/actions/bearbeiten",
    "agrar/kontrakte": "/api/v1/kontrakte/{entity_id}/actions/bearbeiten",
    "crm/opportunity": "/api/v1/crm/opportunities/{entity_id}/actions/bearbeiten",
    "crm/lead": "/api/v1/crm/leads/{entity_id}/actions/bearbeiten",
    "einkauf/anfrage": "/api/v1/einkauf/anfragen/{entity_id}/actions/bearbeiten",
    "einkauf/auftragsbestaetigung": "/api/v1/einkauf/auftragsbestaetigungen/{entity_id}/actions/pruefen",
    "finance/bankkonto": "/api/v1/banken/konten/{entity_id}/actions/bearbeiten",
    "finance/debitor": "/api/v1/finance/debitoren/{entity_id}/actions/bearbeiten",
    "finance/kreditor": "/api/v1/finance/kreditoren/{entity_id}/actions/bearbeiten",
    "futtermittel/mischfuttermittel": "/api/v1/futter/mischfuttermittel/{entity_id}/actions/bearbeiten",
    "qualitaet/reklamation": "/api/v1/reklamationen/{entity_id}/actions/bearbeiten",
}


@pytest.mark.parametrize("maske,endpunkt", sorted(ERWARTET.items()))
def test_jede_maske_deklariert_ihren_bearbeitungsweg(maske, endpunkt):
    from app.core.screen_definitions import get_screen_definition

    aktionen = {a.get("commandEndpoint"): a for a in get_screen_definition(maske)["actions"]}
    assert endpunkt in aktionen
    aktion = aktionen[endpunkt]
    assert aktion["method"] == "POST" and aktion["permission"]
    if aktion["key"] == "bearbeiten":
        assert aktion["inputFields"], "Bearbeiten ohne Eingabefelder"


def test_agentengesperrte_aenderungen_stehen_im_agentenvertrag():
    from app.core.screen_definitions import get_screen_definition

    for maske in ("agrar/kontrakte", "finance/bankkonto", "finance/debitor", "finance/kreditor"):
        definition = get_screen_definition(maske)
        aktion = next(a for a in definition["actions"] if a["key"] == "bearbeiten")
        assert aktion.get("forbiddenForAgents") is True and aktion.get("auditReasonRequired") is True
        assert "bearbeiten" in {a["key"] for a in definition["agentContract"]["dangerousActions"]}


def test_chance_lokal_gefuehrt_wird_geaendert_wenn_crm_sales_nicht_erreichbar():
    """Bis 19.10.2026 scheiterte jede Aenderung einer nur lokal gefuehrten Chance mit 500."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock, patch

    import httpx

    from app.api.v1.endpoints import opportunities

    db = MagicMock()
    kennung = str(uuid.uuid4())
    lokal = {"id": kennung, "tenant_id": "t", "name": "Chance", "status": "prospecting", "stage": "initial_contact"}
    with patch.object(opportunities, "_opportunity_im_mandanten", AsyncMock(return_value=lokal)), \
         patch.object(opportunities, "crm_update_opportunity", AsyncMock(side_effect=httpx.ConnectError("weg"))), \
         patch.object(opportunities, "_local_opportunity", return_value={**lokal, "name": "Neu"}):
        ergebnis = asyncio.run(opportunities.update_opportunity(
            kennung, opportunities.OpportunityUpdate(name="Neu"), db=db, tenant_id="t"))
    assert ergebnis.name == "Neu"
    sql = str(db.execute.call_args[0][0])
    assert "UPDATE domain_crm.crm_opportunities SET title = :title" in sql
    db.commit.assert_called_once()


@pytest.mark.parametrize("maske", sorted(ERWARTET))
def test_unbekanntes_objekt_ist_nicht_gefunden_statt_sql_fehler(client, maske):
    """Die Lesepruefung jedes Wegs laeuft gegen das echte Schema (Spalten, Tabellen, Typumwandlung)."""
    pfad = ERWARTET[maske].format(entity_id=uuid.uuid4())
    antwort = client.post(pfad, json={"_mode": "dryRun", "_auditReason": "Pruefung ohne Objekt",
                                      "notes": "x", "name": "x", "company_name": "x", "anforderer": "x",
                                      "subject": "x", "bank": "x", "credit_limit": 1, "zustaendiger": "x"},
                          headers=kopf())
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["success"] is False
    assert antwort.json()["error"] == "Objekt nicht gefunden.", antwort.json()


def test_auftragsbestaetigung_wird_zur_bestellung_erfasst(client, engine):
    """Bis 20.10.2026 gab es keinen Erfassungsweg; Lieferant und Bestellnummer kommen aus der Bestellung."""
    lieferant, bestellung = str(uuid.uuid4()), str(uuid.uuid4())
    nummer = f"B-{bestellung[:6]}"
    ausfuehren(engine, "INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:id, :h, :nr, 'Muehle Nord')", id=lieferant, h=HAUS_A, nr=f"L-{lieferant[:6]}")
    ausfuehren(engine, "INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       "bestelldatum, waehrung) VALUES (:id, :h, :nr, :l, CURRENT_DATE, 'EUR')",
               id=bestellung, h=HAUS_A, nr=nummer, l=lieferant)
    daten = {"bestellung": nummer, "ab_nummer": "AB-77", "lieferdatum": "2026-11-05", "gesamtbetrag": 1234.5,
             "lieferant_name": "vom Client erfunden"}
    angelegt = client.post("/api/v1/einkauf/auftragsbestaetigungen", json=daten, headers=kopf())
    assert angelegt.status_code == 201, angelegt.text
    ab = zeile(engine, "SELECT lieferant_name, lieferant_id, bestell_nr, status FROM public.einkauf_auftragsbestaetigungen "
                       "WHERE id = :id", id=angelegt.json()["id"])
    assert (ab["lieferant_name"], ab["lieferant_id"], ab["bestell_nr"], ab["status"]) ==         ("Muehle Nord", lieferant, nummer, "OFFEN")
    assert client.post("/api/v1/einkauf/auftragsbestaetigungen", json=daten, headers=kopf()).status_code == 409
    # Eine Bestellung eines anderen Mandanten ist nicht auffindbar.
    fremd = client.post("/api/v1/einkauf/auftragsbestaetigungen", json={**daten, "ab_nummer": "AB-78"},
                        headers=kopf(HAUS_B))
    assert fremd.status_code == 404


def test_auftragsbestaetigung_deklariert_die_anlage():
    from app.core.screen_definitions import get_screen_definition

    anlage = get_screen_definition("einkauf/auftragsbestaetigung")["creation"]
    assert anlage["endpoint"] == "/api/v1/einkauf/auftragsbestaetigungen"
    assert {f["key"] for f in anlage["fields"]} >= {"bestellung", "ab_nummer"}


def test_ordrsp_legt_ab_an_und_gleicht_positionen_ab(client, engine):
    lieferant, bestellung = str(uuid.uuid4()), str(uuid.uuid4())
    nummer = f"B-{bestellung[:6]}"
    ausfuehren(engine, "INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:id, :h, :nr, 'Saatzucht Sued')", id=lieferant, h=HAUS_A, nr=f"L-{lieferant[:6]}")
    ausfuehren(engine, "INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       "bestelldatum, waehrung) VALUES (:id, :h, :nr, :l, CURRENT_DATE, 'EUR')",
               id=bestellung, h=HAUS_A, nr=nummer, l=lieferant)
    for pos, artikel, menge, preis in ((1, "WEIZEN", 100, 24.5), (2, "RAPS", 50, 51.0)):
        ausfuehren(engine, "INSERT INTO domain_einkauf.bestellung_positionen (id, bestellung_id, pos_nr, "
                           "artikel_nr, artikel_bezeichnung, menge, einheit, einzelpreis) "
                           "VALUES (:id, :b, :p, :a, :a, :m, 'dt', :e)",
                   id=str(uuid.uuid4()), b=bestellung, p=pos, a=artikel, m=menge, e=preis)
    nachricht = (f"UNH+1+ORDRSP:D:96A:UN'BGM+231+AB-EDI-1+4'DTM+137:20261020:102'RFF+ON:{nummer}'"
                 "LIN+1+5+WEIZEN:BP'QTY+21:100'PRI+AAA:24.50'LIN+2+3+RAPS:BP'QTY+21:40'PRI+AAA:51.00'UNT+11+1'")
    antwort = client.post("/api/v1/einkauf/auftragsbestaetigungen/edi-ordrsp", json={"nachricht": nachricht},
                          headers=kopf())
    assert antwort.status_code == 201, antwort.text
    ergebnis = antwort.json()
    assert ergebnis["positionsabgleich"] is True
    assert [(a["art"], a["position"]) for a in ergebnis["abweichungen"]] == [("menge", "RAPS")]
    ab = zeile(engine, "SELECT lieferant_name, bestell_nr, abweichungen, notizen FROM public.einkauf_auftragsbestaetigungen "
                       "WHERE id = :id", id=ergebnis["id"])
    assert ab["lieferant_name"] == "Saatzucht Sued" and ab["bestell_nr"] == nummer
    assert "RAPS: Menge" in ab["abweichungen"] and "EDI" in ab["notizen"]
    # Erneute Zustellung derselben Nachricht legt nichts doppelt an.
    assert client.post("/api/v1/einkauf/auftragsbestaetigungen/edi-ordrsp", json={"nachricht": nachricht},
                       headers=kopf()).status_code == 409
    kaputt = client.post("/api/v1/einkauf/auftragsbestaetigungen/edi-ordrsp",
                         json={"nachricht": "UNH+1+ORDERS:D:96A:UN'"}, headers=kopf())
    assert kaputt.status_code == 422
