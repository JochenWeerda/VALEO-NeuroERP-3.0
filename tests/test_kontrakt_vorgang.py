"""Kontrakt-Vorgang: Lesewege mit Zeilenform, Alarme vom Server, Kommandowege fuer Maske, CLI und MCP.

Was hier vorher anders war (handgebaute Seiten agrar/kontrakt-*, bis 08.11.2026):

1. **Bearbeiter aus dem Rumpf.** Fixierung, Mahnung, Uebergabe und Storno schrieben ``bediener or "KIM"``; die
   Seiten schickten keinen Bediener, also stand "KIM" in jeder Zeile. Jetzt kommt er aus dem Token.
2. **Stornierte Kontrakte wurden gemahnt.** Der Mahnkandidaten-Filter verglich mit ``'storniert'``; der Status
   steht gross (``STORNIERT``), der Vergleich traf nie.
3. **Alarme nur im Browser.** Das Alarm-Dashboard rechnete sie aus der Kontraktliste; CLI und MCP sahen sie nie.
4. **Keine Pruefung ohne Wirkung.** Ein Trockenlauf meldet, was der Fachweg ablehnen wuerde, und schreibt nichts.

Geprueft gegen die Pruefstand-Datenbank (``TEST_DATABASE_URL``); ohne sie wird uebersprungen, nicht gruen gewertet.
"""
from __future__ import annotations

from datetime import date, timedelta
import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS = f"kv-a-{uuid.uuid4().hex[:6]}"
FREMD = f"kv-b-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/kontrakt-vorgang"

MATIF = str(uuid.uuid4())       # ueberfaellig, MATIF, 100 t, 50 t abgerufen
STORNIERT = str(uuid.uuid4())   # ueberfaellig und offen, aber storniert: nie mahnen
FREMDER = str(uuid.uuid4())     # anderer Mandant
ZEILE = str(uuid.uuid4())
BEWEGUNG_1 = str(uuid.uuid4())
BEWEGUNG_2 = str(uuid.uuid4())
NR = f"K-{uuid.uuid4().hex[:5].upper()}"

_PRUEFER = {"sub": "pruefer-kv", "roles": ["KONTRAKT_BEARBEITEN", "KONTRAKT_LESEN", "KONTRAKT_ADMIN"]}


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(text(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema='domain_ops' "
                "AND table_name IN ('kon_contract','kon_contract_fixing','kon_contract_reminder','matif_quote')"
            )).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if vorhanden != 4:
        pytest.skip("Kontrakttabellen fehlen im Pruefstand")
    return motor


@pytest.fixture(scope="module", autouse=True)
def bestand(engine):
    from sqlalchemy import text

    vorgestern = date.today() - timedelta(days=2)
    with engine.begin() as v:
        for haus in (HAUS, FREMD):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                      {"id": haus, "n": f"Pruefhandel {haus}"})
        for kid, haus, nr, status in ((MATIF, HAUS, NR, "OFFEN"), (STORNIERT, HAUS, NR + "-S", "STORNIERT"),
                                      (FREMDER, FREMD, NR + "-F", "OFFEN")):
            v.execute(text(
                "INSERT INTO domain_ops.kon_contract (contract_id, tenant_id, contract_no, contract_type, party_id, "
                " contract_date, valid_from, valid_to, quantity_type, total_quantity, unit, allow_overdelivery, status, "
                " pricing_model, premium_value) "
                "VALUES (:id, :t, :nr, 'EINKAUF', 'P-KV', '2026-01-01', '2026-01-01', :bis, 'GESAMTKONTRAKT', 100, 't', "
                " false, :st, 'matif', 10)"), {"id": kid, "t": haus, "nr": nr, "bis": vorgestern, "st": status})
            v.execute(text(
                "INSERT INTO domain_ops.kon_contract_line (line_id, contract_id, tenant_id, position_no, article_id, "
                " description1, qty_contract, is_bio, is_matif) "
                "VALUES (:lid, :cid, :t, 1, 'WEIZEN', 'Weizen B', 100, false, true)"),
                {"lid": ZEILE if kid == MATIF else str(uuid.uuid4()), "cid": kid, "t": haus})
        for mid, menge in ((BEWEGUNG_1, 30), (BEWEGUNG_2, 20)):
            v.execute(text(
                "INSERT INTO domain_ops.kon_contract_movement (movement_id, contract_id, line_id, tenant_id, "
                " movement_date, quantity, is_invoiced, is_archived, is_storniert) "
                "VALUES (:id, :cid, :lid, :t, now(), :q, false, false, false)"),
                {"id": mid, "cid": MATIF, "lid": ZEILE, "t": HAUS, "q": menge})
    yield
    with engine.begin() as v:
        for tabelle in ("kon_contract_reminder", "kon_contract_fixing", "kon_contract_movement", "kon_contract_line",
                        "kon_contract", "matif_quote"):
            v.execute(text(f"DELETE FROM domain_ops.{tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS, FREMD]})
        # Audit und Outbox der Kommandowege (run_delegated_mask_action) gehoeren zum Testmandanten.
        v.execute(text("DELETE FROM domain_crm.crm_action_audit_log WHERE tenant_id = ANY(:h)"), {"h": [HAUS, FREMD]})
        v.execute(text("DELETE FROM outbox_events WHERE tenant_id = ANY(:h)"), {"h": [HAUS, FREMD]})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS, FREMD]})


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def _pruefer():
    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: dict(_PRUEFER)
    yield
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def kopf(haus: str = HAUS) -> dict[str, str]:
    return {"X-Tenant-Id": haus, "Authorization": "Bearer dev-token"}


def aktion(client, pfad: str, **rumpf):
    return client.post(f"{WEG}/{pfad}", json=rumpf, headers=kopf())


# ── Lesewege ───────────────────────────────────────────────────────────────────

def test_kopf_traegt_erfuellung_fixierung_und_abrechnung(client):
    antwort = client.get(f"{WEG}/{MATIF}", headers=kopf())
    assert antwort.status_code == 200, antwort.text
    k = antwort.json()
    assert (k["id"], k["contract_no"], k["einheit"]) == (MATIF, NR, "t")
    assert (k["menge_kontrakt"], k["abgerufen"], k["offen"]) == (100, 50, 50)
    assert k["offen_abruf"] == 50 and k["abgerechnet"] == 0
    assert k["ueberfaellig"] is True


def test_kontraktnummer_fuehrt_zum_selben_kopf(client):
    assert client.get(f"{WEG}/{NR}", headers=kopf()).json()["id"] == MATIF


def test_fremder_mandant_sieht_den_kontrakt_nicht(client):
    assert client.get(f"{WEG}/{MATIF}", headers=kopf(FREMD)).status_code == 404
    ids = {z["id"] for z in client.get(f"{WEG}/uebersicht", headers=kopf(FREMD)).json()["items"]}
    assert MATIF not in ids and FREMDER in ids


def test_positionen_und_bewegungen_haben_eine_zeilenkennung(client):
    pos = client.get(f"{WEG}/{MATIF}/positionen", headers=kopf()).json()["items"]
    assert [(p["id"], p["abgerufen"], p["offen"], p["is_matif"]) for p in pos] == [(ZEILE, 50, 50, True)]
    bew = client.get(f"{WEG}/{MATIF}/bewegungen", headers=kopf()).json()["items"]
    assert {b["id"] for b in bew} == {BEWEGUNG_1, BEWEGUNG_2} and {b["status"] for b in bew} == {"offen"}


def test_stornierter_kontrakt_ist_kein_mahnkandidat(client):
    ids = {z["id"] for z in client.get(f"{WEG}/mahnkandidaten", headers=kopf()).json()["items"]}
    assert MATIF in ids
    assert STORNIERT not in ids


def test_alarme_kommen_vom_server(client):
    alarme = client.get(f"{WEG}/alarme", headers=kopf()).json()["items"]
    eigene = {a["alarm"] for a in alarme if a["kontrakt_id"] == MATIF}
    # Kein Einzelpreis und MATIF -> Fixierung ausstehend; keine Druckvorlage -> Drucksteuerung unvollstaendig.
    assert {"matif", "druck"} <= eigene
    assert all(a["kontrakt_id"] != STORNIERT for a in alarme)


def test_ohne_leserecht_kein_zugriff(client):
    from app.auth.deps import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: {"sub": "gast", "roles": ["LAGER_LESEN"]}
    assert client.get(f"{WEG}/uebersicht", headers=kopf()).status_code == 403


# ── Kommandowege ───────────────────────────────────────────────────────────────

def test_trockenlauf_fixiert_nichts(client, engine):
    from sqlalchemy import text

    antwort = aktion(client, f"{MATIF}/actions/fixieren", _mode="dryRun", menge=10, matif_preis=210)
    assert antwort.status_code == 200 and antwort.json()["success"] is True, antwort.text
    with engine.connect() as c:
        assert c.execute(text("SELECT count(*) FROM domain_ops.kon_contract_fixing WHERE contract_id = :k"),
                         {"k": MATIF}).scalar() == 0


def test_fixieren_schreibt_den_bearbeiter_aus_dem_token(client, engine):
    from sqlalchemy import text

    antwort = aktion(client, f"{MATIF}/actions/fixieren", menge=40, matif_preis=210, praemie=12)
    assert antwort.json()["success"] is True, antwort.text
    with engine.connect() as c:
        bediener, menge, eff = c.execute(text(
            "SELECT bediener, quantity, effective_price FROM domain_ops.kon_contract_fixing WHERE contract_id = :k"),
            {"k": MATIF}).one()
    assert bediener == "pruefer-kv" and float(menge) == 40 and float(eff) == 222
    fix = client.get(f"{WEG}/{MATIF}/fixierungen", headers=kopf()).json()["items"]
    assert [(f["menge"], f["status"], f["bediener"]) for f in fix] == [(40, "aktiv", "pruefer-kv")]


def test_ueberfixieren_wird_abgelehnt(client):
    antwort = aktion(client, f"{MATIF}/actions/fixieren", menge=80, matif_preis=210).json()
    assert antwort["success"] is False and "übersteigt" in antwort["error"]


def test_storno_verlangt_einen_grund(client):
    antwort = aktion(client, f"bewegungen/{BEWEGUNG_2}/actions/stornieren").json()
    assert antwort["success"] is False and antwort["validationErrors"][0]["field"] == "_auditReason"
    antwort = aktion(client, f"bewegungen/{BEWEGUNG_2}/actions/stornieren", _auditReason="Doppelt erfasst").json()
    assert antwort["success"] is True, antwort


def test_uebergabe_rechnet_die_offenen_bewegungen_ab(client):
    antwort = aktion(client, f"{MATIF}/actions/abrechnung_uebergeben").json()
    assert antwort["success"] is True and "1 Bewegung" in antwort["summary"], antwort
    status = {b["id"]: b["status"] for b in client.get(f"{WEG}/{MATIF}/bewegungen", headers=kopf()).json()["items"]}
    assert status == {BEWEGUNG_1: "abgerechnet", BEWEGUNG_2: "storniert"}
    nochmal = aktion(client, f"{MATIF}/actions/abrechnung_uebergeben").json()
    assert nochmal["success"] is False and "Keine offenen" in nochmal["error"]


def test_mahnen_nur_wenn_faellig(client, engine):
    from sqlalchemy import text

    assert aktion(client, f"{MATIF}/actions/mahnen", text="Bitte abrufen").json()["success"] is True
    with engine.connect() as c:
        assert c.execute(text("SELECT bediener FROM domain_ops.kon_contract_reminder WHERE contract_id = :k"),
                         {"k": MATIF}).scalar() == "pruefer-kv"
    abgelehnt = aktion(client, f"{STORNIERT}/actions/mahnen").json()
    assert abgelehnt["success"] is False


def test_fremder_kontrakt_ist_fuer_kommandos_unbekannt(client):
    antwort = aktion(client, f"{FREMDER}/actions/fixieren", menge=1, matif_preis=200).json()
    assert antwort["success"] is False and "nicht gefunden" in antwort["error"]
