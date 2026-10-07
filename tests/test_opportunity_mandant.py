"""Opportunities gehoeren einem Mandanten; ihre Aktivitaeten landen, wo die Maske liest.

Bis zum 07.10.2026 fragte das Opportunity-Modul den Dienst crm-sales ohne Mandant
und las die lokale Ausweichtabelle ohne Filter: Lesen, Aendern, Loeschen und
Aktivitaet anlegen gingen ueber Mandantengrenzen. Die Liste nahm den Mandanten als
**optionalen** Filter (ohne ihn: alle), das Anlegen aus dem Rumpf. Aktivitaeten
wurden in eine Tabelle geschrieben, die keine Migration anlegt; der Reiter las aus
einer anderen, die auf frischer Datenbank fehlt.

Die crm-sales-Aufrufe sind hier "nicht erreichbar" — der lokale Weg ist
deterministisch; die Mandantenpruefung gilt fuer beide Quellen gleich.
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"op-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"op-b-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/crm/opportunities"
REITER = "/api/v1/mask-rollouts/crm/opportunity/{}/tabs/aktivitaeten"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            spalte = v.execute(text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema='domain_crm' "
                "AND table_name='activities' AND column_name='opportunity_id'"
            )).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not spalte:
        pytest.skip("Migration mandant_finanz_crm_20261007 nicht angewandt")
    return motor


@pytest.fixture(autouse=True)
def crm_sales_nicht_erreichbar(monkeypatch):
    from app.api.v1.endpoints import opportunities as modul

    gesendet: dict = {}

    async def weg(*_a, **_k):
        raise httpx.RequestError("crm-sales im Test nicht erreichbar")

    async def anlegen(daten):
        gesendet["anlegen"] = daten
        raise httpx.RequestError("crm-sales im Test nicht erreichbar")

    for name in ("crm_get_opportunity", "crm_list_opportunities", "crm_update_opportunity", "crm_delete_opportunity"):
        monkeypatch.setattr(modul, name, weg)
    monkeypatch.setattr(modul, "crm_create_opportunity", anlegen)
    return gesendet


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
    yield
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_crm.activities WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_crm.crm_opportunities WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def opportunity(engine, haus: str) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text(
            "INSERT INTO domain_crm.crm_opportunities (id, tenant_id, customer_id, title, stage, status) "
            "VALUES (:i, :h, :k, 'Weizenlieferung 2027', 'qualifiziert', 'open')"
        ), {"i": kennung, "h": haus, "k": str(uuid.uuid4())})
    return kennung


def aktivitaeten(engine, kennung: str) -> list[tuple]:
    from sqlalchemy import text

    with engine.connect() as v:
        return [tuple(z) for z in v.execute(text(
            "SELECT tenant_id, title, type FROM domain_crm.activities WHERE opportunity_id = :o"
        ), {"o": kennung})]


class TestLesen:
    def test_nur_der_eigene_mandant_sieht_die_opportunity(self, engine, client):
        kennung = opportunity(engine, HAUS_A)
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_A)).status_code == 200
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404

    def test_die_liste_filtert_immer_nach_dem_kontext(self, engine, client):
        kennung = opportunity(engine, HAUS_A)
        ids_b = [o["id"] for o in client.get(f"{WEG}/", headers=kopf(HAUS_B)).json()["items"]]
        assert kennung not in ids_b
        # Ein Query-Parameter waehlt keinen fremden Mandanten mehr.
        ids_b2 = [o["id"] for o in client.get(f"{WEG}/?tenant_id={HAUS_A}", headers=kopf(HAUS_B)).json()["items"]]
        assert kennung not in ids_b2
        ids_a = [o["id"] for o in client.get(f"{WEG}/", headers=kopf(HAUS_A)).json()["items"]]
        assert kennung in ids_a


class TestSchreiben:
    def test_fremder_mandant_aendert_und_loescht_nicht(self, engine, client):
        kennung = opportunity(engine, HAUS_A)
        assert client.put(f"{WEG}/{kennung}", headers=kopf(HAUS_B), json={"title": "x"}).status_code == 404
        assert client.delete(f"{WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404

    def test_anlegen_nimmt_den_mandanten_aus_dem_kontext(self, client, crm_sales_nicht_erreichbar):
        client.post(f"{WEG}/", headers=kopf(HAUS_A), json={
            "tenant_id": HAUS_B, "name": "Fremd gemeint", "customer_id": str(uuid.uuid4()),
        })
        assert crm_sales_nicht_erreichbar["anlegen"]["tenant_id"] == HAUS_A


class TestAktivitaet:
    def test_die_aktivitaet_landet_beim_mandanten_und_im_reiter(self, engine, client):
        kennung = opportunity(engine, HAUS_A)
        antwort = client.post(
            f"{WEG}/{kennung}/activities?activity_type=CALL&subject=Preis%20besprochen", headers=kopf(HAUS_A)
        )
        assert antwort.status_code == 201, antwort.text
        assert aktivitaeten(engine, kennung) == [(HAUS_A, "Preis besprochen", "CALL")]
        reiter = client.get(REITER.format(kennung), headers=kopf(HAUS_A))
        assert reiter.status_code == 200, reiter.text
        assert "Preis besprochen" in reiter.text

    def test_ein_fremder_mandant_legt_keine_aktivitaet_an(self, engine, client):
        kennung = opportunity(engine, HAUS_A)
        antwort = client.post(f"{WEG}/{kennung}/activities?subject=Fremd", headers=kopf(HAUS_B))
        assert antwort.status_code == 404
        assert aktivitaeten(engine, kennung) == []

    def test_der_reiter_zeigt_keine_fremden_aktivitaeten(self, engine, client):
        kennung = opportunity(engine, HAUS_A)
        client.post(f"{WEG}/{kennung}/activities?subject=Intern", headers=kopf(HAUS_A))
        reiter = client.get(REITER.format(kennung), headers=kopf(HAUS_B))
        assert "Intern" not in reiter.text


def test_kein_weg_nimmt_den_mandanten_aus_dem_query():
    from pathlib import Path

    quelle = Path("app/api/v1/endpoints/opportunities.py").read_text(encoding="utf-8")
    assert "tenant_id: Optional[str] = Query(" not in quelle
    # Jede Abfrage nach einer Opportunity-Kennung traegt den Mandanten mit.
    assert 'WHERE id = :oid"' not in quelle
    assert "WHERE id = :oid\n" not in quelle
