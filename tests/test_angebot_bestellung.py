"""Ein Angebot wird mit seinen Positionen genau einmal zur Bestellung.

Bis zum 07.10.2026 lasen alle Angebots-Wege Spalten, die keine Migration anlegt
(``angebots_nummer``, ``netto_summe``, ``artikel_name``, ``lieferzeit_tage``), und
``except: return None`` machte "nicht gefunden" daraus — in **jeder** Datenbank. Die
Umwandlung erfand eine Sammelposition statt die Angebotspositionen zu nehmen,
committete die Bestellung vor dem Angebotsstatus und konnte doppelt bestellen.
Darunter: Der Bestelldienst rief ``repo.save`` auf, eine Methode, die
``DocumentRepository`` nie hatte (42 Aufrufe in neun Diensten seit 15.05.2026).
"""

from __future__ import annotations

import json
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

HAUS_A = f"an-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"an-b-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/einkauf/angebote"
AKTION = "/api/v1/einkauf/angebote/{}/actions/bestellen"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM einkauf_angebote_positionen LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


def aufraeumen(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text(
            "DELETE FROM documents WHERE doc_type = 'purchase_order' AND data::jsonb->>'tenantId' = ANY(:h)"
        ), {"h": [HAUS_A, HAUS_B]})
        v.execute(text(
            "DELETE FROM einkauf_angebote_positionen WHERE angebot_id IN "
            "(SELECT id FROM einkauf_angebote WHERE tenant_id = ANY(:h))"
        ), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM einkauf_angebote WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        for tabelle in ("domain_crm.crm_action_audit_log", "public.outbox_events"):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
    yield
    aufraeumen(engine)


@pytest.fixture(autouse=True)
def leer(engine):
    aufraeumen(engine)
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def angebot(engine, haus: str, status: str = "offen", positionen: int = 2) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text(
            "INSERT INTO einkauf_angebote (id, tenant_id, lieferant_id, lieferant_name, angebotsnummer, "
            " gueltig_bis, gesamtbetrag, status) "
            "VALUES (:i, :h, 'L-7', 'Saatzucht Nord', :nr, CURRENT_DATE + 30, 1250, :s)"
        ), {"i": kennung, "h": haus, "nr": f"AN-{kennung[:6]}", "s": status})
        for nr in range(1, positionen + 1):
            v.execute(text(
                "INSERT INTO einkauf_angebote_positionen (id, angebot_id, pos_nr, artikel_nr, bezeichnung, "
                " menge, einheit, einheitspreis, gesamtpreis, lieferzeit_tage) "
                "VALUES (:i, :a, :p, :art, :bez, :m, 'dt', 25, :g, :lz)"
            ), {"i": str(uuid.uuid4()), "a": kennung, "p": nr, "art": f"ART-{nr}", "bez": f"Saatweizen Sorte {nr}",
                "m": 10 * nr, "g": 250 * nr, "lz": 5 + nr})
    return kennung


def bestellungen(engine, haus: str) -> list[dict]:
    from sqlalchemy import text

    with engine.connect() as v:
        zeilen = v.execute(text(
            "SELECT data FROM documents WHERE doc_type = 'purchase_order' AND data::jsonb->>'tenantId' = :h"
        ), {"h": haus}).scalars().all()
    return [z if isinstance(z, dict) else json.loads(z) for z in zeilen]


def status(engine, kennung: str) -> str:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text("SELECT status FROM einkauf_angebote WHERE id = :i"), {"i": kennung}).scalar()


class TestLesen:
    def test_ein_angebot_ist_lesbar(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        antwort = client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        assert antwort.text.count(f"AN-{kennung[:6]}") >= 1

    def test_die_liste_zeigt_die_eigenen_angebote(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        assert kennung in client.get(WEG, headers=kopf(HAUS_A)).text
        assert kennung not in client.get(WEG, headers=kopf(HAUS_B)).text

    def test_ein_fremdes_angebot_ist_unsichtbar(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404


class TestUmwandlung:
    def test_die_bestellung_traegt_die_positionen(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        antwort = client.post(f"{WEG}/{kennung}/convert-to-order", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        (bestellung,) = bestellungen(engine, HAUS_A)
        posten = [(i["description"], float(i["quantity"]), float(i["unitPrice"])) for i in bestellung["items"]]
        assert posten == [("Saatweizen Sorte 1", 10.0, 25.0), ("Saatweizen Sorte 2", 20.0, 25.0)]
        assert status(engine, kennung) == "IN_BESTELLUNG"

    def test_kein_zweites_mal(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        assert client.post(f"{WEG}/{kennung}/convert-to-order", headers=kopf(HAUS_A)).status_code == 200
        zweite = client.post(f"{WEG}/{kennung}/convert-to-order", headers=kopf(HAUS_A))
        assert zweite.status_code == 409, zweite.text
        assert len(bestellungen(engine, HAUS_A)) == 1

    def test_ohne_positionen_keine_erfundene_bestellung(self, engine, client):
        kennung = angebot(engine, HAUS_A, positionen=0)
        antwort = client.post(f"{WEG}/{kennung}/convert-to-order", headers=kopf(HAUS_A))
        assert antwort.status_code == 422, antwort.text
        assert bestellungen(engine, HAUS_A) == []
        assert status(engine, kennung) == "offen"

    def test_ein_fremder_mandant_bestellt_nicht(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        assert client.post(f"{WEG}/{kennung}/convert-to-order", headers=kopf(HAUS_B)).status_code == 404
        assert bestellungen(engine, HAUS_A) == [] and bestellungen(engine, HAUS_B) == []


class TestMaskenaktion:
    def test_bestellen_aus_der_maske_wirkt(self, engine, client):
        kennung = angebot(engine, HAUS_A)
        antwort = client.post(AKTION.format(kennung), json={"_mode": "execute"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is True, antwort
        assert len(bestellungen(engine, HAUS_A)) == 1
        assert status(engine, kennung) == "IN_BESTELLUNG"

    def test_trockenlauf_kennt_den_zustand(self, engine, client):
        kennung = angebot(engine, HAUS_A, status="IN_BESTELLUNG")
        antwort = client.post(AKTION.format(kennung), json={"_mode": "dryRun"}, headers=kopf(HAUS_A)).json()
        assert antwort["success"] is False
        assert bestellungen(engine, HAUS_A) == []

    def test_die_maske_zeigt_auf_den_weg(self):
        from app.core.screen_definitions import get_screen_definition

        aktion = next(a for a in get_screen_definition("einkauf/angebot")["actions"] if a["key"] == "bestellen")
        assert aktion.get("commandEndpoint") == "/api/v1/einkauf/angebote/{entity_id}/actions/bestellen"
        assert "stubReason" not in aktion


def test_das_dokumentenlager_kann_speichern():
    """42 Aufrufe in neun Diensten riefen ``repo.save`` — die Methode fehlte."""
    from app.documents.repository import DocumentRepository

    assert callable(getattr(DocumentRepository, "save", None))


def test_nicht_gefunden_hat_immer_entitaet_und_kennung():
    """50 Aufrufe gaben ``EntityNotFoundError`` nur einen Satz — die Klasse verlangt
    Entitaet und Kennung; jedes "nicht gefunden" wurde so zu 500 (bis 07.10.2026)."""
    import ast
    from pathlib import Path

    falsch = []
    for datei in Path("app").rglob("*.py"):
        baum = ast.parse(datei.read_text(encoding="utf-8-sig"))
        for knoten in ast.walk(baum):
            if (isinstance(knoten, ast.Call) and getattr(knoten.func, "id", getattr(knoten.func, "attr", None))
                    == "EntityNotFoundError" and len(knoten.args) + len(knoten.keywords) != 2):
                falsch.append(f"{datei}:{knoten.lineno}")
    assert falsch == []
